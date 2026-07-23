SCRIPT_DIR := $(shell pwd)
UV         := $(shell which uv)
DAY        ?= 1

.PHONY: install uninstall run logout sharepoint-login sharepoint-logout test-upload cron-install cron-uninstall cron-status help

help:
	@echo "Usage:"
	@echo "  make install              One-time setup: install tool + browser + SharePoint config"
	@echo "  make uninstall            Remove tool, sessions, and SharePoint config"
	@echo "  make run                  Download invoices and save receipts"
	@echo "  make logout               Reset Cursor login session"
	@echo "  make sharepoint-login     Manually authenticate with SharePoint (auto on first run)"
	@echo "  make sharepoint-logout    Reset SharePoint session"
	@echo "  make test-upload          Upload a dummy receipt to Receipts/2069/01. January"
	@echo "  make cron-install         Schedule on the 1st of each month (default)"
	@echo "  make cron-install DAY=23  Schedule on a specific day of the month"
	@echo "  make cron-uninstall       Remove the scheduled job"
	@echo "  make cron-status          Check if the scheduled job is active"

install:
	@echo "→ Installing cursor-invoices…"
	uv tool install .
	@echo "→ Installing Playwright Chromium…"
	uv run --with playwright python -m playwright install chromium
	@if [ ! -f .sharepoint.env ]; then \
		cp .sharepoint.env.example .sharepoint.env; \
		printf "SharePoint site URL (press Enter to skip): "; \
		read url; \
		if [ -n "$$url" ]; then \
			sed -i '' "s|https://your-tenant.sharepoint.com/sites/your-site|$$url|" .sharepoint.env; \
			echo "Saved to .sharepoint.env — run 'make sharepoint-login' to authenticate."; \
		else \
			echo "Skipped — edit .sharepoint.env manually to enable SharePoint upload."; \
		fi; \
	else \
		echo ".sharepoint.env already exists — skipping SharePoint config."; \
	fi
	@echo "Done. Run 'make run' to download invoices."

uninstall:
	uv tool uninstall cursor-invoices
	rm -rf ~/.local/share/cursor-invoices/
	rm -rf ~/.config/cursor-invoices/
	rm -f .sharepoint.env
	@echo "cursor-invoices uninstalled and all session data removed."

run:
	uv sync --quiet
	uv run cursor_invoices.py

logout:
	uv run cursor_invoices.py --logout

sharepoint-login:
	uv run cursor_invoices.py --sharepoint-login

sharepoint-logout:
	uv run cursor_invoices.py --sharepoint-logout

test-upload:
	uv run cursor_invoices.py --test-upload

cron-install:
	@NOTIFY_OK="osascript -e 'display notification \"Receipts saved successfully\" with title \"Cursor Invoices\"'"; \
	NOTIFY_FAIL="osascript -e 'display notification \"Download failed — check run.log\" with title \"Cursor Invoices\"'"; \
	CRON_CMD="0 9 $(DAY) * * cd $(SCRIPT_DIR) && $(UV) run cursor_invoices.py >> $(SCRIPT_DIR)/run.log 2>&1 && $$NOTIFY_OK || $$NOTIFY_FAIL"; \
	(crontab -l 2>/dev/null | grep -v "cursor_invoices"; echo "$$CRON_CMD") | crontab -
	@echo "Cron job installed — runs on day $(DAY) of every month at 9:00am"
	@echo "Output log: $(SCRIPT_DIR)/run.log"

cron-uninstall:
	@(crontab -l 2>/dev/null | grep -v "cursor_invoices") | crontab -
	@echo "Cron job removed"

cron-status:
	@crontab -l 2>/dev/null | grep "cursor_invoices" \
		&& echo "Cron job is active" \
		|| echo "No cron job found — run 'make cron-install DAY=<day>' to set it up"