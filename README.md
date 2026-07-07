# cursor-invoices

Downloads all your Cursor.com subscription invoices as PDFs.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — no other setup needed

## First-time setup (once per machine)

```bash
uv run download_cursor_invoices.py --install-browser
```

## Usage

```bash
# Save PDFs to current directory
uv run download_cursor_invoices.py

# Save to a specific directory
uv run download_cursor_invoices.py ~/Documents/cursor-invoices
```

A browser window opens — log in to Cursor normally. The script finds all your invoices and downloads them as PDFs.

## Claude Code users

Open this folder in Claude Code and run:

```
/download-cursor-invoices
```

The skill is bundled in `.claude/skills/` and loads automatically.

## Reset login session

```bash
uv run download_cursor_invoices.py --logout
```

Clears the saved browser profile — next run will prompt for login again. Useful when switching accounts or if the session behaves unexpectedly.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Executable doesn't exist` | Run `--install-browser` |
| No invoices found | Navigate to Settings → Billing manually, then press Enter |
| PDF download 403 | Re-run — invoice URLs expire |
