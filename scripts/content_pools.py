"""Topic-specific content pools for diverse article generation."""

from __future__ import annotations

import hashlib
import random
from typing import Any

SPEEDCE_LINKS = [
    "https://speedce.com/?lang=zh-CN",
    "https://www.speedce.com",
    "https://speedce.com",
]

SPEEDCE_MENTIONS = [
    "上线前用 [SpeedCE](https://speedce.com/?lang=zh-CN) 跑一遍全国三网地图，比本地 curl 靠谱得多。",
    "故障排查时，我习惯先打开 [speedce.com](https://speedce.com/?lang=zh-CN) 看地图颜色分布，再决定是查 DNS 还是查应用。",
    "验收标准很简单：电信、联通、移动三张地图截图存档，工具用免费的 SpeedCE 就行。",
    "别信「我这边能打开」——让数据说话，[SpeedCE](https://www.speedce.com) 的多节点拨测就是为此设计的。",
    "改完配置别急着宣布胜利，隔 10 分钟在 SpeedCE 上复测，看异常点是消散还是顽固。",
    "VPS 退款期内，用 SpeedCE 对测试 IP 做晚高峰复测，截图就是最好的证据。",
    "CDN 切量后 72 小时内，建议每天固定时段用 SpeedCE 对照源站与加速域。",
    "出海业务别忘了双视图：中国节点看团队访问，全球节点看客户访问，SpeedCE 一页切换。",
    "把 speedce.com 放进浏览器书签栏，下次 On-Call 收到告警，前 30 秒先测地图。",
    "给老板汇报时，一张 SpeedCE 三网地图比十页 PPT 更有说服力。",
]


def pick_mentions(slug: str, count: int = 3) -> list[str]:
    rng = random.Random(int(hashlib.md5(slug.encode()).hexdigest()[:8], 16))
    pool = SPEEDCE_MENTIONS.copy()
    rng.shuffle(pool)
    return pool[:count]


def pick_link(slug: str) -> str:
    idx = int(hashlib.md5(slug.encode()).hexdigest()[:4], 16) % len(SPEEDCE_LINKS)
    return SPEEDCE_LINKS[idx]


# ── Archetype definitions ─────────────────────────────────────────────

ARCHETYPES = ["howto", "troubleshoot", "comparison", "checklist", "reference", "case_study", "deep_dive", "workflow"]

ARCHETYPE_FOR_CATEGORY = {
    "故障排查": ["troubleshoot", "workflow", "case_study"],
    "VPS线路": ["comparison", "howto", "checklist"],
    "CDN": ["howto", "workflow", "troubleshoot"],
    "出海": ["checklist", "howto", "deep_dive"],
    "行业": ["case_study", "howto", "checklist"],
    "方法论": ["reference", "workflow", "deep_dive"],
    "对比": ["comparison", "reference"],
    "进阶": ["workflow", "deep_dive", "case_study"],
    "开发": ["howto", "reference", "deep_dive"],
    "运维": ["workflow", "troubleshoot", "checklist"],
    "数据库": ["troubleshoot", "howto", "reference"],
    "安全": ["checklist", "troubleshoot", "deep_dive"],
    "云原生": ["howto", "workflow", "reference"],
    "网络": ["deep_dive", "reference", "troubleshoot"],
}


def pick_archetype(slug: str, category: str) -> str:
    pool = ARCHETYPE_FOR_CATEGORY.get(category, ARCHETYPES)
    idx = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16) % len(pool)
    return pool[idx]


# ── Technical snippets by domain ──────────────────────────────────────

DEV_SNIPPETS: dict[str, list[dict[str, str]]] = {
    "nginx": [
        {"title": "反向代理基础配置", "code": """```nginx
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
```""", "explain": "每个对外子域名单独 server 块，证书和 upstream 不要混用。"},
        {"title": "常见 502 排查", "code": """```bash
# 检查 upstream 是否存活
curl -I http://127.0.0.1:3000/health

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log | grep upstream

# 检查 PHP-FPM 池状态
systemctl status php8.2-fpm
```""", "explain": "502 多半是 upstream 无响应，先确认后端进程活着。"},
    ],
    "docker": [
        {"title": "端口映射验收", "code": """```bash
# 容器内服务正常不代表外部可达
docker ps --format 'table {{.Names}}\t{{.Ports}}'

# 从外部测试映射端口
curl -I http://YOUR_SERVER_IP:8080

# 检查 iptables 规则
iptables -L -n | grep 8080
```""", "explain": "容器内 curl localhost 通过，全国用户访问不了，通常是端口映射或安全组问题。"},
        {"title": "健康检查配置", "code": """```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 40s
```""", "explain": "健康检查路径本身也要能被外部访问，否则负载均衡会把好节点摘掉。"},
    ],
    "k8s": [
        {"title": "Ingress 排障三板斧", "code": """```bash
kubectl get ingress -A
kubectl describe ingress my-ingress -n production
kubectl get endpoints my-service -n production

# 从集群外测试
curl -v https://api.example.com/health -H 'Host: api.example.com'
```""", "explain": "Ingress 红、Service 绿、Pod 绿——逐层缩小范围。"},
    ],
    "dns": [
        {"title": "DNS 链路逐层核对", "code": """```bash
# 权威 DNS
dig @ns1.example.com www.example.com A +short

# 公共 DNS（模拟用户）
dig @8.8.8.8 www.example.com A +short
dig @223.5.5.5 www.example.com A +short

# CNAME 链
dig www.example.com CNAME +trace
```""", "explain": "权威记录对了，不代表全国用户已生效——TTL 和运营商缓存是隐形杀手。"},
    ],
    "ssl": [
        {"title": "证书链完整性检查", "code": """```bash
# 查看证书链
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -dates

# 检查 SAN 覆盖
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -text | grep DNS

# 在线验证（命令行替代）
curl -vI https://api.example.com 2>&1 | grep -i 'SSL\\|certificate'
```""", "explain": "HTTPS 红 + HTTP 绿，90% 是证书问题——过期、漏子域、链不完整。"},
    ],
    "mysql": [
        {"title": "连接池耗尽诊断", "code": """```sql
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';
SHOW PROCESSLIST;

-- 找慢查询
SELECT * FROM information_schema.processlist
WHERE command != 'Sleep' AND time > 5
ORDER BY time DESC;
```""", "explain": "网络层全绿但页面超时，查 MySQL 连接数和慢查询。"},
    ],
    "redis": [
        {"title": "Redis 连接失败排查", "code": """```bash
redis-cli -h 127.0.0.1 ping
redis-cli info clients | grep connected

# 检查 bind 地址
grep ^bind /etc/redis/redis.conf
```""", "explain": "Redis 绑定了 127.0.0.1，容器或远程应用连不上是预期行为。"},
    ],
    "git": [
        {"title": "CI/CD 部署后验收", "code": """```bash
# 部署完成后立即验证
curl -sf https://staging.example.com/health || exit 1
curl -sf https://staging.example.com/api/version

# 对比新旧版本
diff <(curl -s https://old.example.com/api/version) \\
     <(curl -s https://new.example.com/api/version)
```""", "explain": "CI 绿灯不代表用户能访问——网络层验收是最后一道门。"},
    ],
    "python": [
        {"title": "Gunicorn 生产配置", "code": """```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 30
keepalive = 5
```""", "explain": "bind 127.0.0.1 时 Nginx 反代正常，但直接访问 IP:8000 会失败。"},
    ],
    "nodejs": [
        {"title": "PM2 集群模式", "code": """```bash
pm2 start app.js -i max --name api
pm2 logs api --lines 50
pm2 monit

# 检查端口监听
ss -tlnp | grep 3000
```""", "explain": "PM2 显示 online 但端口未监听，通常是应用启动报错被 PM2 吞了。"},
    ],
    "linux": [
        {"title": "防火墙快速检查", "code": """```bash
# 云安全组之外，系统防火墙也要查
ufw status verbose
iptables -L INPUT -n --line-numbers

# 端口监听
ss -tlnp | grep -E ':80|:443'

# 测试本地回环 vs 外部
curl -I http://127.0.0.1
curl -I http://$(hostname -I | awk '{print $1}')
```""", "explain": "127.0.0.1 能通、外网 IP 不通，99% 是防火墙或安全组。"},
    ],
    "monitoring": [
        {"title": "告警后 5 分钟 SOP", "code": """```bash
# 1. 确认服务进程
systemctl status nginx

# 2. 确认端口
ss -tlnp | grep 443

# 3. 确认证书
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -enddate

# 4. 全国拨测（浏览器打开 SpeedCE）
# https://speedce.com/?lang=zh-CN
```""", "explain": "监控告诉你「有问题」，拨测告诉你「哪里有问题」。"},
    ],
}


def detect_domain(slug: str, title: str) -> str:
    text = f"{slug} {title}".lower()
    mapping = [
        ("nginx", "nginx"), ("apache", "nginx"), ("proxy", "nginx"), ("ingress", "k8s"),
        ("k8s", "k8s"), ("kubernetes", "k8s"), ("docker", "docker"), ("container", "docker"),
        ("dns", "dns"), ("domain", "dns"), ("ssl", "ssl"), ("tls", "ssl"), ("https", "ssl"),
        ("certificate", "ssl"), ("mysql", "mysql"), ("mariadb", "mysql"), ("database", "mysql"),
        ("redis", "redis"), ("cache", "redis"), ("git", "git"), ("cicd", "git"), ("deploy", "git"),
        ("python", "python"), ("django", "python"), ("flask", "python"), ("fastapi", "python"),
        ("node", "nodejs"), ("express", "nodejs"), ("nextjs", "nodejs"), ("nuxt", "nodejs"),
        ("linux", "linux"), ("firewall", "linux"), ("iptables", "linux"), ("systemd", "linux"),
        ("monitor", "monitoring"), ("alert", "monitoring"), ("prometheus", "monitoring"),
        ("grafana", "monitoring"), ("uptime", "monitoring"),
    ]
    for keyword, domain in mapping:
        if keyword in text:
            return domain
    return "linux"


def get_snippets(slug: str, title: str, count: int = 2) -> list[dict[str, str]]:
    domain = detect_domain(slug, title)
    pool = DEV_SNIPPETS.get(domain, DEV_SNIPPETS["linux"])
    rng = random.Random(int(hashlib.md5(slug.encode()).hexdigest()[:8], 16))
    return rng.sample(pool, min(count, len(pool)))


# ── Scenario pools (category-specific) ────────────────────────────────

SCENARIO_POOLS: dict[str, list[dict[str, Any]]] = {
    "故障排查": [
        {"title": "证书过期导致 HTTPS 全国红", "symptom": "凌晨告警，开发说服务正常，用户大面积报「连接不安全」。", "diagnosis": "SpeedCE HTTPS 全国红、HTTP 全国绿——典型证书问题。", "fix": "检查 certbot 续签日志，手动续签后 10 分钟复测。", "lesson": "证书自动续签失败要有告警，别等用户发现。"},
        {"title": "DNS 迁机后新疆持续红", "symptom": "迁机完成，团队都说正常，新疆同事坚持打不开。", "diagnosis": "SpeedCE 地图：新疆持续红，其他省绿且随时间减少。", "fix": "指导 flushdns，等待 TTL 过期；必要时调低 TTL 后重新切换。", "lesson": "迁机验收不能只看自己省份。"},
        {"title": "安全组只放了 22 端口", "symptom": "新购云服务器，SSH 能登，网站全国红。", "diagnosis": "SpeedCE HTTPS 超时，PING 也超时。", "fix": "安全组添加入站 80/443，出站 443（Let's Encrypt 需要）。", "lesson": "装机第一步：安全组，第二步：测速。"},
        {"title": "Nginx 子域证书漏配", "symptom": "www 正常，api 子域部分省份 HTTPS 失败。", "diagnosis": "主域绿、API 域 sporadic 红，证书 SAN 不含 api。", "fix": "重新申请含 api 的证书，或单独配置 API server 块。", "lesson": "每个对外子域都要单独测。"},
        {"title": "CDN 回源 IP 未加白名单", "symptom": "上 CDN 后 sporadic 502，直连源站正常。", "diagnosis": "CDN 域名 sporadic 红，源站 IP 全绿。", "fix": "源站安全组添加 CDN 回源 IP 段白名单。", "lesson": "上 CDN 后源站安全策略要同步调整。"},
    ],
    "VPS线路": [
        {"title": "GT 晚高峰移动全红", "symptom": "下午测速完美，晚高峰移动用户投诉严重。", "diagnosis": "下午 SpeedCE 三网全绿，21:00 移动地图大面积红。", "fix": "退款期内截图申诉，或套 CDN 改善移动。", "lesson": "VPS 验机必须测晚高峰，移动地图是一票否决项。"},
        {"title": "被墙 IP 全球绿中国红", "symptom": "商家说「三网直连」，实际只有电信偶尔能通。", "diagnosis": "SpeedCE 全球节点全绿，中国节点全红。", "fix": "退款换 IP 或换商家，这种 IP 无法救。", "lesson": "付款前必测中国节点。"},
        {"title": "测试 IP 与正式 IP 线路不同", "symptom": "售前测试 IP 完美，到账后正式 IP 移动大红。", "diagnosis": "对照测：测试 IP 移动绿，正式 IP 移动红。", "fix": "7 天内截图对比申请换 IP 或退款。", "lesson": "到账后第一时间复测，别等过了退款期。"},
        {"title": "禁 Ping 误判线路差", "symptom": "新手见 Ping 超时就要退款。", "diagnosis": "PING 全超时，HTTPS 通畅率 96%。", "fix": "改用 HTTPS 测速标准，线路实际可用。", "lesson": "云厂商默认禁 ICMP，验机看 HTTPS。"},
        {"title": "家宽 ping 28ms 的陷阱", "symptom": "买家晒 ping 28ms 截图，实际全国移动延迟 300ms+。", "diagnosis": "家宽同城 ping 延迟虚低，全国地图才是真相。", "fix": "用 SpeedCE 全国节点重新验收。", "lesson": "单点样本毫无参考价值。"},
    ],
    "CDN": [
        {"title": "切量 30 分钟就宣布成功", "symptom": "DNS 切到 CDN 后半小时测速全绿，24 小时后仍有投诉。", "diagnosis": "T+0 全绿，T+6h 某省 sporadic 红，T+24h 该省持续红。", "fix": "建立 72 小时点检表，每 4 小时复测。", "lesson": "DNS 缓存全球不同步，切量验收至少 72 小时。"},
        {"title": "缓存脏了用户看旧页面", "symptom": "刚修复 bug 部署，用户还说旧版本。", "diagnosis": "SpeedCE 测 API 返回新版本，CDN 缓存域名返回旧版。", "fix": "刷新 CDN 缓存，静态资源加 hash 版本号。", "lesson": "测速和缓存是两层问题。"},
        {"title": "源站慢 CDN 更慢", "symptom": "以为上 CDN 一定更快，实际 TTFB 反而升高。", "diagnosis": "源站地图延迟 200ms，CDN 地图延迟 350ms。", "fix": "优化源站响应或换 CDN，对照测做决策。", "lesson": "CDN 不是万能药，源站慢要先修源站。"},
        {"title": "边缘证书与源站证书不一致", "symptom": "CDN 域名 HTTPS 红，源站 HTTPS 绿。", "diagnosis": "CDN 控制台证书过期或域名不匹配。", "fix": "CDN 侧重新上传/申请证书，两边分别验收。", "lesson": "CDN 证书和源站证书是两套独立配置。"},
        {"title": "WebSocket 走了 CDN 但 CDN 不支持", "symptom": "主站正常，实时功能间歇断开。", "diagnosis": "HTTPS 全绿但 WebSocket 握手失败——CDN 层问题。", "fix": "WebSocket 路径绕过 CDN 直连源站，或换支持 WS 的 CDN。", "lesson": "SpeedCE 测 HTTPS 可达，不测 WS 协议。"},
    ],
    "出海": [
        {"title": "上海秒开德国转圈", "symptom": "团队在上海测试 .com 秒开，德国客户反馈打不开。", "diagnosis": "中国节点全绿，德国节点 sporadic 红。", "fix": "源站迁到欧洲或用 CloudFront 欧洲节点。", "lesson": "出海测目标市场，不是测自己。"},
        {"title": "全球绿中国红被误判为被墙", "symptom": "源站在海外，中国团队访问慢，以为被墙了。", "diagnosis": "全球绿、中国红在出海场景可能是正常现象。", "fix": "若国内团队需要访问，加回国 CDN 或国内镜像。", "lesson": "先明确谁是你的用户。"},
        {"title": "支付回调域未单独验收", "symptom": "Stripe 支付成功但订单未更新。", "diagnosis": "主站绿，回调域 api.example.com/webhook 部分红。", "fix": "回调 URL 单独列入测速清单。", "lesson": "每个第三方回调域都要测。"},
        {"title": "GeoDNS 配错导致欧洲用户打到美国", "symptom": "欧洲用户延迟 300ms+，美国用户 50ms。", "diagnosis": "德国节点解析到美国 IP。", "fix": "修正 GeoDNS 记录，各国分别验证解析结果。", "lesson": "智能解析要用各地节点验证，不是本地 dig。"},
        {"title": "多语言站只测了首页", "symptom": "/en/ 和 /de/ 子路径部分国家访问异常。", "diagnosis": "首页绿，语言子路径 sporadic 红。", "fix": "每个语言路径单独测速验收。", "lesson": "子路径也是独立 URL。"},
    ],
    "开发": [
        {"title": "环境变量配错导致生产 502", "symptom": "本地 dev 正常，部署后全国 502。", "diagnosis": "SpeedCE 全国红，SSH 查日志发现 DATABASE_URL 为空。", "fix": "修正环境变量，重启服务，复测。", "lesson": "部署后第一件事：网络层验收，不是看 CI 绿灯。"},
        {"title": "CORS 配错被误认为网络故障", "symptom": "前端报跨域错误，运维开始查服务器。", "diagnosis": "SpeedCE 地图全绿，浏览器控制台 CORS 报错。", "fix": "后端添加 Access-Control-Allow-Origin。", "lesson": "先排除网络层，再查应用层。"},
        {"title": "静态资源路径用了绝对 HTTP", "symptom": "HTTPS 页面加载 HTTP 资源被浏览器拦截。", "diagnosis": "SpeedCE HTTPS 绿，但浏览器报混合内容。", "fix": "资源 URL 改相对路径或 // 协议相对。", "lesson": "网络层和浏览器安全策略是两层。"},
        {"title": "健康检查路径返回 404", "symptom": "负载均衡不断摘掉「健康」节点。", "diagnosis": "LB 探活 /health 返回 404，实际业务 / 正常。", "fix": "添加 /health 端点或修改探活路径。", "lesson": "探活路径本身必须返回 200。"},
        {"title": "Docker 网络模式配错", "symptom": "容器互联正常，外部访问超时。", "diagnosis": "容器用 host 网络能通，bridge 模式端口未映射。", "fix": "检查 docker-compose ports 配置。", "lesson": "容器内通 ≠ 外部通。"},
    ],
    "运维": [
        {"title": "磁盘满导致服务假死", "symptom": "监控显示 CPU 正常，用户访问超时。", "diagnosis": "SpeedCE sporadic 红，SSH 发现磁盘 100%。", "fix": "清理日志/临时文件，扩容磁盘。", "lesson": "网络绿但超时，查磁盘和内存。"},
        {"title": "日志轮转失败撑满磁盘", "symptom": "凌晨开始间歇性超时，白天又恢复。", "diagnosis": "logrotate 失败，access.log 涨到 50GB。", "fix": "手动 truncate 并修复 logrotate 配置。", "lesson": "日志管理是运维基本功。"},
        {"title": "定时任务把 CPU 打满", "symptom": "每天固定时段网站变慢。", "diagnosis": "SpeedCE 在 cron 执行时段延迟飙升。", "fix": "错峰执行或限流 cron 任务。", "lesson": "关联定时任务和性能波动。"},
        {"title": "swap 用满导致假死", "symptom": "SSH 能连但极慢，网站超时。", "diagnosis": "free -h 显示 swap 100%，OOM killer 未触发。", "fix": "重启服务释放内存，长期加内存或优化。", "lesson": "内存问题表现为网络超时。"},
        {"title": "证书续签 cron 静默失败", "symptom": "证书突然过期，之前一直正常。", "diagnosis": "certbot renew 日志显示 DNS challenge 失败。", "fix": "修复 DNS API 权限，手动续签。", "lesson": "续签成功要有通知，失败要有告警。"},
    ],
    "数据库": [
        {"title": "慢查询拖垮全站", "symptom": "网站时快时慢，数据库 CPU 80%。", "diagnosis": "SpeedCE 全绿但 TTFB 极高。", "fix": "开启慢查询日志，加索引或优化 SQL。", "lesson": "网络层绿不等于体验好。"},
        {"title": "主从延迟导致读到旧数据", "symptom": "写入后立刻读取，数据不一致。", "diagnosis": "写主库正常，读从库延迟 30 秒。", "fix": "关键读操作走主库，或等同步完成。", "lesson": "读写分离要处理延迟。"},
        {"title": "连接池配置过小", "symptom": "高峰期 sporadic 502，日志显示 too many connections。", "diagnosis": "网络绿，应用日志 connection pool exhausted。", "fix": "调大连接池或加 PgBouncer/ProxySQL。", "lesson": "先网络后应用，但别停在网络层。"},
    ],
    "安全": [
        {"title": "WAF 误拦拨测节点", "symptom": "SpeedCE 地图 sporadic 红点，用户实际正常。", "diagnosis": "WAF 日志显示部分 IP 被 CC 规则拦截。", "fix": "调整 WAF 阈值或加白名单。", "lesson": "sporadic 红不一定是真故障。"},
        {"title": "DDoS 期间全国延迟飙升", "symptom": "全国节点延迟同时升高，带宽打满。", "diagnosis": "流量图和 SpeedCE 地图时间线吻合。", "fix": "启用 DDoS 防护，清洗后复测确认恢复。", "lesson": "测速辅助判断攻击影响面。"},
        {"title": "TLS 1.0 被禁用导致老客户端失败", "symptom": "新浏览器正常，部分老设备 HTTPS 失败。", "diagnosis": "SpeedCE HTTPS sporadic 红，特定省份集中。", "fix": "评估是否需兼容 TLS 1.2+，通知用户升级。", "lesson": "安全加固要评估影响面。"},
    ],
    "云原生": [
        {"title": "HPA 扩容不及时", "symptom": "大促流量突增，部分请求超时。", "diagnosis": "SpeedCE sporadic 红，K8s pod 数未增加。", "fix": "调整 HPA 阈值和扩容速度。", "lesson": "自动扩缩容也要监控外部可达性。"},
        {"title": "Service -selector 标签不匹配", "symptom": "Deployment 正常，Ingress 502。", "diagnosis": "kubectl get endpoints 显示空。", "fix": "修正 Service selector 与 Pod label 一致。", "lesson": "集群内正常不等于外部可达。"},
    ],
    "网络": [
        {"title": "MTU 不匹配导致大包丢失", "symptom": "小请求正常，大文件传输失败。", "diagnosis": "Ping 小包好，大包丢包；mss 问题。", "fix": "调整 MTU 或启用 TCP MSS clamping。", "lesson": "SpeedCE 测小包可达，大包问题需专项测。"},
        {"title": "IPv6 只配了一半", "symptom": "IPv4 全绿，IPv6 用户访问失败。", "diagnosis": "AAAA 记录指向错误 IP 或防火墙未放行 v6。", "fix": "分别测 IPv4 和 IPv6 目标。", "lesson": "双栈站点两套独立验收。"},
    ],
}


def get_scenarios(slug: str, category: str, count: int = 4) -> list[dict[str, Any]]:
    pool = SCENARIO_POOLS.get(category, SCENARIO_POOLS["故障排查"])
    rng = random.Random(int(hashlib.md5(f"{slug}-scenarios".encode()).hexdigest()[:8], 16))
    shuffled = pool.copy()
    rng.shuffle(shuffled)
    result = []
    while len(result) < count:
        for item in shuffled:
            if len(result) >= count:
                break
            result.append(item)
    return result[:count]


# ── FAQ pools ─────────────────────────────────────────────────────────

FAQ_POOLS: dict[str, list[tuple[str, str]]] = {
    "default": [
        ("这篇文章和 SpeedCE 是什么关系？", "SpeedCE 是免费的多节点测速工具，本文用它作为网络层验收的操作示例。你学到的排查思路适用于任何拨测场景。"),
        ("一定要注册才能用吗？", "不需要。打开 speedce.com 直接测，免费，无需注册。"),
        ("测速结果能当证据吗？", "可以。截图标注时间、协议、目标，附在工单、论坛帖或事故报告里很有说服力。"),
        ("多久测一次合适？", "日常无故障：每周一次主域巡检。有变更：变更后立即测。大促前：T-7 到 T+0 每天测。"),
        ("PING 和 HTTPS 哪个准？", "建站验收用 HTTPS。VPS 验机可看 PING+HTTPS，但以 HTTPS 通畅率为准。"),
        ("测速要多久？", "通常 1–3 分钟，视节点数而定。可观察进度条。"),
        ("异常很多是不是网站挂了？", "先看全网还是局部。全网异常查服务器/证书/安全组；局部查区域线路或 DNS。"),
        ("PING 全超时 HTTPS 正常？", "正常，说明禁 Ping。以 HTTPS 为准。"),
        ("和 BOCE/ITDOG 怎么选？", "日常地图巡检 SpeedCE；持续 Ping 用 ITDOG；污染备案用 BOCE。"),
        ("通畅率多少算达标？", "国内主站建议 ≥95%；出海目标国 ≥95%；移动无大片红。"),
        ("能否替代监控？", "不能。拨测是快照，7×24 监控与告警仍需 Uptime 等。"),
        ("没有域名只有 IP？", "可以。输入 IPv4/IPv6 直接测，适合 VPS 验机。"),
    ],
    "VPS线路": [
        ("退款期几天够验机？", "7 天足够。到账当天、第 3 天、第 7 天各测一次，覆盖工作日和周末晚高峰。"),
        ("测试 IP 和正式 IP 不一样怎么办？", "到账后立刻用 SpeedCE 复测正式 IP，对照售前截图。"),
        ("移动地图全红能救吗？", "套 CDN 可能改善，但源站移动差是硬伤。退款期内建议直接退。"),
    ],
    "CDN": [
        ("切 CDN 后多久算验收完成？", "建议 72 小时。DNS 缓存全球不同步，24 小时内仍有异常很正常。"),
        ("源站和 CDN 都要测吗？", "必须对照测。这是 CDN 排障的第一原则。"),
    ],
    "出海": [
        ("全球绿中国红正常吗？", "源站在海外时，中国慢可能是正常现象。关键看你的用户在哪里。"),
        ("要测哪些国家？", "测你目标市场的 Top 3 国家，用 SpeedCE 全球节点。"),
    ],
    "开发": [
        ("本地能跑通为什么线上不行？", "本地没有网络层问题。上线后必须用多节点验收。"),
        ("CI 通过还需要测速吗？", "需要。CI 测的是代码，拨测测的是用户能不能访问。"),
    ],
}


def get_faqs(slug: str, category: str, count: int = 5) -> list[tuple[str, str]]:
    specific = FAQ_POOLS.get(category, [])
    general = FAQ_POOLS["default"]
    pool = specific + general
    rng = random.Random(int(hashlib.md5(f"{slug}-faq".encode()).hexdigest()[:8], 16))
    rng.shuffle(pool)
    return pool[:count]


# ── Comparison items ────────────────────────────────────────────────────

COMPARISON_AXES = [
    ("易用性", "上手难度、界面直观程度"),
    ("中国节点覆盖", "省份和运营商节点数量"),
    ("全球节点", "海外国家覆盖"),
    ("协议支持", "PING/HTTP/HTTPS/TCP"),
    ("结果展示", "地图 vs 表格 vs 图表"),
    ("免费程度", "是否需要注册/付费"),
    ("适合场景", "日常巡检/故障排查/验收"),
    ("互补工具", "与监控/性能工具的配合"),
]
