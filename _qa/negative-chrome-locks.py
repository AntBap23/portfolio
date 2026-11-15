#!/usr/bin/env python3
"""
Fail-closed negative tests for redesign 1d/1e chrome / P2 / F18 locks.

Applies each forbidden edit to a temp copy of the built site (and, where noted,
temp copies of the checker / exceptions) and asserts locked-check exits non-zero.
The unmodified build must still pass.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / '_qa' / '_site'
CHECKER = REPO / '_qa' / 'locked-check.py'
EXCEPTIONS = REPO / '_qa' / 'locked-exceptions.json'
FIXTURE = REPO / '_qa' / 'locked-fixture.json'
HIDDEN = REPO / '_qa' / 'hidden-inventory.json'


def run_check(root: Path, checker: Path = CHECKER, exceptions: Path = EXCEPTIONS) -> int:
    r = subprocess.run(
        [
            sys.executable,
            str(checker),
            'check',
            '--root',
            str(root),
            '--fixture',
            str(FIXTURE),
            '--hidden-inventory',
            str(HIDDEN),
            '--exceptions',
            str(exceptions),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    return r.returncode, r.stdout, r.stderr


def mutate_all_pages(site: Path, old: str, new: str, count: int = 0) -> int:
    """Replace old->new across rendered HTML. count=0 means all."""
    n = 0
    for path in site.rglob('index.html'):
        text = path.read_text(encoding='utf-8')
        if old not in text:
            continue
        if count:
            text2 = text.replace(old, new, count)
        else:
            text2 = text.replace(old, new)
        if text2 != text:
            path.write_text(text2, encoding='utf-8')
            n += 1
    return n


def main() -> int:
    if not SITE.exists():
        print('FAIL: missing _qa/_site; run bash _qa/build.sh first')
        return 1

    code, out, err = run_check(SITE)
    if code != 0:
        print('FAIL: unmodified build must pass before negatives')
        print(out[-2000:])
        print(err[-1000:])
        return 1
    print('PASS: unmodified build passes locked-check')

    tmp = Path(tempfile.mkdtemp(prefix='locked-1e-neg-'))
    site = tmp / '_site'
    results = []
    F18 = 'https://calendly.com/bapanalytics00/project-discussion'
    LEGACY = 'https://calendly.com/bapanalytics00'

    def case(label: str, mutate) -> None:
        if site.exists():
            shutil.rmtree(site)
        shutil.copytree(SITE, site)
        mutate(site)
        code, out, _ = run_check(site)
        ok = code != 0
        print(f"{'PASS' if ok else 'FAIL'} negative: {label} (exit {code})")
        if not ok:
            print(out[-800:])
        results.append(ok)

    # 1) Proposal CTA href in header
    case(
        'header proposal CTA href change fails',
        lambda s: mutate_all_pages(
            s,
            'href="/consulting/#inquiry" class="btn btn-primary nav-cta"',
            'href="/consulting/#changed" class="btn btn-primary nav-cta"',
        ),
    )

    # 2) Proposal CTA label in header
    case(
        'header proposal CTA label change fails',
        lambda s: mutate_all_pages(
            s,
            'class="btn btn-primary nav-cta">Request a Project Proposal</a>',
            'class="btn btn-primary nav-cta">Request a Quote</a>',
        ),
    )

    # 3) Booking bar proposal CTA
    case(
        'booking-bar proposal CTA href change fails',
        lambda s: mutate_all_pages(
            s,
            'href="/consulting/#inquiry" class="btn btn-primary">Request a Project Proposal</a>',
            'href="/consulting/#changed" class="btn btn-primary">Request a Project Proposal</a>',
        ),
    )

    # 4) Footer proposal link
    case(
        'footer proposal link change fails',
        lambda s: mutate_all_pages(
            s,
            '<a href="/consulting/#inquiry">Request a Project Proposal</a>',
            '<a href="/consulting/#changed">Request a Project Proposal</a>',
        ),
    )

    # 5) Footer blurb
    case(
        'footer blurb change fails',
        lambda s: mutate_all_pages(
            s,
            'Independent analytics, digital experience, and applied AI consulting with defined deliverables.',
            'Changed blurb text for testing.',
        ),
    )

    # 6) Footer heading
    case(
        'footer heading change fails',
        lambda s: mutate_all_pages(s, '<h3>Explore</h3>', '<h3>Links</h3>'),
    )

    # 7) Footer email
    case(
        'footer email change fails',
        lambda s: mutate_all_pages(
            s,
            'href="mailto:bapanalytics00@gmail.com">bapanalytics00@gmail.com</a>',
            'href="mailto:changed@example.com">changed@example.com</a>',
        ),
    )

    # 8) Footer copyright
    case(
        'footer copyright change fails',
        lambda s: mutate_all_pages(
            s,
            '&copy; 2026 Anthony Baptiste. All rights reserved.',
            '&copy; 2025 Changed. All rights reserved.',
        ),
    )

    # 9) Remove Research link
    def remove_research(s: Path) -> None:
        mutate_all_pages(
            s,
            '<a href="/research/">Research</a>\n',
            '',
        )

    case('removing Research link fails', remove_research)

    # 9b) Replacing Resume with removed /competitions/ footer link fails (13-URL chrome lock)
    case(
        'replacing resume footer link with competitions fails',
        lambda s: mutate_all_pages(
            s,
            '<a href="/resume/">Resume</a>',
            '<a href="/competitions/">Competitions</a>',
        ),
    )

    # 10) Rename nav Projects
    case(
        "renaming nav 'Projects' fails",
        lambda s: mutate_all_pages(
            s,
            '<a href="/projects/">Projects</a>',
            '<a href="/projects/">Portfolio</a>',
        ),
    )

    # 11) P2 rename in HTML + allowlist (constant must still fail closed)
    def p2_both(s: Path) -> None:
        mutate_all_pages(
            s,
            '>Analytics Clarity Audit</a>',
            '>Analytics Clarity Review</a>',
        )
        exc_path = tmp / 'exceptions-p2.json'
        data = json.loads(EXCEPTIONS.read_text(encoding='utf-8'))
        for exc in data['exceptions']:
            if exc.get('class') == 'P2':
                for el in exc.get('elements', []):
                    if el.get('href') == '/consulting/services/#analytics-clarity-audit':
                        el['text'] = 'Analytics Clarity Review'
        exc_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        # Stash path for runner via attribute
        p2_both.exc_path = exc_path

    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    p2_both(site)
    code, out, _ = run_check(site, exceptions=p2_both.exc_path)
    ok = code != 0
    print(f"{'PASS' if ok else 'FAIL'} negative: P2 rename in HTML+allowlist fails (exit {code})")
    if not ok:
        print(out[-800:])
    results.append(ok)

    # 12) pages:'*' rejected
    def star_pages(_s: Path) -> Path:
        exc_path = tmp / 'exceptions-star.json'
        data = json.loads(EXCEPTIONS.read_text(encoding='utf-8'))
        for exc in data['exceptions']:
            if exc.get('class') == 'P2':
                exc['pages'] = ['*']
        exc_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return exc_path

    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    star_exc = star_pages(site)
    code, out, err = run_check(site, exceptions=star_exc)
    ok = code != 0 and ("'*'" in out or "'*'" in err or 'pages' in out.lower() or 'pages' in err.lower())
    print(f"{'PASS' if ok else 'FAIL'} negative: pages:'*' rejected (exit {code})")
    if not ok:
        print(out[-500:])
        print(err[-500:])
    results.append(ok)

    # 13) Broad P2 element selector rejected
    def broad_p2(_s: Path) -> Path:
        exc_path = tmp / 'exceptions-broad.json'
        data = json.loads(EXCEPTIONS.read_text(encoding='utf-8'))
        for exc in data['exceptions']:
            if exc.get('class') == 'P2':
                exc['element'] = 'footer.site-footer a'
        exc_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return exc_path

    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    broad_exc = broad_p2(site)
    code, out, _ = run_check(site, exceptions=broad_exc)
    ok = code != 0
    print(f"{'PASS' if ok else 'FAIL'} negative: broad P2 footer.site-footer a rejected (exit {code})")
    if not ok:
        print(out[-800:])
    results.append(ok)

    # 14) Old Calendly URL anywhere fails
    case(
        'old-URL Calendly link anywhere fails',
        lambda s: mutate_all_pages(s, F18, LEGACY),
    )

    # 15) Different Calendly label fails
    case(
        'different Calendly label fails',
        lambda s: mutate_all_pages(
            s,
            f'href="{F18}" class="btn btn-secondary nav-cta-secondary" target="_blank" rel="noopener noreferrer">Book an Intro Call</a>',
            f'href="{F18}" class="btn btn-secondary nav-cta-secondary" target="_blank" rel="noopener noreferrer">Book a Call</a>',
        ),
    )

    # 16) Hero CTA href change fails (home Proposal in hero)
    case(
        'hero CTA href change fails',
        lambda s: mutate_all_pages(
            s,
            'href="/consulting/#inquiry" class="btn btn-primary">Request a Project Proposal</a>',
            'href="/consulting/#changed" class="btn btn-primary">Request a Project Proposal</a>',
            count=1,
        ),
    )

    # 17) Home teaser internal link href change fails
    def teaser_href(s: Path) -> None:
        home = s / 'index.html'
        text = home.read_text(encoding='utf-8')
        text2 = text.replace(
            'href="/consulting/services/#analytics-clarity-audit"',
            'href="/consulting/services/#analytics-clarity-audit-CHANGED"',
            1,
        )
        if text2 == text:
            raise RuntimeError('teaser href not found on home')
        home.write_text(text2, encoding='utf-8')

    case('home teaser h3 href change fails', teaser_href)

    shutil.rmtree(tmp, ignore_errors=True)

    # Reconfirm unmodified still passes
    code, _, _ = run_check(SITE)
    results.append(code == 0)
    print(f"{'PASS' if code == 0 else 'FAIL'}: unmodified build still passes")

    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"ALL NEGATIVE {'PASS' if all(results) else 'FAIL'} ({passed}/{total})")
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
