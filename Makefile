.PHONY: install run logout help

help:
	@echo "Usage:"
	@echo "  make install   Install Playwright browser (once per machine)"
	@echo "  make run       Download invoices and save receipts"
	@echo "  make logout    Reset Cursor login session"

install:
	uv run download_cursor_invoices.py --install-browser

run:
	uv run download_cursor_invoices.py

logout:
	uv run download_cursor_invoices.py --logout
