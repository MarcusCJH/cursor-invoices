SCRIPT_DIR := $(shell pwd)
UV         := $(shell which uv)
DAY        ?= 1

.PHONY: install run logout cron-install cron-uninstall cron-status help

help:
	@echo "Usage:"
	@echo "  make install             Install Playwright browser (once per machine)"
	@echo "  make run                 Download invoices and save receipts"
	@echo "  make logout              Reset Cursor login session"
	@echo "  make cron-install        Schedule on the 1st of each month (default)"
	@echo "  make cron-install DAY=23 Schedule on a specific day of the month"
	@echo "  make cron-uninstall      Remove the scheduled job"
	@echo "  make cron-status         Check if the scheduled job is active"

install:
	uv run download_cursor_invoices.py --install-browser

run:
	uv run download_cursor_invoices.py

logout:
	uv run download_cursor_invoices.py --logout

cron-install:
	@NOTIFY_OK="osascript -e 'display notification \"Receipts saved successfully\" with title \"Cursor Invoices\"'"; \
	NOTIFY_FAIL="osascript -e 'display notification \"Download failed — check run.log\" with title \"Cursor Invoices\"'"; \
	CRON_CMD="0 9 $(DAY) * * cd $(SCRIPT_DIR) && $(UV) run download_cursor_invoices.py >> $(SCRIPT_DIR)/run.log 2>&1 && $$NOTIFY_OK || $$NOTIFY_FAIL"; \
	(crontab -l 2>/dev/null | grep -v "download_cursor_invoices"; echo "$$CRON_CMD") | crontab -
	@echo "Cron job installed — runs on day $(DAY) of every month at 9:00am"
	@echo "Output log: $(SCRIPT_DIR)/run.log"

cron-uninstall:
	@(crontab -l 2>/dev/null | grep -v "download_cursor_invoices") | crontab -
	@echo "Cron job removed"

cron-status:
	@crontab -l 2>/dev/null | grep "download_cursor_invoices" \
		&& echo "Cron job is active" \
		|| echo "No cron job found — run 'make cron-install DAY=<day>' to set it up"
