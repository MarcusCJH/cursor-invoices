---
name: download-cursor-invoices
description: Use when the user wants to download, save, or retrieve their Cursor.com subscription invoices or receipts as PDF files.
---

# Download Cursor Invoices

## Steps to execute

### 1. Ensure the script is present

Check that `download_cursor_invoices.py` exists in the current directory. If not, tell the user to run this from inside the `cursor-invoices` folder.

### 2. Check if Playwright Chromium is installed

Run:
```bash
uv run download_cursor_invoices.py --install-browser
```

Only needed once per machine. If it's already installed this is a no-op.

### 3. Run the script

```bash
uv run download_cursor_invoices.py
```

- If `cursor_browser_profile/` does not exist: a browser window will open for one-time login. Tell the user to log in with Google and wait — the window closes automatically.
- Subsequent runs: fully headless, no browser window.
- If `.sharepoint.env` is configured and `sharepoint_browser_profile/` exists, PDFs are uploaded to SharePoint automatically after downloading.

### 4. Report the result

Tell the user which files were saved and where, and whether they were uploaded to SharePoint.

## Flags

| Flag | Effect |
|---|---|
| `--install-browser` | Install Playwright's Chromium (run once per machine) |
| `--logout` | Clear the Cursor session — next run will prompt login again |
| `--sharepoint-login` | Open a browser for one-time SharePoint login (saves session) |
| `--sharepoint-logout` | Clear the saved SharePoint session |
| `--test-upload` | Upload a dummy receipt to `Receipts/2069/01. January` to verify SharePoint |
| `--no-upload` | Skip SharePoint upload for this run |
| `[output_dir]` | Save PDFs to a specific directory instead of current folder |

## SharePoint setup (if not yet configured)

1. Check if `.sharepoint.env` exists. If not, run: `cp .sharepoint.env.example .sharepoint.env`
2. Edit `.sharepoint.env` and set `SHAREPOINT_SITE_URL` to the team's SharePoint site
3. Run `--sharepoint-login` to authenticate — opens a browser, user signs in with work account
4. Run `--test-upload` to verify the integration before doing a real run