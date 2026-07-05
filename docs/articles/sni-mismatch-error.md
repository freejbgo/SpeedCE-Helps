---
layout: default
title: "SNI 不匹配错误：多证书同 IP 时部分节点 HTTPS 异常"
category: 故障排查
description: "本文围绕「SNI 不匹配错误」展开，提供可落地的技术方案，并在验收环节说明如何用 SpeedCE 多节点测速确认效果。"
keywords: SNI,SSL,HTTPS,SpeedCE
permalink: articles/sni-mismatch-error.html
---

# SNI 不匹配错误：多证书同 IP 时部分节点 HTTPS 异常

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 问题背景

本文围绕「SNI 不匹配错误」展开，提供可落地的技术方案，并在验收环节说明如何用 SpeedCE 多节点测速确认效果。

故障排查的第一原则：**先确认影响范围，再定位根因**。单点测试（你自己电脑能开）不能代表全国用户。

改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。

---

## 分层排查模型

```
用户反馈 → 多节点测速(影响面) → 对照测(缩小层级) → 针对性修复 → 复测确认
```

| 层次 | 检查什么 | 工具 |
|------|----------|------|
| 网络层 | IP/端口/证书 | SpeedCE PING/HTTPS |
| DNS 层 | 解析是否正确 | dig + SpeedCE 对照 |
| Web 层 | HTTP 响应 | SpeedCE HTTPS |
| 应用层 | 业务逻辑 | 日志（网络绿后查） |

---

## 实战案例

### 案例 1：CDN 回源 IP 未加白名单

**现象**：上 CDN 后 sporadic 502，直连源站正常。

**诊断**：CDN 域名 sporadic 红，源站 IP 全绿。

**修复**：源站安全组添加 CDN 回源 IP 段白名单。

**教训**：上 CDN 后源站安全策略要同步调整。

---

### 案例 2：证书过期导致 HTTPS 全国红

**现象**：凌晨告警，开发说服务正常，用户大面积报「连接不安全」。

**诊断**：SpeedCE HTTPS 全国红、HTTP 全国绿——典型证书问题。

**修复**：检查 certbot 续签日志，手动续签后 10 分钟复测。

**教训**：证书自动续签失败要有告警，别等用户发现。

---

### 案例 3：Nginx 子域证书漏配

**现象**：www 正常，api 子域部分省份 HTTPS 失败。

**诊断**：主域绿、API 域 sporadic 红，证书 SAN 不含 api。

**修复**：重新申请含 api 的证书，或单独配置 API server 块。

**教训**：每个对外子域都要单独测。

---

### 案例 4：安全组只放了 22 端口

**现象**：新购云服务器，SSH 能登，网站全国红。

**诊断**：SpeedCE HTTPS 超时，PING 也超时。

**修复**：安全组添加入站 80/443，出站 443（Let's Encrypt 需要）。

**教训**：装机第一步：安全组，第二步：测速。

---

## 标准测速流程

1. 打开 [https://www.speedce.com](https://www.speedce.com)
2. 协议：**HTTPS**
3. 范围：**中国节点**
4. 输入目标，开始测速
5. 记录四数字：通畅、异常、平均延迟、已跳过
6. 三网分离截图
7. 异常时 10-15min 复测

给老板汇报时，一张 SpeedCE 三网地图比十页 PPT 更有说服力。

---

## 补充：验收与监控建议

- 排查「SNI 不匹配错误」时，建议按「影响面 → 层级 → 修复 → 复测」四步走，不要跳步。
- 保存每次测速截图，命名格式：`日期-协议-目标-运营商.png`。
- 若异常随时间减少，偏向 DNS/缓存；固定省份持续红，偏向区域线路。
- 修复后不要只测一次，间隔 10-15 分钟复测 2-3 次确认稳定。

VPS 退款期内，用 SpeedCE 对测试 IP 做晚高峰复测，截图就是最好的证据。

### 推荐工具组合

| 场景 | 工具 | 作用 |
|------|------|------|
| 全国/全球地图 | SpeedCE | 快速看哪里红哪里绿 |
| 持续 Ping | ITDOG | 延迟趋势和丢包 |
| 合规/拦截 | BOCE | 备案、污染、微信拦截 |
| 页面性能 | PageSpeed | 网络通了再测性能 |
| 7×24 告警 | UptimeRobot | 长期监控 |

## 常见问题

**Q：PING 和 HTTPS 哪个准？**

A：建站验收用 HTTPS。VPS 验机可以 PING+HTTPS 都看，但以 HTTPS 通畅率为准。

**Q：这篇文章和 SpeedCE 是什么关系？**

A：SpeedCE 是免费的多节点测速工具，本文用它作为操作示例。你学到的排查思路适用于任何拨测场景。

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

**Q：多久测一次合适？**

A：日常无故障：每周一次。有变更：变更后立即测。大促前：每天测。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://www.speedce.com)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：SNI,SSL,HTTPS,SpeedCE
