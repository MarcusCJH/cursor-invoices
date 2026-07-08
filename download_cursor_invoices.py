#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright",
# ]
# ///
"""
Download all Cursor.com invoices as receipts (PDFs), then optionally upload
to SharePoint if .sharepoint.env is configured.

Usage:
    uv run download_cursor_invoices.py [output_dir]

Flags:
    --install-browser    Install Playwright Chromium (once per machine)
    --logout             Reset Cursor session
    --sharepoint-login   Authenticate with SharePoint (opens browser once)
    --sharepoint-logout  Reset SharePoint session
    --test-upload        Upload a dummy receipt to Receipts/2069/01. January
    --no-upload          Skip SharePoint upload for this run
"""

import asyncio
import getpass
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

from playwright.async_api import async_playwright

PROFILE_DIR    = Path(__file__).parent / "cursor_browser_profile"
SP_PROFILE_DIR = Path(__file__).parent / "sharepoint_browser_profile"
BILLING_URL    = "https://cursor.com/settings"
SHAREPOINT_ENV = Path(__file__).parent / ".sharepoint.env"
USERNAME       = re.sub(r"[^\w.-]", "_", getpass.getuser())
CURSOR_PROMPT  = "Opening browser — log in with Google, then wait for the page to load."

def _cursor_landed(url: str) -> bool:
    return "cursor.com/settings" in url or "cursor.com/dashboard" in url

# ── arg parsing ───────────────────────────────────────────────────────────────

args       = {a for a in sys.argv[1:] if a.startswith("--")}
output_args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUTPUT_DIR = Path(output_args[0]) if output_args else Path(".")

if "--install-browser" in args:
    subprocess.run(
        ["uv", "run", "--with", "playwright", "python", "-m", "playwright", "install", "chromium"],
        check=True,
    )
    sys.exit(0)


def _clear_session(profile: Path, name: str) -> None:
    if profile.exists():
        shutil.rmtree(profile)
        print(f"{name} session cleared.")
    else:
        print(f"No saved {name} session found.")


if "--logout" in args:
    _clear_session(PROFILE_DIR, "Cursor")
    sys.exit(0)

if "--sharepoint-logout" in args:
    _clear_session(SP_PROFILE_DIR, "SharePoint")
    sys.exit(0)


# ── browser ───────────────────────────────────────────────────────────────────

async def _open_context(pw, profile: Path, headless: bool):
    kwargs = dict(headless=headless, args=["--disable-blink-features=AutomationControlled"])
    try:
        return await pw.chromium.launch_persistent_context(str(profile), channel="chrome", **kwargs)
    except Exception:
        return await pw.chromium.launch_persistent_context(str(profile), **kwargs)


async def _browser_login(pw, profile: Path, url: str, landed, prompt: str) -> None:
    print(prompt)
    context = await _open_context(pw, profile, headless=False)
    page = await context.new_page()
    await page.goto(url)
    for _ in range(180):
        if landed(page.url):
            break
        await asyncio.sleep(1)
    else:
        await context.close()
        raise TimeoutError("Login timed out — re-run and log in within 3 minutes.")
    await page.wait_for_load_state("load", timeout=15_000)
    await context.close()
    print("Session saved.\n")


async def _open_authed_page(pw, profile: Path, url: str, landed, re_login):
    """Open headless page; triggers re_login once if the session has expired."""
    async def _open():
        ctx = await _open_context(pw, profile, headless=True)
        pg = await ctx.new_page()
        await pg.goto(url)
        await pg.wait_for_load_state("load", timeout=15_000)
        return ctx, pg

    context, page = await _open()
    if not landed(page.url):
        await context.close()
        print("Session expired — one-time re-login needed.")
        await re_login()
        context, page = await _open()
    return context, page


# ── config ────────────────────────────────────────────────────────────────────

def _load_sp_config() -> dict | None:
    if not SHAREPOINT_ENV.exists():
        return None
    config: dict[str, str] = {}
    for line in SHAREPOINT_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            config[k.strip()] = v.strip()
    return config if config.get("SHAREPOINT_SITE_URL") else None


# ── SharePoint ────────────────────────────────────────────────────────────────

async def sp_login(pw, site_url: str) -> None:
    sp_host = urlparse(site_url).netloc
    await _browser_login(
        pw, SP_PROFILE_DIR, site_url,
        lambda url: urlparse(url).netloc == sp_host,
        "Opening browser for SharePoint — sign in with your work account.",
    )


async def sp_upload(pw, config: dict, files: list[tuple[str, bytes]], folder_rel: str) -> None:
    site_url   = config["SHAREPOINT_SITE_URL"].rstrip("/")
    site_path  = urlparse(site_url).path.rstrip("/")
    server_rel = f"{site_path}/Shared Documents/{folder_rel}"
    sp_host    = urlparse(site_url).netloc

    context, page = await _open_authed_page(
        pw, SP_PROFILE_DIR, site_url,
        lambda url: urlparse(url).netloc == sp_host,
        lambda: sp_login(pw, site_url),
    )

    digest = (await (await page.request.post(
        f"{site_url}/_api/contextinfo",
        headers={"Accept": "application/json;odata=verbose"},
    )).json())["d"]["GetContextWebInformation"]["FormDigestValue"]

    sp_headers = {"Accept": "application/json;odata=verbose", "X-RequestDigest": digest}

    current = site_path
    for segment in f"Shared Documents/{folder_rel}".split("/"):
        current = f"{current}/{segment}"
        resp = await page.request.post(
            f"{site_url}/_api/web/folders/add(@p)?@p='{quote(current)}'",
            headers=sp_headers,
        )
        if not resp.ok and resp.status != 409:
            print(f"  Warning: could not create folder '{current}' ({resp.status})")

    print(f"\nUploading to SharePoint: Shared Documents/{folder_rel}")
    for filename, content in files:
        resp = await page.request.post(
            f"{site_url}/_api/web/GetFolderByServerRelativePath(decodedurl=@p)"
            f"/Files/Add(url=@n,overwrite=true)"
            f"?@p='{quote(server_rel)}'&@n='{quote(filename)}'",
            headers={**sp_headers, "Content-Type": "application/octet-stream"},
            data=content,
        )
        print(f"  {'Uploaded' if resp.ok else f'Failed ({resp.status})'}: {filename}")

    await context.close()


# ── Cursor ────────────────────────────────────────────────────────────────────

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
        found = [
            href for a in await page.locator("a[href*='invoice.stripe.com']").all()
            if (href := await a.get_attribute("href"))
        ]
        # Fallback: scrape raw HTML for URLs not in anchor tags
        if not found:
            found = re.findall(r'https://invoice\.stripe\.com/i/[^\s"\'<>]+', await page.content())
        urls += found
    return list(dict.fromkeys(urls))


async def download_receipt(page, invoice_url: str, idx: int) -> Path | None:
    await page.goto(invoice_url)
    await page.wait_for_load_state("load", timeout=15_000)
    try:
        await page.wait_for_selector("button, a", timeout=10_000)
    except Exception:
        pass

    receipt_btn = page.locator("a, button").filter(
        has_text=re.compile(r"download\s+receipt", re.IGNORECASE)
    )
    if await receipt_btn.count() == 0:
        print(f"  Could not find 'Download receipt' on invoice {idx} — skipping.")
        return None

    try:
        async with page.expect_download(timeout=15_000) as dl:
            await receipt_btn.first.click()
        download = await dl.value
        suffix = Path(download.suggested_filename).suffix or ".pdf"
        dest = OUTPUT_DIR / f"{USERNAME}_receipt_{datetime.today().strftime('%Y%m%d')}_{idx:02d}{suffix}"
        await download.save_as(str(dest))
        print(f"  Saved: {dest.name}")
        return dest
    except Exception as exc:
        print(f"  Failed for invoice {idx} ({invoice_url}): {exc}")
        return None


# ── main ──────────────────────────────────────────────────────────────────────

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sp_config = _load_sp_config()

    async with async_playwright() as pw:

        if "--sharepoint-login" in args:
            if not sp_config:
                print("No SHAREPOINT_SITE_URL in .sharepoint.env — copy .sharepoint.env.example first.")
                return
            await sp_login(pw, sp_config["SHAREPOINT_SITE_URL"])
            return

        if "--test-upload" in args:
            if not sp_config:
                print("No .sharepoint.env found — copy .sharepoint.env.example first.")
                return
            dummy_pdf = (
                b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
                b"3 0 obj<</Type/Page/MediaBox[0 0 200 50]/Parent 2 0 R>>endobj\n"
                b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
                b"0000000058 00000 n \n0000000115 00000 n \n"
                b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n173\n%%EOF\n"
            )
            receipts   = sp_config.get("SHAREPOINT_RECEIPTS_FOLDER", "Receipts")
            folder_rel = f"{receipts}/2069/01. January"
            filename   = f"{USERNAME}_receipt_{datetime.today().strftime('%Y%m%d')}_01.pdf"
            print(f"Test upload → Shared Documents/{folder_rel}/{filename}")
            await sp_upload(pw, sp_config, [(filename, dummy_pdf)], folder_rel)
            return

        context, page = await _open_authed_page(
            pw, PROFILE_DIR, BILLING_URL, _cursor_landed,
            lambda: _browser_login(pw, PROFILE_DIR, BILLING_URL, _cursor_landed, CURSOR_PROMPT),
        )

        print("Scanning for invoice links…")
        invoice_urls = await find_invoice_urls(page)
        if not invoice_urls:
            print("No invoice links found — check Settings → Billing is accessible.")
            await context.close()
            return

        print(f"Found {len(invoice_urls)} invoice(s). Downloading to: {OUTPUT_DIR.resolve()}\n")
        downloaded = [p for idx, url in enumerate(invoice_urls, 1)
                      if (p := await download_receipt(page, url, idx))]
        await context.close()

        if downloaded and "--no-upload" not in args and sp_config:
            now        = datetime.today()
            receipts   = sp_config.get("SHAREPOINT_RECEIPTS_FOLDER", "Receipts")
            folder_rel = f"{receipts}/{now.year}/{now.month:02d}. {now.strftime('%B')}"
            try:
                await sp_upload(pw, sp_config, [(p.name, p.read_bytes()) for p in downloaded], folder_rel)
            except Exception as exc:
                print(f"\nSharePoint upload failed (PDFs saved locally): {exc}")

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())