#!/usr/bin/env python3
"""Validate repository skill manifests and required operating-contract sections."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "clip-router", "vtuber-gameplay-facecam-clip", "vtuber-conversation-clip",
    "vtuber-collab-reaction-clip", "transcript-and-speaker-pipeline",
    "caption-design", "audio-mix-and-sfx", "hook-pacing-retention",
    "ffmpeg-vertical-quality", "render-package-for-user", "qa-and-self-review",
]
REQUIRED = [
    "Tujuan", "Aturan wajib", "Langkah kerja", "Potongan FFmpeg",
    "Checklist QA", "Kesalahan umum", "Batas kemampuan AI",
]

def main():
    errors = []
    for folder in SKILLS:
        path = ROOT / folder / "SKILL.md"
        if not path.exists():
            errors.append(f"MISSING {path.relative_to(ROOT)}")
            continue
        body = path.read_text(encoding="utf-8")
        if not body.startswith("---\n"):
            errors.append(f"{folder}: missing YAML frontmatter")
            continue
        end = body.find("\n---", 4)
        if end < 0:
            errors.append(f"{folder}: frontmatter not closed")
            continue
        front = body[4:end]
        name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", front)
        desc = re.search(r"(?m)^description:\s*(.+)$", front)
        if not name or name.group(1) != folder:
            errors.append(f"{folder}: frontmatter name does not match directory")
        if not desc or len(desc.group(1).strip()) < 30:
            errors.append(f"{folder}: description missing or too short")
        content = body[end + 4:]
        for heading in REQUIRED:
            if heading.lower() not in content.lower():
                errors.append(f"{folder}: missing section {heading}")
        if content.count("~~~~") % 2:
            errors.append(f"{folder}: unbalanced tilde code fences")
    for required in ["README.md", "AGENT_OPERATING_CONTRACT.md", "evals/cases.md"]:
        if not (ROOT / required).exists():
            errors.append(f"MISSING {required}")
    if errors:
        print("FAIL")
        for e in errors:
            print("- " + e)
        return 1
    print(f"PASS: {len(SKILLS)} skill directories and repository entry documents checked.")
    print("This validates structure only, not FFmpeg execution or editorial quality.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
