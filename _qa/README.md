# QA Tooling for anthony-baptiste.com

Quality assurance tools for maintaining site integrity during redesigns. All tools run against either the source tree or Jekyll-rendered output.

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
- Contact form fields and Calendly links
- Element IDs (fragment identifiers)
- Locked visible copy (H1s, prices, disclaimers, etc.)
- Hidden element inventory (52 elements)
- Template syntax (`{{`, `{%`, `{#` - must not appear in rendered output)
- Repo files: `llms.txt`, `robots.txt`, `sitemap.xml`

**Usage:**

```bash
# Create fixture from source
python3 _qa/locked-check.py snapshot

# Create fixture from rendered build
python3 _qa/locked-check.py snapshot --root _qa/_site

# Check source against fixture
python3 _qa/locked-check.py check

# Check rendered build against fixture
python3 _qa/locked-check.py check --root _qa/_site
```

**Outputs:**
- `_qa/locked-fixture.json` - Content fingerprints (fixture ID and source commit SHA)
- `_qa/hidden-inventory.json` - Complete hidden element inventory (52 unique elements, 53 selector matches)
- `_qa/locked-exceptions.json` - Approved differences (currently empty)

**Exit codes:**
- `0` - All checks passed
- `1` - One or more checks failed

### 2. Jekyll Build

Builds the site using GitHub Pages configuration.

**Usage:**

```bash
cd _qa
./build.sh
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
# Capture baseline from source
npm run screenshots

# Capture from custom URL
node screenshots.mjs http://localhost:4000

# Capture from rendered build
cd _qa
./build.sh
node screenshots.mjs http://localhost:8080
```

**Output:** `_qa/baseline/*.png` (28 screenshots: 14 pages × 2 viewports)

The script:
- Scrolls each page to trigger reveal animations
- Waits for fonts to load
- Disables animations and transitions before capture
- Saves full-page screenshots

### 4. Visual Diff

Compares screenshots against baseline using pixelmatch.

**Usage:**

```bash
# Compare current/ directory against baseline/
npm run visual-diff

# Compare custom directory
node visual-diff.mjs path/to/screenshots
```

**Output:** Per-page pixel difference counts and percentages.

## Workflow

### Initial baseline (this PR)

```bash
# 1. Capture fixture from rendered output
cd _qa
./build.sh
python3 locked-check.py snapshot --root _site

# 2. Verify check passes
python3 locked-check.py check --root _site

# 3. Capture baseline screenshots
npm install
npm run screenshots

# 4. Commit fixtures and baselines
git add locked-fixture.json hidden-inventory.json baseline/
git commit -m "Add baseline fixtures and screenshots"
```

### Testing a change

```bash
# 1. Make changes to HTML/CSS/JS

# 2. Build and check
cd _qa
./build.sh
python3 locked-check.py check --root _site

# 3. Capture new screenshots and compare
npm run screenshots  # saves to current/
npm run visual-diff

# 4. Review differences
```

## Files

- `locked-check.py` - Content checker (Python 3 stdlib only)
- `build.sh` - Jekyll build script
- `Gemfile` - Ruby dependencies (github-pages gem)
- `package.json` - Node dependencies
- `screenshots.mjs` - Screenshot capture script
- `visual-diff.mjs` - Visual diff comparison
- `locked-fixture.json` - Committed baseline fixture
- `hidden-inventory.json` - Committed hidden element inventory
- `locked-exceptions.json` - Approved differences (empty)
- `baseline/` - Committed baseline screenshots
- `.gitignore` - Excludes `_site/`, `vendor/bundle/`, `node_modules/`

## Notes

- The fixture includes a fixture ID (SHA256 hash) and source commit SHA
- Hidden element inventory format (rev 1.4):
  - Top-level `unique_elements` and `selector_matches` totals (52 and 53)
  - Each entry: page, tag, id, class, matched_selectors array, outerHTML SHA256, occurrence_index
  - Keyed by page + tag + id + class + hash + occurrence (not positional CSS path)
  - CSS selector path included as informational only
  - `#gallery-modal` on `/competitions/` matches both `aria-hidden` and `inline-style`
- Locked files use git blob SHAs:
  - `llms.txt`: `3b51141a346700b57fca132ed5d261360f869637`
  - `robots.txt`: `e698bea3d563b0b4b97a89dbd0c3ca25e037eefb`
- Jekyll automatically excludes `_qa/` from build output (underscore prefix)
