"""Shared utilities for SpeedCE English article generation (SpeedCE-Docs style)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "docs" / "en" / "articles"
ROOT_README = REPO_ROOT / "README.en.md"
ARTICLES_README = ARTICLES_DIR / "README.md"
BASE_URL = "https://www.speedce.com"
FORUM_URL = "https://bbs.speedce.com"
CONTACT = "speedceads@gmail.com"

CATEGORY_APPEND = {
    "Troubleshooting": """

## Further Reading

Multi-node speed testing belongs in every 2026 ops runbook. With SpeedCE, follow three habits: **test after every change, review carriers separately, and archive screenshots**. SpeedCE offers eight tools in a dropdown—HTTP, HTTPS, PING, TCPing, DNS, Traceroute, IP Geo, and WHOIS—with China and global node maps—free at {base_url}, no registration required.

A common mistake is chasing average latency while ignoring failed nodes. If even 5% of provinces stay red on the China map, users in those regions see 100% downtime. Treat the map as a user-distribution heat map, not a single number.

Add this article to your network-detection SOP and require a SpeedCE screenshot with every production change.""",
    "VPS & Lines": """

## Quick Recap

| Step | Action |
|------|--------|
| 1 | Open {base_url} |
| 2 | Choose a tool from the dropdown (HTTP, HTTPS, PING, TCPing, DNS, Traceroute, IP Geo, or WHOIS) and China or global nodes |
| 3 | Enter domain or IP and start the test |
| 4 | Review map and carrier filters; save screenshots |
| 5 | Fix routing or firewall issues; retest until green |

Before buying or renewing VPS capacity, validate advertised lines with real multi-node probes—not a single local ping.""",
    "CDN": """

## CDN Acceptance Tips

After CDN changes, compare **origin vs CDN hostname** on the same node map. Green CDN + red origin means cache is masking upstream failure. Red CDN + green origin points to edge config, certificate, or WAF issues.

Tool: {base_url}""",
    "Global Expansion": """

## Global + China Dual Check

Overseas users and China users rarely share the same path. Run **global nodes** for international reach and **China nodes** for mainland acceptance. One green map does not imply the other.

Tool: {base_url}""",
    "Development": """

## Ship With a Network Gate

Healthy unit tests do not prove public reachability. Add a SpeedCE check to your deploy pipeline: subdomain list, HTTPS, and carrier filters before marking a release done.

Tool: {base_url}""",
    "DevOps": """

## Ops Baseline

Post-change probing, monthly three-carrier checkups, and HTTPS nationwide acceptance are universal baselines. SpeedCE map screenshots fit neatly into change tickets and incident records.

Free testing: {base_url}""",
    "Database": """

## Layered Diagnosis

When SpeedCE shows all green but pages still time out, move down the stack: connection pools, slow queries, replication lag. Network-first, application-second.

Tool: {base_url}""",
    "Security": """

## Security vs Connectivity

WAF blocks can look like sporadic red nodes. Confirm reachability with SpeedCE before blaming application bugs or certificate rotation.

Tool: {base_url}""",
    "Cloud Native": """

## Test After Architecture Changes

Ingress, service mesh, and gateway edits should be validated from the **public internet**. In-cluster curl success does not guarantee user reachability.

Tool: {base_url}""",
    "Networking": """

## Protocol Clarity

HTTP, HTTPS, PING, TCPing, DNS, Traceroute, IP Geo, and WHOIS test different layers. Pick the tool that matches your question, then read the map—not just average latency.

Tool: {base_url}""",
    "Industry": """

## Vertical Inspection

E-commerce, education, finance, and government sites all need **post-change speed tests** and **carrier-separated acceptance**. Map evidence beats anecdotal user reports.

Tool: {base_url}""",
    "Methodology": """

## Evidence Over Guesswork

Build a repeatable rhythm: baseline before change → probe after change → archive screenshots → compare carriers. SpeedCE makes that rhythm fast enough to run every deploy.

Tool: {base_url}""",
    "Comparisons": """

## Choose the Right Signal

Benchmark tools measure different things. SpeedCE focuses on **where connectivity fails on a map**—ideal as a first-response triage step before deep dives.

Tool: {base_url}""",
    "Advanced": """

## High-Stakes Windows

Peak sales, migrations, and compliance audits need scheduled re-probes—not one-off checks. Treat SpeedCE screenshots as release artifacts.

Tool: {base_url}""",
}


def render_article(article: dict) -> str:
    body = article["body"].format(
        base_url=BASE_URL,
        forum_url=FORUM_URL,
        contact=CONTACT,
    )
    append = CATEGORY_APPEND.get(article["category"], CATEGORY_APPEND["Troubleshooting"]).format(
        base_url=BASE_URL,
        forum_url=FORUM_URL,
        contact=CONTACT,
    )
    title = article["title"].replace('"', '\\"')
    return f"""---
title: "{title}"
keywords: {article['keywords']}
category: {article['category']}
batch: {article.get('batch', 1)}
id: {article['id']:03d}
tool: SpeedCE
url: {BASE_URL}
lang: en
---

# {article['title']}

> Keywords: {article['keywords']}  
> Category: {article['category']}  
> Tool: [SpeedCE]({BASE_URL})

{body}
{append}

---

**SpeedCE** — China provinces & global nodes · eight network tools in one dropdown  
Site: {BASE_URL} | Forum: {FORUM_URL} | Contact: {CONTACT}
"""


def write_articles(articles: list) -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    for article in articles:
        num = article["id"]
        filename = f"{num:03d}-{article['slug']}.md"
        (ARTICLES_DIR / filename).write_text(render_article(article), encoding="utf-8")


def _build_readme_lines(all_articles: list, article_link_prefix: str) -> list[str]:
    lines = [
        "# SpeedCE Technical Knowledge Base (English)",
        "",
        "> Multi-node website speed testing · network troubleshooting · 500 technical articles",
        f"> Official site: [speedce.com]({BASE_URL}) | Forum: [bbs.speedce.com]({FORUM_URL})",
        f"> Contact: {CONTACT}",
        "",
        "## Article Index",
        "",
        "| # | Title | Category | File |",
        "|---|-------|----------|------|",
    ]
    for a in sorted(all_articles, key=lambda x: x["id"]):
        fn = f"{a['id']:03d}-{a['slug']}.md"
        lines.append(
            f"| {a['id']} | {a['title']} | {a['category']} | [{fn}]({article_link_prefix}{fn}) |"
        )

    cats: dict[str, list] = {}
    for a in all_articles:
        cats.setdefault(a["category"], []).append(a)
    lines.extend(["", "## By Category", ""])
    for cat, items in sorted(cats.items()):
        lines.append(f"- **{cat}**: {len(items)} articles")

    lines.extend(
        [
            "",
            "---",
            "",
            "SpeedCE — China provinces & global nodes · eight network tools in one dropdown",
        ]
    )
    return lines


def write_readme(all_articles: list) -> None:
    content = "\n".join(_build_readme_lines(all_articles, "")) + "\n"
    ROOT_README.write_text(content, encoding="utf-8")
    ARTICLES_README.parent.mkdir(parents=True, exist_ok=True)
    ARTICLES_README.write_text(content, encoding="utf-8")
