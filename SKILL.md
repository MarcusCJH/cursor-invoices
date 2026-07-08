---
name: download-cursor-invoices
description: Use when the user wants to download, save, or retrieve their Cursor.com subscription invoices or receipts as PDF files.
---

# Download Cursor Invoices

## Steps to execute

### 1. Ensure the script is present

Check that `cursor_invoices.py` exists. If not, tell the user to run from inside the `cursor-invoices` folder.

### 2. Install if needed

```bash
make install
```

One-time setup — installs the `cursor-invoices` command, Playwright Chromium, and SharePoint config. Skip if already done.

### 3. Run

```bash
make run
```

- First run: a browser opens for Cursor login — user signs in with Google, window closes automatically.
- If `.sharepoint.env` is configured: after downloading, a browser opens for SharePoint login on first run. Subsequent runs are fully headless.

### 4. Report the result

Tell the user which files were saved and where, and whether they were uploaded to SharePoint.

## Quick reference

| Command | Effect |
|---|---|
| `make install` | One-time setup |
| `make uninstall` | Remove tool, sessions, and SharePoint config |
| `make run` | Download receipts |
| `make logout` | Reset Cursor session |
| `make sharepoint-logout` | Reset SharePoint session |
| `make test-upload` | Upload a dummy receipt to verify SharePoint |
| `cursor-invoices --help` | Show all CLI flags |