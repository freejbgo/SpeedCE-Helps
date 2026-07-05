#!/usr/bin/env python3
"""Generate premium long-form SpeedCE articles (~12k-18k chars each)."""

from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "articles"
OUT.mkdir(parents=True, exist_ok=True)

HEADER = """> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

"""

FOOTER = """
---

**关键词**：{keywords}

"""

SKIP_SLUGS: set[str] = set()  # all topics generated at premium length


def category_deep_dive(topic: dict) -> str:
    cat = topic["category"]
    title = topic["title"].split("：")[0]
    dives = {
        "故障排查": (
            f"在「{title}」这类故障里，运维最容易犯的错误是**跳步骤**：还没确认全国是红是绿，就开始改代码、换服务器、骂运营商。"
            "正确顺序永远是：多节点确认影响面 → 对照测缩小层级（DNS/证书/CDN/源站/应用）→ 针对性修复 → 复测至达标 → 存档。"
            "SpeedCE 的价值在于第一步和第四步：它给你一张当时当地的路况图，而不是你工位上的主观感受。\n\n"
            "另一个常见坑是**只看平均延迟**。某省全红被各省绿点稀释后，平均延迟可能仍「好看」。"
            "所以本文反复强调：先看地图颜色分布，再看通畅率，最后才看延迟数字。\n\n"
        ),
        "VPS线路": (
            f"选购 VPS 时，「{title}」相关决策最终都会落到一张全国三网地图上。"
            "商家测试 IP、论坛晒单、评测文章——都是二手信息。你拿到的是你的 IP、你的业务、你的用户分布。"
            "付款前测、到账后测、晚高峰测、退款期内测——四次测速成本很低，踩坑成本很高。\n\n"
            "HostLoc 上最有用的帖子，几乎都是**带地图截图**的。本文教你成为那种「发帖有据」的买家/站长，"
            "而不是评论区里只会问「这家怎么样」的人。\n\n"
        ),
        "CDN": (
            f"CDN 故障排查的核心是**对照**：同一时刻，同一协议，CDN 加速域名一张图，源站 IP 一张图。"
            "在「{title}」场景下，任何单边结论都不可靠。A 红 B 绿、A 绿 B 红、都红、都绿——四种组合对应四种完全不同的行动清单。\n\n"
            "切量期还要加上**时间维度**：每 10–30 分钟复测，看异常点是随机消散（DNS 缓存）还是固定省份持续（节点/线路）。"
            "很多人切 DNS 后半小时就宣布成功，结果 24 小时后仍有省份投诉——就是没有做 72 小时点检。\n\n"
        ),
        "出海": (
            f"出海业务的测速逻辑与国内相反：**先看全球节点目标国，再看中国节点团队访问**。"
            "「{title}」若只测了中国，等于只验证了团队能不能加班；没验证客户能不能付钱。\n\n"
            "全球绿、中国红在出海场景里常常是**正常现象**（源站在海外）。"
            "但若中国红的同时目标国也红，那就是全球基础设施故障，与「跨境慢」不是一回事——别混淆。\n\n"
        ),
    }
    return dives.get(cat, (
        f"围绕「{title}」，本文把多节点测速从「偶尔用一下」变成「可重复流程」。"
        "每次故障或变更，按同一套步骤操作，结果可截图、可对比、可汇报。\n\n"
    ))


def communication_chapter(topic: dict) -> str:
    t = topic["title"].split("：")[0]
    return f"""## 第四章补充：对外沟通话术（可直接复制）

用户说「打不开」时，专业回复要**有数据、有范围、有下一步**，而不是「我这边正常」。

### 模板 1：全国基本正常，索要信息

> 您好，我们刚用全国多节点检测（SpeedCE）核实：目前 HTTPS 通畅率 {'{'}96%{'}'}，电信/联通/移动主流省份正常。
> 为精准排查，请提供您的**省份、运营商、访问的完整网址**和**报错截图**，我们将针对性复测该省份节点。

### 模板 2：确认区域性故障，已跟进

> 您好，测速显示**{'{'}XX省{'}'}**部分节点异常，与我们监控一致。技术已在处理【DNS/CDN/源站】，预计 {'{'}XX分钟{'}'} 内恢复。恢复后我们会再次全国复测。

### 模板 3：变更窗口期（迁机/切 CDN）

> 您好，我们正在进行【服务器迁移/CDN 切换】，部分地区可能存在 DNS 缓存延迟。测速显示异常节点随时间减少，属正常现象。若 2 小时后仍无法访问，请告知省份运营商。

### 模板 4：面向老板/客户的非技术汇报

> 【{t}】全国测速结果：通畅率 {'{'}XX%{'}'}，异常集中在 {'{'}XX地区{'}'}（附地图）。根因初步定位为 {'{'}XX{'}'}，处置动作 {'{'}XX{'}'}，复测后通畅率 {'{'}XX%{'}'}。

### 模板 5：论坛/社群「求鉴定」

```
主题：【求鉴定】{t} — SpeedCE 三网截图
目标：https://example.com 或 x.x.x.x
协议：HTTPS | 范围：中国节点
电信：通畅率 __%，延迟 __ms [附图]
联通：通畅率 __%，延迟 __ms [附图]
移动：通畅率 __%，延迟 __ms [附图]
问题：移动是否拖后腿？有没有明显区域红点？
```

---

"""


def case_studies_chapter(topic: dict) -> str:
    return f"""### 案例回放 A：以为程序挂了，其实是证书过期

某站长凌晨收到「全站打不开」。开发查日志无异常，老板催换服务器。运维用 SpeedCE：**HTTPS 全国红，HTTP 全国绿**。
结论：证书过期 6 小时。续签后 10 分钟复测转绿，省去一次无谓迁机。

**教训**：HTTPS 与 HTTP 对照测，是证书问题的「一键分型」。

### 案例回放 B：迁机后「就他不行」

迁机后团队都说正常，新疆同事坚持打不开。SpeedCE：**新疆持续红，其他省绿且随时间扩散减少**。
对照测域名指向新 IP 无误，判断为**区域 DNS 缓存顽固** + 当地运营商 TTL 长。指导同事 `ipconfig /flushdns` 并等待，4 小时后新疆转绿。

**教训**：固定省份持续红 ≠ 全国故障；要分区看地图，别全国回滚。

### 案例回放 C：CDN 背锅

用户报 502。源站直连 IP 正常，CDN 域名 sporadic 红。CDN 控制台回源 5xx 飙升——源站 PHP-FPM 池满。
扩容源站后 CDN 域名复测绿。

**教训**：先对照源站与 CDN，再决定找谁；502 不一定是 CDN 的错，也可能是源站扛不住。

---

"""


def scenario_block(
    num: int,
    title: str,
    phenomenon: str,
    steps: list[str],
    map_rows: list[tuple[str, str, str]],
    causes: list[str],
    actions: list[str],
) -> str:
    lines = [f"#### 场景 {num}：{title}\n\n", f"**现象**\n\n{phenomenon}\n\n", "**SpeedCE 测法**\n\n"]
    for i, s in enumerate(steps, 1):
        lines.append(f"{i}. {s}\n")
    lines.append("\n**地图怎么读**\n\n| 地图形态 | 含义 | 处理建议 |\n|----------|------|----------|\n")
    for a, b, c in map_rows:
        lines.append(f"| {a} | {b} | {c} |\n")
    lines.append("\n**可能原因**\n\n")
    for c in causes:
        lines.append(f"- {c}\n")
    lines.append("\n**处理建议**\n\n")
    for a in actions:
        lines.append(f"- {a}\n")
    lines.append(
        "\n**深度解读**：不要仅凭一次测速下结论。若异常随时间减少，偏向 DNS/缓存；"
        "若固定省份持续异常，偏向区域线路或 CDN 节点；若全国同时异常又恢复，查攻击与负载。"
        "将本次截图与上次变更前基线对比，能判断是「新问题」还是「老毛病复发」。\n"
    )
    lines.append("\n---\n\n")
    return "".join(lines)


def faq_block(pairs: list[tuple[str, str]]) -> str:
    lines = ["### 第十章：FAQ 精选（实战版）\n\n"]
    for q, a in pairs:
        lines.append(f"**Q：{q}**  \nA：{a}\n\n")
    return "".join(lines)


def appendix_card(protocol: str, scope: str, extra_lines: list[str]) -> str:
    lines = [
        "### 附录：SpeedCE 快速参考卡\n\n",
        "```\n",
        "┌─────────────────────────────────────────────────┐\n",
        "│  SpeedCE 快速参考                                │\n",
        "├─────────────────────────────────────────────────┤\n",
        "│  官网    https://www.speedce.com                 │\n",
        "│  中文    https://speedce.com/?lang=zh-CN         │\n",
        "│  邮箱    speedceads@gmail.com                    │\n",
        "├─────────────────────────────────────────────────┤\n",
        f"│  推荐协议    {protocol:<30}│\n",
        f"│  推荐范围    {scope:<30}│\n",
    ]
    for line in extra_lines:
        lines.append(f"│  {line:<47}│\n")
    lines.append("├─────────────────────────────────────────────────┤\n")
    lines.append("│  地图绿色=通畅  红色=异常  先看范围再看运营商   │\n")
    lines.append("└─────────────────────────────────────────────────┘\n```\n")
    return "".join(lines)


# ── Topic registry: 120 premium articles ──────────────────────────────

def build_topics() -> list[dict]:
    """Return list of topic dicts with slug, title, category, keywords, hook, terms, protocol, scope."""
    raw = []

    def add(cat, slug, title, keywords, hook, terms, protocol="HTTPS", scope="中国节点"):
        raw.append({
            "slug": slug, "title": title, "category": cat, "keywords": keywords,
            "hook": hook, "terms": terms, "protocol": protocol, "scope": scope,
        })

    # ── 原手工精品（现统一按长篇规格生成）──
    add("VPS线路", "vps-line-verification-guide",
        "买 VPS 前必看：用全国三网地图验线路，识破 CN2 / 精品网宣传（SpeedCE 实操）",
        "VPS测速,CN2 GIA验证,三网测速,HostLoc验机,SpeedCE",
        "在 HostLoc 群里，买家说「我 ping 才 28ms」、卖家说「三网直连」——一周后移动用户开始骂街。"
        "样本量只有 1，且样本是你自己。全国三网地图才是验机的唯一靠谱标准。",
        [("CN2 GIA", "电信精品网", "电信地图必看"),
         ("CMI", "移动优化", "移动地图一票否决"),
         ("BGP", "多线接入", "三网应均衡"),
         ("禁 Ping", "ICMP 被屏蔽", "改 HTTPS 测")],
        "HTTPS+PING", "中国节点")

    add("CDN", "cdn-deployment-speed-test-guide",
        "CDN 接入全攻略：切量前、切量中、故障时，多节点测速验收怎么做",
        "CDN测速,CDN验收,回源检测,切量,SpeedCE",
        "上了 CDN 反而有人打不开？问题通常不在「CDN 有没有开」，而在验收方法不对。"
        "对照测速：CDN 域名 vs 源站，是 CDN 运维的黄金法则。",
        [("回源", "边缘到源站", "502 先查"),
         ("缓存", "边缘存储", "刷新后复测"),
         ("切量", "DNS 变更", "72h 点检"),
         ("证书", "边缘证书", "与源站分别验收")])

    add("出海", "global-deployment-checklist",
        "网站出海测速验收手册：从中国节点到全球节点的完整检查流程",
        "网站出海,全球测速,国际化,SpeedCE,全球节点",
        "你在上海打开 .com 秒开，德国客户说转圈——测速视角错了。"
        "出海要看目标市场所在地的远端节点，中国节点与全球节点双视图缺一不可。",
        [("目标市场", "用户所在国", "全球节点重点"),
         ("双视图", "中国+全球", "一页切换"),
         ("通畅率", "成功比例", "优先于延迟"),
         ("跨境", "回国链路", "国内慢可能正常")],
        "HTTPS", "中国节点+全球节点")

    # ── A 故障排查 25 ──
    add("故障排查", "dns-troubleshooting-guide",
        "DNS 解析故障完全指南：迁机、换 CDN 后「部分地区打不开」怎么查",
        "DNS故障,域名解析,迁机,多节点测速,SpeedCE",
        "改完 DNS 你这边秒生效，新疆同事说还是旧 IP——这不是他电脑坏了，是解析链路在不同地理位置、不同运营商上不同步。"
        "DNS 问题占「部分地区打不开」工单的一半以上，却最容易被误判成「用户网络不好」。",
        [("A 记录", "域名指向 IPv4", "测域名而非臆测 IP"),
         ("CNAME", "域名指向另一个域名", "CDN 接入后必测 CNAME 链"),
         ("TTL", "缓存存活时间", "迁机前调低到 300s"),
         ("分线路解析", "同一域名国内外不同 IP", "中国/全球节点分别测")])

    add("故障排查", "ssl-certificate-troubleshooting",
        "SSL 证书过期与配置错误：用户报「连接不安全」时 10 分钟定位手册",
        "SSL,HTTPS,证书过期,SpeedCE,网站安全",
        "证书问题最折磨人：你浏览器能开，用户大面积报「您的连接不是私密连接」。"
        "本地 HSTS 缓存、你刚点过的「继续访问」、测试环境白名单——都会骗过你。",
        [("SAN", "证书覆盖的域名列表", "api 子域是否在 SAN 内"),
         ("Let's Encrypt", "免费 90 天证书", "自动续签失败要告警"),
         ("SNI", "多证书同 IP 时按域名选证", "海外节点 SNI 错误会红"),
         ("证书链", "中间证书缺失", "HTTPS 红 HTTP 绿时优先查")])

    add("故障排查", "nginx-reverse-proxy-troubleshooting",
        "Nginx 反向代理故障排查：主站绿、API 红的 8 种典型配置错误",
        "Nginx,反向代理,502,子域名,SpeedCE",
        "Nginx 是无数站点的入口，一行 server_name 写错、一个 proxy_pass 漏配，"
        "表现就是「首页能开、接口全挂」。开发 Postman 本地通，全国用户不通。",
        [("server_name", "匹配的域名", "每个对外域名单独 server 块"),
         ("proxy_pass", "反向代理上游", "末尾斜杠影响 URI"),
         ("upstream", "后端池", "一台后端挂了可能拖全局"),
         ("ssl_certificate", "证书路径", "每个 HTTPS server 块都要配对")])

    add("故障排查", "website-migration-guide",
        "网站迁机完整手册：DNS、源站、CDN 切换的 72 小时测速验收节奏",
        "网站迁机,DNS,服务器迁移,SpeedCE,验收",
        "迁机是站长最紧张的变更之一。你 SSH 上新机器一切正常，"
        "但 DNS 全球生效要时间，CDN 可能还指着旧源站——多节点测速是迁机验收的「客观公证人」。",
        [("TTL", "决定各地缓存多久", "迁机前 48h 调到 300"),
         ("灰度切量", "先切部分流量", "异常节点应随时间减少"),
         ("回源", "CDN 到源站", "迁机后查 CDN 回源 IP"),
         ("双机并行", "新旧同时跑", "对照测两 IP")])

    add("故障排查", "intermittent-fault-diagnosis",
        "间歇性网站故障排查：「有时慢有时好」的科学点检方法",
        "间歇故障,网站不稳定,多节点测速,SpeedCE,运维",
        "间歇故障是运维的噩梦：你测的时候永远正常，用户投诉的时候你不在。"
        "单次测速不够，必须固定间隔多次测，看通畅率和延迟的波动曲线。",
        [("抖动", "延迟不稳定", "持续 Ping 补充观察"),
         ("负载峰值", "晚高峰才暴露", "20:00-22:00 必复测"),
         ("DDoS", "攻击时段异常", "全国同时红又恢复"),
         ("连接池", "应用层间歇耗尽", "网络绿但 502")])

    add("故障排查", "subdomain-troubleshooting",
        "子域名故障排查完全指南：主站能开、接口挂了的 8 种独立原因",
        "子域名,API,cdn,DNS,SpeedCE",
        "www.example.com 和 api.example.com 在 DNS、证书、Nginx、CDN 上是四份独立配置。"
        "主站绿不等于子域绿——每个对外子域都该有一张 SpeedCE 地图。",
        [("CNAME 链", "子域指向", "逐层 dig 核对"),
         ("通配符证书", "*.example.com", "不一定覆盖多级"),
         ("CDN 加速域", "按域名单独添加", "只配 www 是最常见坑"),
         ("备案", "子域也需合规", "未备案可能被拦")])

    add("故障排查", "api-availability-guide",
        "API 接口可达性检测指南：Postman 能通、全国用户不通的真相",
        "API,接口监控,后端,HTTPS,SpeedCE",
        "API 故障往往最后才被发现：前端页面缓存还在，App 直接打接口立刻挂。"
        "SpeedCE 从全国节点对 API 域名做 HTTPS 探测，是网络层验收的第一步。",
        [("可达性", "TCP+TLS+HTTP 成功", "SpeedCE 测这层"),
         ("CORS", "浏览器跨域策略", "网络绿仍可能 CORS 红"),
         ("鉴权", "Token/签名", "测速不带业务 Header"),
         ("Geo 限制", "地域封禁", "全球/中国对照看")])

    add("故障排查", "http-https-redirect-issues",
        "HTTP 与 HTTPS 跳转故障：强制跳转、循环重定向、混合内容排查",
        "HTTPS,301跳转,混合内容,SSL,SpeedCE",
        "301 配成循环、http 和 https 分别指向不同机器、页面资源仍走 http——"
        "用户看到的现象千差万别，但 SpeedCE 的 HTTP/HTTPS 双模式对照能快速缩小范围。",
        [("301/302", "永久/临时跳转", "两次测速对比"),
         ("HSTS", "强制 HTTPS", "浏览器缓存旧策略"),
         ("混合内容", "HTTPS 页含 HTTP 资源", "SpeedCE 不测，浏览器报"),
         ("跳转链", "多次 301", "可能超时")])

    add("故障排查", "firewall-security-group-checklist",
        "云服务器安全组验收：全国地图大面积红时先查这四项",
        "安全组,防火墙,云服务器,443端口,SpeedCE",
        "新手装机最常见：SSH 能登，网站全国红——安全组只放了 22 没放 443。"
        "在怀疑线路、CDN、DNS 之前，先用 SpeedCE 确认端口层到底通不通。",
        [("入站规则", "外部访问端口", "80/443 必放"),
         ("出站规则", "服务器外连", "Let's Encrypt 需出站 443"),
         ("CDN 回源白名单", "只允许 CDN IP", "漏加则 CDN 红"),
         ("iptables", "系统防火墙", "与安全组双重检查")])

    add("故障排查", "502-503-upstream-errors",
        "502/503 与源站过载：CDN 绿、源站红时的判断与修复路径",
        "502,503,源站过载,CDN回源,SpeedCE",
        "502 是「网关收到了坏响应」，503 是「服务暂时不可用」。"
        "用户走 CDN 看到 502，可能是边缘问题，更常见是源站扛不住——对照测一锤定音。",
        [("502 Bad Gateway", "上游无效响应", "查 PHP-FPM/Nginx upstream"),
         ("503 Service Unavailable", "服务过载或维护", "查连接池/限流"),
         ("回源超时", "CDN 等源站太久", "调大 timeout 或扩容"),
         ("健康检查", "负载均衡探活", "探活路径也要绿")])

    add("故障排查", "dns-propagation-slow",
        "域名解析生效慢怎么判断：TTL、运营商缓存与区域 DNS 差异",
        "DNS缓存,TTL,解析生效,SpeedCE,迁机",
        "改 DNS 不是全世界同时变。TTL=86400 时，最坏情况要等 24 小时。"
        "SpeedCE 隔 10 分钟测一次，看异常点是随机消散还是固定省份顽固。",
        [("递归缓存", "运营商本地缓存", "固定省红→缓存"),
         ("权威 DNS", "你的 DNS 服务商", "控制台先确认记录对"),
         ("DNSSEC", "签名验证", "配置错误导致部分解析失败"),
         ("分线路", "国内海外不同记录", "两范围对照")])

    add("故障排查", "regional-access-failure",
        "仅部分地区打不开？用地图精确定位省份、运营商与下一步动作",
        "区域故障,省份,地图测速,SpeedCE,排查",
        "「就新疆不行」「就移动不行」——平均延迟和通畅率帮不上忙，"
        "地图才是区域故障的语言。SpeedCE 中国地图就是为这个问题设计的。",
        [("省级粒度", "各省独立节点", "定位到省"),
         ("运营商", "电信/联通/移动", "三网分离"),
         ("CDN 节点", "边缘覆盖", "某省无节点"),
         ("长途路由", "跨省链路", "西北华南差异")])

    add("故障排查", "mobile-network-issues",
        "移动网络用户访问异常专项：为什么移动投诉往往最多",
        "移动网络,三网测速,运营商,SpeedCE,5G",
        "中国移动用户占比超 50%，但很多「优化线路」只优化电信联通。"
        "不单独测移动地图，等于忽略一半用户。",
        [("CMI", "移动国际出口", "回国线路"),
         ("4G/5G", "无线接入", "与家宽不同"),
         ("DNS", "移动 DNS 服务器", "可能与电信不同"),
         ("WAP 网关", "老移动网络", "少数场景仍影响")])

    add("故障排查", "single-carrier-fault",
        "电信/联通/移动单网故障：一张网全红时的缩小范围排查法",
        "单网故障,电信,联通,移动,SpeedCE",
        "三网分离后只有一张网红——故障范围立刻缩小 66%。"
        "是线路问题、CDN 分网配置、还是运营商 DNS？对照测给出方向。",
        [("单线机房", "只优化一家", "典型单网红"),
         ("DNS 分线路", "按运营商不同 IP", "可能配错一条"),
         ("CDN 分网", "运营商定制", "控制台核对"),
         ("用户样本", "投诉运营商", "与地图互证")])

    add("故障排查", "peak-hour-slowdown",
        "晚高峰网站变慢：下午测正常、晚上测变红的复测策略",
        "晚高峰,网站变慢,线路拥堵,SpeedCE,运维",
        "带宽、国际出口、攻击流量——晚高峰才是照妖镜。"
        "商家挑下午给你看测试 IP，你要在 20:00-22:00 用 SpeedCE 复测。",
        [("国际出口", "晚高峰拥堵", "跨境尤其明显"),
         ("带宽打满", "单机带宽上限", "通畅率仍高但延迟升"),
         ("CC 攻击", "恶意请求", "源站 CPU 升"),
         ("CDN 热点", "缓存击穿", "回源飙升")])

    add("故障排查", "ddos-attack-detection",
        "被攻击期间如何用多节点测速辅助判断影响面",
        "DDoS,攻击,故障排查,SpeedCE,安全",
        "测速不能替代 DDoS 防护，但当全国节点同时变红、延迟飙升，"
        "配合流量图能快速确认是攻击而非配置改错。",
        [("流量型", "带宽打满", "全国延迟升"),
         ("CC 型", "应用层", "可能仍部分绿"),
         ("反射", "放大攻击", "源站带宽"),
         ("恢复验证", "攻击结束", "SpeedCE 复测确认")])

    add("故障排查", "ipv6-troubleshooting",
        "IPv6 双栈站点验收：AAAA 记录、防火墙与 CDN 的完整检查",
        "IPv6,双栈,AAAA,SpeedCE,网站验收",
        "IPv4 全绿不代表 IPv6 正常。双栈站点应对 IPv4、IPv6 目标分别测速。",
        [("AAAA", "IPv6 解析记录", "与 A 记录同步改"),
         ("双栈监听", "Nginx listen [::]:443", "漏配则无 IPv6"),
         ("CDN IPv6", "边缘双栈", "控制台开启"),
         ("防火墙", "ip6tables", "单独放行")])

    add("故障排查", "mixed-content-https",
        "混合内容与 HTTPS：网络层全绿、浏览器仍报不安全的分工排查",
        "混合内容,HTTPS,前端安全,SpeedCE,SSL",
        "SpeedCE 测站点可达性；混合内容是页面里引用了 http:// 资源。"
        "两者分工明确，别在网络层浪费时间。",
        [("主动混合", "script/img http", "浏览器控制台查"),
         ("被动混合", "css 中 url", "较难发现"),
         ("升级策略", "upgrade-insecure-requests", "Header 修复"),
         ("第三方", "统计/广告脚本", "常是元凶")])

    add("故障排查", "cors-vs-network-testing",
        "CORS 报错与网络不通：开发者必分的两层问题",
        "CORS,跨域,API,前端,SpeedCE",
        "地图全绿 + 浏览器报 CORS——恭喜，网络通了，是服务端 Header 没配。"
        "先 SpeedCE 排除网络，再查 Access-Control-Allow-Origin。",
        [("预检 OPTIONS", "复杂请求先发", "可能 OPTIONS 未配"),
         ("Credentials", "带 Cookie 跨域", "规则更严"),
         ("通配符", "* 与凭证冲突", "需指定源"),
         ("代理", "开发环境 proxy", "生产无 proxy 才暴露")])

    add("故障排查", "wechat-qq-access-guide",
        "微信/QQ 打不开先测什么：网络层与合规层的标准分工",
        "微信拦截,QQ,网站合规,备案,SpeedCE",
        "浏览器能开、微信不能开——不一定是服务器问题。"
        "SpeedCE 先排除网络层；拦截/备案/内容用 BOCE 等专项工具。",
        [("网络层", "HTTP/HTTPS 可达", "SpeedCE 负责"),
         ("拦截层", "微信 UA 策略", "专项工具"),
         ("备案", "ICP 未备", "合规问题"),
         ("内容", "违规被标记", "与测速无关")])

    add("故障排查", "waf-false-positive-guide",
        "WAF 误拦与测速异常：全国 sporadic 红点是不是被封了",
        "WAF,防火墙,CDN安全,SpeedCE,误拦",
        "WAF、CC 防护、地域封禁——可能只拦部分拨测节点 IP，"
        "表现为地图 sporadic 红而非全省红。",
        [("IP 信誉", "拨测 IP 被误拦", "换时段复测"),
         ("地域规则", "海外封禁", "全球对照"),
         ("UA 规则", "非浏览器 UA", "可能触发"),
         ("频率限制", "短频请求", "表现为间歇红")])

    add("故障排查", "database-not-network-guide",
        "数据库拖垮网站：网络全绿但页面超时的应用层排查",
        "数据库,慢查询,502,应用层,SpeedCE",
        "SpeedCE 绿 + 页面超时——网络没问题，查 MySQL 慢查询、连接池耗尽。"
        "先网络后应用，顺序不能反。",
        [("连接池", "max_connections", "耗尽则 502"),
         ("慢查询", "SQL 拖时间", "TTFB 极高"),
         ("锁等待", "事务阻塞", "间歇超时"),
         ("只读副本", "延迟", "写后读不一致")])

    add("故障排查", "load-balancer-health-check",
        "负载均衡与健康检查：一半节点绿一半红的典型架构问题",
        "负载均衡,健康检查,高可用,SpeedCE,运维",
        "多台后端一台挂——若 DNS 轮询或 LB 配置不当，"
        "用户感受是「有时能开有时不能」。多节点测速 + 多次复测能印证。",
        [("健康检查", "探活路径", "/health 也要 200"),
         ("权重", "流量分配", "坏节点应自动摘除"),
         ("会话保持", "粘性会话", "打到坏节点更惨"),
         ("DNS 轮询", "多 A 记录", "单 IP 挂则 sporadic 红")])

    add("故障排查", "cache-poisoning-stale",
        "缓存脏了怎么办：CDN/浏览器缓存与网络层对照排查",
        "CDN缓存,浏览器缓存,故障排查,SpeedCE",
        "你刚修好服务器，用户还说旧页面——可能是缓存。"
        "SpeedCE 测的是实时网络响应，可带随机 query 或测 API 避缓存。",
        [("CDN 缓存", "边缘旧内容", "刷新缓存后复测"),
         ("浏览器", "强缓存", "与用户沟通清缓存"),
         ("反向代理", "Nginx proxy_cache", "清缓存"),
         ("版本号", "静态资源 hash", "根治方案")])

    add("故障排查", "third-party-script-failure",
        "第三方脚本拖垮页面：主域绿、功能仍异常的边界说明",
        "第三方脚本,CDN,前端,SpeedCE,监控",
        "支付、统计、客服插件走第三方域——主站绿不代表支付能调起。"
        "每个关键第三方域名单独列入 SpeedCE 巡检清单。",
        [("支付网关", "独立域名", "单独测"),
         ("统计", "google/analytics", "可能被墙"),
         ("客服插件", "外部 JS", "加载失败"),
         ("字体 CDN", "fonts 域", "常忽略")])

    # ── B VPS线路 20 ──
    add("VPS线路", "hong-kong-vps-guide",
        "香港 VPS 线路选购与验收完全手册：个人站、电商、API 场景怎么选",
        "香港VPS,CN2,线路测速,SpeedCE,选购",
        "香港是国人最熟悉的机房：延迟低、免备案、带宽价格适中。"
        "但 CN2、CMI、BGP 混杂，商家文案天花乱坠——全国三网地图是唯一靠谱的验货方式。",
        [("CN2 GIA", "电信精品", "电信地图必看"),
         ("CMI", "移动优化", "移动地图必看"),
         ("HKIX", "本地交换", "影响国际"),
         ("被墙风险", "IP 历史", "中国红全球绿要警惕")],
        "HTTPS+PING", "中国节点+全球节点")

    add("VPS线路", "japan-vps-guide",
        "日本 VPS 适合什么业务：东京大阪机房与三网回国实测验收",
        "日本VPS,东京,线路,SpeedCE,测速",
        "日本机便宜、带宽足、流媒体友好，但回国线路质量参差。"
        "付款前用 SpeedCE 测商家 IP，移动地图是一票否决项。",
        [("NTT", "日本骨干", "国际段"),
         ("软银", "另一骨干", "路由不同"),
         ("回国优化", "商家自称", "用地图验证"),
         ("晚高峰", "国际拥堵", "必复测")],
        "PING+HTTPS", "中国节点")

    add("VPS线路", "us-vps-china-access",
        "美国 VPS 三网回国测评完全手册：西海岸机房怎么验、移动用户怎么办",
        "美国VPS,回国线路,三网,SpeedCE,测速",
        "美国机头便宜大碗，但回国链路长。电信可能尚可，移动常常是灾难。"
        "不要信「洛杉矶 150ms」——那是你本地 ping，不是全国地图。",
        [("西海岸", "LA/SJ", "离中国最近"),
         ("东海岸", "NY", "回国更绕"),
         ("CN2 GIA", "稀有且贵", "地图验证"),
         ("被墙", "IP 污染", "中国全红警惕")],
        "PING+HTTPS", "中国节点+全球节点")

    add("VPS线路", "singapore-vps-guide",
        "新加坡 VPS 验收指南：东南亚枢纽与回国双视角测速",
        "新加坡VPS,东南亚,线路,SpeedCE",
        "新加坡是亚太枢纽，回国、走东南亚都绕这里。"
        "双视图测速：中国节点看回国，全球节点看东南亚覆盖。",
        [("SGIX", "本地交换", "东南亚互联"),
         ("回国", "中继质量", "中国地图"),
         ("带宽", "国际便宜", "注意流量价"),
         ("流媒体", "解锁", "SpeedCE 不测")])

    add("VPS线路", "cn2-gt-vs-gia",
        "CN2 GT 与 CN2 GIA 完全对比：商家话术背后的测速验证法",
        "CN2 GT,CN2 GIA,VPS,线路,SpeedCE",
        "差两个字母，体验差一个档次。GT 晚高峰可能堵，GIA 贵但稳。"
        "别信文案，信三网地图 + 晚高峰复测。",
        [("GT", "普通 CN2", "性价比"),
         ("GIA", "精品 CN2", "延迟稳"),
         ("163", "电信普通骨干", "对比基线"),
         ("移动", "往往都不优化", "移动地图决定")])

    add("VPS线路", "bgp-line-verification",
        "BGP 线路真假辨别：三网均衡才是真 BGP 的验收标准",
        "BGP,VPS,三网,线路测速,SpeedCE",
        "真 BGP：电信、联通、移动都能用。假 BGP：电信绿、移动红。"
        "SpeedCE 三网分离是照妖镜。",
        [("多线接入", "机房能力", "非文案"),
         ("均衡", "三网延迟差小", "验收标准"),
         ("绕路", "假 BGP", "某网全红"),
         ("价格", "真 BGP 更贵", "便宜要警惕")])

    add("VPS线路", "cmi-mobile-line-guide",
        "移动优化 CMI 线路验收：移动用户占比过半时代的一票否决项",
        "CMI,移动线路,VPS,SpeedCE,三网",
        "不单独看移动地图，等于放弃一半用户。"
        "CMI、CMIN2 是否真优化，地图说了算。",
        [("CMI", "移动国际", "移动筛选"),
         ("西北", "移动弱区", "重点看"),
         ("5G", "无线用户", "与家宽不同"),
         ("对比", "电信联通", "均衡才理想")])

    add("VPS线路", "vps-refund-period-checklist",
        "VPS 7 天退款期验机完全清单：截图、三网、晚高峰证据链",
        "VPS退款,验机,证据,SpeedCE,HostLoc",
        "退款要有证据：三网截图 + 通畅率数字 + 晚高峰对比。"
        "比论坛吵架「我觉得慢」强一百倍。",
        [("测试 IP", "商家提供", "到账后对比"),
         ("缩水", "正式 IP 变差", "对照测"),
         ("带宽", "虚标", "测速不测带宽"),
         ("丢包", "晚高峰", "多次测")])

    add("VPS线路", "cloud-security-group-vps",
        "云服务器到手第一步：安全组与防火墙验收再谈线路",
        "安全组,VPS,云服务器,验收,SpeedCE",
        "全国红先别退机——可能是 443 没开。"
        "SpeedCE HTTPS 红 + SSH 能登 = 安全组问题。",
        [("轻量云", "默认规则", "各厂商不同"),
         ("ICMP", "禁 Ping", "改 HTTPS 测"),
         ("IPv6", "第二套规则", "别漏"),
         ("CDN 回源", "源站白名单", "迁 CDN 后查")])

    add("VPS线路", "ping-blocked-not-bad",
        "禁 Ping 不等于线路差：PING 红 HTTPS 绿的正确解读与验机调整",
        "禁Ping,ICMP,VPS,测速,SpeedCE",
        "新手见 Ping 超时就慌。云厂商默认禁 ICMP 是常态。"
        "验机标准改成 HTTPS 通畅率 ≥ 90%。",
        [("ICMP", "网络层", "可被禁"),
         ("TCP 443", "Web 层", "真实建站"),
         ("误导", "Ping 判断线路", "常见误区"),
         ("商家", "用 Ping 宣传", "要求 HTTPS 数据")])

    add("VPS线路", "off-peak-vs-peak-vps",
        "VPS 下午测与晚高峰测：为什么优质线路必须测两次",
        "晚高峰,VPS,线路,复测,SpeedCE",
        "商家测试 IP 在下午往往最美。你要在晚高峰复测，"
        "看通畅率和延迟是否大幅恶化。",
        [("国际出口", "拥堵时段", "20-22点"),
         ("GT", "晚高峰劣化", "尤其明显"),
         ("GIA", "相对稳定", "也要复测"),
         ("记录", "两次截图", "对比发帖")])

    add("VPS线路", "home-broadband-vs-datacenter",
        "家宽测速 vs 全国节点：为什么你 Ping 快不代表用户快",
        "测速偏见,家宽,VPS,SpeedCE,方法论",
        "同城家宽 ping 同机房 VPS，延迟虚低。"
        "全国节点才是用户视角——这是测速方法论第一课。",
        [("地理偏见", "单点样本", "多节点解决"),
         ("家宽运营商", "仅一家", "不代表全国"),
         ("机房内", "curl localhost", "无意义"),
         ("正确姿势", "SpeedCE 中国", "全国地图")])

    add("VPS线路", "vps-with-cdn-comparison",
        "VPS 套 CDN 前后地图对比：该不该上 CDN 的数据决策",
        "VPS,CDN,对比,加速,SpeedCE",
        "源站地图与 CDN 地图并排：加速有没有用、移动有没有改善，"
        "一张对比图说服自己。",
        [("源站", "真实质量", "先测"),
         ("CDN", "边缘加速", "后测"),
         ("移动", "改善最大", "常是 CDN 价值"),
         ("回源", "带宽成本", "别忽视")])

    add("VPS线路", "used-ip-segment-check",
        "二手 IP 段购买前避雷：被墙、被标记 IP 的全国地图特征",
        "IP被墙,二手IP,VPS,SpeedCE,避雷",
        "便宜 IP 可能有前科。典型特征：全球绿、中国红。"
        "付款前 SpeedCE 中国节点测一遍。",
        [("被墙", "GFW", "中国红"),
         ("黑名单", "邮件/SEO", "需另查"),
         ("段内差异", "同段不同命", "测你的 IP"),
         ("换 IP", "商家政策", "不满意就换")])

    add("VPS线路", "datacenter-failover-verify",
        "机房故障换机后应急验证：24 小时 SpeedCE 点检 SOP",
        "机房故障,迁移,应急,SpeedCE,验证",
        "故障迁移争分夺秒，但上线前 5 分钟全国点检能避免二次事故。",
        [("新 IP", "立即测", "全国通畅"),
         ("DNS", "同步改", "72h 复测"),
         ("通知", "用户/客户", "附地图"),
         ("回滚", "预案", "旧机保留")])

    add("VPS线路", "europe-vps-china-guide",
        "欧洲 VPS 回国线路验收：德法荷机房对国内用户的真实体验",
        "欧洲VPS,回国,线路,SpeedCE,测速",
        "欧洲机对欧美用户友好，回国往往绕路。"
        "若国内团队要访问，中国地图必看。",
        [("法兰克福", "欧洲枢纽", "回国路由"),
         ("绕美", "常见路径", "延迟高"),
         ("外贸", "客户在欧洲", "全球绿即可"),
         ("双用途", "欧+中团队", "两地图都要")])

    add("VPS线路", "korea-vps-guide",
        "韩国 VPS 线路测评：离中国近不等于三网都好",
        "韩国VPS,线路,测速,SpeedCE",
        "韩国物理距离近，但线路质量取决于出口优化。"
        "移动地图仍是关键。",
        [("SK/KT", "韩国运营商", "国际出口"),
         ("游戏", "低延迟需求", "PING 为主"),
         ("移动", "回国", "单独看"),
         ("晚高峰", "复测", "必做")])

    add("VPS线路", "taiwan-vps-guide",
        "台湾 VPS 验收要点：延迟优势与线路宣传核实",
        "台湾VPS,线路,SpeedCE,测速",
        "台湾延迟有优势，但「直连」二字要地图验证。",
        [("海峡路由", "运营商差异", "三网分离"),
         ("带宽", "价格", "注意流量"),
         ("合规", "用途", "自行把握"),
         ("解锁", "流媒体", "另测")])

    add("VPS线路", "budget-vps-trap-guide",
        "超低价 VPS 陷阱：地图验收能看出的 6 个危险信号",
        "低价VPS,陷阱,验机,SpeedCE,避雷",
        "年付几十块的机器，不是不能用，但要靠地图知道代价在哪。",
        [("超售", "邻居吵", "延迟抖动"),
         ("线路", "无优化", "移动大红"),
         ("IP", "被墙", "中国红"),
         ("带宽", "峰值虚标", "晚高峰劣化")])

    add("VPS线路", "dedicated-vs-vps-line",
        "独立服务器与 VPS 线路验收差异：IP 段、邻居与测速注意点",
        "独立服务器,VPS,线路,SpeedCE,测速",
        "独服 IP 干净、无邻居干扰，但线路仍取决于机房上游。"
        "验收流程与 VPS 相同：三网地图。",
        [("独服", "资源独占", "稳定性"),
         ("IP 段", "更干净", "仍要测墙"),
         ("线路", "同机房同线", "与 VPS 可比"),
         ("价格", "更高", "验收更严")])

    # Continue with CDN, 出海, 行业, 方法论, 对比, 进阶...
    # For brevity in code, remaining topics use category defaults + title

    extra_titles = [
        ("CDN", "cloudflare-china-access", "Cloudflare 橙云开启后国内访问完整验收手册", "Cloudflare,CDN,国内,SpeedCE"),
        ("CDN", "aliyun-cdn-acceptance", "阿里云 CDN 接入验收完全指南：回源、证书、预热与三网", "阿里云CDN,验收,SpeedCE"),
        ("CDN", "tencent-cdn-acceptance", "腾讯云 CDN 接入验收：静态加速与全站加速差异及测速要点", "腾讯云CDN,全站加速,SpeedCE"),
        ("CDN", "cdn-cache-vs-speed-test", "CDN 缓存与拨测的关系：为什么第一次慢、刷新后又快", "CDN缓存,测速,SpeedCE"),
        ("CDN", "cdn-origin-failure", "CDN 回源失败完全排查：边缘节点、超时与源站对照", "CDN回源,502,SpeedCE"),
        ("CDN", "multi-cdn-comparison", "多家 CDN 试用期地图对比选型：同域不同商的科学方法", "CDN对比,选型,SpeedCE"),
        ("CDN", "static-cdn-split", "静态资源 CDN 分离验收：js/css 域与主站的独立测速清单", "静态CDN,前端,SpeedCE"),
        ("CDN", "dcdn-vs-cdn", "全站加速 DCDN 与普通 CDN：验收标准与 SpeedCE 对照测法", "DCDN,CDN,动态加速,SpeedCE"),
        ("CDN", "cdn-cert-vs-origin", "CDN 证书与源站证书：两边都要绿的完整验收流程", "CDN证书,SSL,SpeedCE"),
        ("CDN", "overseas-cdn-china-pack", "海外 CDN 中国加速包验收：全球绿、国内慢时怎么办", "海外CDN,中国加速,SpeedCE"),
        ("CDN", "cdn-cutover-72h", "CDN 切量 72 小时监控手册：从 T+0 到 T+72 每小时做什么", "CDN切量,DNS,监控,SpeedCE"),
        ("CDN", "free-cdn-enough", "免费 CDN 够用吗：用全国地图数据做个人站决策", "免费CDN,Cloudflare,SpeedCE"),
        ("CDN", "huawei-baidu-cdn-guide", "华为云/百度云 CDN 验收要点与三网地图标准", "华为云,百度云,CDN,SpeedCE"),
        ("CDN", "cdn-websocket-stream", "CDN 加速 WebSocket/直播流的可达性验收边界", "WebSocket,直播,CDN,SpeedCE"),
        ("CDN", "edge-function-troubleshoot", "边缘函数/Workers 故障：主域绿、规则不生效的排查", "边缘计算,CDN,Cloudflare,SpeedCE"),
        ("出海", "saas-global-launch", "出海 SaaS 全球上线验收：目标市场通畅率达标完全手册", "出海SaaS,全球测速,SpeedCE"),
        ("出海", "cross-border-ecommerce", "外贸独立站测速完全指南：Shopify/WooCommerce 与大促前验收", "外贸,独立站,跨境电商,SpeedCE"),
        ("出海", "europe-us-slow-fix", "欧美用户访问慢完全对策：源站、CDN、机房选址三角决策", "欧美,出海,CDN,SpeedCE"),
        ("出海", "southeast-asia-nodes", "东南亚市场节点验收手册：新马泰印尼菲逐国达标线", "东南亚,出海,节点,SpeedCE"),
        ("出海", "global-team-china-admin", "全球团队访问国内后台：双地图协作与加速方案选型", "全球团队,国内后台,SpeedCE"),
        ("出海", "dual-site-cn-com", "双站点 .cn 与 .com 策略：分域名测速与合规分工", "双站点,域名,备案,SpeedCE"),
        ("出海", "geodns-verification", "GeoDNS 智能解析验证：各地解析到不同 IP 的测速方法", "GeoDNS,智能解析,SpeedCE"),
        ("出海", "cross-border-sale-prep", "跨境电商黑五/圣诞大促前测速备战完全清单", "黑五,跨境电商,大促,SpeedCE"),
        ("出海", "overseas-live-streaming", "海外直播与视频会议节点选型：延迟敏感业务的地图标准", "直播,视频会议,出海,SpeedCE"),
        ("出海", "game-server-global", "游戏出海服务器选址：玩家分布与全球 PING 地图对照", "游戏出海,服务器,SpeedCE"),
        ("出海", "stripe-payment-domain-check", "出海支付域名校验：支付页、回调 URL 的独立测速", "支付,Stripe,出海,SpeedCE"),
        ("出海", "multilingual-site-delivery", "多语言站点全球分发：hreflang 与各地可达性验收", "多语言,出海,SEO,SpeedCE"),
        ("出海", "china-blocked-overseas-ok", "全球绿、中国红：被墙/合规问题的标准判断流程", "被墙,出海,合规,SpeedCE"),
        ("行业", "personal-blog-launch", "个人博客上线完全验收：Hexo/Hugo/WordPress 通用测速清单", "个人博客,上线,SpeedCE"),
        ("行业", "wordpress-troubleshooting", "WordPress 站点故障排查手册：白屏、502 与插件冲突的网络层先行", "WordPress,博客,故障,SpeedCE"),
        ("行业", "ecommerce-sale-prep", "电商 618/双11 大促前多节点测速备战完全手册", "电商,双11,618,SpeedCE"),
        ("行业", "online-education-platform", "在线教育平台开课前三网验收：视频域、直播与 API 清单", "在线教育,直播,SpeedCE"),
        ("行业", "corporate-website-sla", "企业官网可用性 SLA：用通畅率数据向管理层汇报", "企业官网,SLA,SpeedCE"),
        ("行业", "miniprogram-backend-api", "小程序后端 API 全国验收：合法域、备案与移动网络", "小程序,微信,API,SpeedCE"),
        ("行业", "mobile-app-api-domain", "App 接口域名监控：iOS/Android 反馈不一致的网络层排查", "App,API,移动,SpeedCE"),
        ("行业", "game-private-server-ping", "游戏联机服务器社群运营：用全国 PING 地图建立信任", "游戏服务器,联机,SpeedCE"),
        ("行业", "forum-community-site", "论坛社区全国可达性：Discuz/Flarum 三网验收", "论坛,社区,SpeedCE"),
        ("行业", "download-site-bandwidth", "下载站可达性与带宽：拨测与下载测速的分工", "下载站,带宽,SpeedCE"),
        ("行业", "government-site-standard", "政府/事业单位网站：全国通畅与 IPv6 双栈验收标准", "政府网站,IPv6,SpeedCE"),
        ("行业", "fintech-medical-compliance", "金融/医疗网站网络层基线：HTTPS、证书与多活验收", "金融,医疗,合规,SpeedCE"),
        ("行业", "saas-b2b-demo-environment", "B2B SaaS 演示环境：潜在客户地域的地图验收", "B2B,SaaS,演示,SpeedCE"),
        ("行业", "news-media-peak-traffic", "新闻媒体流量峰值：突发报道前的全国点检 SOP", "媒体,流量,峰值,SpeedCE"),
        ("方法论", "how-to-read-speed-map", "如何读懂测速地图：绿/红/灰、延迟、通畅率的完全解读", "测速地图,教程,SpeedCE"),
        ("方法论", "tri-network-method", "三网分离检测法完全手册：电信、联通、移动为何必须分开测", "三网测速,电信,联通,移动,SpeedCE"),
        ("方法论", "ab-comparison-method", "A/B 对照测速法：CDN vs 源站、迁机前后、竞品的系统方法", "对照测速,方法论,SpeedCE"),
        ("方法论", "screenshot-archive-sop", "测速截图存档规范：工单、论坛、事故报告的配图标准", "截图,运维文档,SpeedCE"),
        ("方法论", "customer-support-scripts", "客服工单测速话术大全：20+ 专业回复「打不开」模板", "客服话术,工单,SpeedCE"),
        ("方法论", "pre-launch-30-checklist", "网站上线前 30 项检查清单：含 8 项多节点测速必做项", "上线清单,验收,SpeedCE"),
        ("方法论", "monthly-inspection-sop", "月度网站巡检 SOP：个人站 15 分钟、企业站 1 小时版", "月度巡检,SOP,SpeedCE"),
        ("方法论", "quarterly-infra-review", "季度基础设施体检：地图对比、趋势退化与升级决策", "季度体检,基础设施,SpeedCE"),
        ("方法论", "protocol-selection-guide", "PING / HTTP / HTTPS 协议选择完全指南：一次选对少绕弯路", "PING,HTTPS,协议,SpeedCE"),
        ("方法论", "speedtest-vs-pagespeed", "网络拨测与 PageSpeed 分工：通不通 vs 快不快的决策顺序", "PageSpeed,网络测速,SpeedCE"),
        ("方法论", "speedtest-vs-uptime", "拨测快照 vs 7×24 监控：SpeedCE 在运维体系中的位置", "Uptime,监控,拨测,SpeedCE"),
        ("方法论", "speedce-itdog-combo", "SpeedCE + ITDOG 黄金组合：地图巡检与持续 Ping 的协作手册", "SpeedCE,ITDOG,工具组合"),
        ("方法论", "speedce-boce-combo", "SpeedCE + BOCE 协作：网络层排除后的合规与拦截检测", "SpeedCE,BOCE,工具组合"),
        ("方法论", "free-speedtest-tools-2026", "2026 免费测速工具决策树：按场景选 SpeedCE/ITDOG/BOCE", "免费测速,工具推荐,2026"),
        ("方法论", "incident-report-speed-data", "事故报告中的测速数据：运维复盘的专业写法与模板", "事故报告,复盘,SpeedCE"),
        ("方法论", "on-call-first-5-minutes", "On-Call 前 5 分钟：收到告警后 SpeedCE 怎么测", "OnCall,告警,应急,SpeedCE"),
        ("对比", "speedce-vs-itdog", "SpeedCE vs ITDOG 完全对比：场景、优缺点与搭配策略", "SpeedCE,ITDOG,对比"),
        ("对比", "speedce-vs-boce", "SpeedCE vs BOCE 完全对比：轻量地图与全能运维的边界", "SpeedCE,BOCE,对比"),
        ("对比", "map-vs-table-tools", "地图派 vs 表格派测速工具：排障效率的实测对比", "测速工具,地图,对比"),
        ("对比", "top5-free-speedtest-2026", "2026 个人站长免费测速 TOP5 深度评测与收藏建议", "免费测速,TOP5,2026,SpeedCE"),
        ("对比", "ping-pe-use-cases", "Ping.pe 完全使用手册：与 SpeedCE 的全球/中国互补策略", "Ping.pe,全球Ping,SpeedCE"),
        ("对比", "pagespeed-vs-network", "PageSpeed Insights 与网络拨测：站长必须弄清的分工边界", "PageSpeed,网络测速"),
        ("对比", "monitoring-vs-probing", "监控平台 vs 拨测工具：7×24 告警与第一现场的关系", "监控,拨测,运维"),
        ("对比", "developer-bookmark-list", "开发者 2026 检测书签栏：12 个链接应对 90% 网络故障", "开发者,书签,工具,SpeedCE"),
        ("对比", "17ce-vs-speedce", "17CE vs SpeedCE：老牌表格派与新锐地图派实战对比", "17CE,SpeedCE,对比"),
        ("对比", "vsping-vs-speedce", "VSPING vs SpeedCE：污染检测与网络可达性的配合", "VSPING,SpeedCE,对比"),
        ("进阶", "subdomain-inventory-method", "多子域清单巡检法：一张表管理所有对外域名的月度测速", "子域名,巡检,清单,SpeedCE"),
        ("进阶", "competitor-benchmark", "竞品站点对标测速：同赛道地图对比说服管理层升级", "竞品,对标,SpeedCE"),
        ("进阶", "migration-before-after-report", "迁机前后对比汇报模板：给老板和客户看的双地图 PPT", "迁机,汇报,SpeedCE"),
        ("进阶", "icp-filing-launch-check", "ICP 备案通过后全国可达性验收：解析、证书与合规", "ICP备案,上线,SpeedCE"),
        ("进阶", "new-domain-cold-start", "新域名冷启动 72 小时：注册、解析、证书与地图验收节奏", "新域名,DNS,SpeedCE"),
        ("进阶", "spring-festival-traffic", "春节流量保障：移动暴增前的全国三网点检手册", "春节,流量,移动,SpeedCE"),
        ("进阶", "double11-618-prep", "双11/618 大促测速时间表：T-7 到 T+0 的完整节奏", "双11,618,大促,SpeedCE"),
        ("进阶", "ultimate-toolbar-2026", "2026 站长浏览器工具栏终极配置：测速/监控/性能 12 链接", "站长工具,收藏夹,2026,SpeedCE"),
        ("进阶", "xinjiang-tibet-access-guide", "新疆/西藏/西北片区访问优化：地图验收与 CDN 策略", "新疆,西北,区域优化,SpeedCE"),
        ("进阶", "northeast-china-access-guide", "东北三省访问质量验收：寒区线路与 CDN 节点覆盖", "东北,区域,SpeedCE"),
        ("进阶", "guangdong-zhejiang-baseline", "粤浙沪京基准延迟：经济发达省份的地图达标参考线", "广东,浙江,延迟,SpeedCE"),
        ("进阶", "change-management-speedtest", "变更管理中的测速门禁：改 DNS/证书/Nginx 必测制度", "变更管理,测速,运维,SpeedCE"),
        # ── 扩展批次 +75 篇（云厂商/区域/框架/运维）──
        ("故障排查", "mysql-connection-timeout", "数据库连接超时与网站超时：网络绿、页面仍慢的完整分层排查", "MySQL,数据库,超时,SpeedCE"),
        ("故障排查", "redis-connection-issues", "Redis 连接失败对网站的影响：何时该先测网络再查缓存", "Redis,缓存,故障,SpeedCE"),
        ("故障排查", "docker-port-mapping", "Docker 端口映射错误：容器内正常、全国用户打不开的验收", "Docker,端口,容器,SpeedCE"),
        ("故障排查", "k8s-ingress-troubleshoot", "Kubernetes Ingress 故障：集群内正常、公网域名红的排查", "Kubernetes,Ingress,K8s,SpeedCE"),
        ("故障排查", "lets-encrypt-rate-limit", "Let's Encrypt 限流与续签失败：HTTPS 突然全国红的证书向排查", "Let's Encrypt,证书,HTTPS,SpeedCE"),
        ("故障排查", "sni-mismatch-error", "SNI 不匹配错误：多证书同 IP 时部分节点 HTTPS 异常", "SNI,SSL,HTTPS,SpeedCE"),
        ("故障排查", "tls-version-too-low", "TLS 版本过低：老客户端与新安全策略导致的区域性 HTTPS 失败", "TLS,HTTPS,安全,SpeedCE"),
        ("故障排查", "gzip-brotli-compression", "压缩配置与超时：大响应体导致的「能通但极慢」", "Gzip,Brotli,Nginx,SpeedCE"),
        ("VPS线路", "vultr-line-guide", "Vultr 各机房线路验收：按业务选东京/新加坡/洛杉矶", "Vultr,VPS,线路,SpeedCE"),
        ("VPS线路", "bandwagonhost-guide", "搬瓦工 CN2/GIA 套餐验机：经典商家地图验收法", "搬瓦工,BandwagonHost,CN2,SpeedCE"),
        ("VPS线路", "racknerd-dmit-guide", "RackNerd / DMIT 等热门商家：退款期地图验机模板", "RackNerd,DMIT,VPS,SpeedCE"),
        ("VPS线路", "aws-lightsail-china", "AWS Lightsail 对国内访问：全球绿、中国慢的常见形态", "AWS,Lightsail,云服务器,SpeedCE"),
        ("VPS线路", "oracle-cloud-free", "甲骨文云免费 tier 验收：零成本机器的地图标准", "Oracle Cloud,免费VPS,SpeedCE"),
        ("VPS线路", "gcp-azure-china-access", "GCP / Azure 回国访问：企业云对国内团队的地图评估", "GCP,Azure,云,SpeedCE"),
        ("CDN", "aws-cloudfront-china", "AWS CloudFront 中国访问：全球分发与国内体验双验收", "CloudFront,AWS,CDN,SpeedCE"),
        ("CDN", "fastly-cdn-guide", "Fastly CDN 验收：边缘规则与源站对照测速", "Fastly,CDN,边缘,SpeedCE"),
        ("CDN", "bunny-cdn-guide", "Bunny CDN 性价比线路：全球节点地图验收", "BunnyCDN,CDN,SpeedCE"),
        ("CDN", "qiniu-cdn-guide", "七牛云 CDN 接入：国内站长常用方案的测速验收", "七牛云,CDN,SpeedCE"),
        ("CDN", "upyun-cdn-guide", "又拍云 CDN 验收：图片站与静态加速地图标准", "又拍云,CDN,图片站,SpeedCE"),
        ("出海", "shopify-speedtest", "Shopify 店铺全球可达性：主题、支付与应用域的分层测速", "Shopify,外贸,独立站,SpeedCE"),
        ("出海", "woocommerce-global", "WooCommerce 出海验收：插件、支付网关与主域地图清单", "WooCommerce,WordPress,出海,SpeedCE"),
        ("出海", "notion-saas-availability", "Notion 类协作工具自托管：全球团队访问验收", "SaaS,协作,自托管,SpeedCE"),
        ("出海", "api-rate-limit-global", "全球 API 限流与 Geo 封禁：地图绿但仍 403 的边界", "API,限流,出海,SpeedCE"),
        ("出海", "middle-east-africa-nodes", "中东与非洲节点验收：新兴市场的地图达标策略", "中东,非洲,出海,SpeedCE"),
        ("出海", "latin-america-nodes", "拉美节点验收：巴西、墨西哥重点市场地图标准", "拉美,巴西,出海,SpeedCE"),
        ("行业", "hexo-hugo-static-site", "Hexo / Hugo 静态站上线路验收：GitHub Pages 与自建对比", "Hexo,Hugo,静态站,SpeedCE"),
        ("行业", "nextjs-nuxt-ssr-deploy", "Next.js / Nuxt SSR 部署验收：Node 服务与 CDN 分层测速", "Next.js,Nuxt,SSR,SpeedCE"),
        ("行业", "laravel-php-deploy", "Laravel / PHP 站点上线：FPM、Nginx 与全国 HTTPS 验收", "Laravel,PHP,上线,SpeedCE"),
        ("行业", "java-spring-boot-api", "Spring Boot API 全国验收：网关、证书与子域清单", "Spring Boot,Java,API,SpeedCE"),
        ("行业", "python-django-flask", "Django / Flask 部署测速：WSGI 与应用层分工", "Django,Flask,Python,SpeedCE"),
        ("行业", "video-on-demand-site", "点播视频站验收：播放域、CDN 与 API 三域测速", "视频,点播,CDN,SpeedCE"),
        ("行业", "recruitment-careers-site", "招聘官网高峰验收：校招季前的全国点检", "招聘,企业官网,SpeedCE"),
        ("行业", "hospital-appointment-system", "医院预约系统网络基线：高峰与移动用户验收", "医疗,预约,移动,SpeedCE"),
        ("方法论", "oncall-runbook-speedtest", "On-Call Runbook 中的测速章节：告警后 5 分钟 SOP", "OnCall,Runbook,应急,SpeedCE"),
        ("方法论", "postmortem-blameless", "无责复盘中的测速证据：时间线与地图如何写进 Postmortem", "Postmortem,复盘,运维,SpeedCE"),
        ("方法论", "sla-report-monthly", "月度 SLA 报告模板：用通畅率数据汇报老板", "SLA,报告,运维,SpeedCE"),
        ("方法论", "vendor-ticket-evidence", "给云厂商/CDN 工单附证据：截图规范与描述模板", "工单,云厂商,CDN,SpeedCE"),
        ("方法论", "team-onboarding-speedce", "新运维入职第一天：SpeedCE 与工具链培训手册", "入职,培训,运维,SpeedCE"),
        ("对比", "cesu-vs-speedce", "CESU.ai vs SpeedCE：新兴工具站与地图派实测对比", "CESU,SpeedCE,对比"),
        ("对比", "chinaz-toolkit-review", "站长之家工具生态 vs SpeedCE：Ping/测速/Whois 分工", "站长之家,工具,SpeedCE"),
        ("对比", "aliyun-boce-vs-speedce", "阿里云云拨测 vs SpeedCE：同云用户如何搭配", "阿里云,拨测,SpeedCE"),
        ("进阶", "province-henan-hubei", "河南/湖北中部省份访问优化：地图特征与 CDN 策略", "河南,湖北,区域,SpeedCE"),
        ("进阶", "province-sichuan-chongqing", "川渝地区访问验收：西南节点与线路特征", "四川,重庆,西南,SpeedCE"),
        ("进阶", "province-fujian-taiwan-trade", "闽粤台贸相关站点：东南沿海地图验收要点", "福建,广东,东南,SpeedCE"),
        ("进阶", "province-shandong-hebei", "京津冀鲁访问基线：华北片区地图达标参考", "山东,河北,华北,SpeedCE"),
        ("进阶", "province-yunnan-guizhou", "云贵地区访问：西南边陲地图与移动网络", "云南,贵州,西南,SpeedCE"),
        ("进阶", "hainan-special-zone", "海南自贸相关站点：岛屿地理与访问特征验收", "海南,区域,SpeedCE"),
        ("进阶", "inner-mongolia-northeast", "内蒙古/东北三省：高寒地区线路与冬季高峰", "内蒙古,东北,区域,SpeedCE"),
        ("进阶", "cctv-news-peak", "新闻发布与热点峰值：突发流量前的 30 分钟点检", "新闻,峰值,流量,SpeedCE"),
        ("进阶", "school-start-september", "九月开学季：教育类站点流量保障测速", "开学季,教育,流量,SpeedCE"),
        ("进阶", "national-holiday-golden-week", "国庆黄金周流量：全国移动用户暴增前点检", "国庆,黄金周,流量,SpeedCE"),
        ("进阶", "year-end-summary-report", "年终基础设施报告：12 个月地图存档如何汇总", "年终,报告,运维,SpeedCE"),
        ("故障排查", "websocket-wss-check", "WebSocket / WSS 长连接：SpeedCE HTTPS 与实时业务边界", "WebSocket,WSS,实时,SpeedCE"),
        ("故障排查", "grpc-gateway-check", "gRPC / HTTP2 网关：REST 可达与 gRPC 故障分工", "gRPC,HTTP2,API,SpeedCE"),
        ("故障排查", "oauth-callback-domain", "OAuth 回调域名校验：登录失败的网络层先行排查", "OAuth,登录,回调,SpeedCE"),
        ("故障排查", "payment-callback-url", "支付回调 URL 可达性：全国节点对回调域的验收", "支付,回调,电商,SpeedCE"),
        ("故障排查", "email-link-tracking", "邮件内链接追踪域：营销邮件点击失败的网络排查", "邮件,营销,域名,SpeedCE"),
        ("VPS线路", "colocation-vs-cloud", "托管机房 vs 公有云：同一业务选型后的地图验收差异", "托管,公有云,选型,SpeedCE"),
        ("VPS线路", "bare-metal-dedicated-line", "物理机专线接入：企业专线用户的地图验收", "专线,物理机,企业,SpeedCE"),
        ("CDN", "image-cdn-webp-avif", "图片 CDN 与 WebP/AVIF：静态域全国验收", "图片CDN,WebP,前端,SpeedCE"),
        ("CDN", "font-cdn-google-china", "字体 CDN 与 Google Fonts：国内加载失败的测速分工", "字体,Google Fonts,CDN,SpeedCE"),
        ("出海", "app-store-review-server", "App Store 审核期间服务器：海外审核节点可达性", "App Store,审核,出海,SpeedCE"),
        ("出海", "gdpr-cookie-wall", "GDPR 与 Cookie 墙：欧洲用户访问的网络层基线", "GDPR,欧洲,合规,SpeedCE"),
        ("行业", "discuz-qzone-share", "Discuz 论坛分享链：主站与分享域的分层测速", "Discuz,论坛,分享,SpeedCE"),
        ("行业", "typecho-emlog-blog", "Typecho / Emlog 轻量博客：小站也要做的全国验收", "Typecho,Emlog,博客,SpeedCE"),
        ("行业", "ghost-blog-deploy", "Ghost 博客部署：Headless 与主题域测速", "Ghost,博客,部署,SpeedCE"),
        ("方法论", "regex-domain-inventory", "正则匹配子域发现：漏测域名的自动化清单思路", "子域,清单,自动化,SpeedCE"),
        ("方法论", "calendar-reminder-inspect", "日历提醒巡检：把测速写进 Google Calendar / 飞书", "日历,提醒,巡检,SpeedCE"),
        ("对比", "gtmetrix-vs-speedce", "GTmetrix vs SpeedCE：性能测试与网络拨测分工", "GTmetrix,测速,对比"),
        ("对比", "webpagetest-vs-speedce", "WebPageTest vs SpeedCE：何时用哪个", "WebPageTest,测速,对比"),
        ("进阶", "multi-team-handover", "运维交接文档中的测速基线：离职前必须留下的地图包", "交接,文档,运维,SpeedCE"),
        ("进阶", "acquisition-due-diligence", "收购技术尽调：目标站点全国可达性快速评估", "尽调,收购,评估,SpeedCE"),
        ("进阶", "penetration-test-prep", "渗透测试前网络暴露面：对外域名测速清单", "安全,渗透,域名,SpeedCE"),
        ("进阶", "disaster-recovery-drill", "灾备演练：切换 DR 站点后的全国 SpeedCE 点检", "灾备,演练,DR,SpeedCE"),
        ("进阶", "zero-downtime-deploy", "零停机发布：蓝绿/金丝雀发布中的地图对照", "蓝绿,金丝雀,发布,SpeedCE"),
        ("进阶", "status-page-setup", "Status Page 搭建：测速数据如何支撑公开状态页", "Status Page,监控,SpeedCE"),
        ("进阶", "client-report-quarterly", "给客户季报附地图：B2B 服务商的测速汇报模板", "客户报告,B2B,SpeedCE"),
        ("进阶", "seo-crawl-baidu-google", "百度/Google 爬虫与站长可达性：SEO 视角的测速", "SEO,爬虫,收录,SpeedCE"),
        ("进阶", "affiliate-tracking-domain", "联盟营销追踪域：全国可达对转化链的影响", "联盟营销,追踪,域名,SpeedCE"),
        ("进阶", "short-link-domain-check", "短链域名验收：跳转链路的全国节点测试", "短链,跳转,域名,SpeedCE"),
        ("进阶", "landing-page-campaign", "投放落地页：广告上线前 10 分钟全国点检", "落地页,投放,广告,SpeedCE"),
        ("进阶", "ab-test-traffic-split", "A/B 测试分流域：实验组域名的独立地图验收", "AB测试,分流,SpeedCE"),
    ]

    default_hooks = {
        "CDN": "CDN 让网站更快，也让排障更复杂——源站、边缘、证书、缓存四层交织。对照测速是 CDN 运维的基本功。",
        "出海": "全球化不是加一个英文版就完事。目标市场的通畅率，决定了你能不能在那里做生意。",
        "行业": "不同行业的可用性标准不同，但网络层验收是共性——先保证各地能访问，再谈体验优化。",
        "方法论": "工具会用不难，形成方法论难。本文把多节点测速变成可重复、可存档、可汇报的标准流程。",
        "对比": "没有最好的工具，只有最合适的场景。客观对比帮你建立个人工具栏。",
        "进阶": "进阶技巧不是炫技，是减少重复踩坑——把测速嵌入变更、巡检、大促、汇报全流程。",
    }
    default_terms = {
        "CDN": [("源站", "你的真实服务器", "先测源站"), ("边缘", "CDN 节点", "再测加速域"), ("回源", "边缘到源站", "502 查回源"), ("缓存", "边缘存储", "刷新后复测")],
        "出海": [("目标市场", "用户所在国", "全球节点重点看"), ("跨境", "跨国链路", "延迟常高"), ("合规", "备案/隐私", "与测速分工"), ("双栈", "国内+海外", "两地图")],
        "行业": [("主域", "用户入口", "HTTPS 必测"), ("API 域", "业务接口", "单独测"), ("静态域", "js/css", "CDN 域"), ("监控", "7×24", "与拨测互补")],
        "方法论": [("对照", "A/B 两图", "排障第一原则"), ("三网", "电信联通移动", "分开测"), ("快照", "单次拨测", "变更后必做"), ("趋势", "多次对比", "月度巡检")],
        "对比": [("地图派", "区域直观", "SpeedCE"), ("表格派", "数字精确", "ITDOG 等"), ("全能派", "功能多", "BOCE"), ("性能派", "页面评分", "PageSpeed")],
        "进阶": [("清单", "子域列表", "逐项打勾"), ("存档", "截图命名", "可回溯"), ("门禁", "变更必测", "流程化"), ("对标", "竞品地图", "说服升级")],
    }

    for cat, slug, title, kw in extra_titles:
        if any(t["slug"] == slug for t in raw):
            continue
        hook = default_hooks.get(cat, "多节点测速是现代站长必备技能。") + f" 本文围绕「{title.split('：')[0]}」展开，以 SpeedCE 为实操示例。"
        terms = default_terms.get(cat, [("多节点", "全国各地探测", "SpeedCE"), ("地图", "红绿分布", "看区域"), ("通畅率", "成功比例", "≥95%"), ("对照", "两目标对比", "A/B 测")])
        scope = "中国节点+全球节点" if cat == "出海" else "中国节点"
        add(cat, slug, title, kw, hook, terms, scope=scope)

    return raw


def make_scenarios(topic: dict) -> list[dict]:
    """Generate 8 rich scenarios tailored to topic."""
    cat = topic["category"]
    title_kw = topic["title"].split("：")[0].split("——")[0][:20]
    base_maps = [
        ("全国大面积红", "全局性故障：源站、证书、安全组、DNS 全链路问题", "SSH 查服务；查 443/80；对照源站 IP；修完复测至通畅率≥95%"),
        ("单省或单区域持续红", "区域性：DNS 缓存、CDN 节点缺失、省级线路", "记录省份；对照源站；联系 CDN 查该省节点；隔 10min 复测"),
        ("仅移动红，电信联通绿", "移动线路未优化或单网配置错误", "移动地图截图；考虑 CDN 移动优化或换线路；勿忽视移动用户"),
        ("全球绿、中国红", "跨境访问问题、被墙、国内合规或线路", "全球对照；查备案与墙；考虑国内 CDN 或镜像"),
        ("中国绿、全球红", "源站在国内或 Geo 限制海外", "检查海外解析；上全球 CDN；安全组是否限海外 IP"),
        ("通畅但延迟极高", "能通但体验差：跨境、绕路、未上 CDN", "对照竞品；评估 CDN；PageSpeed 查页面层"),
        ("sporadic 零星红点", "间歇：攻击、负载、WAF 误拦、路由抖动", "每 15min 测 6 次；查 CPU/带宽；查 WAF 日志"),
        ("全国绿但用户仍投诉", "应用层、缓存、拦截、客户端问题", "查业务日志；BOCE 查拦截；让用户提供省+运营商复测"),
    ]
    phenomena_templates = [
        f"用户反馈与「{title_kw}」相关：部分省份、部分运营商或特定时段访问异常，而你本地测试往往正常。",
        f"变更后出现：改 DNS、上 CDN、换证书、迁机、调 Nginx 之后，工单量上升，需要客观验证影响面。",
        f"客服无法复现：用户说打不开，你这边无痕模式正常——典型单点偏见，需要全国多节点视角。",
        f"晚高峰才暴露：下午 SpeedCE 全绿，20:00 后通畅率下降或延迟飙升，怀疑线路拥堵或攻击。",
        f"子域/接口独立故障：主站正常，但 API、静态资源或支付域异常，需单独对目标域名测速。",
        f"出海/跨境场景：国内团队正常，海外客户反馈慢或打不开，或相反。",
        f"新购 VPS/新上 CDN 验收：商家称「三网直连」「全球加速」，需要第三方地图验证。",
        f"间歇性 sporadic：有时正常有时异常，单次测速容易误判，需多次点检留曲线。",
    ]
    steps_base = [
        "打开 https://speedce.com/?lang=zh-CN",
        f"协议选 **{topic['protocol'].split('+')[0]}**（Ping 不通改 HTTPS）",
        f"范围选 **{topic['scope']}**",
        "输入主域名、子域或 IP，点击开始测速",
        "记录通畅、异常、平均延迟四数字",
        "按电信/联通/移动分别筛选，各截图存档",
        "若用 CDN：对加速域名与源站 IP 各测一次对照",
        "异常时隔 10–15 分钟复测，观察是消散还是持续",
    ]
    scenarios = []
    for i in range(8):
        causes = [
            f"与{cat}相关的配置错误或资源瓶颈",
            "DNS 未全球/全国生效或分线路解析错误",
            "HTTPS 证书过期、漏配子域或链不完整",
            "安全组/防火墙未放行 80/443 或 CDN 回源 IP",
            "CDN 回源失败、缓存脏数据或边缘节点故障",
            "单网线路劣化（尤其移动未优化）",
            "源站过载、DDoS 或晚高峰国际出口拥堵",
            "应用层问题（需在网络层排除后继续查）",
        ]
        actions = [
            "保存 SpeedCE 地图截图，标注时间、协议、目标",
            "对照测第二目标（源站/CDN/迁机前后）缩小范围",
            "修复后复测直至通畅率达标",
            "更新内部运维文档与变更记录",
            "向用户/客服提供基于省份运营商的针对性回复",
            "必要时配合 ITDOG 持续 Ping、BOCE 合规检测",
            "长期监控接入 Uptime 类工具",
            "重大变更纳入「变更必测」门禁",
        ]
        scenarios.append({
            "title": phenomena_templates[i].split("：")[0].replace(f"与「{title_kw}」相关", title_kw)[:40],
            "phenomenon": (
                phenomena_templates[i]
                + " 这类问题的共同点是：单点测试无法代表全国用户，必须用 SpeedCE 多节点地图获取客观样本。"
                f"\n\n在「{topic['title'].split('：')[0]}」语境下，还应记录：**变更发生时间点**、**用户省份运营商样本**、**是持续还是间歇**。"
                "三者与地图叠在一起，根因判断会快很多。"
            ),
            "steps": steps_base,
            "map_rows": [base_maps[i % 8], base_maps[(i + 1) % 8], base_maps[(i + 2) % 8], base_maps[(i + 3) % 8]],
            "causes": causes[:5],
            "actions": actions[:6],
        })
    return scenarios


def generate_article(topic: dict) -> str:
    slug = topic["slug"]
    title = topic["title"]
    scenarios = make_scenarios(topic)

    parts = [f"# {title}\n\n", HEADER]
    parts.append(f"## 写在前面\n\n{topic['hook']}\n\n")
    parts.append(category_deep_dive(topic))
    parts.append(
        "做网站的人，几乎都说过：「我这边打开好好的啊。」——然后工单、群里反馈接踵而至。"
        "问题往往不是你眼花，而是**测速方法错了**：单点、单省、单运营商、单时段，都不能代表全国用户。\n\n"
        f"本文是一份围绕「{title.split('：')[0]}」的**可执行长文手册**（建议阅读 15–20 分钟）。"
        "全文以免费工具 SpeedCE 为操作示例，但你学到的排查思路适用于任何多节点测速场景。"
        "建议收藏，故障时按章节对照操作。\n\n"
        "**阅读导航**：第一章建立观念 → 第二章上手 SpeedCE → 第三章八个实战场景（核心）→ "
        "第四章进阶与话术 → 第五章工具链 → 第六章检查清单 → 第七至十章误区/工作流/FAQ。\n\n---\n\n"
    )

    parts.append("## 第一章：先建立正确观念——测速评什么\n\n")
    parts.append("### 1.1 三个层次别混\n\n| 层次 | 回答什么 | SpeedCE 角色 |\n|------|----------|-------------|\n")
    parts.append("| 网络层 | IP/端口通不通 | PING / HTTPS 可达 |\n")
    parts.append("| Web 层 | 网站能否正常响应 | HTTPS 首选 |\n")
    parts.append("| 应用层 | 业务逻辑对不对 | 网络绿后再查日志 |\n\n")
    parts.append("### 1.2 本文关键术语\n\n| 术语 | 含义 | 实操提示 |\n|------|------|----------|\n")
    for term, meaning, tip in topic["terms"]:
        parts.append(f"| {term} | {meaning} | {tip} |\n")
    parts.append("\n### 1.3 三个原则\n\n")
    parts.append("| 原则 | 说明 |\n|------|------|\n")
    parts.append("| **对照测** | CDN 域 vs 源站、迁机前后、改配置前后 |\n")
    parts.append("| **三网分** | 电信、联通、移动各一张图 |\n")
    parts.append("| **多次测** | DNS 生效、晚高峰、间歇故障至少 2–3 次 |\n\n")
    parts.append("### 1.4 PING / HTTP / HTTPS 分别什么时候用\n\n")
    parts.append("| 你想知道 | 选 | 说明 |\n|----------|-----|------|\n")
    parts.append("| IP 通不通 | PING | 很多云禁 Ping，超时改 HTTPS |\n")
    parts.append("| 网站能不能打开 | HTTPS | 生产环境首选 |\n")
    parts.append("| 证书有没有问题 | HTTPS 红 + HTTP 绿 | 高度怀疑证书 |\n")
    parts.append("| 仅 80 端口 | HTTP | 排查跳转与老链接 |\n\n---\n\n")

    parts.append("## 第二章：SpeedCE 标准流程（建议跟着做一遍）\n\n")
    parts.append("打开 https://speedce.com/?lang=zh-CN\n\n")
    parts.append("| 步骤 | 操作 |\n|------|------|\n")
    parts.append(f"| 1 | 选协议：**{topic['protocol'].replace('+', ' / ')}** |\n")
    parts.append(f"| 2 | 选范围：**{topic['scope']}** |\n")
    parts.append("| 3 | 输入域名、子域、IPv4/IPv6 |\n")
    parts.append("| 4 | 开始测速，看地图四态：通畅/异常/检测中/等待 |\n")
    parts.append("| 5 | 记录通畅数、异常数、平均延迟 |\n")
    parts.append("| 6 | 电信/联通/移动筛选各截图 |\n\n")
    parts.append("**四个数字怎么读**：通畅越高越好（建议≥95%）；异常看集中省份；平均延迟结合业务；已跳过可忽略。\n\n---\n\n")

    parts.append(f"## 第三章：八大实战场景——{topic['category']}对号入座\n\n")
    parts.append("以下每个场景统一结构：现象 → SpeedCE 测法 → 地图解读 → 原因 → 处理。\n\n")
    for i, sc in enumerate(scenarios, 1):
        parts.append(scenario_block(i, sc["title"], sc["phenomenon"], sc["steps"], sc["map_rows"], sc["causes"], sc["actions"]))

    parts.append("## 第四章：进阶技巧——让测速数据产生更大价值\n\n")
    advances = [
        ("三网分离存档法", "每月固定一天，电信/联通/移动各截图命名归档。用户说「移动打不开」时翻相册对比是新问题还是老问题。"),
        ("迁机/变更前后对比", "任何重大变更前测一次、变更后测一次。两张地图并排，汇报老板/客户极具说服力。"),
        ("CDN 与源站对照", "加速域名和源站 IP 各测一张。A 红 B 绿找 CDN；A 绿 B 红修源站；都红先源站。"),
        ("竞品对标", "同赛道头部站和自己各测一张。人家全绿你全红——不是用户挑剔，是基础设施落后。"),
        ("子域清单巡检", "列出 www/api/cdn/m/static 等所有对外域，每月 HTTPS+中国节点逐项打勾。"),
    ]
    for j, (name, desc) in enumerate(advances, 1):
        parts.append(f"### 4.{j} {name}\n\n{desc}\n\n")
    parts.append(communication_chapter(topic))
    parts.append("## 第五章：案例回放——三张地图如何避免大坑\n\n")
    parts.append(case_studies_chapter(topic))
    parts.append("## 第六章：巡检节奏与变更门禁\n\n")
    parts.append("#### 每日（有故障时）\n\n收到反馈 → SpeedCE HTTPS+中国节点 → 5 分钟判断全局/局部 → 决定自修/找 CDN/回复用户。\n\n")
    parts.append("#### 每周（无故障）\n\n周一上午巡检主域，对比上周通畅率是否下降。\n\n")
    parts.append("#### 每月\n\n三网分离体检 + 全球抽测 + 子域清单 + 截图归档。\n\n")
    parts.append("#### 每次变更后（必做）\n\n改 DNS、换服务器、上 CDN、续证书、改 Nginx/防火墙 —— **必测**。未测不上线。\n\n---\n\n")

    parts.append("## 第七章：工具链分工——SpeedCE 不是唯一，但是第一现场\n\n")
    parts.append("| 需求 | 推荐 | SpeedCE 角色 |\n|------|------|-------------|\n")
    parts.append("| 快速看全国/全球哪里红 | SpeedCE | **主力** |\n")
    parts.append("| 持续 Ping/TCPing | ITDOG | 互补 |\n")
    parts.append("| 污染/拦截/备案 | BOCE | 互补 |\n")
    parts.append("| 页面性能 CWV | PageSpeed | 互补 |\n")
    parts.append("| 7×24 告警 | UptimeRobot 等 | 互补 |\n\n")
    parts.append("记住：**SpeedCE 回答「各地能不能访问」**；PageSpeed 回答「页面快不快」；监控回答「过去 30 天可用率」。\n\n---\n\n")

    parts.append("## 第八章：为什么推荐 SpeedCE 做第一现场工具\n\n")
    reasons = [
        ("地图比表格适合找区域", "平均 127ms 不告诉你问题在新疆；地图会。"),
        ("中国+全球双视图", "一个页面切换，出海与国内都覆盖。"),
        ("HTTP/HTTPS/PING 一页集成", "排障时思维不断裂。"),
        ("免费免注册", "故障现场争分夺秒。"),
        ("三网筛选", "电信/联通/移动独立地图。"),
        ("支持 IPv4/IPv6", "双栈站点分别验证。"),
    ]
    for k, (r, d) in enumerate(reasons, 1):
        parts.append(f"### 8.{k} {r}\n\n{d}\n\n")
    parts.append("---\n\n")

    parts.append("## 第九章：检查清单（可打印）\n\n```\n")
    checklist = [
        "HTTPS + 中国节点：主域名通畅率 ≥ 95%",
        "电信/联通/移动三网各目测无大面积异常",
        "关键子域（api/cdn/m）单独测过",
        "全球节点（若出海）：目标国通畅率 ≥ 95%",
        "CDN 域名与源站 IP 对照测（若用 CDN）",
        "迁机/改 DNS/换证书后已复测",
        "地图截图已标注时间协议并归档",
        "异常省份已记录并跟进至修复",
    ]
    for item in checklist:
        parts.append(f"□ {item}\n")
    parts.append("```\n\n工具：https://speedce.com/?lang=zh-CN\n\n---\n\n")

    parts.append("## 第十章：常见误区——别再这样测了\n\n")
    myths = [
        ("「我 ping 通了就没问题」", "Ping 只说明 ICMP 可达。Web、证书、WAF 任一环节错，用户仍打不开。"),
        ("「我无痕模式能开，用户也该能开」", "你只代表一条宽带、一个省、一个时段。"),
        ("「测一次就够了」", "DNS 有缓存、网络有抖动、迁机有过渡期。关键变更后至少 3 次。"),
        ("「平均延迟 200ms 太差」", "静态站 200ms 可接受，实时 API 可能不行。结合业务看。"),
        ("「出问题先换服务器」", "先测地图定位：DNS？证书？CDN？源站？换机是最后手段。"),
        ("「测速工具都是骗人的」", "多节点、可重复、可截图对比的拨测仍是业内通用方法。"),
        ("「CDN 开了就一定更快」", "源站慢或回源差时 CDN 可能更慢。对照源站地图。"),
        ("「全国绿就不用看了」", "通畅率 100% 也可能延迟不均。看三网与目标省。"),
    ]
    for m, expl in myths:
        parts.append(f"#### 误区：{m}\n\n{expl}\n\n")
    parts.append("---\n\n")

    parts.append("## 第十一章：真实工作流——从今天起这样用\n\n")
    parts.append("把测速嵌入变更管理：任何上线、迁机、切 CDN、续证书，在工单系统里增加「SpeedCE 截图已附」勾选框。")
    parts.append("半年后你会积累一批地图档案，故障时对比基线，效率翻倍。\n\n---\n\n")

    faqs = [
        ("测速要多久？", "通常 1–3 分钟，视节点数而定。可观察进度条。"),
        ("异常很多是不是网站挂了？", "先看全网还是局部。全网异常查服务器/证书/安全组；局部查区域线路或 DNS。"),
        ("PING 全超时 HTTPS 正常？", "正常，说明禁 Ping。以 HTTPS 为准。"),
        ("私有 IP 能测吗？", "不能。10.x、192.168.x 等会被拒绝。"),
        ("和 BOCE/ITDOG 怎么选？", "日常地图巡检 SpeedCE；持续 Ping 用 ITDOG；污染备案用 BOCE。"),
        ("测速会被封 IP 吗？", "分布式节点合理频率，正常不会。严格 WAF 可能个别节点限流。"),
        ("结果能分享吗？", "可以，截图地图即可，非技术人员也能看懂。"),
        ("变更后多久复测？", "DNS 类每 10–30 分钟一次至 72h；证书/防火墙修完立即复测。"),
        ("通畅率多少算达标？", "国内主站建议 ≥95%；出海目标国 ≥95%；移动无大片红。"),
        ("能否替代监控？", "不能。拨测是快照，7×24 监控与告警仍需 Uptime 等。"),
        ("和实战手册关系？", "本文是专题深潜；通用场景请看已发布《站长多节点测速实战手册》。"),
        ("没有域名只有 IP？", "可以。输入 IPv4/IPv6 直接测，适合 VPS 验机。"),
    ]
    parts.append("## 第十二章：FAQ 精选（实战版）\n\n")
    for q, a in faqs:
        parts.append(f"**Q：{q}**  \nA：{a}\n\n")
    parts.append("---\n\n")

    parts.append("## 第十三章：结语\n\n")
    parts.append(
        f"围绕「{title.split('：')[0]}」，最靠谱的方法始终是从多节点发起真实访问，把结果画在地图上。"
        "SpeedCE 给你实时路况图——哪里通畅、哪里堵塞。方向盘仍在你手里：改 DNS、换 CDN、续证书、扩容。"
        "把 https://speedce.com/?lang=zh-CN 放进书签栏。下次有人说打不开，打开它，选 HTTPS，看地图，用数据服人。\n\n"
    )
    parts.append(appendix_card(
        topic["protocol"].split("+")[0],
        topic["scope"][:12],
        [f"{topic['category']}巡检  HTTPS+地图", "三网筛选  电信/联通/移动", "变更后    必复测"],
    ))
    parts.append(FOOTER.format(keywords=topic["keywords"]))
    return "".join(parts)


def main():
    topics = build_topics()
    index = []
    stats = []

    for topic in topics:
        if topic["slug"] in SKIP_SLUGS:
            continue
        content = generate_article(topic)
        path = OUT / f"{topic['slug']}.md"
        path.write_text(content, encoding="utf-8")
        chars = len(content)
        lines = content.count("\n") + 1
        stats.append(chars)
        index.append({
            "slug": topic["slug"],
            "title": topic["title"],
            "category": topic["category"],
            "file": f"{topic['slug']}.md",
            "chars": chars,
            "lines": lines,
        })

    avg_c = sum(stats) // len(stats) if stats else 0
    lines = [
        "# SpeedCE 高质量长文库\n",
        "\n> 目标规格：每篇 **8000–15000 字** 级实战长文\n",
        f"\n> 工具：https://www.speedce.com | 中文：https://speedce.com/?lang=zh-CN\n",
        f"\n**库内文章**：{len(index)} 篇\n",
        f"**生成长文平均字数**：约 {avg_c} 字符/篇\n",
    ]

    cats = {}
    for item in index:
        cats.setdefault(item["category"], []).append(item)

    lines.append("\n## 生成长文索引（按类别）\n")
    for cat in sorted(cats.keys()):
        lines.append(f"\n### {cat}（{len(cats[cat])} 篇）\n\n| 文件 | 标题 | 字数 |\n|------|------|------|\n")
        for item in sorted(cats[cat], key=lambda x: x["slug"]):
            lines.append(f"| `{item['file']}` | {item['title']} | {item['chars']} |\n")

    lines.append("\n## 发布建议\n\n")
    lines.append("1. **规格**：每篇发布前配 3–5 张 SpeedCE 实拍地图（电信/联通/移动/全球）\n")
    lines.append("2. **节奏**：每 3–5 天 1 篇，优先故障排查 → VPS/CDN\n")
    lines.append("3. **互链**：文内互链到其他专题文章 + SpeedCE 中文页\n")
    lines.append("4. **标签**：网站测速、CDN、VPS、运维、SpeedCE\n")

    (OUT / "README.md").write_text("".join(lines), encoding="utf-8")
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated {len(index)} premium articles")
    print(f"Char range: {min(stats)} - {max(stats)}, avg {avg_c}")
    print(f"Min lines: {min(i['lines'] for i in index)}")


if __name__ == "__main__":
    main()
