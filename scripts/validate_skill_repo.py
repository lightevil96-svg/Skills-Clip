#!/usr/bin/env python3
"""Validate skill discovery, links, schemas and example semantics offline."""
from pathlib import Path
import re
import sys

import yaml

from validate_artifacts import ROOT, SKILLS, load_json, validate

REQUIRED = ['Tujuan', 'Aturan wajib', 'Langkah kerja', 'Potongan FFmpeg',
            'Checklist QA', 'Kesalahan umum', 'Batas kemampuan AI']
CONVERSATION_REQUIRED = ['Objective', 'Non-negotiable rules', 'Editing workflow',
                         'Quality-control checklist', 'Anti-patterns']


def check_structure(root=ROOT):
    root = Path(root)
    errors = []
    found = {p.parent.name for p in root.glob('*/SKILL.md')}
    for folder in sorted(SKILLS - found):
        errors.append(f'MISSING {folder}/SKILL.md')
    for folder in sorted(found - SKILLS):
        errors.append(f'Unregistered skill: {folder}; update discovery registry')
    readme = (root / 'README.md').read_text(encoding='utf-8') if (root / 'README.md').exists() else ''
    for folder in sorted(found):
        body = (root / folder / 'SKILL.md').read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---(?:\n|$)', body, re.S)
        if not match:
            errors.append(f'{folder}: missing/unclosed YAML frontmatter')
            continue
        try:
            front = yaml.safe_load(match[1])
        except yaml.YAMLError as exc:
            errors.append(f'{folder}: invalid YAML: {exc}')
            continue
        if not isinstance(front, dict):
            errors.append(f'{folder}: frontmatter must be a mapping')
            continue
        if front.get('name') != folder or not re.fullmatch(r'[a-z0-9-]{1,64}', folder):
            errors.append(f'{folder}: invalid or mismatched name')
        if not isinstance(front.get('description'), str) or len(front['description']) < 30:
            errors.append(f'{folder}: description missing or too short')
        if set(front) != {'name', 'description'}:
            errors.append(f'{folder}: unexpected frontmatter keys')
        content = body[match.end():]
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.M)
        needed = CONVERSATION_REQUIRED if folder == 'vtuber-conversation-clip' else REQUIRED
        for heading in needed:
            if heading not in headings:
                errors.append(f'{folder}: missing heading {heading}')
        if f'{folder}/SKILL.md' not in readme:
            errors.append(f'{folder}: not discoverable from README')
        if folder != 'editorial-intelligence' and '../editorial-intelligence/SKILL.md' not in body:
            errors.append(f'{folder}: missing editorial handoff link')
    for required in ['README.md', 'AGENT_OPERATING_CONTRACT.md', 'evals/cases.md',
                     'schemas/README.md', 'qa-and-self-review/references/editorial-rubric.md']:
        if not (root / required).exists():
            errors.append(f'MISSING {required}')
    for path in root.rglob('*.md'):
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        fence = None
        clean = []
        for line in text.splitlines():
            m = re.match(r'^\s*(`{3,}|~{3,})', line)
            if m:
                marker = m[1]
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
                continue
            if fence is None:
                clean.append(line)
        if fence:
            errors.append(f'{path.relative_to(root)}: unbalanced code fence')
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', '\n'.join(clean)):
            if re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#)', target):
                continue
            target = target.split('#', 1)[0]
            if target and not (path.parent / target).exists():
                errors.append(f'{path.relative_to(root)}: broken link {target}')
    cases = (root/'evals/cases.md').read_text() if (root/'evals/cases.md').exists() else ''
    for gate in range(1, 9):
        if not re.search(rf'^## Gate {gate}\b', cases, re.M):
            errors.append(f'Missing original evaluation gate {gate}')
    for case in range(1, 13):
        if not re.search(rf'^## E{case:02}\b', cases, re.M):
            errors.append(f'Missing editorial scenario E{case:02}')
    return errors


def check_examples():
    errors = []
    mapping = {
        'edit-plan.example.json':'edit-plan',
        'edit-plan.editorial.example.json':'edit-plan',
        'transcript.example.json':'transcript',
        'transcript.editorial.example.json':'transcript',
        'style-profile.example.json':'style-profile',
        'editorial-review.example.json':'editorial-review',
    }
    for name, kind in mapping.items():
        try:
            data = load_json(ROOT/'examples'/name)
            supplied = {}
            if name == 'edit-plan.editorial.example.json':
                supplied['transcript'] = load_json(ROOT/'examples/transcript.editorial.example.json')
            problems, _ = validate(kind, data, **supplied)
            errors.extend(f'{name}: {p}' for p in problems)
        except (OSError, ValueError) as exc:
            errors.append(f'{name}: {exc}')
    for path in (ROOT/'examples').glob('*.json'):
        if path.name not in mapping:
            errors.append(f'Unregistered example {path.name}')
    return errors


def main():
    errors = check_structure() + check_examples()
    if errors:
        print('FAIL')
        for error in errors:
            print('- '+error)
        return 1
    print(f'PASS: {len(SKILLS)} skills, local links, 5 schemas and 6 examples checked.')
    print('Checks validate structure and declared consistency, not source truth or editorial quality.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
