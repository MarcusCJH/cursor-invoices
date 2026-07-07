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

### 4. Report the result

Tell the user which files were saved and where.

## All commands

| Command | Effect |
|---|---|
| `make install` | Install Playwright browser (once per machine) |
| `make run` | Download receipts |
| `make logout` | Clear saved session — next run will prompt login again |
