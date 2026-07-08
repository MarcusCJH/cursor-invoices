---
name: download-cursor-invoices
description: Use when the user wants to download, save, or retrieve their Cursor.com subscription invoices or receipts as PDF files.
---

# Download Cursor Invoices

## Steps to execute

### 1. Ensure the script is present

Check that `download_cursor_invoices.py` exists in the current directory. If not, tell the user to run this from inside the `cursor-invoices` folder.

### 2. Check if Playwright Chromium is installed

```bash
make install
```

Only needed once per machine.

### 3. Run the script

```bash
make run
```

- If `cursor_browser_profile/` does not exist: a browser window opens for one-time login. Tell the user to log in with Google — the window closes automatically once done.
- Subsequent runs: fully headless, no browser window.
- If `.sharepoint.env` is configured and `sharepoint_browser_profile/` exists, PDFs are uploaded to SharePoint automatically after downloading.

### 4. Report the result

Tell the user which files were saved and where, and whether they were uploaded to SharePoint.

## All commands

| Command | Effect |
|---|---|
| `make install` | Install Playwright browser (once per machine) |
| `make run` | Download receipts (and upload to SharePoint if configured) |
| `make logout` | Clear Cursor session — next run will prompt login again |
| `make sharepoint-login` | One-time SharePoint login (opens browser) |
| `make sharepoint-logout` | Clear the saved SharePoint session |
| `make test-upload` | Upload a dummy receipt to `Receipts/2069/01. January` to verify SharePoint |

## SharePoint setup (if not yet configured)

1. Check if `.sharepoint.env` exists. If not, run: `cp .sharepoint.env.example .sharepoint.env`
2. Edit `.sharepoint.env` and set `SHAREPOINT_SITE_URL` to the team's SharePoint site
3. Run `make sharepoint-login` to authenticate — opens a browser, user signs in with work account
4. Run `make test-upload` to verify the integration before doing a real run