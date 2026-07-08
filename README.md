# cursor-invoices

Downloads all your Cursor.com subscription invoices as PDFs and optionally uploads them to SharePoint.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — no other setup needed

## First-time setup (once per machine)

```bash
uv run download_cursor_invoices.py --install-browser
```

## Usage

```bash
# Download PDFs to current directory (and upload to SharePoint if configured)
uv run download_cursor_invoices.py

# Save to a specific directory
uv run download_cursor_invoices.py ~/Documents/cursor-invoices

# Skip SharePoint upload for this run
uv run download_cursor_invoices.py --no-upload
```

A browser window opens — log in to Cursor normally. The script finds all your invoices and downloads them as PDFs.

## Claude Code / Cursor users

Open this folder and run:

```
/download-cursor-invoices
```

The skill is bundled in `.claude/skills/` and `.cursor/skills/` and loads automatically.

## SharePoint upload (optional)

Automatically upload downloaded receipts to a SharePoint folder organised by year and month (e.g. `Receipts/2026/07. July`).

**One-time setup:**

1. Copy the config template: `cp .sharepoint.env.example .sharepoint.env`
2. Edit `.sharepoint.env` and set your SharePoint site URL
3. Authenticate: `make sharepoint-login` — opens a browser, sign in with your work account

**Verify it works:**

```bash
make test-upload   # uploads a dummy receipt to Receipts/2069/01. January
```

After that, `make run` downloads invoices and uploads them automatically.

```bash
make sharepoint-logout   # reset the SharePoint session
```

## Automatic monthly download

Schedule the script to run on the 1st of every month at 9am with a macOS notification on completion.

```bash
make cron-install    # set up the schedule
make cron-status     # check if it's active
make cron-uninstall  # remove it
```

Logs are written to `run.log` in the project folder.

> **Note:** The machine must be on and logged in at 9am on the 1st. If it's asleep or off, the job will be skipped until next month.

## Reset sessions

```bash
uv run download_cursor_invoices.py --logout             # reset Cursor session
uv run download_cursor_invoices.py --sharepoint-logout  # reset SharePoint session
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Executable doesn't exist` | Run `--install-browser` |
| No invoices found | Navigate to Settings → Billing manually, then press Enter |
| PDF download 403 | Re-run — invoice URLs expire |
| SharePoint upload fails | Run `make sharepoint-login` to refresh the session |