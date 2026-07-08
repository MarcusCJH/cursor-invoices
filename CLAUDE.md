# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Python script (`download_cursor_invoices.py`) that downloads Cursor.com subscription invoices as PDFs and optionally uploads them to SharePoint. No package.json, no pyproject.toml — `uv` handles dependencies inline via PEP 723 script metadata.

## Commands

```bash
make install              # install Playwright Chromium (once per machine)
make run                  # download invoices + upload to SharePoint if configured
make logout               # reset Cursor session
make sharepoint-logout    # reset SharePoint session
make test-upload          # upload a dummy receipt to Receipts/2069/01. January
make cron-install         # schedule for 1st of each month at 9am
make cron-install DAY=5   # schedule for a specific day
make cron-status
make cron-uninstall
```

## Claude Code skill

The `/download-cursor-invoices` skill is bundled in `.claude/skills/` and loads automatically.

## SharePoint configuration

Copy `.sharepoint.env.example` to `.sharepoint.env` (gitignored) and set `SHAREPOINT_SITE_URL`. No Azure subscription needed — auth uses a saved Playwright browser session.

## Architecture

The script runs in three phases:

1. **Cursor login** (visible browser, one-time): opens a Chromium window to authenticate. Session saved to `cursor_browser_profile/` (gitignored).

2. **Scrape + download** (headless): navigates to `cursor.com/settings` and `/dashboard/billing`, finds Stripe invoice URLs, clicks "Download receipt" on each.

3. **SharePoint upload** (headless, optional): if `.sharepoint.env` is present, uploads PDFs via SharePoint REST API. On first run the browser opens for SharePoint login — subsequent runs are headless. Destination folder `Shared Documents/{RECEIPTS_FOLDER}/{year}/{MM}. {MonthName}` is created automatically.

PDFs are named `{username}_receipt_{YYYYMMDD}_{index:02d}.pdf`.