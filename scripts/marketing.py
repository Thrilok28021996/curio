#!/usr/bin/env python3
"""Curio — Marketing Automation.

Generates social media posts from git history, tracks metrics,
and schedules content.

Usage:
    python marketing.py generate    # Generate posts from recent commits
    python marketing.py metrics     # Fetch GitHub metrics
    python marketing.py schedule    # Show content calendar
    python marketing.py summary     # Full marketing summary
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# Git history → social media posts
# ============================================================

def get_recent_commits(days: int = 7) -> list[dict]:
    """Get recent commits from git log."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--pretty=format:%H|%s|%ad",
         "--date=short"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0][:8],
                    "message": parts[1],
                    "date": parts[2],
                })
    return commits


def generate_twitter_thread(commits: list[dict]) -> str:
    """Generate a Twitter thread from recent commits."""
    if not commits:
        return "No recent commits to post about."

    lines = []
    lines.append("🧵 Curio update — here's what's new:\n")

    # Group commits by type
    features = [c for c in commits if c["message"].startswith("feat:")]
    fixes = [c for c in commits if c["message"].startswith("fix:")]
    docs = [c for c in commits if c["message"].startswith("docs:")]
    tests = [c for c in commits if c["message"].startswith("test:")]

    if features:
        lines.append(f"✨ {len(features)} new features:")
        for c in features[:5]:
            msg = c["message"].replace("feat: ", "")
            lines.append(f"  • {msg}")
        lines.append("")

    if fixes:
        lines.append(f"🔧 {len(fixes)} fixes:")
        for c in fixes[:3]:
            msg = c["message"].replace("fix: ", "")
            lines.append(f"  • {msg}")
        lines.append("")

    if docs:
        lines.append(f"📚 {len(docs)} doc updates")
        lines.append("")

    lines.append("All open source. All free. All local-first.")
    lines.append("")
    lines.append("GitHub: https://github.com/Thrilok28021996/curio")
    lines.append("")
    lines.append("#AI #OpenSource #LearningAI #MCP")

    return "\n".join(lines)


def generate_hacker_news_post(commits: list[dict]) -> str:
    """Generate a Show HN post from recent commits."""
    features = [c for c in commits if c["message"].startswith("feat:")]

    post = f"""Show HN: Curio – AI that learns like a child (open source update)

Curio is an autonomous learning AI agent that detects knowledge gaps, seeks information to fill them, stores what matters, and forgets what doesn't.

Latest updates ({len(features)} new features this week):

"""
    for c in features[:5]:
        msg = c["message"].replace("feat: ", "")
        post += f"- {msg}\n"

    post += """
What makes it different:
- Detects what it doesn't know (gap detection)
- Decides what's worth learning (relevance scoring)
- Searches the web automatically (DuckDuckGo, no API keys)
- Stores concise lessons, not raw data (confidence scoring)
- Forgets stale knowledge (principled forgetting)
- Full audit trail (every decision logged)

Works with Claude Code, Cursor, and LM Studio (fully local, no API keys).

GitHub: https://github.com/Thrilok28021996/curio
"""
    return post


def generate_blog_snippet(commits: list[dict]) -> str:
    """Generate a blog post snippet from recent commits."""
    features = [c for c in commits if c["message"].startswith("feat:")]

    snippet = f"## What's New\n\n"
    snippet += f"**{len(features)} new features** this week:\n\n"

    for c in features:
        msg = c["message"].replace("feat: ", "")
        snippet += f"- **{msg}**\n"

    snippet += "\nTry it: `pip install curio-ai`\n"
    return snippet


# ============================================================
# GitHub metrics
# ============================================================

def fetch_github_metrics() -> dict:
    """Fetch GitHub metrics for the repo."""
    repo = "Thrilok28021996/curio"

    try:
        # Stars
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"],
            capture_output=True, text=True
        )
        stars = int(result.stdout.strip()) if result.stdout.strip() else 0

        # Forks
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".forks_count"],
            capture_output=True, text=True
        )
        forks = int(result.stdout.strip()) if result.stdout.strip() else 0

        # Open issues
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".open_issues_count"],
            capture_output=True, text=True
        )
        issues = int(result.stdout.strip()) if result.stdout.strip() else 0

        # Watchers
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".subscribers_count"],
            capture_output=True, text=True
        )
        watchers = int(result.stdout.strip()) if result.stdout.strip() else 0

        return {
            "stars": stars,
            "forks": forks,
            "issues": issues,
            "watchers": watchers,
            "url": f"https://github.com/{repo}",
        }
    except Exception as e:
        return {"error": str(e)}


def generate_metrics_report(metrics: dict) -> str:
    """Generate a metrics report."""
    if "error" in metrics:
        return f"Error fetching metrics: {metrics['error']}"

    report = f"""# Curio — Metrics Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## GitHub Stats
| Metric | Value |
|---|---|
| ⭐ Stars | {metrics['stars']} |
| 🍴 Forks | {metrics['forks']} |
| 🐛 Open Issues | {metrics['issues']} |
| 👁️ Watchers | {metrics['watchers']} |

## Targets (30 days)
| Metric | Target | Status |
|---|---|---|
| Stars | 100 | {'✅' if metrics['stars'] >= 100 else '🔄'} {metrics['stars']}/100 |
| Forks | 20 | {'✅' if metrics['forks'] >= 20 else '🔄'} {metrics['forks']}/20 |
| Issues | 5+ | {'✅' if metrics['issues'] >= 5 else '🔄'} {metrics['issues']}/5 |

## Links
- Repo: {metrics['url']}
- Issues: {metrics['url']}/issues
- PyPI: https://pypi.org/project/curio-ai/
"""
    return report


# ============================================================
# Content calendar
# ============================================================

def generate_content_calendar() -> str:
    """Generate a 4-week content calendar."""
    today = datetime.now()

    calendar = f"""# Curio — Content Calendar
Week of {today.strftime("%Y-%m-%d")}

## Week 1: Launch
| Day | Platform | Content |
|---|---|---|
| Mon | GitHub | Push README, LICENSE, quickstart |
| Tue | Hacker News | Show HN post |
| Tue | Twitter | Launch thread (10 tweets) |
| Wed | Reddit | r/programming post |
| Thu | Dev.to | Blog post: "How I built an AI that learns like a child" |
| Fri | Discord | Share in Claude Code, Cursor, LocalLLaMA communities |

## Week 2: Follow-up
| Day | Platform | Content |
|---|---|---|
| Mon | Twitter | Response thread to HN feedback |
| Wed | Reddit | r/LocalLLaMA post |
| Thu | YouTube | Demo video (3-5 min) |
| Fri | Twitter | Weekly update thread |

## Week 3: Community
| Day | Platform | Content |
|---|---|---|
| Mon | GitHub | Close issues, merge PRs |
| Wed | Twitter | "What we learned" thread |
| Thu | Dev.to | Blog post: "The architecture behind Curio" |
| Fri | Discord | Community highlights |

## Week 4: Growth
| Day | Platform | Content |
|---|---|---|
| Mon | Twitter | User spotlight / testimonial |
| Wed | Reddit | "30 days of Curio" update |
| Thu | Product Hunt | Launch (if ready) |
| Fri | Twitter | Month 1 summary + what's next |
"""
    return calendar


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python marketing.py [generate|metrics|schedule|summary]")
        sys.exit(1)

    command = sys.argv[1]
    output_dir = Path(__file__).parent.parent / "marketing-output"
    output_dir.mkdir(exist_ok=True)

    if command == "generate":
        commits = get_recent_commits(7)
        print(f"Found {len(commits)} commits in the last 7 days.\n")

        # Twitter thread
        thread = generate_twitter_thread(commits)
        (output_dir / "twitter-thread.txt").write_text(thread)
        print("=== Twitter Thread ===")
        print(thread)

        # Hacker News
        hn = generate_hacker_news_post(commits)
        (output_dir / "hacker-news.txt").write_text(hn)
        print("\n=== Hacker News Post ===")
        print(hn[:500] + "...")

        # Blog snippet
        blog = generate_blog_snippet(commits)
        (output_dir / "blog-snippet.md").write_text(blog)
        print(f"\n✅ Generated 3 files in {output_dir}/")

    elif command == "metrics":
        metrics = fetch_github_metrics()
        report = generate_metrics_report(metrics)
        (output_dir / "metrics-report.md").write_text(report)
        print(report)

    elif command == "schedule":
        calendar = generate_content_calendar()
        (output_dir / "content-calendar.md").write_text(calendar)
        print(calendar)

    elif command == "summary":
        commits = get_recent_commits(7)
        metrics = fetch_github_metrics()

        summary = f"""# Curio — Marketing Summary
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Recent Activity
- {len(commits)} commits in last 7 days
- Top commits:"""
        for c in commits[:5]:
            summary += f"\n  - {c['message']}"

        summary += f"\n\n## GitHub Metrics"
        if "error" not in metrics:
            summary += f"""
- Stars: {metrics['stars']}
- Forks: {metrics['forks']}
- Issues: {metrics['issues']}
- Watchers: {metrics['watchers']}"""

        summary += "\n\n## Next Actions"
        summary += "\n1. Push to GitHub"
        summary += "\n2. Post Show HN"
        summary += "\n3. Post Twitter thread"
        summary += "\n4. Post Reddit"
        summary += "\n5. Publish blog post"

        (output_dir / "marketing-summary.md").write_text(summary)
        print(summary)

    else:
        print(f"Unknown command: {command}")
        print("Usage: python marketing.py [generate|metrics|schedule|summary]")
        sys.exit(1)


if __name__ == "__main__":
    main()
