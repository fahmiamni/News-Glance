import base64
import html as html_lib
import json
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import feedparser
import requests
from flask import Flask, Response, request
from waitress import serve
from xml.sax.saxutils import escape, quoteattr

FEED_TTL = 10 * 60
IMAGE_TTL = 6 * 3600
NEGATIVE_TTL = 1 * 3600
DECODE_TTL = 24 * 3600
OG_TIMEOUT = 8
UPSTREAM_TIMEOUT = 15
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("image-injector")

app = Flask(__name__)
session = requests.Session()
session.headers.update({"User-Agent": UA})
pool = ThreadPoolExecutor(max_workers=12)
lock = threading.Lock()

feeds = {}
images = {}
decodes = {}
inflight = set()


def fetch_upstream(url):
    r = session.get(url, timeout=UPSTREAM_TIMEOUT)
    r.raise_for_status()
    return r.text


def parse_items(xml_text):
    parsed = feedparser.parse(xml_text)
    items = []
    for e in parsed.entries:
        link = e.get("link") or ""
        if not link:
            continue
        src = e.get("source")
        items.append({
            "title": (e.get("title") or "").strip(),
            "link": link,
            "pub": (e.get("published") or e.get("updated") or "").strip(),
            "source": (src.get("title") or "") if src else "",
        })
    return items


def has_fresh_image(link):
    with lock:
        v = images.get(link)
    if not v:
        return False
    ttl = IMAGE_TTL if v["value"] else NEGATIVE_TTL
    return time.time() - v["ts"] < ttl


def decode_b64(gn_id):
    try:
        pad = "=" * (-len(gn_id) % 4)
        raw = base64.urlsafe_b64decode(gn_id + pad)
        m = re.search(rb"https?://[!-~]+", raw)
        if m:
            return m.group(0).decode("ascii", "ignore")
    except Exception:
        pass
    return None


def decode_batchexecute(gn_id):
    try:
        page = session.get("https://news.google.com/rss/articles/" + gn_id, timeout=10)
        sig = re.search(r'data-n-a-sg="([^"]+)"', page.text)
        ts = re.search(r'data-n-a-ts="(\d+)"', page.text) or re.search(r'data-n-a-timestamp="(\d+)"', page.text)
        if not sig or not ts:
            return None
        req = ('["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,'
               'null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"'
               + gn_id + '",' + ts.group(1) + ',"' + sig.group(1) + '"]')
        r = session.post(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data={"f.req": json.dumps([[["Fbv4je", req, None, "generic"]]])},
            timeout=10)
        seg = r.text[r.text.find("garturlres"):][:4000]
        i = seg.find("http")
        if i == -1:
            return None
        j = i
        while j < len(seg):
            if seg[j] == '"':
                break
            if seg[j] == "\\" and j + 1 < len(seg) and seg[j + 1] == '"':
                break
            j += 1
        url = seg[i:j].replace("\\/", "/").replace("\\u002F", "/")
        if url.startswith("http"):
            return url
    except Exception as e:
        log.warning("batchexecute failed for %s: %s", gn_id[:40], e)
    return None


def resolve_link(link):
    m = re.match(r"https://news\.google\.com/rss/articles/([^?/]+)", link)
    if not m:
        return link
    gn_id = m.group(1)
    with lock:
        v = decodes.get(gn_id)
    if v and time.time() - v["ts"] < DECODE_TTL:
        return v["value"]
    url = decode_b64(gn_id)
    if not url:
        url = decode_batchexecute(gn_id)
    with lock:
        decodes[gn_id] = {"value": url, "ts": time.time()}
    return url


def fetch_og_image(url):
    if not url or not url.startswith("http"):
        return None
    try:
        r = session.get(url, timeout=OG_TIMEOUT)
        for tag in re.findall(r"<meta[^>]+>", r.text[:300000]):
            prop = re.search(
                r'(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image)["\']',
                tag, re.I)
            if not prop:
                continue
            content = re.search(r'content=["\']([^"\']+)["\']', tag, re.I)
            if content:
                return html_lib.unescape(content.group(1))
    except Exception:
        pass
    return None


def enrich(link):
    with lock:
        if link in inflight:
            return
        inflight.add(link)
    try:
        publisher = resolve_link(link)
        img = fetch_og_image(publisher)
        with lock:
            images[link] = {"value": img, "ts": time.time()}
        if img:
            log.info("image ok %s", publisher[:100])
        else:
            log.info("no image for %s", (publisher or link)[:100])
    except Exception as e:
        log.warning("enrich failed %s: %s", link[:80], e)
    finally:
        with lock:
            inflight.discard(link)


def schedule_enrichment(items):
    for it in items:
        if not has_fresh_image(it["link"]):
            pool.submit(enrich, it["link"])


def build_rss(items):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">',
        "<channel><title>Image-injected feed</title><link>http://localhost</link>"
        "<description>Feed with og:image thumbnails injected</description>",
    ]
    for it in items:
        parts.append("<item>")
        parts.append("<title>%s</title>" % escape(it["title"]))
        parts.append("<link>%s</link>" % escape(it["link"]))
        parts.append('<guid isPermaLink="false">%s</guid>' % escape(it["link"]))
        if it["pub"]:
            parts.append("<pubDate>%s</pubDate>" % escape(it["pub"]))
        if it["source"]:
            parts.append("<source>%s</source>" % escape(it["source"]))
        if has_fresh_image(it["link"]):
            with lock:
                img = images[it["link"]]["value"]
            if img:
                a = quoteattr(img)
                parts.append('<media:content url=%s medium="image"/>' % a)
                parts.append("<media:thumbnail url=%s/>" % a)
        parts.append("</item>")
    parts.append("</channel></rss>")
    return "\n".join(parts)


@app.get("/feed")
def feed():
    url = request.args.get("url", "").strip()
    if not re.match(r"^https?://", url):
        return ("bad url", 400)
    with lock:
        entry = feeds.get(url)
        fresh = bool(entry) and time.time() - entry["ts"] < FEED_TTL
    if not fresh:
        try:
            xml_text = fetch_upstream(url)
        except Exception as e:
            log.warning("upstream failed %s: %s", url, e)
            if entry is None:
                return ("upstream failed", 502)
            with lock:
                feeds[url]["ts"] = time.time()
        else:
            items = parse_items(xml_text)
            with lock:
                feeds[url] = {"items": items, "ts": time.time()}
            schedule_enrichment(items)
            entry = feeds[url]
    return Response(build_rss(entry["items"]), mimetype="application/rss+xml")


@app.get("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080, threads=16)
