# Marketplace Sources — Complete Inventory

## UK Electronics Marketplaces (Priority)

### 1. eBay UK
- **URL:** https://www.ebay.co.uk
- **Data:** Broken/working/parts prices, sold history
- **API:** Browse API (needs OAuth), or Apify actors ($5/mo free)
- **Status:** VPS blocked, use Apify
- **Apify actors:** kestrel/ebay-search-scraper, scrape.badger/ebay-search-scraper

### 2. CeX
- **URL:** https://uk.webuy.com
- **Data:** UK buy/sell/trade prices for phones, laptops, consoles, GPUs
- **API:** No public API (search page works, API blocked from VPS)
- **Status:** Collector built, needs non-VPS machine
- **Why:** UK's biggest used electronics dealer. Buy/sell spread = repair margin signal.

### 3. Back Market
- **URL:** https://www.backmarket.com
- **Data:** Professional refurbished prices (ceiling for repair value)
- **API:** Marketplace integration (access-dependent)
- **Status:** Not implemented

### 4. Cash Converters
- **URL:** https://www.cashconverters.co.uk
- **Data:** Local store buy/sell prices
- **API:** No (public web only)
- **Status:** Not implemented

### 5. MusicMagpie
- **URL:** https://www.musicmagpie.co.uk
- **Data:** Buy/sell prices for phones, laptops, consoles
- **API:** No (public web only)
- **Status:** Not implemented

## UK Trade Suppliers

### 6. Screwfix
- **URL:** https://www.screwfix.com
- **Data:** Trade pricing for power tools, electrical, EV charging
- **API:** No (public web)
- **Status:** Collector built, needs non-VPS machine

### 7. Toolstation
- **URL:** https://www.toolstation.com
- **Data:** Trade pricing for power tools, electrical
- **API:** No (public web)
- **Status:** Collector built, needs non-VPS machine

### 8. RS Components
- **URL:** https://www.rs-online.com
- **Data:** UK trade electronic components
- **API:** Yes (developer registration)
- **Status:** Needs API key

### 9. Farnell/element14
- **URL:** https://uk.farnell.com
- **Data:** UK/EU electronic components
- **API:** Yes (API key)
- **Status:** Needs API key

## Component Distributors

### 10. Mouser
- **URL:** https://www.mouser.com
- **Data:** Global component pricing, stock, lead times
- **API:** Yes (free 1000 calls/day)
- **Status:** Needs API key

### 11. DigiKey
- **URL:** https://www.digikey.com
- **Data:** Component pricing + substitutions
- **API:** Yes (OAuth)
- **Status:** Needs API key

### 12. TME
- **URL:** https://www.tme.eu
- **Data:** European component pricing
- **API:** Yes (developer portal)
- **Status:** Needs API key

### 13. PartsDB.io
- **URL:** https://www.partsdb.io
- **Data:** European distributor pricing (reichelt, Conrad)
- **API:** Yes (free 100/day, no credit card)
- **Status:** Collector built, needs API key

### 14. Omkar DigiKey Scraper
- **URL:** https://www.omkar.cloud/tools/digikey-scraper/
- **Data:** DigiKey component data
- **API:** Yes (free 100/month)
- **Status:** Collector built

## Robot Parts

### 15. RobotShop UK
- **URL:** https://uk.robotshop.com
- **Data:** Robot parts — actuators, servos, controllers
- **API:** No (public web)
- **Status:** Collector built, needs non-VPS machine

### 16. Unitree Official Shop
- **URL:** https://shop.unitree.com
- **Data:** OEM robot parts pricing
- **API:** No (public web)
- **Status:** Not implemented

### 17. Alibaba
- **URL:** https://www.alibaba.com
- **Data:** China OEM/aftermarket supply
- **API:** Partner route
- **Status:** Discovery only

### 18. AliExpress
- **URL:** https://www.aliexpress.com
- **Data:** Small-quantity aftermarket parts
- **API:** Terms apply
- **Status:** Not implemented

## Auction/Liquidation

### 19. BidSpotter
- **URL:** https://www.bidspotter.co.uk
- **Data:** Industrial liquidation auctions
- **API:** No (public web)
- **Status:** Not implemented

### 20. The Saleroom
- **URL:** https://www.the-saleroom.com
- **Data:** Auction house hammer prices
- **API:** Paid history
- **Status:** Not implemented

### 21. B-Stock
- **URL:** https://www.b-stock.com
- **Data:** Returns/overstock pallets
- **API:** Marketplace access
- **Status:** Not implemented

## Apify Actors (recommended for eBay + others)

| Actor | What | Cost |
|-------|------|------|
| kestrel/ebay-search-scraper | eBay search + listings | $5/mo free |
| scrape.badger/ebay-search-scraper | eBay search + browse | $5/mo free |
| webdatalabs/ebay-scraper-pro | eBay with TLS fingerprint | $5/mo free |
| hamzamihaidaniel/uk-product-safety-alerts-api | OPSS recalls | $5/mo free |

## Immediate Actions

1. **Register Apify** (free $5/mo) — unlocks eBay + OPSS
2. **Register PartsDB.io** (free, instant) — unlocks component pricing
3. **Run CeX collector** from non-VPS machine
