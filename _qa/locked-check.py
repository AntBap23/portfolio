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
import sys
from html.parser import HTMLParser
from pathlib import Path


class ElementTracker:
    """Track elements and build CSS selector paths."""
    
    def __init__(self):
        self.path = []
        self.id_map = {}
        self.class_counts = {}
        
    def push(self, tag, attrs_dict):
        """Push element onto stack."""
        elem_id = attrs_dict.get('id')
        classes = attrs_dict.get('class', '').split()
        
        if elem_id:
            selector = f"{tag}#{elem_id}"
        elif classes:
            selector = f"{tag}.{'.'.join(classes)}"
        else:
            # Count this tag at current level
            key = (len(self.path), tag)
            self.class_counts[key] = self.class_counts.get(key, 0) + 1
            nth = self.class_counts[key]
            selector = f"{tag}:nth-of-type({nth})"
            
        self.path.append(selector)
        
    def pop(self):
        """Pop element from stack."""
        if self.path:
            self.path.pop()
            
    def get_selector(self):
        """Get CSS selector path."""
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
            'hidden_elements': [],
            'template_syntax': []
        }
        self.tracker = ElementTracker()
        self.current_tag = None
        self.current_attrs = {}
        self.tag_stack = []
        self.form_context = None
        
        # For capturing raw content including whitespace
        self.in_script_jsonld = False
        self.in_title = False
        self.jsonld_raw = []
        self.title_raw = []
        
        # For hidden element tracking
        self.hidden_capture = None
        self.hidden_html = []
        
        # For general content capture
        self.capture_contexts = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag
        self.current_attrs = attrs_dict
        self.tag_stack.append((tag, attrs_dict, self.getpos()))
        self.tracker.push(tag, attrs_dict)
        
        # Check for hidden elements - exact QA definition
        is_hidden = False
        hidden_reason = None
        
        if attrs_dict.get('hidden') is not None:
            is_hidden = True
            hidden_reason = 'hidden-attribute'
        elif attrs_dict.get('aria-hidden') == 'true':
            is_hidden = True
            hidden_reason = 'aria-hidden'
        elif 'sr-only' in attrs_dict.get('class', '').split():
            is_hidden = True
            hidden_reason = 'sr-only'
        else:
            style = attrs_dict.get('style', '')
            if 'display:none' in style.replace(' ', '') or 'display: none' in style:
                is_hidden = True
                hidden_reason = 'display-none'
            elif 'visibility:hidden' in style.replace(' ', '') or 'visibility: hidden' in style:
                is_hidden = True
                hidden_reason = 'visibility-hidden'
                
        if is_hidden:
            self.hidden_capture = {
                'selector': self.tracker.get_selector(),
                'reason': hidden_reason,
                'tag': tag,
                'start_pos': self.getpos()
            }
            self.hidden_html = [self.get_starttag_text()]
            
        # JSON-LD blocks - capture exact raw content
        if tag == 'script' and attrs_dict.get('type') == 'application/ld+json':
            self.in_script_jsonld = True
            self.jsonld_raw = [self.get_starttag_text()]
            
        # Title tag - capture with exact whitespace
        if tag == 'title':
            self.in_title = True
            self.title_raw = [self.get_starttag_text()]
            
        # Meta description - capture raw tag
        if tag == 'meta' and attrs_dict.get('name') == 'description':
            content = attrs_dict.get('content', '')
            self.results['meta_description'] = content
            self.results['meta_description_raw'] = self.get_starttag_text()
            
        # Element IDs (fragment identifiers)
        if 'id' in attrs_dict:
            self.results['element_ids'].append(attrs_dict['id'])
            
        # Contact forms
        if tag == 'form' and 'formspree.io' in attrs_dict.get('action', ''):
            self.form_context = {
                'action': attrs_dict.get('action', ''),
                'fields': []
            }
            
        # Form fields
        if self.form_context and tag in ('input', 'select', 'textarea'):
            field_info = {
                'type': tag,
                'name': attrs_dict.get('name', ''),
                'value': attrs_dict.get('value', ''),
                'id': attrs_dict.get('id', '')
            }
            if tag == 'input':
                field_info['input_type'] = attrs_dict.get('type', '')
            self.form_context['fields'].append(field_info)
            
        # Calendly links
        if tag == 'a' and 'calendly.com' in attrs_dict.get('href', ''):
            self.capture_contexts.append({
                'type': 'calendly',
                'href': attrs_dict.get('href', ''),
                'content': []
            })
            
        # Locked visible copy elements
        if tag == 'h1':
            self.capture_contexts.append({
                'type': 'h1',
                'content': []
            })
        elif 'answer-summary' in attrs_dict.get('class', '').split():
            self.capture_contexts.append({
                'type': 'answer-summary',
                'content': []
            })
            
    def handle_endtag(self, tag):
        # Hidden element capture
        if self.hidden_capture and self.hidden_capture['tag'] == tag:
            self.hidden_html.append(f"</{tag}>")
            outer_html = ''.join(self.hidden_html)
            outer_hash = hashlib.sha256(outer_html.encode('utf-8')).hexdigest()
            
            self.results['hidden_elements'].append({
                'selector': self.hidden_capture['selector'],
                'reason': self.hidden_capture['reason'],
                'outer_html_sha256': outer_hash
            })
            
            self.hidden_capture = None
            self.hidden_html = []
            
        # JSON-LD blocks
        if self.in_script_jsonld and tag == 'script':
            self.jsonld_raw.append('</script>')
            raw_block = ''.join(self.jsonld_raw)
            self.results['jsonld_blocks'].append(raw_block)
            self.in_script_jsonld = False
            self.jsonld_raw = []
            
        # Title tag
        if self.in_title and tag == 'title':
            self.title_raw.append('</title>')
            self.results['title_raw'] = ''.join(self.title_raw)
            self.in_title = False
            self.title_raw = []
            
        # Contact forms
        if self.form_context and tag == 'form':
            self.results['contact_forms'].append(self.form_context)
            self.form_context = None
            
        # Capture contexts
        if self.capture_contexts:
            for ctx in self.capture_contexts[:]:
                content_text = ''.join(ctx['content']).strip()
                
                if ctx['type'] == 'calendly':
                    self.results['calendly_links'].append({
                        'href': ctx['href'],
                        'text': content_text
                    })
                    self.capture_contexts.remove(ctx)
                elif ctx['type'] in ('h1', 'answer-summary'):
                    if content_text:
                        self.results['locked_copy'].append({
                            'type': ctx['type'],
                            'text': content_text
                        })
                    self.capture_contexts.remove(ctx)
                    
        if self.tag_stack:
            self.tag_stack.pop()
        self.tracker.pop()
        
    def handle_data(self, data):
        # Hidden element capture
        if self.hidden_capture:
            self.hidden_html.append(data)
            
        # JSON-LD raw capture
        if self.in_script_jsonld:
            self.jsonld_raw.append(data)
            
        # Title raw capture
        if self.in_title:
            self.title_raw.append(data)
            
        # Capture contexts
        for ctx in self.capture_contexts:
            ctx['content'].append(data)
            
        # Check for template syntax
        if data and ('{{' in data or '{%' in data or '{#' in data):
            self.results['template_syntax'].append({
                'context': data[:100],
                'markers': [m for m in ['{{', '{%', '{#'] if m in data]
            })
            
    def handle_comment(self, data):
        """Track HTML comments - expect 0."""
        selector = self.tracker.get_selector() + ' > comment()'
        outer_html = f"<!--{data}-->"
        outer_hash = hashlib.sha256(outer_html.encode('utf-8')).hexdigest()
        
        self.results['hidden_elements'].append({
            'selector': selector,
            'reason': 'html-comment',
            'outer_html_sha256': outer_hash
        })


def scan_for_locked_copy(html_content):
    """Scan for additional locked copy patterns using string search."""
    locked_patterns = []
    
    # Prices (text containing $)
    lines = html_content.split('\n')
    for line in lines:
        if '$' in line and '<' in line:
            # Extract visible text around $ signs
            price_pattern = r'>\s*([^<]*\$[^<]*)<'
            matches = re.findall(price_pattern, line)
            for match in matches:
                text = match.strip()
                if text and len(text) < 200:
                    locked_patterns.append({'type': 'price', 'text': text})
                    
    # Employer disclaimer
    if 'Employers are not presented as independent consulting clients' in html_content:
        match = re.search(r'(Employers are not presented as independent consulting clients\.?[^<]*)', html_content)
        if match:
            locked_patterns.append({'type': 'employer_disclaimer', 'text': match.group(1).strip()})
            
    return locked_patterns


def parse_html_file(filepath):
    """Parse an HTML file and extract locked content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    parser = LockedContentParser()
    parser.feed(html_content)
    
    # Add additional locked copy from string scanning
    additional_copy = scan_for_locked_copy(html_content)
    parser.results['locked_copy'].extend(additional_copy)
    
    # Sort JSON-LD blocks for order-independent comparison (raw strings)
    parser.results['jsonld_blocks'] = sorted(parser.results['jsonld_blocks'])
    
    return parser.results


def get_page_paths(root_dir):
    """Find all index.html pages that GitHub Pages serves."""
    root_path = Path(root_dir)
    pages = []
    
    # Find all index.html files
    for index_file in sorted(root_path.rglob('index.html')):
        # Skip _qa, node_modules, and other non-published directories
        rel_path = index_file.relative_to(root_path)
        path_parts = rel_path.parts
        
        if any(part.startswith('_') or part == 'node_modules' or part == 'vendor' for part in path_parts):
            continue
            
        # Convert to URL path
        if rel_path == Path('index.html'):
            url_path = '/'
        else:
            url_path = '/' + str(rel_path.parent) + '/'
            
        pages.append({
            'url_path': url_path,
            'file_path': str(index_file)
        })
        
    return pages


def compute_fixture_id(fixture_data):
    """Compute SHA256 hash of fixture content (excluding metadata fields)."""
    # Create a copy without metadata
    data_copy = {k: v for k, v in fixture_data.items() if k not in ('fixture_id', 'source_commit')}
    canonical = json.dumps(data_copy, sort_keys=True, indent=2)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def snapshot_command(root_dir, output_file, hidden_inventory_file):
    """Generate and save a locked content fixture."""
    print(f"Scanning pages in {root_dir}...")
    pages = get_page_paths(root_dir)
    
    print(f"Found {len(pages)} pages:")
    for page in pages:
        print(f"  {page['url_path']}")
        
    fixture = {
        'pages': {}
    }
    
    hidden_inventory = []
    
    for page in pages:
        print(f"Processing {page['url_path']}...")
        results = parse_html_file(page['file_path'])
        
        # Extract hidden elements for inventory
        for hidden_elem in results['hidden_elements']:
            hidden_inventory.append({
                'page': page['url_path'],
                'selector': hidden_elem['selector'],
                'reason': hidden_elem['reason'],
                'outer_html_sha256': hidden_elem['outer_html_sha256']
            })
            
        fixture['pages'][page['url_path']] = results
        
    # Repo-level checks
    print("Checking repo-level files...")
    root_path = Path(root_dir)
    
    # Find git repo root
    import subprocess
    try:
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                              capture_output=True, text=True, cwd=root_dir)
        if result.returncode == 0:
            git_root = Path(result.stdout.strip())
        else:
            git_root = root_path
    except:
        git_root = root_path
    
    # llms.txt - lock by git blob SHA (look in git root)
    llms_file = git_root / 'llms.txt'
    if llms_file.exists():
        result = subprocess.run(['git', 'hash-object', str(llms_file)],
                              capture_output=True, text=True, cwd=git_root)
        if result.returncode == 0:
            fixture['llms_txt_blob_sha'] = result.stdout.strip()
            
    # robots.txt - lock by git blob SHA (look in git root)
    robots_file = git_root / 'robots.txt'
    if robots_file.exists():
        result = subprocess.run(['git', 'hash-object', str(robots_file)],
                              capture_output=True, text=True, cwd=git_root)
        if result.returncode == 0:
            fixture['robots_txt_blob_sha'] = result.stdout.strip()
            
    # sitemap.xml (ignoring lastmod values) - check in root_dir
    sitemap_file = root_path / 'sitemap.xml'
    if sitemap_file.exists():
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove lastmod tags for comparison
        content_no_lastmod = re.sub(r'<lastmod>.*?</lastmod>', '<lastmod></lastmod>', content)
        fixture['sitemap_xml_normalized'] = content_no_lastmod
        
    # Get source commit SHA if in git repo
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=root_dir)
        if result.returncode == 0:
            fixture['source_commit'] = result.stdout.strip()
    except:
        pass
        
    # Compute fixture ID
    fixture['fixture_id'] = compute_fixture_id(fixture)
    
    # Count hidden elements
    total_hidden = len(hidden_inventory)
    print(f"\nTotal hidden elements across all pages: {total_hidden}")
    
    # Per-page counts
    page_counts = {}
    for item in hidden_inventory:
        page_counts[item['page']] = page_counts.get(item['page'], 0) + 1
    print("\nPer-page hidden element counts:")
    for page_url in sorted(page_counts.keys()):
        print(f"  {page_url}: {page_counts[page_url]}")
    
    # Save fixture
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, indent=2)
        
    # Save hidden inventory
    with open(hidden_inventory_file, 'w', encoding='utf-8') as f:
        json.dump(hidden_inventory, f, indent=2)
        
    print(f"\nFixture saved to {output_file}")
    print(f"Hidden inventory saved to {hidden_inventory_file}")
    print(f"Fixture ID: {fixture['fixture_id']}")
    if 'source_commit' in fixture:
        print(f"Source commit: {fixture['source_commit']}")


def check_command(root_dir, fixture_file, hidden_inventory_file, exceptions_file):
    """Check current content against the locked fixture."""
    # Load fixture
    with open(fixture_file, 'r', encoding='utf-8') as f:
        fixture = json.load(f)
        
    print(f"Loaded fixture: {fixture_file}")
    print(f"Fixture ID: {fixture.get('fixture_id', 'N/A')}")
    if 'source_commit' in fixture:
        print(f"Source commit: {fixture['source_commit']}")
    print()
    
    # Load hidden inventory
    with open(hidden_inventory_file, 'r', encoding='utf-8') as f:
        expected_inventory = json.load(f)
        
    # Load exceptions
    exceptions = {}
    if os.path.exists(exceptions_file):
        with open(exceptions_file, 'r', encoding='utf-8') as f:
            exceptions = json.load(f)
            
    # Get current pages
    pages = get_page_paths(root_dir)
    all_pass = True
    
    # Build current inventory
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
        
        # Add to current inventory
        for hidden_elem in actual['hidden_elements']:
            current_inventory.append({
                'page': url_path,
                'selector': hidden_elem['selector'],
                'reason': hidden_elem['reason'],
                'outer_html_sha256': hidden_elem['outer_html_sha256']
            })
        
        # Check each category
        checks = [
            ('JSON-LD blocks', 'jsonld_blocks'),
            ('Title (raw)', 'title_raw'),
            ('Meta description (raw)', 'meta_description_raw'),
            ('Contact forms', 'contact_forms'),
            ('Calendly links', 'calendly_links'),
            ('Element IDs', 'element_ids'),
            ('Locked copy', 'locked_copy')
        ]
        
        for check_name, key in checks:
            if expected.get(key) != actual.get(key):
                print(f"  FAIL: {check_name} mismatch")
                all_pass = False
            else:
                print(f"  PASS: {check_name}")
                
        # Check for template syntax
        if actual.get('template_syntax'):
            print(f"  FAIL: Template syntax found: {actual['template_syntax']}")
            all_pass = False
        else:
            print(f"  PASS: No template syntax")
            
    # Check hidden inventory
    print("\nChecking hidden element inventory...")
    
    # Sort for comparison
    expected_sorted = sorted(expected_inventory, key=lambda x: (x['page'], x['selector']))
    current_sorted = sorted(current_inventory, key=lambda x: (x['page'], x['selector']))
    
    if expected_sorted != current_sorted:
        print("  FAIL: Hidden element inventory changed")
        
        # Show differences
        expected_set = {(item['page'], item['selector'], item['outer_html_sha256']) for item in expected_inventory}
        current_set = {(item['page'], item['selector'], item['outer_html_sha256']) for item in current_inventory}
        
        added = current_set - expected_set
        removed = expected_set - current_set
        
        if added:
            print(f"    Added elements: {len(added)}")
            for page, selector, sha in sorted(added)[:5]:
                print(f"      {page} > {selector}")
                
        if removed:
            print(f"    Removed elements: {len(removed)}")
            for page, selector, sha in sorted(removed)[:5]:
                print(f"      {page} > {selector}")
                
        all_pass = False
    else:
        print(f"  PASS: Hidden element inventory unchanged ({len(current_inventory)} elements)")
    
    # Repo-level checks
    print("\nChecking repo-level files...")
    root_path = Path(root_dir)
    
    # Find git repo root
    import subprocess
    try:
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                              capture_output=True, text=True, cwd=root_dir)
        if result.returncode == 0:
            git_root = Path(result.stdout.strip())
        else:
            git_root = root_path
    except:
        git_root = root_path
    
    # llms.txt - check blob SHA (look in git root)
    llms_file = git_root / 'llms.txt'
    if llms_file.exists() and 'llms_txt_blob_sha' in fixture:
        result = subprocess.run(['git', 'hash-object', str(llms_file)],
                              capture_output=True, text=True, cwd=git_root)
        if result.returncode == 0:
            current_sha = result.stdout.strip()
            expected_sha = fixture['llms_txt_blob_sha']
            if current_sha != expected_sha:
                print(f"  FAIL: llms.txt blob SHA mismatch (expected {expected_sha}, got {current_sha})")
                all_pass = False
            else:
                print(f"  PASS: llms.txt blob SHA matches ({expected_sha})")
                
    # robots.txt - check blob SHA (look in git root)
    robots_file = git_root / 'robots.txt'
    if robots_file.exists() and 'robots_txt_blob_sha' in fixture:
        result = subprocess.run(['git', 'hash-object', str(robots_file)],
                              capture_output=True, text=True, cwd=git_root)
        if result.returncode == 0:
            current_sha = result.stdout.strip()
            expected_sha = fixture['robots_txt_blob_sha']
            if current_sha != expected_sha:
                print(f"  FAIL: robots.txt blob SHA mismatch (expected {expected_sha}, got {current_sha})")
                all_pass = False
            else:
                print(f"  PASS: robots.txt blob SHA matches ({expected_sha})")
            
    # sitemap.xml - check in root_dir
    sitemap_file = root_path / 'sitemap.xml'
    if sitemap_file.exists():
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content_no_lastmod = re.sub(r'<lastmod>.*?</lastmod>', '<lastmod></lastmod>', content)
        if content_no_lastmod != fixture.get('sitemap_xml_normalized'):
            print("  FAIL: sitemap.xml structure changed")
            all_pass = False
        else:
            print("  PASS: sitemap.xml structure unchanged")
            
    print()
    if all_pass:
        print("✓ All checks PASSED")
        return 0
    else:
        print("✗ Some checks FAILED")
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
    
    args = parser.parse_args()
    
    if args.mode == 'snapshot':
        snapshot_command(args.root, args.fixture, args.hidden_inventory)
        return 0
    elif args.mode == 'check':
        return check_command(args.root, args.fixture, args.hidden_inventory, args.exceptions)
        
    return 1


if __name__ == '__main__':
    sys.exit(main())
