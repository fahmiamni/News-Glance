# glance-news

A single [Glance](https://github.com/glanceapp/glance) dashboard combining all news dashboards into one instance, with four pages (tabs in the top navigation):

| Page | Content |
|---|---|
| **Malaysia** | Malaysia Watch searches (politics, economy, courts, Borneo), top wires (Malay Mail, NST, FMT), in-depth (The Star, Malaysiakini) + business (The Edge, Bursa) tab groups, top stories cards, KL + Singapore weather, KLCI/MYR/banks/palm-oil markets |
| **AI & Tech News** | AI Watch searches (industry, labs, chips, policy), top wires (TechCrunch, The Verge, Ars Technica), AI In Depth (TechCrunch AI, The Decoder) + Dev & Open Source (Hacker News, GitHub Blog) tab groups, tech headline cards, San Francisco + Seattle weather, big-tech markets |
| **World News** | World In Depth (BBC, Guardian) + Global Perspectives (France 24, Al Jazeera, DW) tab groups, headline cards (BBC, Guardian, AJ, France 24), breaking wires (AJ, Sky, NBC), world clocks, global markets |
| **Middle East** | US-Iran conflict watch searches, top wires (AJ, BBC ME, DW), Guardian Iran/ME, The Cradle, MEE, CNN, r/worldnews + r/geopolitics, Tehran/DC weather, oil & defense stocks |

Plus shared widgets per page: calendar, weather, markets.

## Run

```sh
docker compose up -d
```

Then open http://localhost:8082

## Configure

Edit `config/glance.yml` — widget docs: https://github.com/glanceapp/glance/blob/main/docs/configuration.md
