#!/usr/bin/env python3
"""Regenerate the FEPs section of README.md from local FEP directories and open GitHub PRs."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
FEPS_DIR = REPO_ROOT / "FEPs"
README_PATH = REPO_ROOT / "README.md"

SECTIONS = [
    ("Proposed",                           ["Proposed"]),
    ("Draft",                              ["Draft"]),
    ("Active",                             ["Active"]),
    ("Accepted (awaiting implementation)", ["Accepted"]),
    ("Implemented",                        ["Implemented"]),
    ("Rejected",                           ["Rejected"]),
    ("Withdrawn",                          ["Withdrawn"]),
]

STATUS_TO_SECTION: dict[str, str] = {
    status: section
    for section, statuses in SECTIONS
    for status in statuses
}

STAGE_LABEL_PREFIX = "Stage: "

GITHUB_OWNER = "FreeCAD"
GITHUB_REPO = "FreeCAD-Enhancement-Proposals"


def parse_fep_content(content: str) -> Optional[dict]:
    title_match = re.search(r"^# (FEP-(\d+)[: ].+)$", content, re.MULTILINE)
    if not title_match:
        return None

    raw_title = title_match.group(1)
    number = int(title_match.group(2))
    # Normalize separators: "FEP-0001 Title", "FEP-0001 — Title" → "FEP-0001: Title"
    title = re.sub(r"^(FEP-\d+)[: ]+(?:—\s*)?", r"\1: ", raw_title)

    status_match = re.search(r"^\| Status\s+\| (.+?) \|", content, re.MULTILINE)
    if not status_match:
        return None
    status = status_match.group(1).strip()

    desc_match = re.search(r"^\| Description\s+\| (.+?) \|", content, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        # Find first paragraph after the metadata table (series of | lines followed by blank line)
        after_table = re.search(r"(?:\|[^\n]+\n)+\n(.+?)(?:\n\n|$)", content, re.DOTALL)
        description = ""
        if after_table:
            para = after_table.group(1).strip()
            # Collapse soft-wrapped lines (single newline → space)
            para = re.sub(r"(?<!\n)\n(?!\n)", " ", para)
            # Strip bold markers
            para = re.sub(r"\*\*(.+?)\*\*", r"\1", para)
            # Take first sentence
            sentence = re.search(r"^(.+?[.!?])(?:\s|$)", para)
            if sentence:
                description = sentence.group(1).strip()
            else:
                description = para[:120].strip()

    return {
        "number": number,
        "title": title,
        "status": status,
        "description": description,
    }


def parse_existing_pr_entries(content: str, exclude_numbers: set[int]) -> list[dict]:
    """Read non-local FEP entries from the current README to use as fallback."""
    feps = []
    current_status: Optional[str] = None
    in_feps = False

    for line in content.splitlines():
        if line == "## FEPs":
            in_feps = True
            continue
        if not in_feps:
            continue
        if line.startswith("## "):
            break  # left the FEPs section

        if line.startswith("### "):
            section_name = line[4:].strip()
            current_status = next(
                (statuses[0] for sec, statuses in SECTIONS if sec == section_name),
                None,
            )
            continue

        # Match PR-based entries (external https://github.com/ links only)
        m = re.match(r"^ - \[(.+?)\]\((https://github\.com/[^)]+)\)(?:\s+-\s+(.+))?$", line)
        if m and current_status:
            title = m.group(1)
            link = m.group(2)
            num_m = re.match(r"FEP-(\d+):", title)
            if num_m:
                number = int(num_m.group(1))
                if number not in exclude_numbers:
                    feps.append({
                        "number": number,
                        "pr_number": 0,
                        "title": title,
                        "status": current_status,
                        "description": "",
                        "link": link,
                        "is_local": False,
                    })

    return feps


# ---------------------------------------------------------------------------
# Local FEPs
# ---------------------------------------------------------------------------

def get_local_feps() -> list[dict]:
    feps = []
    for fep_dir in sorted(FEPS_DIR.iterdir()):
        if not fep_dir.is_dir():
            continue
        if not re.match(r"FEP-\d+-", fep_dir.name):
            continue
        if fep_dir.name == "FEP-0000-template":
            continue

        readme = fep_dir / "README.md"
        if not readme.exists():
            continue

        parsed = parse_fep_content(readme.read_text(encoding="utf-8"))
        if not parsed:
            print(f"Warning: could not parse {fep_dir.name}/README.md", file=sys.stderr)
            continue

        parsed["link"] = f"./FEPs/{fep_dir.name}/README.md"
        parsed["is_local"] = True
        feps.append(parsed)

    return feps



def _github_request(url: str, token: Optional[str]) -> Optional[tuple[object, str]]:
    """Make a single GitHub API request. Returns (parsed_json, link_header) or None on error."""
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            link_header = resp.headers.get("Link", "")
            return data, link_header
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return None


def github_get_paged(url: str, token: Optional[str]) -> Optional[list]:
    """Fetch all pages of a list endpoint.

    Returns None if the first request fails (caller should treat as unavailable),
    or a list (possibly empty) on success.
    """
    result = _github_request(url, token)
    if result is None:
        return None  # first request failed — signal unavailability
    data, link_header = result
    if not isinstance(data, list):
        return None

    results = list(data)
    next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
    while next_match:
        r = _github_request(next_match.group(1), token)
        if r is None:
            break
        page_data, link_header = r
        if not isinstance(page_data, list):
            break
        results.extend(page_data)
        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)

    return results


def fetch_raw(url: str) -> Optional[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "fep-update-readme/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------------------
# PR FEPs
# ---------------------------------------------------------------------------

def _normalize_pr_title(pr_title: str, fep_number: int) -> str:
    m = re.match(r"(FEP-\d+[: ].+)", pr_title.strip())
    if m:
        return re.sub(r"^(FEP-\d+)[: ]+(?:—\s*)?", r"\1: ", m.group(1))
    return f"FEP-{fep_number:04d}: {pr_title.strip()}"


def get_pr_feps(
    owner: str, repo: str, local_numbers: set[int], token: Optional[str]
) -> Optional[list[dict]]:
    """Fetch FEPs from open PRs. Returns None if the GitHub API is unavailable."""
    prs = github_get_paged(
        f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open&per_page=100",
        token,
    )
    if prs is None:
        return None  # API unavailable

    feps = []
    for pr in prs:
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        labels = [lbl["name"] for lbl in pr.get("labels", [])]
        label_status = next(
            (lbl[len(STAGE_LABEL_PREFIX):] for lbl in labels if lbl.startswith(STAGE_LABEL_PREFIX)),
            None,
        )
        head = pr.get("head", {})
        head_repo = (head.get("repo") or {}).get("full_name", "")
        head_ref = head.get("ref", "")

        files_data = github_get_paged(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files?per_page=100",
            token,
        )
        if files_data is None:
            continue

        fep_file = next(
            (
                f["filename"]
                for f in files_data
                if re.match(r"FEPs/FEP-\d+-[^/]+/README\.md", f.get("filename", ""))
            ),
            None,
        )
        if not fep_file:
            continue

        dir_match = re.match(r"FEPs/(FEP-(\d+)-[^/]+)/README\.md", fep_file)
        if not dir_match:
            continue

        fep_number = int(dir_match.group(2))
        if fep_number in local_numbers:
            continue

        link = f"https://github.com/{head_repo}/blob/{head_ref}/{fep_file}"

        # Always use the PR title — it distinguishes alternatives for the same FEP number.
        title = _normalize_pr_title(pr_title, fep_number)

        raw_url = f"https://raw.githubusercontent.com/{head_repo}/{head_ref}/{fep_file}"
        raw_content = fetch_raw(raw_url)
        parsed = parse_fep_content(raw_content) if raw_content else None
        status = label_status or (parsed["status"] if parsed else "Draft")

        feps.append({
            "number": fep_number,
            "pr_number": pr_number,
            "title": title,
            "status": status,
            "description": "",
            "link": link,
            "is_local": False,
        })

    return feps


# ---------------------------------------------------------------------------
# README generation
# ---------------------------------------------------------------------------

def build_feps_section(all_feps: list[dict]) -> str:
    known_statuses = {s for statuses in [v for _, v in SECTIONS] for s in statuses}

    by_section: dict[str, list[dict]] = {section: [] for section, _ in SECTIONS}
    for fep in all_feps:
        status = fep["status"]
        if status not in known_statuses:
            print(f"Warning: FEP-{fep['number']:04d} has unknown status '{status}', skipping", file=sys.stderr)
            continue
        section = STATUS_TO_SECTION[status]
        by_section[section].append(fep)

    for feps in by_section.values():
        feps.sort(key=lambda f: (f["number"], f.get("pr_number", 0)))

    lines = []
    for section, _ in SECTIONS:
        lines.append(f"### {section}")
        for fep in by_section[section]:
            entry = f" - [{fep['title']}]({fep['link']})"
            if fep.get("description"):
                entry += f" - {fep['description']}"
            lines.append(entry)

    return "\n".join(lines) + "\n"


def update_readme(all_feps: list[dict]) -> bool:
    content = README_PATH.read_text(encoding="utf-8")

    marker = "\n## FEPs\n"
    idx = content.find(marker)
    if idx == -1:
        print("Error: could not find '## FEPs' section in README.md", file=sys.stderr)
        sys.exit(2)

    prefix = content[: idx + len(marker)]
    new_section = build_feps_section(all_feps)
    new_content = prefix + new_section

    if new_content == content:
        return False

    README_PATH.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-pr-check",
        action="store_true",
        help="Skip GitHub API calls; preserve existing PR entries from README.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        metavar="TOKEN",
        help="GitHub personal access token (default: $GITHUB_TOKEN).",
    )
    args = parser.parse_args()

    no_pr_check = args.no_pr_check
    token = args.token

    local_feps = get_local_feps()
    local_numbers = {f["number"] for f in local_feps}

    pr_feps: list[dict]
    if no_pr_check:
        # Preserve existing PR entries from README — no API calls made.
        existing = README_PATH.read_text(encoding="utf-8")
        pr_feps = parse_existing_pr_entries(existing, local_numbers)
    else:
        result = get_pr_feps(GITHUB_OWNER, GITHUB_REPO, local_numbers, token)
        if result is None:
            print(
                "Warning: GitHub API unavailable (rate limit or network error), "
                "keeping existing PR entries from README.",
                file=sys.stderr,
            )
            existing = README_PATH.read_text(encoding="utf-8")
            pr_feps = parse_existing_pr_entries(existing, local_numbers)
        else:
            pr_feps = result

    all_feps = local_feps + pr_feps

    changed = update_readme(all_feps)
    if changed:
        print("README.md updated with current FEP listing.")
        sys.exit(1)
    else:
        print("README.md is already up to date.")


if __name__ == "__main__":
    main()
