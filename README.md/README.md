# Companies House Lead Engine

Automated lead intelligence for UK accountancy practices.

Pulls daily filing data from the Companies House API, scores each company 0–100 for fit, enriches with region and age data, and exports a clean CSV with ready-to-use outreach lines — delivered weekly by email.

## What it produces

- Company name, incorporation date, region
- Lead score 0–100 with plain-English reason
- Pre-written outreach line per company
- Exported as a clean CSV, delivered by email via n8n

## Sample output

| Company Name | Region | Score | Priority | Suggested Outreach |
|---|---|---|---|---|
| Frank AI Limited | London | 85 | high | Hi, I noticed Frank AI Limited was recently incorporated — tech startups often need specialist advice on R&D tax credits from day one. Would you be open to a brief chat? |
| Jimjam AI Ltd | London | 80 | high | Hi, I noticed Jimjam AI Ltd was recently incorporated — tech startups often need specialist advice on R&D tax credits from day one. Would you be open to a brief chat? |
| Lumière Body Studio Ltd | London | 70 | medium | Hi, I noticed Lumière Body Studio Ltd was recently incorporated — new London businesses often benefit from early advice on company structure and tax planning. |

## Who it is for

Independent accountancy practices (1–15 staff) in the UK who want a consistent, targeted pipeline of new business prospects without manual searching.

## Stack

Python 3 · Companies House API · pandas · n8n · dotenv

## Contact

aaronakoto2.@gmail.com
```
