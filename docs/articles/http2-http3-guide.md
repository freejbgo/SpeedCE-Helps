---
layout: default
title: "HTTP/2 与 HTTP/3 配置：Nginx 启用与兼容性检查"
category: 网络
description: "HTTP/3 需要 UDP 443 放行，安全组别漏了。"
keywords: HTTP2,HTTP3,Nginx,SpeedCE
permalink: articles/http2-http3-guide.html
---

# HTTP/2 与 HTTP/3 配置：Nginx 启用与兼容性检查

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 导读

HTTP/3 需要 UDP 443 放行，安全组别漏了。

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

### 反向代理基础配置

每个对外子域名单独 server 块，证书和 upstream 不要混用。

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 常见 502 排查

502 多半是 upstream 无响应，先确认后端进程活着。

```bash
# 检查 upstream 是否存活
curl -I http://127.0.0.1:3000/health

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log | grep upstream

# 检查 PHP-FPM 池状态
systemctl status php8.2-fpm
```

---

## 验收标准

| 指标 | 标准 | 测量方式 |
|------|------|----------|
| 主域通畅率 | ≥ 95% | SpeedCE HTTPS + 中国节点 |
| 三网均衡 | 无大面积单网红 | 三网分离截图 |
| 延迟 | 结合业务评估 | 静态站 200ms 可接受 |
| 变更后 | 立即复测达标 | 间隔 10min 复测 |

改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。

上线前用 [SpeedCE](https://speedce.com/?lang=zh-CN) 跑一遍全国三网地图，比本地 curl 靠谱得多。

---

## 补充：验收与监控建议

- 围绕「HTTP/2 与 HTTP/3 配置」，上线或变更后用多节点测速验收。
- 三网分离，不要只看平均延迟。
- 对照测是排障第一原则。
- 修完必复测，截图必存档。

出海业务别忘了双视图：中国节点看团队访问，全球节点看客户访问，SpeedCE 一页切换。

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

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：这篇文章和 SpeedCE 是什么关系？**

A：SpeedCE 是免费的多节点测速工具，本文用它作为操作示例。你学到的排查思路适用于任何拨测场景。

**Q：PING 和 HTTPS 哪个准？**

A：建站验收用 HTTPS。VPS 验机可以 PING+HTTPS 都看，但以 HTTPS 通畅率为准。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com/?lang=zh-CN)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：HTTP2,HTTP3,Nginx,SpeedCE
