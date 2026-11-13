#!/usr/bin/env python3
"""
Locked content checker for anthony-baptiste.com static site.
Ensures critical content, structure, and metadata remain unchanged during redesigns.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


VOID_ELEMENTS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
})

TEMPLATE_MARKERS = ('{{', '{%', '{#')


def normalize_visible_text(text):
    """Collapse whitespace for stable visible-text comparison."""
    return re.sub(r'\s+', ' ', text).strip()


def has_template_syntax(text):
    return any(m in text for m in TEMPLATE_MARKERS) if text else False


def record_template(results, text, where):
    if has_template_syntax(text):
        results['template_syntax'].append({
            'where': where,
            'context': text[:120],
            'markers': [m for m in TEMPLATE_MARKERS if m in text]
        })


class ElementTracker:
    """Track elements and build informational CSS selector paths."""

    def __init__(self):
        self.path = []
        self.class_counts = {}

    def push(self, tag, attrs_dict):
        elem_id = attrs_dict.get('id')
        classes = attrs_dict.get('class', '').split()
        if elem_id:
            selector = f"{tag}#{elem_id}"
        elif classes:
            selector = f"{tag}.{'.'.join(classes)}"
        else:
            key = (len(self.path), tag)
            self.class_counts[key] = self.class_counts.get(key, 0) + 1
            selector = f"{tag}:nth-of-type({self.class_counts[key]})"
        self.path.append(selector)

    def pop(self):
        if self.path:
            self.path.pop()

    def get_selector(self):
        return ' > '.join(self.path)


class LockedContentParser(HTMLParser):
    """Parse HTML and extract locked elements for fingerprinting."""

    def __init__(self):
        super().__init__()
        self.results = {
            'jsonld_blocks': [],
            'title': None,
            'title_raw': None,
            'meta_description': None,
            'meta_description_raw': None,
            'contact_forms': [],
            'calendly_links': [],
            'element_ids': [],
            'locked_copy': [],
            'main_visible_text': '',
            'hidden_elements': [],
            'template_syntax': []
        }
        self.tracker = ElementTracker()
        self.tag_stack = []
        self.form_context = None
        self.current_label = None
        self.current_option = None

        self.in_script_jsonld = False
        self.in_title = False
        self.jsonld_raw = []
        self.title_raw = []

        # Nested hidden-element captures: list of {..., depth, chunks}
        self.hidden_stack = []

        self.capture_contexts = []

        # Visible main/body text
        self.in_main = False
        self.saw_main = False
        self.in_body = False
        self.skip_visible_depth = 0  # inside script/style
        self.main_chunks = []

        # Offer card / FAQ helpers
        self.in_offer_card = False
        self.offer_card_p_count = 0
        self.in_faq_details = False
        self.faq_waiting_answer = False

    def _classes(self, attrs_dict):
        return attrs_dict.get('class', '').split()

    def _start_hidden_capture(self, tag, attrs_dict, matched_selectors):
        capture = {
            'selector': self.tracker.get_selector(),
            'matched_selectors': matched_selectors[:],
            'tag': tag,
            'id': attrs_dict.get('id', ''),
            'class': attrs_dict.get('class', ''),
            'depth': 1,
            'chunks': [self.get_starttag_text()]
        }
        if tag in VOID_ELEMENTS:
            outer_html = ''.join(capture['chunks'])
            self.results['hidden_elements'].append({
                'selector': capture['selector'],
                'tag': capture['tag'],
                'id': capture['id'],
                'class': capture['class'],
                'matched_selectors': capture['matched_selectors'],
                'outer_html_sha256': hashlib.sha256(outer_html.encode('utf-8')).hexdigest()
            })
        else:
            self.hidden_stack.append(capture)

    def _append_to_hidden(self, text):
        for capture in self.hidden_stack:
            capture['chunks'].append(text)

    def _finalize_hidden(self, capture):
        outer_html = ''.join(capture['chunks'])
        self.results['hidden_elements'].append({
            'selector': capture['selector'],
            'tag': capture['tag'],
            'id': capture['id'],
            'class': capture['class'],
            'matched_selectors': capture['matched_selectors'],
            'outer_html_sha256': hashlib.sha256(outer_html.encode('utf-8')).hexdigest()
        })

    def _push_text_capture(self, kind, start_tag, extra=None):
        ctx = {'type': kind, 'start_tag': start_tag, 'content': [], 'depth': 1}
        if extra:
            ctx.update(extra)
        self.capture_contexts.append(ctx)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append((tag, attrs_dict))
        self.tracker.push(tag, attrs_dict)

        # Template syntax in attribute values
        for attr_name, attr_value in attrs:
            if attr_value:
                record_template(self.results, attr_value, f'attr:{tag}:{attr_name}')

        # Visible-text skip for script/style
        if tag in ('script', 'style'):
            self.skip_visible_depth += 1

        if tag == 'body':
            self.in_body = True
        if tag == 'main':
            self.in_main = True
            self.saw_main = True

        # Hidden element matches
        matched_selectors = []
        if 'hidden' in attrs_dict:
            matched_selectors.append('hidden-attribute')
        if attrs_dict.get('aria-hidden') == 'true':
            matched_selectors.append('aria-hidden')
        if 'sr-only' in self._classes(attrs_dict):
            matched_selectors.append('sr-only')
        style = attrs_dict.get('style', '') or ''
        style_compact = style.replace(' ', '')
        if 'display:none' in style_compact or 'visibility:hidden' in style_compact:
            matched_selectors.append('inline-style')

        # Nested content for active hidden captures
        start_text = self.get_starttag_text()
        for capture in self.hidden_stack:
            if capture['tag'] == tag and tag not in VOID_ELEMENTS:
                capture['depth'] += 1
            capture['chunks'].append(start_text)

        if matched_selectors:
            self._start_hidden_capture(tag, attrs_dict, matched_selectors)

        # Nested depth for open text captures of the same start tag
        for ctx in self.capture_contexts:
            if ctx.get('start_tag') == tag:
                ctx['depth'] += 1

        # JSON-LD
        if tag == 'script' and attrs_dict.get('type') == 'application/ld+json':
            self.in_script_jsonld = True
            self.jsonld_raw = [self.get_starttag_text()]

        # Title
        if tag == 'title':
            self.in_title = True
            self.title_raw = [self.get_starttag_text()]

        # Meta description
        if tag == 'meta' and attrs_dict.get('name') == 'description':
            self.results['meta_description'] = attrs_dict.get('content', '')
            self.results['meta_description_raw'] = self.get_starttag_text()

        # Element IDs
        if 'id' in attrs_dict:
            self.results['element_ids'].append(attrs_dict['id'])

        # Contact forms
        if tag == 'form' and 'formspree.io' in (attrs_dict.get('action') or ''):
            self.form_context = {
                'action': attrs_dict.get('action', ''),
                'fields': [],
                'labels': [],
                'options': []
            }

        if self.form_context:
            if tag == 'label':
                self.current_label = {
                    'for': attrs_dict.get('for', ''),
                    'content': []
                }
            if tag in ('input', 'select', 'textarea'):
                field_info = {
                    'type': tag,
                    'name': attrs_dict.get('name', ''),
                    'value': attrs_dict.get('value', ''),
                    'id': attrs_dict.get('id', '')
                }
                if tag == 'input':
                    field_info['input_type'] = attrs_dict.get('type', '')
                self.form_context['fields'].append(field_info)
            if tag == 'option':
                self.current_option = {
                    'value': attrs_dict.get('value', ''),
                    'content': [],
                    'select_name': ''
                }
                # Associate with nearest select name
                for t, a in reversed(self.tag_stack):
                    if t == 'select':
                        self.current_option['select_name'] = a.get('name', '')
                        break

        # Calendly
        if tag == 'a' and 'calendly.com' in (attrs_dict.get('href') or ''):
            self._push_text_capture('calendly', 'a', {'href': attrs_dict.get('href', '')})

        # Offer card tracking
        if 'consulting-offer-card' in self._classes(attrs_dict):
            self.in_offer_card = True
            self.offer_card_p_count = 0

        # FAQ details
        if tag == 'details' and any(
            'faq' in (a.get('class') or '') for t, a in self.tag_stack
        ):
            self.in_faq_details = True
        if tag == 'summary' and self.in_faq_details:
            self._push_text_capture('faq_question', 'summary')
            self.faq_waiting_answer = True

        # Locked visible copy targets
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._push_text_capture(tag, tag)
            if tag == 'h3' and self.in_offer_card:
                self._push_text_capture('service_name', 'h3')
        classes = self._classes(attrs_dict)
        if 'section-kicker' in classes:
            self._push_text_capture('section-kicker', tag)
        if 'answer-summary' in classes:
            self._push_text_capture('answer-summary', tag)
        if 'offer-eyebrow' in classes:
            self._push_text_capture('offer-eyebrow', tag)
        if 'sample-notice' in classes:
            self._push_text_capture('sample-notice', tag)
        if tag == 'p' and self.in_offer_card and 'offer-eyebrow' not in classes:
            # First non-eyebrow paragraph in an offer card is the service opener
            if self.offer_card_p_count == 0:
                self._push_text_capture('service_opener', 'p')
            self.offer_card_p_count += 1
        if tag == 'p' and self.faq_waiting_answer:
            self._push_text_capture('faq_answer', 'p')
            self.faq_waiting_answer = False

    def handle_endtag(self, tag):
        # Close hidden captures with proper nesting
        i = len(self.hidden_stack) - 1
        while i >= 0:
            capture = self.hidden_stack[i]
            capture['chunks'].append(f'</{tag}>')
            if capture['tag'] == tag:
                capture['depth'] -= 1
                if capture['depth'] == 0:
                    self._finalize_hidden(capture)
                    self.hidden_stack.pop(i)
            i -= 1

        if tag in ('script', 'style') and self.skip_visible_depth > 0:
            self.skip_visible_depth -= 1

        if self.in_script_jsonld and tag == 'script':
            self.jsonld_raw.append('</script>')
            self.results['jsonld_blocks'].append(''.join(self.jsonld_raw))
            self.in_script_jsonld = False
            self.jsonld_raw = []

        if self.in_title and tag == 'title':
            self.title_raw.append('</title>')
            self.results['title_raw'] = ''.join(self.title_raw)
            self.in_title = False
            self.title_raw = []

        if self.form_context and tag == 'label' and self.current_label is not None:
            self.form_context['labels'].append({
                'for': self.current_label['for'],
                'text': normalize_visible_text(''.join(self.current_label['content']))
            })
            self.current_label = None

        if self.form_context and tag == 'option' and self.current_option is not None:
            self.form_context['options'].append({
                'select_name': self.current_option['select_name'],
                'value': self.current_option['value'],
                'text': normalize_visible_text(''.join(self.current_option['content']))
            })
            self.current_option = None

        if self.form_context and tag == 'form':
            self.results['contact_forms'].append(self.form_context)
            self.form_context = None

        if tag == 'details':
            self.in_faq_details = False
            self.faq_waiting_answer = False

        if tag == 'article' and self.in_offer_card:
            self.in_offer_card = False
            self.offer_card_p_count = 0

        if tag == 'main':
            self.in_main = False
        if tag == 'body':
            self.in_body = False

        # Finish text captures when their start-tag depth returns to 0
        if self.capture_contexts:
            for ctx in list(self.capture_contexts):
                if ctx.get('start_tag') != tag:
                    continue
                ctx['depth'] -= 1
                if ctx['depth'] != 0:
                    continue
                content_text = normalize_visible_text(''.join(ctx['content']))
                kind = ctx['type']
                if kind == 'calendly':
                    self.results['calendly_links'].append({
                        'href': ctx['href'],
                        'text': content_text
                    })
                elif content_text:
                    self.results['locked_copy'].append({'type': kind, 'text': content_text})
                self.capture_contexts.remove(ctx)

        if self.tag_stack:
            self.tag_stack.pop()
        self.tracker.pop()

    def handle_data(self, data):
        self._append_to_hidden(data)

        if self.in_script_jsonld:
            self.jsonld_raw.append(data)
        if self.in_title:
            self.title_raw.append(data)

        if self.current_label is not None:
            self.current_label['content'].append(data)
        if self.current_option is not None:
            self.current_option['content'].append(data)

        for ctx in self.capture_contexts:
            ctx['content'].append(data)

        record_template(self.results, data, 'text')

        # Visible main/body text (exclude script/style)
        if self.skip_visible_depth == 0:
            if self.in_main or (self.in_body and not self.saw_main):
                self.main_chunks.append(data)

    def handle_comment(self, data):
        selector = self.tracker.get_selector() + ' > comment()'
        outer_html = f'<!--{data}-->'
        self.results['hidden_elements'].append({
            'selector': selector,
            'tag': '!--',
            'id': '',
            'class': '',
            'matched_selectors': ['html-comment'],
            'outer_html_sha256': hashlib.sha256(outer_html.encode('utf-8')).hexdigest()
        })
        # Comments inside hidden elements
        self._append_to_hidden(outer_html)

    def finalize(self):
        self.results['main_visible_text'] = normalize_visible_text(''.join(self.main_chunks))
        # Sort JSON-LD for order-independence within head
        self.results['jsonld_blocks'] = sorted(self.results['jsonld_blocks'])


def scan_for_locked_copy(html_content):
    """Scan for price strings and the employer disclaimer."""
    locked_patterns = []

    price_pattern = r'>\s*([^<]*\$[^<]*)<'
    for match in re.findall(price_pattern, html_content):
        text = normalize_visible_text(match)
        if text and len(text) < 200:
            locked_patterns.append({'type': 'price', 'text': text})

    if 'Employers are not presented as independent consulting clients' in html_content:
        match = re.search(
            r'(Employers are not presented as independent consulting clients\.?[^<]*)',
            html_content
        )
        if match:
            locked_patterns.append({
                'type': 'employer_disclaimer',
                'text': normalize_visible_text(match.group(1))
            })

    return locked_patterns


def parse_html_file(filepath):
    """Parse an HTML file and extract locked content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = LockedContentParser()
    parser.feed(html_content)
    parser.finalize()

    parser.results['locked_copy'].extend(scan_for_locked_copy(html_content))
    return parser.results


def get_page_paths(root_dir):
    """Find all index.html pages that GitHub Pages serves."""
    root_path = Path(root_dir)
    pages = []

    for index_file in sorted(root_path.rglob('index.html')):
        rel_path = index_file.relative_to(root_path)
        path_parts = rel_path.parts
        if any(part.startswith('_') or part in ('node_modules', 'vendor') for part in path_parts):
            continue
        if rel_path == Path('index.html'):
            url_path = '/'
        else:
            url_path = '/' + str(rel_path.parent).replace('\\', '/') + '/'
        pages.append({'url_path': url_path, 'file_path': str(index_file)})

    return pages


def page_file_for_url(root_dir, url_path):
    root_path = Path(root_dir)
    if url_path == '/':
        return root_path / 'index.html'
    return root_path / url_path.lstrip('/') / 'index.html'


def resolve_git_root(root_dir):
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, cwd=root_dir
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(root_dir)


def compute_fixture_id(fixture_data):
    data_copy = {k: v for k, v in fixture_data.items() if k not in ('fixture_id', 'source_commit')}
    canonical = json.dumps(data_copy, sort_keys=True, indent=2)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def build_hidden_inventory_entries(page_url, hidden_elements):
    entries = []
    occurrence_counts = {}
    for hidden_elem in hidden_elements:
        key = (
            hidden_elem['tag'],
            hidden_elem['id'],
            hidden_elem['class'],
            hidden_elem['outer_html_sha256']
        )
        occurrence_counts[key] = occurrence_counts.get(key, 0) + 1
        entries.append({
            'page': page_url,
            'tag': hidden_elem['tag'],
            'id': hidden_elem['id'],
            'class': hidden_elem['class'],
            'matched_selectors': sorted(set(hidden_elem['matched_selectors'])),
            'outer_html_sha256': hidden_elem['outer_html_sha256'],
            'occurrence_index': occurrence_counts[key],
            'selector': hidden_elem['selector']
        })
    return entries


def snapshot_command(root_dir, output_file, hidden_inventory_file, source_commit=None):
    print(f"Scanning pages in {root_dir}...")
    pages = get_page_paths(root_dir)

    print(f"Found {len(pages)} pages:")
    for page in pages:
        print(f"  {page['url_path']}")

    fixture = {'pages': {}}
    hidden_inventory = []

    for page in pages:
        print(f"Processing {page['url_path']}...")
        results = parse_html_file(page['file_path'])
        hidden_inventory.extend(
            build_hidden_inventory_entries(page['url_path'], results['hidden_elements'])
        )
        fixture['pages'][page['url_path']] = results

    print("Checking repo-level files...")
    root_path = Path(root_dir)
    git_root = resolve_git_root(root_dir)

    # Prefer files in the scanned root (rendered tree); fall back to git root for snapshot
    for name, key in (('llms.txt', 'llms_txt_blob_sha'), ('robots.txt', 'robots_txt_blob_sha')):
        candidate = root_path / name
        if not candidate.exists():
            candidate = git_root / name
        if not candidate.exists():
            raise SystemExit(f"FAIL: required file missing for snapshot: {name}")
        result = subprocess.run(
            ['git', 'hash-object', str(candidate)],
            capture_output=True, text=True, cwd=git_root
        )
        if result.returncode != 0:
            raise SystemExit(f"FAIL: could not hash {name}")
        fixture[key] = result.stdout.strip()

    sitemap_file = root_path / 'sitemap.xml'
    if not sitemap_file.exists():
        raise SystemExit("FAIL: required file missing for snapshot: sitemap.xml")
    with open(sitemap_file, 'r', encoding='utf-8') as f:
        content = f.read()
    fixture['sitemap_xml_normalized'] = re.sub(
        r'<lastmod>.*?</lastmod>', '<lastmod></lastmod>', content
    )

    cname_file = root_path / 'CNAME'
    if not cname_file.exists():
        cname_file = git_root / 'CNAME'
    if cname_file.exists():
        with open(cname_file, 'rb') as f:
            fixture['cname_sha256'] = hashlib.sha256(f.read()).hexdigest()

    if source_commit:
        fixture['source_commit'] = source_commit
    else:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, cwd=git_root
        )
        if result.returncode == 0:
            fixture['source_commit'] = result.stdout.strip()

    fixture['fixture_id'] = compute_fixture_id(fixture)

    unique_elements = len(hidden_inventory)
    selector_matches = sum(len(item['matched_selectors']) for item in hidden_inventory)

    print(f"\nHidden element counts:")
    print(f"  Unique elements: {unique_elements}")
    print(f"  Selector matches: {selector_matches}")

    page_counts = {}
    for item in hidden_inventory:
        page_counts[item['page']] = page_counts.get(item['page'], 0) + 1
    print("\nPer-page unique element counts:")
    for page_url in sorted(page_counts.keys()):
        print(f"  {page_url}: {page_counts[page_url]}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, indent=2)

    inventory_data = {
        'unique_elements': unique_elements,
        'selector_matches': selector_matches,
        'elements': hidden_inventory
    }
    with open(hidden_inventory_file, 'w', encoding='utf-8') as f:
        json.dump(inventory_data, f, indent=2)

    print(f"\nFixture saved to {output_file}")
    print(f"Hidden inventory saved to {hidden_inventory_file}")
    print(f"Fixture ID: {fixture['fixture_id']}")
    if 'source_commit' in fixture:
        print(f"Source commit: {fixture['source_commit']}")


def check_command(root_dir, fixture_file, hidden_inventory_file, exceptions_file):
    with open(fixture_file, 'r', encoding='utf-8') as f:
        fixture = json.load(f)

    print(f"Loaded fixture: {fixture_file}")
    print(f"Fixture ID: {fixture.get('fixture_id', 'N/A')}")
    if 'source_commit' in fixture:
        print(f"Source commit: {fixture['source_commit']}")
    print()

    with open(hidden_inventory_file, 'r', encoding='utf-8') as f:
        expected_inventory_data = json.load(f)

    expected_unique = expected_inventory_data.get('unique_elements', 0)
    expected_matches = expected_inventory_data.get('selector_matches', 0)
    expected_inventory = expected_inventory_data.get('elements', [])

    # Exceptions file is loaded for forward compatibility but not applied in 1a.
    # Later redesign PRs may declare approved differences (rev 1.1: P1, P2, P3, F18).
    if os.path.exists(exceptions_file):
        with open(exceptions_file, 'r', encoding='utf-8') as f:
            json.load(f)

    root_path = Path(root_dir)
    git_root = resolve_git_root(root_dir)
    all_pass = True

    # Fail closed: every fixture page must exist in the scanned tree
    print("Checking fixture pages exist...")
    fixture_pages = sorted(fixture.get('pages', {}).keys())
    for url_path in fixture_pages:
        page_file = page_file_for_url(root_dir, url_path)
        if not page_file.exists():
            print(f"  FAIL: Missing page {url_path} (expected {page_file})")
            all_pass = False
        else:
            print(f"  PASS: Page present {url_path}")

    pages = get_page_paths(root_dir)
    current_inventory = []

    for page in pages:
        url_path = page['url_path']
        print(f"Checking {url_path}...")

        if url_path not in fixture['pages']:
            print(f"  FAIL: Page not in fixture")
            all_pass = False
            continue

        expected = fixture['pages'][url_path]
        actual = parse_html_file(page['file_path'])
        current_inventory.extend(
            build_hidden_inventory_entries(url_path, actual['hidden_elements'])
        )

        checks = [
            ('JSON-LD blocks', 'jsonld_blocks'),
            ('Title (raw)', 'title_raw'),
            ('Meta description (raw)', 'meta_description_raw'),
            ('Contact forms', 'contact_forms'),
            ('Calendly links', 'calendly_links'),
            ('Element IDs', 'element_ids'),
            ('Locked copy', 'locked_copy'),
            ('Main visible text', 'main_visible_text'),
        ]

        for check_name, key in checks:
            if expected.get(key) != actual.get(key):
                print(f"  FAIL: {check_name} mismatch")
                all_pass = False
            else:
                print(f"  PASS: {check_name}")

        if actual.get('template_syntax'):
            print(f"  FAIL: Template syntax found: {actual['template_syntax']}")
            all_pass = False
        else:
            print(f"  PASS: No template syntax")

    print("\nChecking hidden element inventory...")
    current_unique = len(current_inventory)
    current_matches = sum(len(item['matched_selectors']) for item in current_inventory)
    print(f"  Expected: {expected_unique} unique elements, {expected_matches} selector matches")
    print(f"  Current:  {current_unique} unique elements, {current_matches} selector matches")

    if current_unique != expected_unique or current_matches != expected_matches:
        print("  FAIL: Totals changed")
        all_pass = False
    else:
        print("  PASS: Totals unchanged")

    def sort_key(x):
        return (x['page'], x['tag'], x['id'], x['class'], x['occurrence_index'])

    expected_sorted = sorted(expected_inventory, key=sort_key)
    current_sorted = sorted(current_inventory, key=sort_key)

    inventory_match = len(expected_sorted) == len(current_sorted)
    if inventory_match:
        for exp, cur in zip(expected_sorted, current_sorted):
            exp_key = (
                exp['page'], exp['tag'], exp['id'], exp['class'],
                exp['matched_selectors'], exp['outer_html_sha256'], exp['occurrence_index']
            )
            cur_key = (
                cur['page'], cur['tag'], cur['id'], cur['class'],
                cur['matched_selectors'], cur['outer_html_sha256'], cur['occurrence_index']
            )
            if exp_key != cur_key:
                inventory_match = False
                break

    if not inventory_match:
        print("  FAIL: Hidden element inventory changed")
        all_pass = False
    else:
        print("  PASS: Hidden element inventory unchanged")

    print("\nChecking repo-level files...")

    # Fail closed: required files must exist in the scanned tree
    for name, key in (('llms.txt', 'llms_txt_blob_sha'), ('robots.txt', 'robots_txt_blob_sha')):
        candidate = root_path / name
        if not candidate.exists():
            print(f"  FAIL: {name} missing from {root_path}")
            all_pass = False
            continue
        if key not in fixture:
            print(f"  FAIL: fixture missing {key}")
            all_pass = False
            continue
        result = subprocess.run(
            ['git', 'hash-object', str(candidate)],
            capture_output=True, text=True, cwd=git_root
        )
        current_sha = result.stdout.strip()
        expected_sha = fixture[key]
        if current_sha != expected_sha:
            print(f"  FAIL: {name} blob SHA mismatch (expected {expected_sha}, got {current_sha})")
            all_pass = False
        else:
            print(f"  PASS: {name} blob SHA matches ({expected_sha})")

    sitemap_file = root_path / 'sitemap.xml'
    if not sitemap_file.exists():
        print(f"  FAIL: sitemap.xml missing from {root_path}")
        all_pass = False
    else:
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content_no_lastmod = re.sub(r'<lastmod>.*?</lastmod>', '<lastmod></lastmod>', content)
        if content_no_lastmod != fixture.get('sitemap_xml_normalized'):
            print("  FAIL: sitemap.xml structure changed")
            all_pass = False
        else:
            print("  PASS: sitemap.xml structure unchanged")

    if 'cname_sha256' in fixture:
        cname_file = root_path / 'CNAME'
        if not cname_file.exists():
            print(f"  FAIL: CNAME missing from {root_path}")
            all_pass = False
        else:
            with open(cname_file, 'rb') as f:
                current = hashlib.sha256(f.read()).hexdigest()
            if current != fixture['cname_sha256']:
                print("  FAIL: CNAME changed")
                all_pass = False
            else:
                print("  PASS: CNAME unchanged")

    print()
    if all_pass:
        print("All checks PASSED")
        return 0
    print("Some checks FAILED")
    return 1


def main():
    parser = argparse.ArgumentParser(description='Lock and verify critical site content')
    parser.add_argument('mode', choices=['snapshot', 'check'],
                        help='Mode: snapshot (create fixture) or check (verify against fixture)')
    parser.add_argument('--root', default='.',
                        help='Root directory to scan (default: current directory)')
    parser.add_argument('--fixture', default='_qa/locked-fixture.json',
                        help='Fixture file path')
    parser.add_argument('--hidden-inventory', default='_qa/hidden-inventory.json',
                        help='Hidden element inventory file path')
    parser.add_argument('--exceptions', default='_qa/locked-exceptions.json',
                        help='Exceptions file path')
    parser.add_argument('--source-commit', default=None,
                        help='Source commit SHA to record in the fixture (snapshot only)')

    args = parser.parse_args()

    if args.mode == 'snapshot':
        snapshot_command(
            args.root, args.fixture, args.hidden_inventory,
            source_commit=args.source_commit
        )
        return 0
    if args.mode == 'check':
        return check_command(
            args.root, args.fixture, args.hidden_inventory, args.exceptions
        )
    return 1


if __name__ == '__main__':
    sys.exit(main())
