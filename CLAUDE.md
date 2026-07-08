# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Python script (`cursor_invoices.py`) that downloads Cursor.com subscription invoices as PDFs and optionally uploads them to SharePoint. Packaged via `pyproject.toml` (setuptools) so it can be installed with `uv tool install`. Dependencies are also declared inline via PEP 723 script metadata for `uv run` usage.

## Commands

```bash
make install              # one-time setup: install tool + Playwright browser + SharePoint config
make uninstall            # remove tool, session tokens, and SharePoint config
make run                  # download invoices + upload to SharePoint if configured
make logout               # reset Cursor session
make sharepoint-logout    # reset SharePoint session
make test-upload          # upload a dummy receipt to Receipts/2069/01. January
make cron-install         # schedule for 1st of each month at 9am
make cron-install DAY=5   # schedule for a specific day
make cron-status
make cron-uninstall
```

## CLI flags (cursor-invoices command)

```bash
cursor-invoices                   # download invoices to current directory
cursor-invoices ~/receipts        # download to a specific directory
cursor-invoices --no-upload       # skip SharePoint upload this run
cursor-invoices --sharepoint-login   # authenticate SharePoint (opens browser)
cursor-invoices --sharepoint-logout  # reset SharePoint session
cursor-invoices --logout          # reset Cursor session
cursor-invoices --help            # show usage
```

## Claude Code skill

The `/download-cursor-invoices` skill is bundled in `.claude/skills/` and loads automatically.

## SharePoint configuration

`make install` handles first-time setup — copies `.sharepoint.env.example`, prompts for `SHAREPOINT_SITE_URL`, and saves to `.sharepoint.env` (gitignored). No Azure subscription needed — auth uses a saved Playwright browser session.

## Architecture

The script runs in three phases:

1. **Cursor login** (visible browser, one-time): opens a Chromium window to authenticate. Session saved to `~/.local/share/cursor-invoices/cursor_browser_profile/`.

2. **Scrape + download** (headless): navigates to `cursor.com/settings` and `/dashboard/billing`, finds Stripe invoice URLs, clicks "Download receipt" on each.

3. **SharePoint upload** (headless, optional): if `.sharepoint.env` is present (checked in CWD first, then `~/.config/cursor-invoices/`), uploads PDFs via SharePoint REST API. On first run the browser opens for SharePoint login — subsequent runs are headless. Session saved to `~/.local/share/cursor-invoices/sharepoint_browser_profile/`. Destination folder `Shared Documents/{RECEIPTS_FOLDER}/{year}/{MM}. {MonthName}` is created automatically.

PDFs are named `{username}_receipt_{YYYYMMDD}_{index:02d}.pdf`.