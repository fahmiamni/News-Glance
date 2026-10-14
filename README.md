# glance-news

A single [Glance](https://github.com/glanceapp/glance) dashboard combining all news dashboards into one instance, with four pages (tabs in the top navigation):

| Page | Content |
|---|---|
| **Malaysia** | Malaysia Watch searches (politics, economy, courts, Borneo), top wires (Malay Mail, NST, FMT), in-depth (The Star, Malaysiakini) + business (The Edge, Bursa) tab groups, top stories cards, Google News Top Stories |
| **AI & Tech News** | AI Watch searches (industry, labs, chips, policy), top wires (TechCrunch, The Verge, Ars Technica), AI In Depth (TechCrunch AI, The Decoder) + Dev & Open Source (Hacker News, GitHub Blog) tab groups, tech headline cards, Google News Top Stories |
| **World News** | World In Depth (BBC, Guardian) + Global Perspectives (France 24, DW) tab groups, headline cards (Al Jazeera, Google News World), Google News Top Stories, breaking wires (Sky, NBC), in depth (NPR, UN, CBS) |
| **Middle East** | US-Iran conflict watch searches, top wires (Sky, NBC, France 24), Iran In Depth (Guardian, The Cradle) + Diplomacy & Region (MEE, Guardian ME, CNN) tab groups, Middle East headline cards (Al Jazeera, BBC), Google News (Middle East, Top Stories) group |

Shared across every page: a markets banner across the top (KLCI, USD/MYR, S&P 500, FTSE 100, Nikkei 225, Gold); search bar with `!g` / `!yt` / `!w` bangs, world clocks (Kuala Lumpur, New York, London, Tokyo) and Kuala Lumpur weather in the left column; calendar in the right column.

Shared widgets are defined **once** as YAML anchors at the top of `config/glance.yml` and reused via aliases — edit the anchor to change every page.

## Run

```sh
docker compose up -d
```

Then open http://localhost:8082

## Update

The image is pinned to a specific version in `docker-compose.yml`. To upgrade:

```sh
# edit the image tag in docker-compose.yml first
docker compose pull && docker compose up -d
```

Config changes (`config/glance.yml`) auto-reload without restarting.

## Image injection

Google News and Al Jazeera RSS feeds carry no per-article images, so Glance shows a favicon placeholder on the headline cards. The `image-injector` sidecar fixes that: it proxies the banner feeds, resolves each article's real URL (including Google News redirects), fetches the page's `og:image`, and re-serves the feed with `media:thumbnail` tags. Images are cached 6 h, feeds 10 min; enrichment runs in the background, so brand-new articles may show placeholders for a few minutes. If the injector is down, widgets show a red dot but everything else keeps working.

```sh
docker compose up -d --build   # first run / after changing the injector
```

The injector is only reachable inside the Docker network — it has no published port.

## Configure

Edit `config/glance.yml` — widget docs: https://github.com/glanceapp/glance/blob/main/docs/configuration.md

If you expose the dashboard beyond localhost, add the `auth` block (hashed passwords supported): https://github.com/glanceapp/glance/blob/main/docs/configuration.md#authentication
