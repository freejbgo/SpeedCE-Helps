---
layout: default
title: "SSL 证书过期与配置错误：用户报「连接不安全」时 10 分钟定位手册"
category: 故障排查
description: "证书问题最折磨人：你浏览器能开，用户大面积报「您的连接不是私密连接」。"
keywords: SSL,HTTPS,证书过期,SpeedCE
permalink: articles/ssl-certificate-troubleshooting.html
---

# SSL 证书过期与配置错误：用户报「连接不安全」时 10 分钟定位手册

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 引言

证书问题最折磨人：你浏览器能开，用户大面积报「您的连接不是私密连接」。

以下案例来自真实运维场景（细节已脱敏），展示如何用多节点测速快速定位和解决问题。

把 speedce.com 放进浏览器书签栏，下次 On-Call 收到告警，前 30 秒先测地图。

---

## 案例 1：安全组只放了 22 端口

### 背景

新购云服务器，SSH 能登，网站全国红。

### 排查过程

1. 打开 SpeedCE，协议 HTTPS，范围 中国节点
2. 测速结果：SpeedCE HTTPS 超时，PING 也超时。
3. 定位根因并修复
4. 复测确认恢复

### 处理结果

安全组添加入站 80/443，出站 443（Let's Encrypt 需要）。

### 经验总结

装机第一步：安全组，第二步：测速。

---

## 案例 2：Nginx 子域证书漏配

### 背景

www 正常，api 子域部分省份 HTTPS 失败。

### 排查过程

1. 打开 SpeedCE，协议 HTTPS，范围 中国节点
2. 测速结果：主域绿、API 域 sporadic 红，证书 SAN 不含 api。
3. 定位根因并修复
4. 复测确认恢复

### 处理结果

重新申请含 api 的证书，或单独配置 API server 块。

### 经验总结

每个对外子域都要单独测。

---

## 案例 3：证书过期导致 HTTPS 全国红

### 背景

凌晨告警，开发说服务正常，用户大面积报「连接不安全」。

### 排查过程

1. 打开 SpeedCE，协议 HTTPS，范围 中国节点
2. 测速结果：SpeedCE HTTPS 全国红、HTTP 全国绿——典型证书问题。
3. 定位根因并修复
4. 复测确认恢复

### 处理结果

检查 certbot 续签日志，手动续签后 10 分钟复测。

### 经验总结

证书自动续签失败要有告警，别等用户发现。

---

## 案例 4：CDN 回源 IP 未加白名单

### 背景

上 CDN 后 sporadic 502，直连源站正常。

### 排查过程

1. 打开 SpeedCE，协议 HTTPS，范围 中国节点
2. 测速结果：CDN 域名 sporadic 红，源站 IP 全绿。
3. 定位根因并修复
4. 复测确认恢复

### 处理结果

源站安全组添加 CDN 回源 IP 段白名单。

### 经验总结

上 CDN 后源站安全策略要同步调整。


故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。

VPS 退款期内，用 SpeedCE 对测试 IP 做晚高峰复测，截图就是最好的证据。

---

## 补充：验收与监控建议

- 排查「SSL 证书过期与配置错误」时，建议按「影响面 → 层级 → 修复 → 复测」四步走，不要跳步。
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

**Q：多久测一次合适？**

A：日常无故障：每周一次。有变更：变更后立即测。大促前：每天测。

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：PING 和 HTTPS 哪个准？**

A：建站验收用 HTTPS。VPS 验机可以 PING+HTTPS 都看，但以 HTTPS 通畅率为准。

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

**Q：这篇文章和 SpeedCE 是什么关系？**

A：SpeedCE 是免费的多节点测速工具，本文用它作为操作示例。你学到的排查思路适用于任何拨测场景。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com/?lang=zh-CN)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：SSL,HTTPS,证书过期,SpeedCE
