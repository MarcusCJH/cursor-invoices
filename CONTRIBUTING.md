# Contributing

## Getting started

1. Fork the repo and clone your fork.
2. Install dependencies:
   ```bash
   uv sync
   uv run --with playwright python -m playwright install chromium
   ```

## Making changes

Create a branch from `master`:

```bash
git checkout -b your-feature-or-fix
```

Edit `cursor_invoices.py` directly. There is no build step.

Test your changes:

```bash
uv run cursor_invoices.py        # full run against a real Cursor account
make test-upload                 # verify SharePoint upload without touching real receipts
```

## Opening a pull request

Push your branch to your fork and open a PR against `master`. In the description:

- Explain what changed and why.
- Note any manual testing you did.

Keep PRs focused on one concern. If you are unsure whether something is worth a PR, open an issue first.