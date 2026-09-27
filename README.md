# LedgerLite

**Sell-ready invoicing toolkit** from Operator Pages.

A small, sharp product you can use internally or sell as a digital kit:

- Python CLI that turns JSON into a computed invoice
- Excel invoice workbook with live formulas
- Word master service agreement
- Sample PDF invoice
- Sales pitch deck
- Pricing one-pager

## Quick start

```bash
python3 src/ledgerlite.py --json samples/invoice-001.json
```

Write a text invoice and computed JSON:

```bash
python3 src/ledgerlite.py --json samples/invoice-001.json \
  --out samples/invoice-001.txt \
  --dump-json samples/invoice-001.computed.json
```

## What you can sell

| SKU | Price suggestion | Includes |
|-----|------------------|----------|
| Starter | $49 | Excel + Word templates |
| Pro | $149 | + CLI + PDF branding + deck |
| Agency | $399 | + reseller rights for client-facing invoices |

Position it to freelancers, trades, and local operators who hate QuickBooks.

## Brand

Operator Pages LLC — Missouri, USA  
https://operatorpages.com
