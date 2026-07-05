---
layout: default
title: "Node.js PM2 集群部署：多进程、负载均衡与验收"
category: 开发
description: "PM2 cluster 模式端口监听和 Nginx upstream 要配对。"
keywords: Node.js,PM2,部署,SpeedCE
permalink: articles/nodejs-pm2-cluster.html
---

# Node.js PM2 集群部署：多进程、负载均衡与验收

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 深入理解

PM2 cluster 模式端口监听和 Nginx upstream 要配对。

本文深入探讨技术原理，并在关键节点说明如何用测速数据验证理论判断。

---

## 原理剖析

### PM2 集群模式

PM2 显示 online 但端口未监听，通常是应用启动报错被 PM2 吞了。

```bash
pm2 start app.js -i max --name api
pm2 logs api --lines 50
pm2 monit

# 检查端口监听
ss -tlnp | grep 3000
```

---

## 为什么需要多节点视角

单点测试有三个致命偏见：

1. **地理偏见**：你和服务器的物理距离不代表用户距离
2. **运营商偏见**：你的宽带运营商不代表全国用户
3. **时间偏见**：你测试的时刻不代表晚高峰

SpeedCE 的多节点地图消除了这三个偏见。打开 [https://speedce.com](https://speedce.com)，选 HTTPS + 中国节点，获取全国/全球视角。

---

## 实践建议

| 阶段 | 动作 | 频率 |
|------|------|------|
| 上线前 | 全国三网验收 | 一次 |
| 日常 | 主域巡检 | 每周 |
| 变更后 | 立即复测 | 每次变更 |
| 大促前 | 全量点检 | T-7 到 T+0 |
| 故障时 | 第一时间测地图 | 按需 |

出海业务别忘了双视图：中国节点看团队访问，全球节点看客户访问，SpeedCE 一页切换。

改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。

---

## 补充：验收与监控建议

- CI 绿灯 ≠ 用户能访问，上线后必须多节点验收。
- 本地 localhost 测试通过不代表生产环境可达。
- 每个对外 API 域、静态资源域单独测。
- 环境变量配错是部署后 502 的常见原因。

把 speedce.com 放进浏览器书签栏，下次 On-Call 收到告警，前 30 秒先测地图。

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

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：多久测一次合适？**

A：日常无故障：每周一次。有变更：变更后立即测。大促前：每天测。

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：Node.js,PM2,部署,SpeedCE
