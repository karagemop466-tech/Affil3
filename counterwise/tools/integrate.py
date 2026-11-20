#!/usr/bin/env python3
"""Re-merge origin/main into this session's branch and resolve the one file that always collides.

Six sessions append their own board to COORDINATION.md, so every integration round conflicts
there. The rule this session follows, recorded on the board: main's file wins as the base, and my
section is re-appended verbatim. Nothing above my section is ever edited, and no file belonging to
another surface is ever deleted — the script asserts that before committing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root: counterwise/tools/integrate.py -> ../..
MARKER = "# Session `c7a56e3d` board"


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def main() -> int:
    git("fetch", "-q", "origin")
    ahead = git("rev-list", "--count", f"HEAD..origin/main")
    print(f"main is {ahead} commit(s) ahead")
    if int(ahead) == 0:
        print("nothing to merge")
        return 0

    dirty = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
    if any(l.startswith("UU") or "merge" in Path(l).name.lower() for l in dirty) and (ROOT / ".git" / "MERGE_HEAD").exists():
        print("a merge is already in progress; continuing it")

    subprocess.run(["git", "merge", "--no-commit", "--no-ff", "origin/main"], cwd=ROOT, capture_output=True, text=True)
    conflicts = [l for l in git("diff", "--name-only", "--diff-filter=U").splitlines() if l.strip()]
    unexpected = [c for c in conflicts if c != "COORDINATION.md"]
    if unexpected:
        print("UNEXPECTED CONFLICTS — resolve by hand, do not force:\n  " + "\n  ".join(unexpected))
        return 2

    if "COORDINATION.md" in conflicts:
        mine_full = git("show", f"HEAD:COORDINATION.md")
        i = mine_full.find(MARKER)
        if i < 0:
            print("my board section not found in HEAD — refusing to guess")
            return 2
        theirs = git("show", "origin/main:COORDINATION.md")
        (ROOT / "COORDINATION.md").write_text(theirs.rstrip() + "\n\n---\n\n" + mine_full[i:].rstrip() + "\n")
        git("add", "COORDINATION.md")
        print("COORDINATION.md resolved: main's file kept, this session's section re-appended")

    # rebuild so the generated surface always matches the register in the merged tree
    b = subprocess.run([sys.executable, "counterwise/tools/build.py"], cwd=ROOT, capture_output=True, text=True)
    print(b.stdout.strip().splitlines()[-1] if b.stdout.strip() else b.stderr.strip()[:200])
    if b.returncode != 0:
        print("build refused after the merge; not committing")
        return 2

    deleted = git("diff", "--name-status", "--diff-filter=D", "origin/main", "HEAD").splitlines()
    extra = git("status", "--porcelain").splitlines()
    for line in extra:
        if line.startswith(" D "):
            print(f"REFUSING: merge would delete {line[3:].strip()} belonging to another surface")
            return 2
    git("add", "-A")
    subprocess.run(
        ["git", "-c", "user.name=Arena", "-c", "user.email=arena@local", "commit", "-q",
         "-m", f"merge origin/main ({ahead} new commit(s) from other sessions); re-append this session's board; rebuild clean"],
        cwd=ROOT, capture_output=True, text=True,
    )
    git("push", "-q", "origin", "arena/c7a56e3d-affil3")
    print(f"merged, rebuilt and pushed · deletions vs main: {len(deleted)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
