# cursor-invoices

Downloads all your Cursor.com subscription invoices as PDFs and optionally uploads them to SharePoint.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — no other setup needed

## First-time setup (once per machine)

```bash
make install
```

## Usage

```bash
make run        # download invoices (+ upload to SharePoint if configured)
make logout     # reset Cursor session
```

On first run a browser window opens — log in to Cursor. Subsequent runs are fully headless.

## SharePoint upload (optional)

Automatically uploads receipts to a SharePoint folder by year and month (e.g. `Receipts/2026/07. July`).

**Setup:**

1. `cp .sharepoint.env.example .sharepoint.env`
2. Set `SHAREPOINT_SITE_URL` in `.sharepoint.env`

That's it. On the next `make run`, a browser will open for SharePoint login if no session exists — sign in with your work account and it saves automatically.

**Verify before a real run:**

```bash
make test-upload   # uploads a dummy receipt to Receipts/2069/01. January
```

```bash
make sharepoint-logout   # reset the SharePoint session
```

## Automatic monthly download

```bash
make cron-install         # schedule for 1st of each month at 9am
make cron-install DAY=23  # or a specific day
make cron-status
make cron-uninstall
```

Logs are written to `run.log`. The machine must be on and logged in at the scheduled time.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Executable doesn't exist` | `make install` |
| No invoices found | Navigate to Settings → Billing manually, then press Enter |
| PDF download 403 | Re-run — invoice URLs expire |
| SharePoint upload fails | `make sharepoint-logout` then re-run |