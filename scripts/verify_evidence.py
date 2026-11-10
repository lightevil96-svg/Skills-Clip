#!/usr/bin/env python3
"""Verify inspection-file integrity, separately from source truth and human review."""
import argparse
from pathlib import Path
import subprocess
import sys

from media_tools import check_source, confined_file, sha256
from validate_artifacts import load_json


def verify_manifest(manifest_path, source):
    manifest_path = Path(manifest_path)
    manifest = load_json(manifest_path)
    if manifest['format'] != 'skills-clip-inspection-v1' or not manifest['artifacts']:
        raise ValueError('Unknown or empty inspection manifest')
    check_source(manifest['source'], source)
    seen = set()
    for artifact in manifest['artifacts']:
        path = confined_file(manifest_path.parent, artifact['path'])
        if path in seen:
            raise ValueError('Duplicate evidence file')
        seen.add(path)
        if sha256(path) != artifact['sha256']:
            raise ValueError(f'Evidence hash mismatch: {artifact["path"]}')
    return {'integrity': 'PASS', 'files_checked': len(seen), 'semantic_review': 'NOT_RUN',
            'limitation': 'A matching hash proves neither an observation nor an authentic review receipt.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_manifest(args.manifest, args.source)
        print(f'PASS: source metadata/hash and {result["files_checked"]} files; semantic review NOT_RUN')
        return 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
