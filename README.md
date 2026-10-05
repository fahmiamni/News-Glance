# glance-news

A single [Glance](https://github.com/glanceapp/glance) dashboard combining all news dashboards into one instance, with four pages (tabs in the top navigation):

| Page | Content |
|---|---|
| **Malaysia** | Malaysia Watch searches (politics, economy, courts, Borneo), top wires (Malay Mail, NST, FMT), in-depth (The Star, Malaysiakini) + business (The Edge, Bursa) tab groups, top stories cards, KL + Singapore weather, KLCI/MYR/banks/palm-oil markets |
| **Local** | Malaysia breaking news (Google News, Malaysiakini, FMT), local headlines with thumbnails, AWANI/Bernama/Star videos, r/Malaysia + r/malaysians, BM feeds (Berita Harian, Utusan, Malaysiakini BM) |
| **World News** | BBC/Guardian/Al Jazeera/France 24 horizontal cards, breaking wires (AJ, Sky, NBC), YouTube live (BBC, AJ, DW, Sky, CNN), world clocks, global markets |
| **Middle East** | US-Iran conflict watch searches, top wires (AJ, BBC ME, DW), Guardian Iran/ME, The Cradle, MEE, CNN, r/worldnews + r/geopolitics, Tehran/DC weather, oil & defense stocks |

Plus shared widgets per page: calendar, weather (Kuala Lumpur), markets.

## Run

```sh
docker compose up -d
```

Then open http://localhost:8082

## Configure

Edit `config/glance.yml` — widget docs: https://github.com/glanceapp/glance/blob/main/docs/configuration.md
