#!/usr/bin/env python3
"""
repo-health-cli
A zero-dependency GitHub repository health analyzer.
"""

import argparse
import json
import math
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request


API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 15

CHECKS = (
    ("README.md", "README.md", 20, "file"),
    ("LICENSE", "LICENSE", 20, "file"),
    ("CONTRIBUTING.md", "CONTRIBUTING.md", 15, "file"),
    ("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.md", 15, "file"),
    (".gitignore", ".gitignore", 10, "file"),
    (
        "ISSUE_TEMPLATE",
        ".github/ISSUE_TEMPLATE",
        10,
        "directory",
    ),
    (
        "GitHub Actions",
        ".github/workflows",
        10,
        "directory",
    ),
)

OWNER_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
)

REPO_PATTERN = re.compile(
    r"^[A-Za-z0-9._-]{1,100}$"
)


class HealthCheckError(Exception):
    """Expected application-level error."""


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def use_color():
    """Determine whether terminal colors are supported."""

    return (
        sys.stdout.isatty()
        and "NO_COLOR" not in os.environ
    )


def paint(value, color):
    """Apply terminal color when supported."""

    if use_color():
        return f"{color}{value}{Colors.RESET}"

    return str(value)


def validate_repo(repo):
    """Validate and split a GitHub owner/repository identifier."""

    if not isinstance(repo, str) or repo.count("/") != 1:
        raise HealthCheckError(
            "Invalid repository name. Use owner/name."
        )

    owner, name = repo.split("/")

    if not OWNER_PATTERN.fullmatch(owner):
        raise HealthCheckError("Invalid GitHub owner name.")

    if (
        not REPO_PATTERN.fullmatch(name)
        or name in (".", "..")
        or name.endswith(".git")
    ):
        raise HealthCheckError(
            "Invalid GitHub repository name."
        )

    return owner, name


def github_get(url, timeout):
    """Perform a GitHub REST API GET request."""

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "repo-health-cli/1.1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw_data = response.read()

            try:
                data = json.loads(
                    raw_data.decode("utf-8")
                )
            except (
                json.JSONDecodeError,
                UnicodeDecodeError,
            ):
                raise HealthCheckError(
                    "GitHub API returned invalid JSON."
                )

            if not isinstance(data, dict):
                raise HealthCheckError(
                    "Unexpected GitHub API response."
                )

            return data

    except urllib.error.HTTPError as error:

        if error.code == 404:
            raise HealthCheckError(
                "Repository not found or private. "
                "Only publicly accessible repositories "
                "are supported."
            )

        if error.code == 403:
            remaining = error.headers.get(
                "X-RateLimit-Remaining"
            )

            if remaining == "0":
                raise HealthCheckError(
                    "GitHub API rate limit exceeded. "
                    "Try again later."
                )

            raise HealthCheckError(
                "GitHub API rate limit exceeded or "
                "access forbidden."
            )

        if error.code == 401:
            raise HealthCheckError(
                "GitHub API authentication failed."
            )

        if error.code == 451:
            raise HealthCheckError(
                "Repository unavailable for legal reasons."
            )

        raise HealthCheckError(
            f"GitHub API error: HTTP {error.code}."
        )

    except urllib.error.URLError as error:

        if isinstance(
            error.reason,
            (TimeoutError, socket.timeout),
        ):
            raise HealthCheckError(
                f"GitHub API request timed out "
                f"after {timeout} seconds."
            )

        raise HealthCheckError(
            f"Network error: {error.reason}"
        )

    except (TimeoutError, socket.timeout):
        raise HealthCheckError(
            f"GitHub API request timed out "
            f"after {timeout} seconds."
        )

    except OSError as error:
        raise HealthCheckError(
            f"Network or system error: {error}"
        )


def fetch_repository_tree(owner, name, timeout):
    """Fetch repository metadata and recursive file tree."""

    owner = urllib.parse.quote(owner, safe="")
    name = urllib.parse.quote(name, safe="")

    repository_url = (
        f"{API_BASE}/repos/{owner}/{name}"
    )

    metadata = github_get(
        repository_url,
        timeout,
    )

    branch = metadata.get("default_branch")

    if not isinstance(branch, str) or not branch:
        raise HealthCheckError(
            "Repository default branch could not be identified."
        )

    encoded_branch = urllib.parse.quote(
        branch,
        safe="",
    )

    tree_url = (
        f"{API_BASE}/repos/{owner}/{name}"
        f"/git/trees/{encoded_branch}?recursive=1"
    )

    tree_data = github_get(
        tree_url,
        timeout,
    )

    if tree_data.get("truncated"):
        raise HealthCheckError(
            "GitHub returned a truncated file tree. "
            "A complete assessment cannot be guaranteed."
        )

    tree = tree_data.get("tree")

    if not isinstance(tree, list):
        raise HealthCheckError(
            "GitHub API returned an invalid repository tree."
        )

    return metadata, tree


def check_repository(tree):
    """Evaluate required files and calculate the health score."""

    available = {
        item["path"]: item.get("type")
        for item in tree
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
    }

    results = []
    score = 0

    for label, path, points, kind in CHECKS:

        if kind == "file":
            exists = available.get(path) == "blob"

        else:
            exists = (
                available.get(path) == "tree"
                or any(
                    item.startswith(path + "/")
                    for item in available
                )
            )

        if exists:
            score += points

        results.append({
            "name": label,
            "path": path,
            "points": points,
            "exists": exists,
        })

    return score, results


def progress_bar(score, width=30):
    """Build a percentage-based progress bar."""

    filled = round(score * width / 100)
    empty = width - filled

    bar = "[" + "#" * filled + "-" * empty + "]"

    if score >= 80:
        return paint(bar, Colors.GREEN)

    if score >= 50:
        return paint(bar, Colors.YELLOW)

    return paint(bar, Colors.RED)


def get_status(score):
    """Return the health status and associated terminal color."""

    if score >= 80:
        return "Excellent", Colors.GREEN

    if score >= 50:
        return "Needs Improvement", Colors.YELLOW

    return "Poor", Colors.RED


def build_report(repo, metadata, score, results):
    """Build a machine-readable report."""

    missing = [
        item["path"]
        for item in results
        if not item["exists"]
    ]

    return {
        "repository": repo,
        "name": metadata.get("full_name", repo),
        "default_branch": metadata.get("default_branch"),
        "health_score": score,
        "maximum_score": 100,
        "status": get_status(score)[0],
        "checks_passed": len(results) - len(missing),
        "checks_total": len(results),
        "missing": missing,
        "checks": results,
    }


def display_report(report):
    """Print the human-readable terminal report."""

    score = report["health_score"]
    status, status_color = get_status(score)

    print()
    print(paint("=" * 58, Colors.CYAN))
    print(
        paint(
            "             REPOSITORY HEALTH REPORT",
            Colors.BOLD,
        )
    )
    print(paint("=" * 58, Colors.CYAN))

    print(f"\n Repository : {report['repository']}")
    print(f" Name       : {report['name']}")
    print(f" Branch     : {report['default_branch']}")

    print("\n" + "-" * 58)
    print(paint(" HEALTH SCORE", Colors.BOLD))
    print()

    print(
        f" {paint(str(score) + '/100', status_color)}"
        f"  {paint(status, status_color)}"
    )

    print(f" {progress_bar(score)}")
    print()

    print(paint(" REQUIREMENTS CHECKLIST", Colors.BOLD))
    print("-" * 58)

    for item in report["checks"]:

        if item["exists"]:
            symbol = paint("[PASS]", Colors.GREEN)
            state = "Present"
        else:
            symbol = paint("[MISS]", Colors.RED)
            state = "Missing"

        print(
            f" {symbol} {item['name']:<19}"
            f" {state:<10} {item['points']:>2} pts"
        )

    print("-" * 58)

    print(f"\n Passed : {report['checks_passed']}")
    print(f" Failed : {len(report['missing'])}")
    print(f" Total  : {report['checks_total']}")

    if report["missing"]:
        print(paint("\n RECOMMENDED ACTIONS", Colors.BOLD))

        for path in report["missing"]:
            print(f"  - Add {path}")

    else:
        print(
            paint(
                "\n All checks passed!",
                Colors.GREEN,
            )
        )

    print("\n" + paint("=" * 58, Colors.CYAN))
    print()


def main():
    """Run the command-line application."""

    parser = argparse.ArgumentParser(
        prog="repo-health-cli",
        description=(
            "Evaluate public GitHub repositories "
            "against open-source best practices."
        ),
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in owner/name format.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=(
            "API request timeout in seconds "
            f"(default: {DEFAULT_TIMEOUT})."
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the report in JSON format.",
    )

    args = parser.parse_args()

    if (
        not math.isfinite(args.timeout)
        or args.timeout <= 0
    ):
        parser.error(
            "--timeout must be a finite number greater than zero."
        )

    try:
        owner, name = validate_repo(args.repo)

        if not args.json:
            print(
                paint(
                    f"\nAnalyzing {owner}/{name}...",
                    Colors.CYAN,
                )
            )

        metadata, tree = fetch_repository_tree(
            owner,
            name,
            args.timeout,
        )

        score, results = check_repository(tree)

        report = build_report(
            args.repo,
            metadata,
            score,
            results,
        )

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            display_report(report)

        return 0

    except HealthCheckError as error:

        if args.json:
            print(
                json.dumps({"error": str(error)}),
                file=sys.stderr,
            )
        else:
            print(
                paint(
                    f"\nError: {error}",
                    Colors.RED,
                ),
                file=sys.stderr,
            )

        return 1

    except KeyboardInterrupt:
        print(
            "\nOperation cancelled.",
            file=sys.stderr,
        )
        return 130


if __name__ == "__main__":
    sys.exit(main())