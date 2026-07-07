#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright",
# ]
# ///
"""
Download all Cursor.com invoices as receipts (PDFs).

Usage:
    uv run download_cursor_invoices.py [output_dir]

    # Or make it executable and run directly:
    chmod +x download_cursor_invoices.py
    ./download_cursor_invoices.py [output_dir]

First run on a new machine:
    uv run download_cursor_invoices.py --install-browser

Reset saved login session:
    uv run download_cursor_invoices.py --logout
"""

import asyncio
import getpass
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

PROFILE_DIR = Path(__file__).parent / "cursor_browser_profile"
BILLING_URL = "https://cursor.com/settings"

args = set(sys.argv[1:])

if "--install-browser" in args:
    subprocess.run(
        ["uv", "run", "--with", "playwright", "python", "-m", "playwright", "install", "chromium"],
        check=True,
    )
    sys.exit(0)

if "--logout" in args:
    import shutil
    if PROFILE_DIR.exists():
        shutil.rmtree(PROFILE_DIR)
        print("Session cleared. You'll be prompted to log in on the next run.")
    else:
        print("No saved session found.")
    sys.exit(0)

output_args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUTPUT_DIR = Path(output_args[0]) if output_args else Path(".")


async def open_context(pw, headless: bool):
    kwargs = dict(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
    )
    try:
        return await pw.chromium.launch_persistent_context(
            str(PROFILE_DIR), channel="chrome", **kwargs
        )
    except Exception:
        return await pw.chromium.launch_persistent_context(str(PROFILE_DIR), **kwargs)


async def login(pw):
    """Open a visible browser for one-time login, then close it."""
    print("Opening browser for login — log in with Google, then wait for the page to load.")
    context = await open_context(pw, headless=False)
    page = await context.new_page()
    await page.goto(BILLING_URL)

    for _ in range(180):  # up to 3 minutes
        if "cursor.com/settings" in page.url or "cursor.com/dashboard" in page.url:
            break
        await asyncio.sleep(1)
    else:
        await context.close()
        raise TimeoutError("Login timed out — re-run and log in within 3 minutes.")

    await page.wait_for_load_state("load", timeout=15_000)
    await context.close()
    print("Login saved. Running silently from now on.\n")


async def find_invoice_urls(page) -> list[str]:
    urls: list[str] = []
    for path in ["/settings", "/dashboard/billing"]:
        target = f"https://cursor.com{path}"
        if page.url != target:
            await page.goto(target)
            await page.wait_for_load_state("load", timeout=15_000)

        try:
            await page.wait_for_selector("a[href*='invoice.stripe.com']", timeout=10_000)
        except Exception:
            pass

        content = await page.content()
        found = re.findall(r'https://invoice\.stripe\.com/i/[^\s"\'<>]+', content)
        urls.extend(found)

        anchors = await page.locator("a[href*='invoice.stripe.com']").all()
        for a in anchors:
            href = await a.get_attribute("href")
            if href:
                urls.append(href)

    seen: set[str] = set()
    unique: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


async def download_receipt(page, invoice_url: str, idx: int) -> Path | None:
    await page.goto(invoice_url)
    await page.wait_for_load_state("load", timeout=15_000)

    try:
        await page.wait_for_selector("button, a", timeout=10_000)
    except Exception:
        pass

    candidates = [
        page.get_by_role("button", name="Download receipt", exact=True),
        page.get_by_role("link", name="Download receipt", exact=True),
        page.locator("a, button").filter(has_text=re.compile(r"download\s+receipt", re.IGNORECASE)),
    ]

    receipt_btn = None
    for locator in candidates:
        if await locator.count() > 0:
            receipt_btn = locator.first
            break

    if receipt_btn is None:
        print(f"  Could not find 'Download receipt' button on invoice {idx} — skipping.")
        return None

    try:
        async with page.expect_download(timeout=15_000) as dl:
            await receipt_btn.click()
        download = await dl.value
        suffix = Path(download.suggested_filename).suffix or ".pdf"
        user = re.sub(r"[^\w.-]", "_", getpass.getuser())
        date = datetime.today().strftime("%Y%m%d")
        filename = OUTPUT_DIR / f"{user}_receipt_{date}_{idx:02d}{suffix}"
        await download.save_as(str(filename))
        print(f"  Saved: {filename.name}")
        return filename
    except Exception as exc:
        print(f"  Failed for invoice {idx} ({invoice_url}): {exc}")
        return None


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        # Phase 1: login (visible browser, one-time only)
        if not PROFILE_DIR.exists():
            await login(pw)

        # Phase 2: scrape + download (fully headless, no browser window)
        context = await open_context(pw, headless=True)
        page = await context.new_page()
        await page.goto(BILLING_URL)
        await page.wait_for_load_state("load", timeout=15_000)

        # Detect expired session and re-login if needed
        if "cursor.com/settings" not in page.url and "cursor.com/dashboard" not in page.url:
            await context.close()
            print("Session expired — one-time re-login needed.")
            await login(pw)
            context = await open_context(pw, headless=True)
            page = await context.new_page()
            await page.goto(BILLING_URL)
            await page.wait_for_load_state("load", timeout=15_000)

        print("Scanning for invoice links…")
        invoice_urls = await find_invoice_urls(page)

        if not invoice_urls:
            print("No invoice links found — check Settings → Billing is accessible.")
            await context.close()
            return

        print(f"Found {len(invoice_urls)} invoice(s). Downloading to: {OUTPUT_DIR.resolve()}\n")

        for idx, url in enumerate(invoice_urls, start=1):
            await download_receipt(page, url, idx)

        await context.close()

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
