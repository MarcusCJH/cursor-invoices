---
name: download-cursor-invoices
description: Use when the user wants to download, save, or retrieve their Cursor.com subscription invoices or receipts as PDF files.
---

# Download Cursor Invoices

## Steps to execute

### 1. Ensure the script is present

Check that `download_cursor_invoices.py` exists. If not, tell the user to run from inside the `cursor-invoices` folder.

### 2. Check Playwright is installed

```bash
make install
```

Only needed once per machine.

### 3. Run

```bash
make run
```

- First run: a browser opens for Cursor login — user signs in with Google, window closes automatically.
- If `.sharepoint.env` is configured: after downloading, a browser opens for SharePoint login on first run — user signs in with their work account. Subsequent runs are fully headless.

### 4. Report the result

Tell the user which files were saved and where, and whether they were uploaded to SharePoint.

## Commands

| Command | Effect |
|---|---|
| `make install` | Install Playwright browser (once per machine) |
| `make run` | Download receipts and upload to SharePoint if configured |
| `make logout` | Reset Cursor session |
| `make sharepoint-logout` | Reset SharePoint session |
| `make test-upload` | Upload a dummy receipt to `Receipts/2069/01. January` |

## SharePoint setup (if not yet configured)

1. `cp .sharepoint.env.example .sharepoint.env`
2. Set `SHAREPOINT_SITE_URL` in `.sharepoint.env`
3. `make test-upload` to verify before a real run