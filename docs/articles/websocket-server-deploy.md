---
layout: default
title: "WebSocket 服务部署：长连接、代理配置与验收边界"
category: 开发
description: "WebSocket 需要 Nginx proxy_read_timeout 等特殊配置。"
keywords: WebSocket,部署,实时,SpeedCE
permalink: articles/websocket-server-deploy.html
---

# WebSocket 服务部署：长连接、代理配置与验收边界

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 概述

WebSocket 需要 Nginx proxy_read_timeout 等特殊配置。

本文是一份关于「WebSocket 服务部署」的实操指南。每个关键步骤都会说明如何用多节点测速验证效果。

别信「我这边能打开」——让数据说话，[SpeedCE](https://www.speedce.com) 的多节点拨测就是为此设计的。

---

## 前置条件

| 项目 | 要求 |
|------|------|
| 网络验收工具 | [SpeedCE](https://speedce.com)（免费） |
| 推荐协议 | HTTPS |
| 推荐范围 | 中国节点 |
| 基础知识 | 了解 Linux 命令行和基本网络概念 |

---

## 步骤一：环境准备

### CI/CD 部署后验收

CI 绿灯不代表用户能访问——网络层验收是最后一道门。

```bash
# 部署完成后立即验证
curl -sf https://staging.example.com/health || exit 1
curl -sf https://staging.example.com/api/version

# 对比新旧版本
diff <(curl -s https://old.example.com/api/version) \
     <(curl -s https://new.example.com/api/version)
```

---

## 步骤二：配置与部署

1. 完成基础配置后，先在本地验证服务进程正常（systemctl status / docker ps）。
2. 确认端口监听：ss -tlnp | grep -E ':80|:443'。
3. 检查防火墙和安全组：80/443 入站、443 出站（证书续签需要）。
4. 打开 SpeedCE，协议选 **HTTPS**，范围选 **中国节点**。
5. 输入域名或 IP，记录通畅率、异常数、平均延迟。
6. 按电信/联通/移动分别筛选，各截图存档。
7. 若有 CDN：对加速域名和源站 IP 各测一次对照。

改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。

---

## 步骤三：验收与排障

| 验收项 | 标准 | 未达标处理 |
|--------|------|------------|
| 主域名通畅率 | ≥ 95% | 查安全组、证书、DNS |
| 三网均衡 | 无明显单网红 | 查线路或上 CDN |
| 子域/API 域 | 单独测过且达标 | 查证书 SAN、Nginx 配置 |
| 变更后复测 | 修完立即复测 | 间隔 10min 复测至达标 |

### 常见问题

- **全国红**：优先查安全组、证书、服务进程
- **单省红**：DNS 缓存或 CDN 节点缺失，隔 10min 复测
- **仅移动红**：移动线路未优化，考虑 CDN 或换线路
- **通畅但慢**：跨境绕路或未上 CDN，对照竞品评估

故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。

---

## 补充：验收与监控建议

- CI 绿灯 ≠ 用户能访问，上线后必须多节点验收。
- 本地 localhost 测试通过不代表生产环境可达。
- 每个对外 API 域、静态资源域单独测。
- 环境变量配错是部署后 502 的常见原因。

故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。

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

**Q：本地能跑通为什么线上不行？**

A：本地没有网络层问题。上线后必须用多节点验收。

**Q：CI 通过还需要测速吗？**

A：需要。CI 测的是代码，拨测测的是用户能不能访问。

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：这篇文章和 SpeedCE 是什么关系？**

A：SpeedCE 是免费的多节点测速工具，本文用它作为操作示例。你学到的排查思路适用于任何拨测场景。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：WebSocket,部署,实时,SpeedCE
