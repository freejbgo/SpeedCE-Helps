#!/usr/bin/env python3
"""Generate 500 English SEO articles (SpeedCE-Docs style) from articles/index.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from speedce_articles_common_en import write_articles, write_readme

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "articles" / "index.json"

CN_TO_EN_CATEGORY = {
    "故障排查": "Troubleshooting",
    "VPS线路": "VPS & Lines",
    "CDN": "CDN",
    "出海": "Global Expansion",
    "开发": "Development",
    "运维": "DevOps",
    "数据库": "Database",
    "安全": "Security",
    "云原生": "Cloud Native",
    "网络": "Networking",
    "行业": "Industry",
    "方法论": "Methodology",
    "对比": "Comparisons",
    "进阶": "Advanced",
}

CATEGORY_SUBTITLE = {
    "Troubleshooting": "Symptoms, Scope, and Fixes with Multi-Node Testing",
    "VPS & Lines": "Line Verification and Pre-Purchase Acceptance",
    "CDN": "Edge Configuration and Origin Comparison",
    "Global Expansion": "Dual China + Global Reachability Checks",
    "Development": "From Local Dev to Production Reachability",
    "DevOps": "Deploy Gates and Incident Triage",
    "Database": "When the Network Is Green but Pages Stall",
    "Security": "Connectivity vs Policy Blocks",
    "Cloud Native": "Ingress, Mesh, and Public Probing",
    "Networking": "Protocols, Routes, and Carrier Variance",
    "Industry": "Vertical Acceptance Standards",
    "Methodology": "Repeatable Speed-Test Workflows",
    "Comparisons": "Choosing the Right Diagnostic Signal",
    "Advanced": "Peak Traffic and High-Stakes Changes",
}

# Latin tokens often present in Chinese titles
LATIN_IN_TITLE = re.compile(
    r"[A-Za-z][A-Za-z0-9+./_-]*(?:\s+[A-Za-z0-9+./_-]+)*"
)

SLUG_STOP = {
    "guide", "topic", "more", "fix", "dev", "ops", "db", "sec", "net", "adv",
    "method", "industry", "cloud", "vps", "region", "vendor", "vertical",
    "framework", "tool", "cmd", "lib", "dc", "global",
}


def slug_ascii_words(slug: str) -> str:
    ascii_part = re.sub(r"[^\x00-\x7F]+", " ", slug)
    words = [w for w in re.split(r"[-_\s]+", ascii_part) if w and w.lower() not in SLUG_STOP]
    if not words:
        return ""
    titled = []
    acronyms = {"dns", "ssl", "tls", "cdn", "vps", "api", "http", "https", "ping", "ipv6", "ipv4", "waf", "k8s", "oauth", "jwt", "rbac", "csp", "wss", "tcp", "udp", "bgp", "gia", "cn2", "ip", "sql", "orm", "ci", "cd", "gpu", "aws", "gcp", "saas", "seo", "icp", "mtls", "ecmp", "vlan", "vxlan", "ospf", "nat", "rds", "ec2", "s3", "vm", "php", "oom", "jvm", "gc"}
    for w in words:
        if w.lower() in acronyms:
            titled.append(w.upper())
        elif w.isupper() and len(w) <= 5:
            titled.append(w)
        else:
            titled.append(w.capitalize())
    return " ".join(titled)


def title_from_latin(title_zh: str) -> str:
    matches = LATIN_IN_TITLE.findall(title_zh)
    if matches:
        return max(matches, key=len).strip()
    return ""


def build_en_title(slug: str, title_zh: str, en_category: str) -> str:
    subject = slug_ascii_words(slug) or title_from_latin(title_zh)
    if not subject:
        subject = en_category
    subtitle = CATEGORY_SUBTITLE.get(en_category, "Practical Guide with SpeedCE")
    if subject.lower() in subtitle.lower():
        return f"{subject}: {en_category} Playbook"
    return f"{subject}: {subtitle}"


def build_keywords(slug: str, en_category: str) -> str:
    words = [w for w in re.split(r"[-_]+", slug) if w and w.isascii() and w.lower() not in SLUG_STOP]
    base = ",".join(words[:6]) if words else en_category.lower().replace(" & ", ",")
    return f"{base},speed test,SpeedCE,multi-node"


def pick_variant(slug: str, n: int) -> int:
    return sum(ord(c) for c in slug) % n


BODY_OPENERS = [
    "A single local `ping` or browser refresh cannot represent users spread across provinces and carriers. **Regional failures** often hide behind a green laptop screen.",
    "Production changes look safe in staging until real users hit different DNS caches, carrier routes, or edge nodes. That gap is exactly what multi-node probing closes.",
    "When stakeholders ask \"is the site up?\", the honest answer is \"for whom, on which network, and over which protocol?\" Map-based testing makes that answer visible.",
    "Intermittent tickets are the hardest: your test passes, their province fails. Distributed probes turn anecdotal complaints into a geographic pattern.",
]

BODY_MIDDLES = [
    """## Why one probe is not enough

Your city, ISP, and time of day are only one path through the internet. China Telecom, China Unicom, and China Mobile may route the same hostname differently. A VPS labeled \"BGP\" can still be slow or unreachable for mobile users.

**SpeedCE** runs HTTP, HTTPS, PING, TCPing, DNS, and Traceroute from many Chinese provinces plus global locations. Pick a tool from the dropdown, then read results as red/green distributions on a **China node map** and a **global node map**—not a single average latency line. Filter by carrier to see whether failure is nationwide, provincial, or ISP-specific.""",
    """## Read the map before opening logs

Start with scope: all red (likely DNS, firewall, or origin down), single-carrier red (routing or line issue), single-province red (regional DNS or CDN edge), or sporadic red (WAF, rate limits, or flaky upstream). HTTP green with HTTPS red often means certificate or TLS termination problems.

Archive screenshots with timestamps. They become evidence for vendors, auditors, and post-incident reviews.""",
    """## A practical acceptance loop

1. Open {zh_url} and pick the tool that matches your question (usually **HTTPS** for websites, **DNS** after record changes, **Traceroute** for routing issues).
2. Test the exact hostname users hit—`www`, `api`, callbacks, and CDN CNAMEs are separate targets.
3. Switch China vs global nodes depending on audience.
4. Filter Telecom / Unicom / Mobile separately on the China map.
5. Fix the narrowest layer indicated by the map, then retest until failures shrink to zero.""",
]

BODY_CLOSERS = [
    "Pair this checklist with your change-management process: baseline before edits, probe after edits, and keep SpeedCE screenshots in the ticket.",
    "If the map is green but users still fail, move to application layers—CORS, auth callbacks, WebSocket handshakes, or database timeouts. Network-first triage saves hours.",
    "For vendor disputes (hosting, CDN, ISP), a dated multi-node screenshot is more persuasive than a single ping from your office.",
]

TOPIC_HINTS: list[tuple[str, str]] = [
    (r"dns", "Focus on TTL, recursive vs authoritative DNS, and GeoDNS. Use SpeedCE's **DNS tool** to compare resolver results across provinces."),
    (r"ssl|https|cert|tls|lets-encrypt", "Check certificate chain completeness, SNI on shared IPs, and expiry on every subdomain—not only the homepage."),
    (r"nginx|apache|caddy|traefik", "Validate `server_name`, upstream health, and whether HTTP redirects loop before blaming the CDN."),
    (r"migrat|cdn", "Probe origin hostname and CDN hostname on the same map. Divergence tells you whether the edge or origin is wrong."),
    (r"vps|line|bgp|cn2|gia", "Run China carrier filters on the advertised IP before payment. Marketing labels are not measurements."),
    (r"k8s|docker|ingress|container", "In-cluster health does not prove public ingress. Test the public URL after every Service or Ingress edit."),
    (r"waf|firewall|security-group|443", "SSH access with a red HTTPS map usually means security groups or WAF rules—not application bugs."),
    (r"api|oauth|callback|payment", "Test callback and API hostnames independently. Main-site green plus API red is a common release mistake."),
    (r"database|mysql|redis|mongo", "When SpeedCE is all green, inspect pools, replication, and slow queries—network triage is already done."),
    (r"websocket|wss", "HTTPS reachability is necessary but not sufficient for WebSocket workloads—still eliminate network scope first."),
    (r"ipv6|aaaa", "Validate IPv4 and IPv6 separately; dual-stack misconfig produces \"works for me\" reports."),
    (r"mobile|unicom|telecom|carrier|三网", "Always filter carriers on the China map—mobile-only red is invisible to a desktop telecom test."),
    (r"global|overseas|出海", "Run global nodes for international users and China nodes for mainland users—audiences are not interchangeable."),
]


def topic_hint(slug: str, title_zh: str) -> str:
    blob = f"{slug} {title_zh}".lower()
    for pattern, hint in TOPIC_HINTS:
        if re.search(pattern, blob):
            return hint
    return "Treat the node map as a heat map of real users. Even a small red region is total outage for people living there."


def build_body(slug: str, title_zh: str, en_category: str) -> str:
    v = pick_variant(slug, len(BODY_OPENERS))
    opener = BODY_OPENERS[v]
    middle = "\n\n".join(BODY_MIDDLES)
    closer = BODY_CLOSERS[(v + 1) % len(BODY_CLOSERS)]
    hint = topic_hint(slug, title_zh)
    return f"""{opener}

{middle}

## Topic focus

{hint}

{closer}

**Recommended tool:** [SpeedCE free speed test]({{base_url}}) | Chinese UI: {{zh_url}}"""


def load_topics() -> list[dict]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def build_articles() -> list[dict]:
    topics = load_topics()
    articles: list[dict] = []
    for idx, topic in enumerate(topics, start=1):
        slug = topic["slug"]
        title_zh = topic["title"]
        cn_cat = topic["category"]
        en_cat = CN_TO_EN_CATEGORY.get(cn_cat, "Troubleshooting")
        articles.append(
            {
                "id": idx,
                "slug": slug,
                "title": build_en_title(slug, title_zh, en_cat),
                "keywords": build_keywords(slug, en_cat),
                "category": en_cat,
                "batch": 1,
                "body": build_body(slug, title_zh, en_cat),
            }
        )
    return articles


def main() -> None:
    articles = build_articles()
    write_articles(articles)
    write_readme(articles)
    print(f"Generated {len(articles)} English articles in docs/en/articles/")


if __name__ == "__main__":
    main()
