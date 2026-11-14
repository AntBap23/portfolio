# QA Tooling for anthony-baptiste.com

Quality assurance tools for maintaining site integrity during redesigns. All tools run against either the source tree or Jekyll-rendered output. Run commands from the **repo root**.

## Prerequisites

- Python 3 (standard library only)
- Ruby and Bundler (for Jekyll builds)
- Node.js and npm (for screenshots)

## Tools

### 1. Locked Content Checker

Fingerprints critical content, structure, and metadata to detect unintended changes.

**Checks:**
- JSON-LD structured data (exact byte-for-byte)
- Page titles and meta descriptions (exact byte-for-byte)
- Contact forms (Formspree action, fields, labels, every option value/text including `name="budget"`)
- Calendly links
- Element IDs (fragment identifiers)
- Locked copy: all h1-h6, `.section-kicker`, `.answer-summary`, `.offer-eyebrow`, `.sample-notice`, service openers, service names, visible FAQ Q&A, prices, employer disclaimer
- Normalized visible text of each page `<main>` (or `<body>` if no main), excluding script/style
- Hidden element inventory (52 unique elements, 53 selector matches)
- Template syntax (`{{`, `{%`, `{#`) in text nodes and attribute values
- Repo files in the scanned tree: `llms.txt`, `robots.txt`, `sitemap.xml`, `CNAME` (missing file = FAIL)
- Every fixture page must exist in the scanned tree (missing page = FAIL)

**Usage (from repo root):**

```bash
# Build rendered output
bash _qa/build.sh

# Create fixture from rendered build
python3 _qa/locked-check.py snapshot --root _qa/_site --source-commit <sha>

# Check rendered build against fixture
python3 _qa/locked-check.py check --root _qa/_site
```

**Outputs:**
- `_qa/locked-fixture.json` - Content fingerprints (fixture ID and source commit SHA)
- `_qa/hidden-inventory.json` - Complete hidden element inventory (52 unique elements, 53 selector matches)
- `_qa/locked-exceptions.json` - Approved differences allowlist (empty and unapplied for 1a)

**Exit codes:**
- `0` - All checks passed
- `1` - One or more checks failed

### 2. Jekyll Build

Builds the site using GitHub Pages configuration. Copies only `CNAME` into `_qa/_site/` (Jekyll does not emit it). Does **not** copy `llms.txt` or `robots.txt`; Jekyll emits those byte-identical from source, and the checker reads Jekyll's own output (missing or changed = FAIL).

**Usage (from repo root):**

```bash
bash _qa/build.sh
```

**Output:** `_qa/_site/` (gitignored)

The build script verifies that `_qa/` itself is excluded from the build output.

### 3. Visual Regression Screenshots

Captures full-page screenshots at desktop (1280x800) and mobile (390x844) viewports.

**Setup:**

```bash
cd _qa
npm install
```

**Usage:**

```bash
# Capture from a running local server (recommended: serve _qa/_site)
node _qa/screenshots.mjs http://localhost:8080
```

**Output:** `_qa/baseline/*.png` (28 screenshots: 14 pages × 2 viewports)

The script scrolls each page to trigger reveal animations, waits for fonts, disables animations and transitions, then saves full-page screenshots.

### 4. Visual Diff

Compares screenshots against baseline using pixelmatch.

```bash
node _qa/visual-diff.mjs path/to/screenshots
```

## Exceptions allowlist

`_qa/locked-exceptions.json` declares approved differences by page and element. **1c applies only P1 and P2**:

- **P1** - Visible breadcrumb markup on pages with BreadcrumbList JSON-LD. The checker verifies visible names/URLs equal that page's schema items (it does not blindly skip them).
- **P2** - Footer link labels inside the unified footer include (official service names).

**F18 (Calendly) is not permitted here** (belongs to 1e). Unknown exception classes cause `check` to exit non-zero.

`check` also refuses an unexpanded source root: if scanned HTML still contains `{%`, `{{`, or `{#`, it exits non-zero and asks for `_qa/_site`.

## Workflow

```bash
# 1. Build and snapshot
bash _qa/build.sh
python3 _qa/locked-check.py snapshot --root _qa/_site --source-commit 218193ad3132bbe1fe397194b9fdccedb045977d

# 2. Verify check passes
python3 _qa/locked-check.py check --root _qa/_site

# 3. Capture baseline screenshots from the rendered build
cd _qa && npm install && node screenshots.mjs http://localhost:8080
```

## Files

- `locked-check.py` - Content checker (Python 3 stdlib only)
- `build.sh` - Jekyll build script (copies only CNAME into `_site`; llms.txt/robots.txt come from Jekyll)
- `Gemfile` - Ruby dependencies (github-pages gem)
- `package.json` - Node dependencies
- `screenshots.mjs` - Screenshot capture script
- `visual-diff.mjs` - Visual diff comparison
- `locked-fixture.json` - Committed baseline fixture
- `hidden-inventory.json` - Committed hidden element inventory
- `locked-exceptions.json` - Allowlist (empty/unapplied for 1a; later P1, P2, P3, F18)
- `baseline/` - Committed baseline screenshots
- `.gitignore` - Excludes `_site/`, `vendor/bundle/`, `node_modules/`

## Notes

- The fixture includes a fixture ID (SHA256 hash) and source commit SHA
- Hidden element inventory format (rev 1.4):
  - Top-level `unique_elements` and `selector_matches` totals (52 and 53)
  - Each entry: page, tag, id, class, matched_selectors array, outerHTML SHA256, occurrence_index
  - Keyed by page + tag + id + class + hash + occurrence (not positional CSS path)
  - outerHTML hashes cover the full element subtree (nesting-aware, void-element aware)
  - `#gallery-modal` on `/competitions/` matches both `aria-hidden` and `inline-style`
- Locked files use git blob SHAs:
  - `llms.txt`: `3b51141a346700b57fca132ed5d261360f869637`
  - `robots.txt`: `e698bea3d563b0b4b97a89dbd0c3ca25e037eefb`
- Jekyll automatically excludes `_qa/` from build output (underscore prefix)
