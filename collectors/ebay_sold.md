# Breadup eBay UK Sold Collector

Uses Apify actor to scrape eBay UK sold listings.
Cost: ~$2/1K listings. Free tier: $5/mo credit.

## Setup

1. Sign up at apify.com (free, no credit card)
2. Get API token from Settings → API & Integrations
3. Set APIFY_TOKEN in .env

## Usage

```bash
# Collect sold prices for one category
python -m collectors.ebay_sold --query "technics turntable" --count 100

# Collect multiple categories
python -m collectors.ebay_sold --categories categories.txt

# Schedule daily via cron
0 6 * * * cd /home/box/datagarden && python -m collectors.ebay_sold --categories categories.txt
```

## Output

Saves to `forests/breadup/data/ebay_sold/YYYY-MM-DD.jsonl`

Each record:
```json
{
  "itemId": "377309614758",
  "title": "ASUS TUF Gaming RTX 3080 OC 10GB",
  "soldPrice": 163.34,
  "soldCurrency": "GBP",
  "endedAt": "2026-09-19T12:00:00.000Z",
  "condition": "Used",
  "keyword": "rtx 3080",
  "collected_at": "2026-09-19T18:00:00Z"
}
```
