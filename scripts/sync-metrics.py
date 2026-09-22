#!/usr/bin/env python3
import os
import re
import json
import time
from datetime import datetime, timezone
import urllib.request

REPO_OWNER = "deanybytes"
FLAGSHIP_REPO = "QuranicWords"
PROFILE_REPO = "deanybytes"

def get_headers():
    headers = {"User-Agent": "DeanyBytes-Sync-Bot"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def fetch_json(url):
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print(f"=== Starting Realtime Telemetry Sync for @{REPO_OWNER} ===")
    
    # 1. Fetch Flagship Repo Data
    qw_data = fetch_json(f"https://api.github.com/repos/{REPO_OWNER}/{FLAGSHIP_REPO}") or {}
    stars = qw_data.get("stargazers_count", 0)
    forks = qw_data.get("forks_count", 0)
    watchers = qw_data.get("watchers_count", 0)
    open_issues = qw_data.get("open_issues_count", 0)
    repo_size_kb = qw_data.get("size", 0)
    
    # 2. Fetch Profile Repo Data
    prof_data = fetch_json(f"https://api.github.com/repos/{REPO_OWNER}/{PROFILE_REPO}") or {}
    prof_stars = prof_data.get("stargazers_count", 0)
    
    # Format stats
    star_label = f"{stars} STAR{'S' if stars != 1 else ''}" if stars > 0 else "STARS TRACKED"
    fork_label = f"{forks} FORK{'S' if forks != 1 else ''}" if forks > 0 else "COMMUNITY OPEN"
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    epoch_v = int(time.time())

    print(f"Metrics: Stars={stars}, Forks={forks}, Watchers={watchers}, Size={repo_size_kb}KB, Time={now_utc}")

    # 3. Update assets/repo-stats.svg
    svg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "repo-stats.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            svg = f.read()

        # Update node status in header console
        svg = re.sub(
            r'<text x="875" y="24" text-anchor="end" class="mono" font-size="10\.5" fill="#6EE7B7" letter-spacing="1\.5">[^<]*</text>',
            f'<text x="875" y="24" text-anchor="end" class="mono" font-size="10.5" fill="#6EE7B7" letter-spacing="1.5">SYNC: {now_utc}</text>',
            svg
        )

        # Update Star Status
        svg = re.sub(
            r'(<text x="14" y="48" class="mono" font-size="10" fill="#A7F3D0">★ STAR STATUS:</text>\s*<text x="260" y="48" text-anchor="end" class="mono" font-size="10" fill="#00FF9D" font-weight="bold">)[^<]*(</text>)',
            rf'\g<1>{star_label}\g<2>',
            svg
        )

        # Update Forks & PRs
        svg = re.sub(
            r'(<text x="14" y="68" class="mono" font-size="10" fill="#A7F3D0">⑂ FORKS &amp; PRs:</text>\s*<text x="260" y="68" text-anchor="end" class="mono" font-size="10" fill="#34D399" font-weight="bold">)[^<]*(</text>)',
            rf'\g<1>{fork_label}\g<2>',
            svg
        )

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Updated {svg_path}")

    # 4. Update Cache-Busters in README.md
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme = f.read()

        # Replace existing ?v=\d+ with current epoch timestamp
        new_readme = re.sub(r'(\.svg)\?v=\d+', rf'\1?v={epoch_v}', readme)
        new_readme = re.sub(r'(\.png)\?v=\d+', rf'\1?v={epoch_v}', new_readme)

        if new_readme != readme:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_readme)
            print(f"Updated cache busters in {readme_path} to ?v={epoch_v}")
        else:
            print("README.md cache busters are already up to date")

    print("=== Realtime Telemetry Sync Finished Successfully ===")

if __name__ == "__main__":
    main()
