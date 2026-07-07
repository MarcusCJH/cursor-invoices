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

### 4. Report the result

Tell the user which files were saved and where.

## Flags

| Flag | Effect |
|---|---|
| `--logout` | Clears the saved session — next run will prompt login again |
| `--install-browser` | Installs Playwright's Chromium (run once per machine) |
| `[output_dir]` | Save PDFs to a specific directory instead of current folder |
