# cursor-invoices

Downloads all your Cursor.com subscription invoices as PDFs and optionally uploads them to SharePoint.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — no other setup needed

## Install

```bash
make install
```

One-time setup: installs the `cursor-invoices` command, installs Playwright Chromium, and walks you through SharePoint configuration.

```bash
make uninstall   # remove tool, session tokens, and SharePoint config
```

## Usage

```bash
make run        # download invoices (+ upload to SharePoint if configured)
make logout     # reset Cursor session
```

On first run a browser window opens — log in to Cursor. Subsequent runs are fully headless.

## SharePoint upload (optional)

Automatically uploads receipts to a SharePoint folder by year and month (e.g. `Receipts/2026/07. July`).

`make install` handles the setup — it copies `.sharepoint.env.example`, prompts for your SharePoint site URL, and saves it to `.sharepoint.env`. On the next `make run`, a browser opens for SharePoint login if no session exists — sign in with your work account and it saves automatically.

To configure manually after the fact:

1. Edit `SHAREPOINT_SITE_URL` in `.sharepoint.env`
2. `make sharepoint-login` to authenticate

**Verify before a real run:**

```bash
make test-upload        # uploads a dummy receipt to Receipts/2069/01. January
make sharepoint-logout  # reset the SharePoint session
```

## Without Make

```bash
# Install (once)
uv tool install .
uv run --with playwright python -m playwright install chromium
cp .sharepoint.env.example .sharepoint.env
# edit .sharepoint.env and set SHAREPOINT_SITE_URL

# Run
cursor-invoices

# Reset sessions
cursor-invoices --logout
cursor-invoices --sharepoint-logout

# Help
cursor-invoices --help
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
| `cursor-invoices: command not found` | `make install` |
| `Executable doesn't exist` (Playwright) | `make install` |
| No invoices found | Navigate to Settings → Billing manually, then press Enter |
| PDF download 403 | Re-run — invoice URLs expire |
| SharePoint upload fails | `make sharepoint-logout` then re-run |