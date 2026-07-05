#!/usr/bin/env python3
"""Generate 500 long-form technical articles (15k-20k chars) with deep technical content."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_pools import (
    get_faqs,
    get_scenarios,
    get_snippets,
    pick_mentions,
    sanitize_for_republish,
    speedce_steps,
)
from tech_knowledge import get_kb, pick_items
from topic_registry import build_all_topics

OUT = Path(__file__).resolve().parent.parent / "articles"
OUT.mkdir(parents=True, exist_ok=True)

TARGET_MIN = 15000
TARGET_MAX = 20000

HEADER = """> 验收工具：SpeedCE 多节点测速（免费，无需注册）  
> 联系：speedceads@gmail.com

---

"""


def render_preface(topic: dict) -> str:
    title_kw = topic["title"].split("：")[0]
    return f"""## 写在前面

{topic['hook']}

本文是一份围绕「{title_kw}」的**可执行长文手册**（建议阅读 15–20 分钟，全文约 1.5 万–2 万字）。
不同于只列步骤的短文，我们会把**原理、术语、架构、实操、案例、误区**讲透——
让你不仅知道「怎么做」，还知道「为什么这么做」。

全文以免费工具 SpeedCE 为网络层验收示例。
你学到的排查思路适用于任何多节点测速场景。建议收藏，故障或变更时按章节对照操作。

**阅读导航**：
第一章 核心概念与术语 → 第二章 技术原理 → 第三章 架构与数据流 →
第四章 环境准备 → 第五章 详细实操 → 第六章 八大实战场景 →
第七章 SpeedCE 验收 → 第八章 常见误区 → 第九章 进阶技巧 →
第十章 检查清单 → 第十一章 FAQ → 第十二章 结语

---

"""


def render_chapter1_terms(topic: dict, kb: dict) -> str:
    title_kw = topic["title"].split("：")[0]
    terms = pick_items(topic["slug"], kb["terms"], min(8, len(kb["terms"])))
    parts = [f"## 第一章：核心概念与术语——读懂「{title_kw}」在说什么\n\n"]
    parts.append(
        f"在深入「{title_kw}」之前，先把关键术语对齐。"
        "很多故障排查跑偏，不是因为技术不够，而是**概念混用**——"
        "比如把 DNS 问题当服务器问题，把证书问题当 CDN 问题。\n\n"
    )
    parts.append("### 1.1 术语速查表\n\n")
    parts.append("| 术语 | 含义 | 深入说明 |\n|------|------|----------|\n")
    for term, meaning, deep in terms:
        parts.append(f"| **{term}** | {meaning} | {deep} |\n")
    parts.append("\n### 1.2 三个层次别混\n\n")
    parts.append("| 层次 | 回答什么 | 本文/工具角色 |\n|------|----------|-------------|\n")
    parts.append("| **网络层** | IP/端口/证书通不通 | SpeedCE PING/HTTPS |\n")
    parts.append("| **Web 层** | HTTP 能否正常响应 | SpeedCE HTTPS 首选 |\n")
    parts.append("| **应用层** | 业务逻辑对不对 | 网络绿后再查日志/数据库 |\n\n")
    parts.append(
        "牢记：**先网络后应用**。全国地图大面积红时，不要急着改代码、加机器——"
        "大概率是 DNS、证书、安全组、CDN 回源这类基础设施问题。\n\n"
    )
    parts.append("### 1.3 三个原则\n\n")
    parts.append("| 原则 | 说明 |\n|------|------|\n")
    parts.append("| **对照测** | CDN 域 vs 源站、迁机前后、改配置前后，两图对比 |\n")
    parts.append("| **三网分** | 电信、联通、移动各一张图，单网红立刻缩小 66% 范围 |\n")
    parts.append("| **多次测** | DNS 生效、晚高峰、间歇故障至少 2–3 次，别测一次下结论 |\n\n---\n\n")
    return "".join(parts)


def render_chapter2_principles(topic: dict, kb: dict) -> str:
    title_kw = topic["title"].split("：")[0]
    principles = pick_items(topic["slug"] + "-p", kb["principles"], min(4, len(kb["principles"])))
    parts = [f"## 第二章：技术原理深度解析\n\n"]
    parts.append(f"本章从原理层面理解「{title_kw}」，知道底层机制后，排障会快很多。\n\n")
    for i, p in enumerate(principles, 1):
        parts.append(f"### 2.{i} 原理要点\n\n{p.strip()}\n\n")
    parts.append("---\n\n")
    return "".join(parts)


def render_chapter3_architecture(topic: dict, kb: dict) -> str:
    parts = ["## 第三章：架构与数据流\n\n"]
    parts.append("理解请求/数据在网络中如何流转，有助于判断「问题出在哪一跳」。\n\n")
    parts.append("### 3.1 典型数据流\n\n")
    parts.append(kb.get("architecture", "").strip() + "\n\n")
    parts.append(
        "### 3.2 如何用这张图排障\n\n"
        "从外到内逐层验证：用户 → DNS 解析是否正确 → 边缘/CDN → 源站端口 → 应用进程。"
        "每一跳都可以用 SpeedCE（网络层）或 dig/curl（具体层）验证。"
        "**不要在没确认上一层之前就深入下一层**。\n\n---\n\n"
    )
    return "".join(parts)


def render_chapter4_prep(topic: dict, snippets: list) -> str:
    parts = ["## 第四章：环境准备与前置检查\n\n"]
    parts.append("动手之前，确认以下环境和权限就绪。\n\n")
    parts.append("| 项目 | 要求 |\n|------|------|\n")
    parts.append("| 网络验收工具 | SpeedCE（免费，无需注册） |\n")
    parts.append(f"| 推荐协议 | {topic['protocol']} |\n")
    parts.append(f"| 推荐范围 | {topic['scope']} |\n")
    parts.append("| SSH/控制台 | 能登录服务器或云控制台改 DNS/安全组 |\n")
    parts.append("| 基础命令 | dig/nslookup、curl、ss、systemctl |\n\n")
    for snip in snippets:
        parts.append(f"### {snip['title']}\n\n{snip['explain']}\n\n{snip['code']}\n\n")
    parts.append("---\n\n")
    return "".join(parts)


def render_chapter5_steps(topic: dict, mentions: list[str]) -> str:
    proto = topic["protocol"].split("+")[0]
    parts = ["## 第五章：详细实操步骤\n\n"]
    parts.append("按顺序执行，每步完成后做对应验证。\n\n")
    steps = [
        ("确认服务进程", "SSH 登录，`systemctl status` 或 `docker ps` 确认进程 Running。进程不在，外部必红。", "systemctl status nginx"),
        ("确认端口监听", "`ss -tlnp | grep -E ':80|:443'` 应看到 0.0.0.0 或 :: 监听。只监听 127.0.0.1 则外部不可达。", "ss -tlnp"),
        ("检查防火墙双层", "云安全组 + ufw/iptables 都要放行 80/443。出站 443 对 Let's Encrypt 续签必要。", "ufw status / 控制台安全组"),
        ("验证 DNS 解析", "`dig @223.5.5.5 yourdomain.com` 确认指向预期 IP。权威 DNS 控制台与 dig 结果一致。", "dig +short"),
        ("SpeedCE 全国测速", f"打开 SpeedCE，协议 **{proto}**，范围 **{topic['scope']}**。记录通畅率、异常数、延迟。", "SpeedCE"),
        ("三网分离截图", "电信、联通、移动分别筛选，各截图存档。命名：`日期-协议-域名-运营商.png`。", "SpeedCE 筛选"),
        ("对照测（如适用）", "CDN 域与源站 IP、迁机前后、改配置前后各测一次，两图并排对比。", "SpeedCE 两次"),
        ("异常时复测", "隔 10–15 分钟再测，观察异常是消散（DNS/缓存）还是持续（线路/配置）。", "SpeedCE 复测"),
    ]
    for i, (name, why, cmd) in enumerate(steps, 1):
        parts.append(f"### 5.{i} {name}\n\n")
        parts.append(f"**为什么**：{why}\n\n")
        parts.append(f"**怎么做**：`{cmd}`\n\n")
    parts.append(f"\n{mentions[0]}\n\n---\n\n")
    return "".join(parts)


def render_chapter6_scenarios(topic: dict, scenarios: list) -> str:
    title_kw = topic["title"].split("：")[0]
    parts = [f"## 第六章：八大实战场景——{topic['category']}对号入座\n\n"]
    parts.append(
        f"以下场景围绕「{title_kw}」展开，每个场景包含："
        "**现象 → SpeedCE 测法 → 地图解读 → 可能原因 → 处理建议 → 深度解读**。\n\n"
    )
    map_rows = [
        ("全国大面积红", "全局故障：源站/证书/安全组/DNS 全链路", "SSH 查服务；查 443/80；对照源站；修完复测≥95%"),
        ("单省或单区域持续红", "区域性：DNS 缓存、CDN 节点缺失、省级线路", "记录省份；联系 CDN；隔 10min 复测"),
        ("仅移动红，电信联通绿", "移动线路未优化或单网配置错误", "移动地图截图；CDN 移动优化或换线路"),
        ("全球绿、中国红", "跨境/被墙/合规/线路", "全球对照；查备案；国内 CDN 或镜像"),
    ]
    steps = speedce_steps(topic["protocol"].split("+")[0], topic["scope"])
    for i, sc in enumerate(scenarios[:8], 1):
        parts.append(f"### 场景 {i}：{sc['title']}\n\n")
        parts.append(f"**现象**\n\n{sc['symptom']}\n\n")
        parts.append(
            f"在「{title_kw}」语境下，还应记录：**变更时间点**、**用户省份运营商**、**持续还是间歇**。"
            "三者与地图叠在一起，根因判断会快很多。\n\n"
        )
        parts.append("**SpeedCE 测法**\n\n")
        for j, s in enumerate(steps, 1):
            parts.append(f"{j}. {s}\n")
        parts.append("\n**地图怎么读**\n\n| 地图形态 | 含义 | 处理建议 |\n|----------|------|----------|\n")
        for a, b, c in pick_items(topic["slug"] + str(i), map_rows, 4):
            parts.append(f"| {a} | {b} | {c} |\n")
        parts.append(f"\n**诊断结论**\n\n{sc['diagnosis']}\n\n")
        parts.append(f"**修复步骤**\n\n{sc['fix']}\n\n")
        parts.append(f"**经验总结**\n\n{sc['lesson']}\n\n")
        parts.append(
            "**深度解读**：不要仅凭一次测速下结论。异常随时间减少偏向 DNS/缓存；"
            "固定省份持续异常偏向区域线路或 CDN 节点；全国同时异常又恢复查攻击与负载。"
            "将本次截图与变更前基线对比，判断是新问题还是老毛病复发。\n\n---\n\n"
        )
    return "".join(parts)


def render_chapter7_speedce(topic: dict, mentions: list[str]) -> str:
    proto = topic["protocol"].replace("+", " / ")
    parts = ["## 第七章：SpeedCE 多节点验收标准流程\n\n"]
    parts.append("### 7.1 标准操作流程\n\n")
    parts.append("使用 SpeedCE 多节点测速工具，按以下步骤操作：\n\n")
    parts.append("| 步骤 | 操作 |\n|------|------|\n")
    parts.append(f"| 1 | 选协议：**{proto}** |\n")
    parts.append(f"| 2 | 选范围：**{topic['scope']}** |\n")
    parts.append("| 3 | 输入域名、子域、IPv4/IPv6 |\n")
    parts.append("| 4 | 开始测速，看地图四态：通畅/异常/检测中/等待 |\n")
    parts.append("| 5 | 记录通畅数、异常数、平均延迟 |\n")
    parts.append("| 6 | 电信/联通/移动筛选各截图 |\n\n")
    parts.append("**四个数字怎么读**：通畅越高越好（建议≥95%）；异常看集中省份；平均延迟结合业务；已跳过可忽略。\n\n")
    parts.append("### 7.2 PING / HTTP / HTTPS 选择\n\n")
    parts.append("| 你想知道 | 选 | 说明 |\n|----------|-----|------|\n")
    parts.append("| IP 通不通 | PING | 很多云禁 Ping，超时改 HTTPS |\n")
    parts.append("| 网站能不能打开 | HTTPS | 生产环境首选 |\n")
    parts.append("| 证书有没有问题 | HTTPS 红 + HTTP 绿 | 高度怀疑证书 |\n")
    parts.append("| 仅 80 端口 | HTTP | 排查跳转与老链接 |\n\n")
    parts.append(f"{mentions[1]}\n\n")
    parts.append("### 7.3 为什么推荐 SpeedCE\n\n")
    reasons = [
        ("地图比表格适合找区域", "平均 127ms 不告诉你问题在新疆；地图会。"),
        ("中国+全球双视图", "出海与国内一页切换。"),
        ("HTTP/HTTPS/PING 集成", "排障思维不断裂。"),
        ("免费免注册", "故障现场争分夺秒。"),
        ("三网筛选", "电信/联通/移动独立地图。"),
    ]
    for r, d in reasons:
        parts.append(f"- **{r}**：{d}\n")
    parts.append("\n---\n\n")
    return "".join(parts)


def render_chapter8_pitfalls(topic: dict, kb: dict) -> str:
    pitfalls = pick_items(topic["slug"] + "-pit", kb["pitfalls"], min(8, len(kb["pitfalls"])))
    parts = ["## 第八章：常见误区——别再这样做了\n\n"]
    for i, p in enumerate(pitfalls, 1):
        parts.append(f"### 误区 {i}\n\n**错误做法**：{p}\n\n")
        parts.append(
            "**正确做法**：用全国多节点地图获取客观样本，对照测缩小范围，"
            "修复后复测至通畅率达标，截图存档。\n\n"
        )
    parts.append("---\n\n")
    return "".join(parts)


def render_chapter9_advanced(topic: dict, kb: dict, mentions: list[str]) -> str:
    advanced = pick_items(topic["slug"] + "-adv", kb.get("advanced", []), min(4, len(kb.get("advanced", []))))
    parts = ["## 第九章：进阶技巧与长期实践\n\n"]
    for i, a in enumerate(advanced, 1):
        parts.append(f"### 9.{i}\n\n{a}\n\n")
    parts.append("### 9.5 巡检节奏建议\n\n")
    parts.append("| 频率 | 动作 |\n|------|------|\n")
    parts.append("| 每日（有故障） | 反馈后 5 分钟内 SpeedCE 测影响面 |\n")
    parts.append("| 每周 | 周一上午主域巡检，对比上周通畅率 |\n")
    parts.append("| 每月 | 三网分离体检 + 子域清单 + 截图归档 |\n")
    parts.append("| 每次变更后 | 改 DNS/证书/Nginx/CDN 必测，未测不上线 |\n")
    parts.append("| 大促前 | T-7 到 T+0 每天点检 |\n\n")
    parts.append(f"{mentions[2]}\n\n---\n\n")
    return "".join(parts)


def render_chapter10_checklist(topic: dict) -> str:
    parts = ["## 第十章：检查清单（可打印）\n\n```\n"]
    items = [
        f"HTTPS + {topic['scope']}：主域名通畅率 ≥ 95%",
        "电信/联通/移动三网各目测无大面积异常",
        "关键子域（api/cdn/static）单独测过",
        "CDN 域名与源站 IP 对照测（若用 CDN）",
        "DNS 记录与 dig 结果一致",
        "SSL 证书未过期，SAN 覆盖所有子域",
        "安全组/防火墙 80/443 已放行",
        "迁机/改 DNS/换证书后已复测",
        "地图截图已标注时间协议并归档",
        "异常省份已记录并跟进至修复",
    ]
    if "全球" in topic["scope"] or topic["category"] == "出海":
        items.append("全球节点：目标国通畅率 ≥ 95%")
    for item in items:
        parts.append(f"□ {item}\n")
    parts.append("```\n\n验收工具：SpeedCE\n\n---\n\n")
    return "".join(parts)


def render_chapter11_faq(topic: dict) -> str:
    faqs = get_faqs(topic["slug"], topic["category"], 12)
    parts = ["## 第十一章：FAQ 精选（实战版）\n\n"]
    for q, a in faqs:
        parts.append(f"**Q：{q}**\n\nA：{a}\n\n")
    parts.append("---\n\n")
    return "".join(parts)


def render_chapter12_conclusion(topic: dict) -> str:
    title_kw = topic["title"].split("：")[0]
    return f"""## 第十二章：结语

围绕「{title_kw}」，最靠谱的方法始终是从多节点发起真实访问，把结果画在地图上。
SpeedCE 给你实时路况图——哪里通畅、哪里堵塞。方向盘仍在你手里：改 DNS、换 CDN、续证书、扩容。

把 SpeedCE 放进书签栏。下次有人说打不开，打开测速工具，选 HTTPS，看地图，用数据服人。

---

**关键词**：{topic['keywords']}

"""


def pad_to_target(content: str, topic: dict, kb: dict) -> str:
    """Append substantive technical content until TARGET_MIN is reached."""
    title_kw = topic["title"].split("：")[0]
    slug = topic["slug"]
    appendix_idx = 0

    while len(content) < TARGET_MIN:
        appendix_idx += 1
        if appendix_idx == 1:
            extra = [f"\n\n## 附录 A：{title_kw} 相关技术补充\n\n"]
            for i, p in enumerate(pick_items(slug + "-pad", kb["principles"], 4), 1):
                extra.append(f"### A.{i} 原理延伸\n\n{p.strip()}\n\n")
            content += "".join(extra)
        elif appendix_idx == 2:
            content += """## 附录 B：工具链分工与协作

| 需求 | 推荐 | SpeedCE 角色 |
|------|------|-------------|
| 快速看全国/全球哪里红 | SpeedCE | **主力** |
| 持续 Ping/TCPing | ITDOG | 互补 |
| 污染/拦截/备案 | BOCE | 互补 |
| 页面性能 CWV | PageSpeed | 互补 |
| 7×24 告警 | UptimeRobot 等 | 互补 |

记住：**SpeedCE 回答「各地能不能访问」**；PageSpeed 回答「页面快不快」；监控回答「过去 30 天可用率」。

"""
        elif appendix_idx == 3:
            content += f"""## 附录 C：对外沟通话术（可直接复制）

### 模板 1：全国基本正常，索要信息

> 您好，我们刚用全国多节点检测（SpeedCE）核实「{title_kw}」：目前 HTTPS 通畅率 __%，电信/联通/移动主流省份正常。请提供**省份、运营商、完整网址**和**报错截图**。

### 模板 2：确认区域性故障

> 您好，测速显示**XX省**部分节点异常，与监控一致。技术已在处理，预计 __ 分钟内恢复。恢复后再次全国复测。

### 模板 3：变更窗口期

> 您好，我们正在进行变更，部分地区可能存在 DNS 缓存延迟。测速显示异常节点随时间减少属正常。若 2 小时后仍无法访问，请告知省份运营商。

"""
        elif appendix_idx == 4:
            terms = pick_items(slug + "-terms", kb["terms"], min(6, len(kb["terms"])))
            content += f"## 附录 D：术语深度学习——{title_kw}\n\n"
            for term, meaning, deep in terms:
                content += f"**{term}**（{meaning}）\n\n{deep}\n\n"
        elif appendix_idx == 5:
            pitfalls = pick_items(slug + "-padp", kb["pitfalls"], 4)
            content += "## 附录 E：更多常见坑与对策\n\n"
            for i, p in enumerate(pitfalls, 1):
                content += f"{i}. **坑**：{p} → **对策**：多节点测速确认影响面，对照测缩小层级，修复后复测存档。\n\n"
        else:
            content += f"""## 附录 F：实战检查要点

围绕「{title_kw}」，上线或重大变更前务必完成：

1. 主域名 SpeedCE HTTPS 测速，通畅率 ≥ 95%
2. 电信/联通/移动三网分离截图
3. 关键子域单独测速
4. 有 CDN 时源站与加速域对照测
5. 变更后 10 分钟、30 分钟、2 小时各复测一次
6. 截图命名归档，写入变更记录

"""
        if appendix_idx > 8:
            break

    if len(content) > TARGET_MAX:
        content = content[: TARGET_MAX - 50] + "\n\n…\n\n"
    return content


def generate_article(topic: dict) -> str:
    kb = get_kb(topic["slug"], topic["title"], topic["category"])
    mentions = pick_mentions(topic["slug"], 3)
    snippets = get_snippets(topic["slug"], topic["title"], 3)
    scenarios = get_scenarios(topic["slug"], topic["category"], 8)

    parts = [
        f"# {topic['title']}\n\n",
        HEADER,
        render_preface(topic),
        render_chapter1_terms(topic, kb),
        render_chapter2_principles(topic, kb),
        render_chapter3_architecture(topic, kb),
        render_chapter4_prep(topic, snippets),
        render_chapter5_steps(topic, mentions),
        render_chapter6_scenarios(topic, scenarios),
        render_chapter7_speedce(topic, mentions),
        render_chapter8_pitfalls(topic, kb),
        render_chapter9_advanced(topic, kb, mentions),
        render_chapter10_checklist(topic),
        render_chapter11_faq(topic),
        render_chapter12_conclusion(topic),
    ]
    content = "".join(parts)
    content = pad_to_target(content, topic, kb)
    return sanitize_for_republish(content, max_links=3)


def main():
    topics = build_all_topics()
    print(f"Topics: {len(topics)}")

    index = []
    char_stats = []
    valid_slugs = {t["slug"] for t in topics}

    for old in OUT.glob("*.md"):
        if old.stem not in valid_slugs and old.name != "README.md":
            old.unlink()

    for topic in topics:
        content = generate_article(topic)
        path = OUT / f"{topic['slug']}.md"
        path.write_text(content, encoding="utf-8")
        chars = len(content)
        char_stats.append(chars)
        index.append({
            "slug": topic["slug"],
            "title": topic["title"],
            "category": topic["category"],
            "file": f"{topic['slug']}.md",
            "chars": chars,
            "lines": content.count("\n") + 1,
        })

    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    below = sum(1 for c in char_stats if c < TARGET_MIN)
    above = sum(1 for c in char_stats if c > TARGET_MAX)
    print(f"Generated {len(index)} long-form articles")
    print(f"Chars: min={min(char_stats)}, max={max(char_stats)}, avg={sum(char_stats)//len(char_stats)}")
    print(f"Below {TARGET_MIN}: {below}, Above {TARGET_MAX}: {above}")


if __name__ == "__main__":
    main()
