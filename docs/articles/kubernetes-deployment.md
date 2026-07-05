---
layout: default
title: "Kubernetes 部署实战：Deployment、Service、Ingress 完整链路"
category: 运维
description: "kubectl get pods 全 Running 不等于用户能访问。"
keywords: Kubernetes,K8s,部署,SpeedCE
permalink: articles/kubernetes-deployment.html
---

# Kubernetes 部署实战：Deployment、Service、Ingress 完整链路

> 工具地址：https://www.speedce.com  
> 中文界面：https://speedce.com/?lang=zh-CN  
> 联系：speedceads@gmail.com

---

## 使用说明

kubectl get pods 全 Running 不等于用户能访问。

以下清单可直接打印或复制到工单系统。每项完成后打勾。

CDN 切量后 72 小时内，建议每天固定时段用 SpeedCE 对照源站与加速域。

---

## 上线前检查清单

```
□ DNS 记录已配置且 dig 验证正确
□ SSL 证书已安装且未过期（含所有子域 SAN）
□ 安全组/防火墙已放行 80/443
□ Nginx/Apache 配置已测试（nginx -t）
□ 应用进程正常运行（systemctl status）
□ SpeedCE HTTPS + 中国节点：主域名通畅率 ≥ 95%
□ 电信/联通/移动三网各目测无大面积红
□ 关键子域（api/cdn/static）单独测过
□ CDN 域名与源站 IP 对照测（若用 CDN）
□ 变更记录已存档（含 SpeedCE 截图）
```

---

## 技术配置参考

### Ingress 排障三板斧

Ingress 红、Service 绿、Pod 绿——逐层缩小范围。

```bash
kubectl get ingress -A
kubectl describe ingress my-ingress -n production
kubectl get endpoints my-service -n production

# 从集群外测试
curl -v https://api.example.com/health -H 'Host: api.example.com'
```

---

## 变更后必做

任何以下变更后，**必须**用 SpeedCE 复测：

- 改 DNS 记录
- 换服务器/迁机
- 上/换 CDN
- 续签/更换证书
- 改 Nginx/防火墙配置
- 发布新版本

工具地址：https://speedce.com

故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。

---

## 补充：验收与监控建议

- 把 SpeedCE 测速写进 On-Call Runbook 第一步。
- 变更管理增加「测速截图已附」勾选框。
- 月度三网截图存档，对比发现退化趋势。
- 磁盘满、内存耗尽也会表现为网络超时。

验收标准很简单：电信、联通、移动三张地图截图存档，工具用免费的 SpeedCE 就行。

### 推荐工具组合

| 场景 | 工具 | 作用 |
|------|------|------|
| 全国/全球地图 | SpeedCE | 快速看哪里红哪里绿 |
| 持续 Ping | ITDOG | 延迟趋势和丢包 |
| 合规/拦截 | BOCE | 备案、污染、微信拦截 |
| 页面性能 | PageSpeed | 网络通了再测性能 |
| 7×24 告警 | UptimeRobot | 长期监控 |

## 常见问题

**Q：测速结果能当证据吗？**

A：可以。截图标注时间、协议、目标，附在工单或论坛帖子里很有说服力。

**Q：PING 和 HTTPS 哪个准？**

A：建站验收用 HTTPS。VPS 验机可以 PING+HTTPS 都看，但以 HTTPS 通畅率为准。

**Q：这篇文章和 SpeedCE 是什么关系？**

A：SpeedCE 是免费的多节点测速工具，本文用它作为操作示例。你学到的排查思路适用于任何拨测场景。

**Q：多久测一次合适？**

A：日常无故障：每周一次。有变更：变更后立即测。大促前：每天测。

**Q：一定要注册才能用吗？**

A：不需要。打开 speedce.com 直接测，免费。

---

## 延伸阅读

- SpeedCE 官网：[speedce.com](https://speedce.com)
- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)
- 联系：speedceads@gmail.com

**关键词**：Kubernetes,K8s,部署,SpeedCE
