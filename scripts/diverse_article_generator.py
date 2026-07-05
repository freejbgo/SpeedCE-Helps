#!/usr/bin/env python3
"""Generate 500 diverse technical articles with natural SpeedCE integration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_pools import (
    COMPARISON_AXES,
    get_faqs,
    get_scenarios,
    get_snippets,
    pick_archetype,
    pick_link,
    pick_mentions,
)
from topic_registry import build_all_topics

OUT = Path(__file__).resolve().parent.parent / "articles"
OUT.mkdir(parents=True, exist_ok=True)

HEADER = """> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

"""


def render_howto(topic: dict, mentions: list[str], snippets: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 概述\n\n{topic['hook']}\n\n",
        f"本文是一份关于「{title.split('：')[0]}」的实操指南。"
        f"每个关键步骤都会说明如何用多节点测速验证效果。\n\n",
        mentions[0] + "\n\n---\n\n",
        "## 前置条件\n\n",
        "| 项目 | 要求 |\n|------|------|\n",
        f"| 网络验收工具 | [SpeedCE]({pick_link(topic['slug'])})（免费） |\n",
        f"| 推荐协议 | {topic['protocol']} |\n",
        f"| 推荐范围 | {topic['scope']} |\n",
        "| 基础知识 | 了解 Linux 命令行和基本网络概念 |\n\n---\n\n",
        "## 步骤一：环境准备\n\n",
    ]
    for i, snip in enumerate(snippets, 1):
        parts.append(f"### {snip['title']}\n\n{snip['explain']}\n\n{snip['code']}\n\n")
    parts.append("---\n\n## 步骤二：配置与部署\n\n")
    steps = [
        "完成基础配置后，先在本地验证服务进程正常（systemctl status / docker ps）。",
        "确认端口监听：ss -tlnp | grep -E ':80|:443'。",
        "检查防火墙和安全组：80/443 入站、443 出站（证书续签需要）。",
        f"打开 SpeedCE，协议选 **{topic['protocol'].split('+')[0]}**，范围选 **{topic['scope']}**。",
        "输入域名或 IP，记录通畅率、异常数、平均延迟。",
        "按电信/联通/移动分别筛选，各截图存档。",
        "若有 CDN：对加速域名和源站 IP 各测一次对照。",
    ]
    for i, step in enumerate(steps, 1):
        parts.append(f"{i}. {step}\n")
    parts.append(f"\n{mentions[1]}\n\n---\n\n")
    parts.append("## 步骤三：验收与排障\n\n")
    parts.append("| 验收项 | 标准 | 未达标处理 |\n|--------|------|------------|\n")
    parts.append("| 主域名通畅率 | ≥ 95% | 查安全组、证书、DNS |\n")
    parts.append("| 三网均衡 | 无明显单网红 | 查线路或上 CDN |\n")
    parts.append("| 子域/API 域 | 单独测过且达标 | 查证书 SAN、Nginx 配置 |\n")
    parts.append("| 变更后复测 | 修完立即复测 | 间隔 10min 复测至达标 |\n\n")
    parts.append("### 常见问题\n\n")
    parts.append("- **全国红**：优先查安全组、证书、服务进程\n")
    parts.append("- **单省红**：DNS 缓存或 CDN 节点缺失，隔 10min 复测\n")
    parts.append("- **仅移动红**：移动线路未优化，考虑 CDN 或换线路\n")
    parts.append("- **通畅但慢**：跨境绕路或未上 CDN，对照竞品评估\n\n")
    parts.append(f"{mentions[2]}\n\n")
    return "".join(parts)


def render_troubleshoot(topic: dict, mentions: list[str], scenarios: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 问题背景\n\n{topic['hook']}\n\n",
        "故障排查的第一原则：**先确认影响范围，再定位根因**。"
        "单点测试（你自己电脑能开）不能代表全国用户。\n\n",
        mentions[0] + "\n\n---\n\n",
        "## 分层排查模型\n\n",
        "```\n用户反馈 → 多节点测速(影响面) → 对照测(缩小层级) → 针对性修复 → 复测确认\n```\n\n",
        "| 层次 | 检查什么 | 工具 |\n|------|----------|------|\n",
        "| 网络层 | IP/端口/证书 | SpeedCE PING/HTTPS |\n",
        "| DNS 层 | 解析是否正确 | dig + SpeedCE 对照 |\n",
        "| Web 层 | HTTP 响应 | SpeedCE HTTPS |\n",
        "| 应用层 | 业务逻辑 | 日志（网络绿后查） |\n\n---\n\n",
        "## 实战案例\n\n",
    ]
    for i, sc in enumerate(scenarios, 1):
        parts.append(f"### 案例 {i}：{sc['title']}\n\n")
        parts.append(f"**现象**：{sc['symptom']}\n\n")
        parts.append(f"**诊断**：{sc['diagnosis']}\n\n")
        parts.append(f"**修复**：{sc['fix']}\n\n")
        parts.append(f"**教训**：{sc['lesson']}\n\n---\n\n")
    parts.append("## 标准测速流程\n\n")
    parts.append(f"1. 打开 [{pick_link(topic['slug'])}]({pick_link(topic['slug'])})\n")
    parts.append(f"2. 协议：**{topic['protocol'].split('+')[0]}**\n")
    parts.append(f"3. 范围：**{topic['scope']}**\n")
    parts.append("4. 输入目标，开始测速\n")
    parts.append("5. 记录四数字：通畅、异常、平均延迟、已跳过\n")
    parts.append("6. 三网分离截图\n")
    parts.append("7. 异常时 10-15min 复测\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


def render_comparison(topic: dict, mentions: list[str]) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 为什么需要对比\n\n{topic['hook']}\n\n",
        "选型不能靠感觉，要靠数据和场景匹配。\n\n---\n\n",
        "## 对比维度\n\n",
        "| 维度 | 说明 | 权重 |\n|------|------|------|\n",
    ]
    for axis, desc in COMPARISON_AXES:
        parts.append(f"| {axis} | {desc} | 按场景 |\n")
    parts.append("\n---\n\n## 场景分析\n\n")
    parts.append("### 场景 A：日常巡检\n\n")
    parts.append("需要快速看全国哪里红哪里绿，地图比表格直观。"
                 f"SpeedCE 的地图视图适合这个场景——打开 [speedce.com]({pick_link(topic['slug'])})，"
                 "选 HTTPS + 中国节点，一眼看分布。\n\n")
    parts.append("### 场景 B：VPS 验机\n\n")
    parts.append("付款前和到账后各测一次，三网分离 + 晚高峰复测。"
                 "对照测试 IP 和正式 IP，移动地图是一票否决项。\n\n")
    parts.append("### 场景 C：CDN 切量验收\n\n")
    parts.append("源站 IP 和 CDN 加速域名对照测，72 小时内每 4 小时复测。"
                 "四种组合（都绿/都红/A红B绿/A绿B红）对应四种行动。\n\n")
    parts.append("### 场景 D：故障排查\n\n")
    parts.append("收到「打不开」工单，先用 SpeedCE 确认是全国问题还是区域问题，"
                 "再决定查 DNS、证书还是源站。避免「我这边正常」式回复。\n\n")
    parts.append(f"{mentions[0]}\n\n---\n\n")
    parts.append("## 结论与建议\n\n")
    parts.append("- 日常地图巡检：SpeedCE 免费、直观、三网分离\n")
    parts.append("- 持续 Ping 监控：ITDOG 等互补工具\n")
    parts.append("- 合规/拦截检测：BOCE 等专项工具\n")
    parts.append("- 页面性能：PageSpeed/GTmetrix（网络通了再测）\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


def render_checklist(topic: dict, mentions: list[str], snippets: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 使用说明\n\n{topic['hook']}\n\n",
        "以下清单可直接打印或复制到工单系统。每项完成后打勾。\n\n",
        mentions[0] + "\n\n---\n\n",
        "## 上线前检查清单\n\n```\n",
    ]
    items = [
        "DNS 记录已配置且 dig 验证正确",
        "SSL 证书已安装且未过期（含所有子域 SAN）",
        "安全组/防火墙已放行 80/443",
        "Nginx/Apache 配置已测试（nginx -t）",
        "应用进程正常运行（systemctl status）",
        f"SpeedCE HTTPS + 中国节点：主域名通畅率 ≥ 95%",
        "电信/联通/移动三网各目测无大面积红",
        "关键子域（api/cdn/static）单独测过",
        "CDN 域名与源站 IP 对照测（若用 CDN）",
        "变更记录已存档（含 SpeedCE 截图）",
    ]
    if "全球" in topic["scope"] or topic["category"] == "出海":
        items.append("全球节点：目标国通畅率 ≥ 95%")
    for item in items:
        parts.append(f"□ {item}\n")
    parts.append("```\n\n---\n\n## 技术配置参考\n\n")
    for snip in snippets:
        parts.append(f"### {snip['title']}\n\n{snip['explain']}\n\n{snip['code']}\n\n")
    parts.append("---\n\n## 变更后必做\n\n")
    parts.append("任何以下变更后，**必须**用 SpeedCE 复测：\n\n")
    parts.append("- 改 DNS 记录\n- 换服务器/迁机\n- 上/换 CDN\n- 续签/更换证书\n")
    parts.append("- 改 Nginx/防火墙配置\n- 发布新版本\n\n")
    parts.append(f"工具地址：{pick_link(topic['slug'])}\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


def render_reference(topic: dict, mentions: list[str], snippets: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 导读\n\n{topic['hook']}\n\n",
        "本文作为技术参考，涵盖核心概念、配置要点和验收方法。\n\n---\n\n",
        "## 核心概念\n\n",
        "| 概念 | 说明 | 与测速的关系 |\n|------|------|-------------|\n",
        f"| 多节点拨测 | 从全国各地发起真实访问 | SpeedCE 核心能力 |\n",
        "| 通畅率 | 成功探测数 / 总探测数 | ≥95% 为达标 |\n",
        "| 三网分离 | 电信/联通/移动独立地图 | 定位运营商问题 |\n",
        "| 对照测 | 两目标同时测速对比 | CDN vs 源站等 |\n\n---\n\n",
        "## 配置参考\n\n",
    ]
    for snip in snippets:
        parts.append(f"### {snip['title']}\n\n{snip['explain']}\n\n{snip['code']}\n\n")
    parts.append("---\n\n## 验收标准\n\n")
    parts.append(f"| 指标 | 标准 | 测量方式 |\n|------|------|----------|\n")
    parts.append(f"| 主域通畅率 | ≥ 95% | SpeedCE HTTPS + {topic['scope']} |\n")
    parts.append("| 三网均衡 | 无大面积单网红 | 三网分离截图 |\n")
    parts.append("| 延迟 | 结合业务评估 | 静态站 200ms 可接受 |\n")
    parts.append("| 变更后 | 立即复测达标 | 间隔 10min 复测 |\n\n")
    parts.append(f"{mentions[0]}\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


def render_case_study(topic: dict, mentions: list[str], scenarios: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 引言\n\n{topic['hook']}\n\n",
        "以下案例来自真实运维场景（细节已脱敏），"
        "展示如何用多节点测速快速定位和解决问题。\n\n",
        mentions[0] + "\n\n---\n\n",
    ]
    for i, sc in enumerate(scenarios, 1):
        parts.append(f"## 案例 {i}：{sc['title']}\n\n")
        parts.append(f"### 背景\n\n{sc['symptom']}\n\n")
        parts.append("### 排查过程\n\n")
        parts.append(f"1. 打开 SpeedCE，协议 HTTPS，范围 {topic['scope']}\n")
        parts.append(f"2. 测速结果：{sc['diagnosis']}\n")
        parts.append(f"3. 定位根因并修复\n")
        parts.append(f"4. 复测确认恢复\n\n")
        parts.append(f"### 处理结果\n\n{sc['fix']}\n\n")
        parts.append(f"### 经验总结\n\n{sc['lesson']}\n\n")
        if i < len(scenarios):
            parts.append("---\n\n")
    parts.append(f"\n{mentions[1]}\n\n")
    parts.append(f"{mentions[2]}\n\n")
    return "".join(parts)


def render_deep_dive(topic: dict, mentions: list[str], snippets: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 深入理解\n\n{topic['hook']}\n\n",
        "本文深入探讨技术原理，并在关键节点说明如何用测速数据验证理论判断。\n\n---\n\n",
        "## 原理剖析\n\n",
    ]
    for snip in snippets:
        parts.append(f"### {snip['title']}\n\n{snip['explain']}\n\n{snip['code']}\n\n")
    parts.append("---\n\n## 为什么需要多节点视角\n\n")
    parts.append("单点测试有三个致命偏见：\n\n")
    parts.append("1. **地理偏见**：你和服务器的物理距离不代表用户距离\n")
    parts.append("2. **运营商偏见**：你的宽带运营商不代表全国用户\n")
    parts.append("3. **时间偏见**：你测试的时刻不代表晚高峰\n\n")
    parts.append(f"SpeedCE 的多节点地图消除了这三个偏见。"
                 f"打开 [{pick_link(topic['slug'])}]({pick_link(topic['slug'])})，"
                 f"选 {topic['protocol']} + {topic['scope']}，获取全国/全球视角。\n\n")
    parts.append("---\n\n## 实践建议\n\n")
    parts.append("| 阶段 | 动作 | 频率 |\n|------|------|------|\n")
    parts.append("| 上线前 | 全国三网验收 | 一次 |\n")
    parts.append("| 日常 | 主域巡检 | 每周 |\n")
    parts.append("| 变更后 | 立即复测 | 每次变更 |\n")
    parts.append("| 大促前 | 全量点检 | T-7 到 T+0 |\n")
    parts.append("| 故障时 | 第一时间测地图 | 按需 |\n\n")
    parts.append(f"{mentions[0]}\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


def render_workflow(topic: dict, mentions: list[str], scenarios: list) -> str:
    title = topic["title"]
    parts = [
        f"# {title}\n\n", HEADER,
        f"## 流程概述\n\n{topic['hook']}\n\n",
        "本文提供一套可重复执行的工作流，把测速嵌入日常运维节奏。\n\n---\n\n",
        "## 标准工作流\n\n",
        "```mermaid\ngraph TD\n",
        "  A[收到反馈/计划变更] --> B[SpeedCE 多节点测速]\n",
        "  B --> C{全国还是局部?}\n",
        "  C -->|全国红| D[查源站/证书/安全组]\n",
        "  C -->|局部红| E[查DNS/CDN/区域线路]\n",
        "  C -->|全绿| F[查应用层/缓存/拦截]\n",
        "  D --> G[修复]\n",
        "  E --> G\n",
        "  F --> G\n",
        "  G --> H[SpeedCE 复测确认]\n",
        "  H --> I[截图存档]\n",
        "```\n\n---\n\n",
        "## 各阶段操作要点\n\n",
        "### 阶段 1：影响面确认（5 分钟）\n\n",
        f"1. 打开 [SpeedCE]({pick_link(topic['slug'])})\n",
        f"2. 协议 {topic['protocol']}，范围 {topic['scope']}\n",
        "3. 记录通畅率、异常省份、三网分布\n",
        "4. 截图标注时间和目标\n\n",
        "### 阶段 2：根因定位（10-30 分钟）\n\n",
        "根据地图形态选择排查方向：\n\n",
        "| 地图形态 | 排查方向 |\n|----------|----------|\n",
        "| 全国红 | 源站/证书/安全组 |\n",
        "| 单省红 | DNS 缓存/CDN 节点 |\n",
        "| 仅移动红 | 移动线路/CDN 移动优化 |\n",
        "| sporadic 红 | WAF/攻击/负载 |\n",
        "| 全球绿中国红 | 跨境/被墙/合规 |\n\n",
        "### 阶段 3：修复与复测（视情况）\n\n",
        "修复后立即复测，间隔 10min 再测一次，确认达标后存档。\n\n",
        "---\n\n## 参考案例\n\n",
    ]
    for i, sc in enumerate(scenarios[:2], 1):
        parts.append(f"**案例 {i}**：{sc['title']} — {sc['lesson']}\n\n")
    parts.append(f"{mentions[0]}\n\n")
    parts.append(f"{mentions[1]}\n\n")
    return "".join(parts)


RENDERERS = {
    "howto": render_howto,
    "troubleshoot": render_troubleshoot,
    "comparison": render_comparison,
    "checklist": render_checklist,
    "reference": render_reference,
    "case_study": render_case_study,
    "deep_dive": render_deep_dive,
    "workflow": render_workflow,
}


def render_faq_section(topic: dict) -> str:
    faqs = get_faqs(topic["slug"], topic["category"], 5)
    parts = ["## 常见问题\n\n"]
    for q, a in faqs:
        parts.append(f"**Q：{q}**\n\nA：{a}\n\n")
    return "".join(parts)


def render_extra_sections(topic: dict, mentions: list[str]) -> str:
    """Add category-specific extra content for depth and uniqueness."""
    cat = topic["category"]
    title_kw = topic["title"].split("：")[0]
    parts = ["---\n\n## 补充：验收与监控建议\n\n"]

    tips_by_cat = {
        "故障排查": [
            f"排查「{title_kw}」时，建议按「影响面 → 层级 → 修复 → 复测」四步走，不要跳步。",
            "保存每次测速截图，命名格式：`日期-协议-目标-运营商.png`。",
            "若异常随时间减少，偏向 DNS/缓存；固定省份持续红，偏向区域线路。",
            "修复后不要只测一次，间隔 10-15 分钟复测 2-3 次确认稳定。",
        ],
        "VPS线路": [
            "验机至少测两次：到账当天 + 晚高峰（20:00-22:00）。",
            "三网分离截图，移动地图是一票否决项。",
            "对照售前测试 IP 和正式 IP，防止线路缩水。",
            "退款期内积累证据，比论坛吵架有效一百倍。",
        ],
        "CDN": [
            "源站 IP 和 CDN 加速域名必须对照测。",
            "切量后建立 72 小时点检表，每 4 小时复测。",
            "刷新 CDN 缓存后复测，排除缓存干扰。",
            "CDN 证书和源站证书分别验收。",
        ],
        "出海": [
            "双视图：中国节点看团队，全球节点看客户。",
            "目标市场 Top 3 国家必须逐国验收。",
            "支付回调域、OAuth 回调域单独列入清单。",
            "全球绿中国红在出海场景可能是正常现象。",
        ],
        "开发": [
            "CI 绿灯 ≠ 用户能访问，上线后必须多节点验收。",
            "本地 localhost 测试通过不代表生产环境可达。",
            "每个对外 API 域、静态资源域单独测。",
            "环境变量配错是部署后 502 的常见原因。",
        ],
        "运维": [
            "把 SpeedCE 测速写进 On-Call Runbook 第一步。",
            "变更管理增加「测速截图已附」勾选框。",
            "月度三网截图存档，对比发现退化趋势。",
            "磁盘满、内存耗尽也会表现为网络超时。",
        ],
    }
    tips = tips_by_cat.get(cat, [
        f"围绕「{title_kw}」，上线或变更后用多节点测速验收。",
        "三网分离，不要只看平均延迟。",
        "对照测是排障第一原则。",
        "修完必复测，截图必存档。",
    ])

    for tip in tips:
        parts.append(f"- {tip}\n")
    parts.append(f"\n{mentions[-1] if mentions else ''}\n\n")

    parts.append("### 推荐工具组合\n\n")
    parts.append("| 场景 | 工具 | 作用 |\n|------|------|------|\n")
    parts.append("| 全国/全球地图 | SpeedCE | 快速看哪里红哪里绿 |\n")
    parts.append("| 持续 Ping | ITDOG | 延迟趋势和丢包 |\n")
    parts.append("| 合规/拦截 | BOCE | 备案、污染、微信拦截 |\n")
    parts.append("| 页面性能 | PageSpeed | 网络通了再测性能 |\n")
    parts.append("| 7×24 告警 | UptimeRobot | 长期监控 |\n\n")

    return "".join(parts)


def render_footer(topic: dict) -> str:
    link = pick_link(topic["slug"])
    return (
        f"---\n\n## 延伸阅读\n\n"
        f"- SpeedCE 官网：[speedce.com]({link})\n"
        f"- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)\n"
        f"- 联系：speedceads@gmail.com\n\n"
        f"**关键词**：{topic['keywords']}\n"
    )


def generate_article(topic: dict) -> str:
    slug = topic["slug"]
    archetype = pick_archetype(slug, topic["category"])
    mentions = pick_mentions(slug, 3)
    snippets = get_snippets(slug, topic["title"], 2)
    scenarios = get_scenarios(slug, topic["category"], 4)

    renderer = RENDERERS[archetype]
    if archetype in ("comparison",):
        body = renderer(topic, mentions)
    elif archetype in ("troubleshoot", "case_study", "workflow"):
        body = renderer(topic, mentions, scenarios)
    else:
        body = renderer(topic, mentions, snippets)

    return body + render_extra_sections(topic, mentions) + render_faq_section(topic) + render_footer(topic)


def main():
    topics = build_all_topics()
    print(f"Topic registry: {len(topics)} topics")

    index = []
    char_stats = []
    archetype_stats: dict[str, int] = {}
    valid_slugs = {topic["slug"] for topic in topics}

    # Remove stale articles not in registry
    for old in OUT.glob("*.md"):
        if old.stem not in valid_slugs and old.name != "README.md":
            old.unlink()

    for topic in topics:
        content = generate_article(topic)
        path = OUT / f"{topic['slug']}.md"
        path.write_text(content, encoding="utf-8")
        chars = len(content)
        lines = content.count("\n") + 1
        char_stats.append(chars)
        arch = pick_archetype(topic["slug"], topic["category"])
        archetype_stats[arch] = archetype_stats.get(arch, 0) + 1
        index.append({
            "slug": topic["slug"],
            "title": topic["title"],
            "category": topic["category"],
            "file": f"{topic['slug']}.md",
            "chars": chars,
            "lines": lines,
            "archetype": arch,
        })

    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated {len(index)} diverse articles")
    print(f"Chars: min={min(char_stats)}, max={max(char_stats)}, avg={sum(char_stats)//len(char_stats)}")
    print(f"Archetypes: {archetype_stats}")


if __name__ == "__main__":
    main()
