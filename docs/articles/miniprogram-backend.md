---
layout: default
title: "小程序后端 API 部署：合法域、备案与移动网络验收"
category: 开发
description: "小程序要求 HTTPS + 备案，后端 API 域要单独测。"
keywords: 小程序,微信,API,SpeedCE
permalink: articles/miniprogram-backend.html
---

# 小程序后端 API 部署：合法域、备案与移动网络验收

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 导读

小程序要求 HTTPS + 备案，后端 API 域要单独测。

本文作为技术参考，涵盖核心概念、配置要点和验收方法。

---

## 核心概念

| 概念 | 说明 | 与测速的关系 |
|------|------|-------------|
| 多节点拨测 | 从全国各地发起真实访问 | SpeedCE 核心能力 |
| 通畅率 | 成功探测数 / 总探测数 | ≥95% 为达标 |
| 三网分离 | 电信/联通/移动独立地图 | 定位运营商问题 |
| 对照测 | 两目标同时测速对比 | CDN vs 源站等 |

---

## 配置参考

### 防火墙快速检查

127.0.0.1 能通、外网 IP 不通，99% 是防火墙或安全组。

```bash
# 云安全组之外，系统防火墙也要查
ufw status verbose
iptables -L INPUT -n --line-numbers

# 端口监听
ss -tlnp | grep -E ':80|:443'

# 测试本地回环 vs 外部
curl -I http://127.0.0.1
curl -I http://$(hostname -I | awk '{print $1}')
```

---

## 验收标准

| 指标 | 标准 | 测量方式 |
|------|------|----------|
| 主域通畅率 | ≥ 95% | SpeedCE HTTPS + 中国节点 |
| 三网均衡 | 无大面积单网红 | 三网分离截图 |
| 延迟 | 结合业务评估 | 静态站 200ms 可接受 |
| 变更后 | 立即复测达标 | 间隔 10min 复测 |

出海业务别忘了双视图：中国节点看团队访问，全球节点看客户访问，SpeedCE 一页切换。

故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。

---

## 补充：验收与监控建议

- CI 绿灯 ≠ 用户能访问，上线后必须多节点验收。
- 本地 localhost 测试通过不代表生产环境可达。
- 每个对外 API 域、静态资源域单独测。
- 环境变量配错是部署后 502 的常见原因。

改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。

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

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：CI 通过还需要测速吗？**

A：需要。CI 测的是代码，拨测测的是用户能不能访问。

**Q：多久测一次合适？**

A：日常无故障：每周一次。有变更：变更后立即测。大促前：每天测。

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com/?lang=zh-CN)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：小程序,微信,API,SpeedCE
