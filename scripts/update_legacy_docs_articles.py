#!/usr/bin/env python3
"""Update 9 legacy GitHub Pages articles with SpeedCE eight-tool content."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIR = ROOT / "docs" / "articles"

LEGACY_SLUGS = [
    "hexo-hugo-static-site",
    "java-spring-boot-api",
    "laravel-php-deploy",
    "miniprogram-backend-api",
    "nextjs-nuxt-ssr-deploy",
    "postmortem-blameless",
    "python-django-flask",
    "typecho-emlog-blog",
    "wordpress-troubleshooting",
]

OLD_TOOL_BLOCK = """### 1.4 六种检测工具怎么选

SpeedCE 顶部下拉菜单可选 **HTTP、HTTPS、PING、TCPing、DNS、路由追踪** 六种工具：

| 工具 | 测什么 | 典型场景 |
|------|--------|----------|
| **HTTP** | 检测 80 端口 HTTP 连通性 | 排查跳转、混合内容、仅开 80 的场景 |
| **HTTPS** | 检测 443 端口 TLS 与 HTTP 响应 | 建站验收首选，覆盖证书与 Web 层 |
| **PING** | ICMP 连通性与延迟 | 快速看 IP 通不通；云厂商禁 Ping 时改 HTTPS |
| **TCPing** | TCP 端口连通性（默认 443） | 禁 ICMP 时替代 Ping，验证端口是否监听 |
| **DNS** | 全国/全球多节点 DNS 解析 | 迁机、换 CDN、分线路解析后看各地解析是否一致 |
| **路由追踪** | 逐跳路由路径与延迟 | 定位跨省/跨网路由绕路、中间节点异常 |"""

NEW_TOOL_BLOCK = """### 1.4 八种检测工具怎么选

SpeedCE 顶部下拉菜单可选 **HTTP、HTTPS、PING、TCPing、DNS、路由追踪、IP Geo、WHOIS** 八种工具：

| 工具 | 测什么 | 典型场景 |
|------|--------|----------|
| **HTTP** | 检测 80 端口 HTTP 连通性 | 排查跳转、混合内容、仅开 80 的场景 |
| **HTTPS** | 检测 443 端口 TLS 与 HTTP 响应 | 建站验收首选，覆盖证书与 Web 层 |
| **PING** | ICMP 连通性与延迟 | 快速看 IP 通不通；云厂商禁 Ping 时改 HTTPS |
| **TCPing** | TCP 端口连通性（默认 443） | 禁 ICMP 时替代 Ping，验证端口是否监听 |
| **DNS** | 全国/全球多节点 DNS 解析 | 迁机、换 CDN、分线路解析后看各地解析是否一致 |
| **路由追踪** | 逐跳路由路径与延迟 | 定位跨省/跨网路由绕路、中间节点异常 |
| **IP Geo** | 查询 IP 地理位置与运营商归属 | 迁机验收核对 IP 区域；排查异常解析是否指向错误地区 |
| **WHOIS** | 查询域名/IP 注册信息与到期时间 | 域名即将到期、备案主体核对、异常 IP 溯源 |

**组合建议**：建站验收用 **HTTPS**；迁机/换 CDN 后用 **DNS**；核对 IP 区域用 **IP Geo**；查域名到期与注册主体用 **WHOIS**。"""

REPLACEMENTS = [
    (OLD_TOOL_BLOCK, NEW_TOOL_BLOCK),
    ("### 8.3 六种工具一页集成", "### 8.3 八种工具一页集成"),
    (
        "排障时思维不断裂。",
        "HTTP/HTTPS/PING/TCPing/DNS/路由追踪/IP Geo/WHOIS 下拉切换，排障思维不断裂。",
    ),
    (
        "| 网络层 | IP/端口/证书通不通 | SpeedCE HTTPS / PING / TCPing |",
        "| 网络层 | IP/端口/证书通不通 | SpeedCE HTTPS / PING / TCPing |\n"
        "| 资产层 | IP 归属与注册信息 | SpeedCE IP Geo / WHOIS |",
    ),
]


def main() -> None:
    updated = 0
    for slug in LEGACY_SLUGS:
        path = LEGACY_DIR / f"{slug}.md"
        if not path.exists():
            print(f"skip missing: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
            print(f"updated: {path.name}")
        else:
            print(f"unchanged: {path.name}")
    print(f"Done. Updated {updated} legacy articles.")


if __name__ == "__main__":
    main()
