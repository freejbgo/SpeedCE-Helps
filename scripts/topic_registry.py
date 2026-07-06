"""500-topic registry with rich metadata for diverse article generation."""

from __future__ import annotations


def _add(topics: list, cat: str, slug: str, title: str, keywords: str, hook: str,
         protocol: str = "HTTPS", scope: str = "中国节点") -> None:
    topics.append({
        "slug": slug, "title": title, "category": cat, "keywords": keywords,
        "hook": hook, "protocol": protocol, "scope": scope,
    })


def build_all_topics() -> list[dict]:
    t: list[dict] = []

    # ── 故障排查 60 ──
    troubles = [
        ("dns-troubleshooting-guide", "DNS 解析故障完全指南：迁机、换 CDN 后「部分地区打不开」怎么查",
         "DNS故障,域名解析,迁机,SpeedCE", "改完 DNS 你这边秒生效，新疆同事说还是旧 IP——这不是他电脑坏了，是解析链路不同步。"),
        ("ssl-certificate-troubleshooting", "SSL 证书过期与配置错误：用户报「连接不安全」时 10 分钟定位手册",
         "SSL,HTTPS,证书过期,SpeedCE", "证书问题最折磨人：你浏览器能开，用户大面积报「您的连接不是私密连接」。"),
        ("nginx-reverse-proxy-troubleshooting", "Nginx 反向代理故障排查：主站绿、API 红的 8 种典型配置错误",
         "Nginx,反向代理,502,SpeedCE", "一行 server_name 写错，表现就是「首页能开、接口全挂」。"),
        ("website-migration-guide", "网站迁机完整手册：DNS、源站、CDN 切换的 72 小时测速验收节奏",
         "网站迁机,DNS,迁移,SpeedCE", "迁机最紧张的是 DNS 全球生效时间——多节点测速是迁机验收的客观公证人。"),
        ("intermittent-fault-diagnosis", "间歇性网站故障排查：「有时慢有时好」的科学点检方法",
         "间歇故障,网站不稳定,SpeedCE", "间歇故障是运维噩梦：你测的时候永远正常，用户投诉的时候你不在。"),
        ("subdomain-troubleshooting", "子域名故障排查：主站能开、接口挂了的 8 种独立原因",
         "子域名,API,DNS,SpeedCE", "www 和 api 在 DNS、证书、Nginx 上是四份独立配置。"),
        ("api-availability-guide", "API 接口可达性检测：Postman 能通、全国用户不通的真相",
         "API,接口监控,HTTPS,SpeedCE", "API 故障往往最后才发现：前端缓存还在，App 打接口立刻挂。"),
        ("502-503-upstream-errors", "502/503 与源站过载：CDN 绿、源站红时的判断与修复",
         "502,503,源站过载,SpeedCE", "502 是网关收到坏响应，503 是服务暂时不可用——对照测一锤定音。"),
        ("firewall-security-group-checklist", "云服务器安全组验收：全国地图大面积红时先查这四项",
         "安全组,防火墙,443端口,SpeedCE", "SSH 能登、网站全国红——安全组只放了 22 没放 443。"),
        ("regional-access-failure", "仅部分地区打不开？用地图精确定位省份与运营商",
         "区域故障,省份,地图测速,SpeedCE", "「就新疆不行」「就移动不行」——地图才是区域故障的语言。"),
        ("mobile-network-issues", "移动网络用户访问异常专项：为什么移动投诉往往最多",
         "移动网络,三网测速,SpeedCE", "移动用户占比超 50%，不单独测移动地图等于忽略一半用户。"),
        ("ipv6-troubleshooting", "IPv6 双栈站点验收：AAAA 记录、防火墙与 CDN 完整检查",
         "IPv6,双栈,AAAA,SpeedCE", "IPv4 全绿不代表 IPv6 正常，双栈站点应分别验证。"),
        ("cors-vs-network-testing", "CORS 报错与网络不通：开发者必分的两层问题",
         "CORS,跨域,API,SpeedCE", "地图全绿 + 浏览器报 CORS——恭喜，网络通了，是 Header 没配。"),
        ("waf-false-positive-guide", "WAF 误拦与测速异常：sporadic 红点是不是被封了",
         "WAF,防火墙,CDN安全,SpeedCE", "WAF 可能只拦部分拨测 IP，表现为 sporadic 红而非全省红。"),
        ("k8s-ingress-troubleshoot", "Kubernetes Ingress 故障：集群内正常、公网域名红的排查",
         "Kubernetes,Ingress,K8s,SpeedCE", "kubectl get pods 全 Running，但公网域名红——Ingress 层断了。"),
        ("docker-port-mapping", "Docker 端口映射错误：容器内正常、全国用户打不开的验收",
         "Docker,端口,容器,SpeedCE", "docker exec 里 curl 通过，外部访问超时——端口映射或安全组问题。"),
        ("lets-encrypt-rate-limit", "Let's Encrypt 限流与续签失败：HTTPS 突然全国红的证书向排查",
         "Let's Encrypt,证书,HTTPS,SpeedCE", "certbot renew 静默失败三个月，某天 HTTPS 突然全国红。"),
        ("websocket-wss-check", "WebSocket / WSS 长连接：HTTPS 可达与实时业务的分工边界",
         "WebSocket,WSS,实时,SpeedCE", "SpeedCE 测 HTTPS 可达，WebSocket 握手失败是另一层问题。"),
        ("oauth-callback-domain", "OAuth 回调域名校验：登录失败的网络层先行排查",
         "OAuth,登录,回调,SpeedCE", "登录页绿、回调域红——OAuth 失败不一定是代码 bug。"),
        ("payment-callback-url", "支付回调 URL 可达性：全国节点对回调域的验收",
         "支付,回调,电商,SpeedCE", "主站绿、支付回调域红——订单状态不更新可能是网络层问题。"),
        ("mysql-connection-timeout", "数据库连接超时与网站超时：网络绿、页面仍慢的分层排查",
         "MySQL,数据库,超时,SpeedCE", "SpeedCE 全绿但页面超时——查 MySQL 连接池和慢查询。"),
        ("redis-connection-issues", "Redis 连接失败对网站的影响：何时该先测网络再查缓存",
         "Redis,缓存,故障,SpeedCE", "Redis 挂了页面可能还能打开但功能异常——先网络后缓存。"),
        ("gzip-brotli-compression", "Gzip/Brotli 压缩配置与超时：能通但极慢的排查",
         "Gzip,Brotli,Nginx,SpeedCE", "没开压缩，大 JSON 响应体导致 TTFB 极高——网络通但体验差。"),
        ("http-https-redirect-issues", "HTTP 与 HTTPS 跳转故障：循环重定向与混合内容排查",
         "HTTPS,301跳转,混合内容,SpeedCE", "301 配成循环、http 和 https 指向不同机器——对照测快速缩小范围。"),
        ("dns-propagation-slow", "域名解析生效慢怎么判断：TTL、运营商缓存与区域差异",
         "DNS缓存,TTL,解析生效,SpeedCE", "改 DNS 不是全世界同时变，隔 10 分钟复测看异常点变化。"),
        ("peak-hour-slowdown", "晚高峰网站变慢：下午测正常、晚上变红的复测策略",
         "晚高峰,网站变慢,线路拥堵,SpeedCE", "晚高峰才是照妖镜——商家挑下午给你看测试 IP。"),
        ("ddos-attack-detection", "被攻击期间如何用多节点测速辅助判断影响面",
         "DDoS,攻击,故障排查,SpeedCE", "全国节点同时变红、延迟飙升——配合流量图确认攻击。"),
        ("cache-poisoning-stale", "缓存脏了怎么办：CDN/浏览器缓存与网络层对照排查",
         "CDN缓存,浏览器缓存,SpeedCE", "刚修好服务器用户还说旧页面——可能是缓存，不是网络。"),
        ("load-balancer-health-check", "负载均衡与健康检查：一半节点绿一半红的架构问题",
         "负载均衡,健康检查,高可用,SpeedCE", "多台后端一台挂，用户感受是「有时能开有时不能」。"),
        ("third-party-script-failure", "第三方脚本拖垮页面：主域绿、功能仍异常的边界",
         "第三方脚本,CDN,前端,SpeedCE", "支付、统计、客服插件走第三方域——主站绿不代表支付能调起。"),
    ]
    for slug, title, kw, hook in troubles:
        _add(t, "故障排查", slug, title, kw, hook)

    # ── VPS线路 45 ──
    vps = [
        ("vps-line-verification-guide", "买 VPS 前必看：用全国三网地图验线路，识破 CN2 宣传",
         "VPS测速,CN2 GIA,三网测速,SpeedCE", "在 HostLoc 群里，买家说 ping 28ms——样本量只有 1，且样本是你自己。"),
        ("hong-kong-vps-guide", "香港 VPS 线路选购与验收：个人站、电商、API 场景怎么选",
         "香港VPS,CN2,线路测速,SpeedCE", "香港机房 CN2、CMI、BGP 混杂，全国三网地图是唯一靠谱验货方式。"),
        ("japan-vps-guide", "日本 VPS 适合什么业务：东京大阪机房与三网回国实测",
         "日本VPS,东京,线路,SpeedCE", "日本机便宜带宽足，但回国线路质量参差，移动地图是一票否决项。"),
        ("us-vps-china-access", "美国 VPS 三网回国测评：西海岸机房怎么验、移动用户怎么办",
         "美国VPS,回国线路,三网,SpeedCE", "不要信「洛杉矶 150ms」——那是你本地 ping，不是全国地图。"),
        ("cn2-gt-vs-gia", "CN2 GT 与 CN2 GIA 完全对比：商家话术背后的测速验证法",
         "CN2 GT,CN2 GIA,VPS,SpeedCE", "差两个字母，体验差一个档次。GT 晚高峰可能堵，GIA 贵但稳。"),
        ("bgp-line-verification", "BGP 线路真假辨别：三网均衡才是真 BGP 的验收标准",
         "BGP,VPS,三网,SpeedCE", "真 BGP：电信联通移动都能用。假 BGP：电信绿、移动红。"),
        ("cmi-mobile-line-guide", "移动优化 CMI 线路验收：移动用户占比过半时代的一票否决项",
         "CMI,移动线路,VPS,SpeedCE", "不单独看移动地图，等于放弃一半用户。"),
        ("vps-refund-period-checklist", "VPS 7 天退款期验机清单：截图、三网、晚高峰证据链",
         "VPS退款,验机,证据,SpeedCE", "退款要有证据：三网截图 + 通畅率数字 + 晚高峰对比。"),
        ("ping-blocked-not-bad", "禁 Ping 不等于线路差：PING 红 HTTPS 绿的正确解读",
         "禁Ping,ICMP,VPS,SpeedCE", "云厂商默认禁 ICMP 是常态，验机标准改成 HTTPS 通畅率 ≥ 90%。"),
        ("off-peak-vs-peak-vps", "VPS 下午测与晚高峰测：为什么优质线路必须测两次",
         "晚高峰,VPS,线路,SpeedCE", "商家测试 IP 在下午往往最美，你要在 20:00-22:00 复测。"),
        ("vultr-line-guide", "Vultr 各机房线路验收：按业务选东京/新加坡/洛杉矶",
         "Vultr,VPS,线路,SpeedCE", "Vultr 机房多但线路质量差异大，按目标用户选机房。"),
        ("bandwagonhost-guide", "搬瓦工 CN2/GIA 套餐验机：经典商家地图验收法",
         "搬瓦工,BandwagonHost,CN2,SpeedCE", "搬瓦工经典套餐也要地图验收——不同机房线路差异明显。"),
        ("oracle-cloud-free", "甲骨文云免费 tier 验收：零成本机器的地图标准",
         "Oracle Cloud,免费VPS,SpeedCE", "免费机也要验收：被墙 IP 和超售邻居是常见坑。"),
        ("colocation-vs-cloud", "托管机房 vs 公有云：同一业务选型后的地图验收差异",
         "托管,公有云,选型,SpeedCE", "托管和云的核心差异在运维责任，但网络验收方法相同。"),
        ("budget-vps-trap-guide", "超低价 VPS 陷阱：地图验收能看出的 6 个危险信号",
         "低价VPS,陷阱,验机,SpeedCE", "年付几十块的机器不是不能用，但要靠地图知道代价在哪。"),
    ]
    for slug, title, kw, hook in vps:
        proto = "HTTPS+PING" if "vps" in slug or "cn2" in slug else "HTTPS"
        scope = "中国节点+全球节点" if "us-" in slug or "europe" in slug else "中国节点"
        _add(t, "VPS线路", slug, title, kw, hook, proto, scope)

    # ── CDN 35 ──
    cdn = [
        ("cdn-deployment-speed-test-guide", "CDN 接入全攻略：切量前、切量中、故障时的多节点验收",
         "CDN测速,CDN验收,回源,SpeedCE", "上了 CDN 反而有人打不开？对照测速是 CDN 运维的黄金法则。"),
        ("cloudflare-china-access", "Cloudflare 橙云开启后国内访问完整验收手册",
         "Cloudflare,CDN,国内,SpeedCE", "Cloudflare 免费版对国内访问有争议——用地图数据说话。"),
        ("aliyun-cdn-acceptance", "阿里云 CDN 接入验收：回源、证书、预热与三网",
         "阿里云CDN,验收,SpeedCE", "国内 CDN 厂商验收重点：三网均衡和回源配置。"),
        ("cdn-origin-failure", "CDN 回源失败完全排查：边缘节点、超时与源站对照",
         "CDN回源,502,SpeedCE", "CDN 域名 sporadic 红、源站 IP 全绿——回源链路问题。"),
        ("cdn-cutover-72h", "CDN 切量 72 小时监控手册：从 T+0 到 T+72 每小时做什么",
         "CDN切量,DNS,监控,SpeedCE", "切 DNS 后半小时宣布成功，24 小时后仍有投诉——没做 72 小时点检。"),
        ("multi-cdn-comparison", "多家 CDN 试用期地图对比选型：同域不同商的科学方法",
         "CDN对比,选型,SpeedCE", "试用期用同域名分别接入，地图对比选最优。"),
        ("static-cdn-split", "静态资源 CDN 分离验收：js/css 域与主站的独立测速清单",
         "静态CDN,前端,SpeedCE", "主站绿不代表静态资源域绿——每个 CDN 域单独测。"),
        ("cdn-cert-vs-origin", "CDN 证书与源站证书：两边都要绿的完整验收流程",
         "CDN证书,SSL,SpeedCE", "CDN 证书和源站证书是两套独立配置，分别验收。"),
        ("qiniu-cdn-guide", "七牛云 CDN 接入：国内站长常用方案的测速验收",
         "七牛云,CDN,SpeedCE", "七牛云适合图片和静态资源，接入后三网地图验收。"),
        ("bunny-cdn-guide", "Bunny CDN 性价比线路：全球节点地图验收",
         "BunnyCDN,CDN,SpeedCE", "Bunny CDN 便宜但国内节点覆盖有限——用地图确认。"),
    ]
    for slug, title, kw, hook in cdn:
        _add(t, "CDN", slug, title, kw, hook)

    # ── 出海 35 ──
    global_topics = [
        ("global-deployment-checklist", "网站出海测速验收：从中国节点到全球节点的完整检查",
         "网站出海,全球测速,SpeedCE", "你在上海打开 .com 秒开，德国客户说转圈——测速视角错了。"),
        ("cross-border-ecommerce", "外贸独立站测速指南：Shopify/WooCommerce 与大促前验收",
         "外贸,独立站,跨境电商,SpeedCE", "大促前不测目标市场，等于闭着眼睛做生意。"),
        ("southeast-asia-nodes", "东南亚市场节点验收：新马泰印尼菲逐国达标线",
         "东南亚,出海,节点,SpeedCE", "东南亚各国网络质量差异大，逐国验收不能偷懒。"),
        ("saas-global-launch", "出海 SaaS 全球上线验收：目标市场通畅率达标手册",
         "出海SaaS,全球测速,SpeedCE", "SaaS 出海看目标国通畅率，不是看团队能不能访问。"),
        ("shopify-speedtest", "Shopify 店铺全球可达性：主题、支付与应用域分层测速",
         "Shopify,外贸,独立站,SpeedCE", "Shopify 主域由平台管，但自定义域和 App 域要自测。"),
        ("stripe-payment-domain-check", "出海支付域名校验：支付页、回调 URL 的独立测速",
         "支付,Stripe,出海,SpeedCE", "支付成功但订单不更新——查回调域可达性。"),
        ("china-blocked-overseas-ok", "全球绿、中国红：被墙/合规问题的标准判断流程",
         "被墙,出海,合规,SpeedCE", "全球绿中国红在出海场景可能是正常现象，先明确用户在哪。"),
        ("geodns-verification", "GeoDNS 智能解析验证：各地解析到不同 IP 的测速方法",
         "GeoDNS,智能解析,SpeedCE", "本地 dig 不能代表德国用户看到的解析结果。"),
        ("latin-america-nodes", "拉美节点验收：巴西、墨西哥重点市场地图标准",
         "拉美,巴西,出海,SpeedCE", "拉美网络基础设施参差，巴西和墨西哥要分开测。"),
        ("middle-east-africa-nodes", "中东与非洲节点验收：新兴市场的地图达标策略",
         "中东,非洲,出海,SpeedCE", "新兴市场延迟高是常态，关键是通畅率达标。"),
    ]
    for slug, title, kw, hook in global_topics:
        _add(t, "出海", slug, title, kw, hook, "HTTPS", "中国节点+全球节点")

    # ── 开发 80 (new category) ──
    dev_topics = [
        ("react-production-deploy", "React 生产环境部署验收：构建产物、CDN 与 API 域分层检查",
         "React,前端,部署,SpeedCE", "npm run build 成功不等于用户能访问——上线后多节点验收是最后一步。"),
        ("vue-nuxt-deploy-guide", "Vue/Nuxt 项目上线：SSR 与静态生成的网络层验收差异",
         "Vue,Nuxt,SSR,SpeedCE", "SSR 站点要测 Node 服务可达性，静态站测 CDN 分发。"),
        ("nextjs-deploy-checklist", "Next.js 部署检查清单：Vercel 自托管与 Docker 部署的验收",
         "Next.js,部署,React,SpeedCE", "Next.js 部署方式不同，网络验收重点也不同。"),
        ("django-deployment-guide", "Django 生产部署：Gunicorn、Nginx 与静态文件的三层验收",
         "Django,Python,部署,SpeedCE", "Django 部署三层：WSGI 进程、Nginx 反代、静态文件 CDN。"),
        ("flask-gunicorn-setup", "Flask + Gunicorn 生产配置：从开发到上线的完整流程",
         "Flask,Python,Gunicorn,SpeedCE", "Flask debug 模式能跑，Gunicorn 生产配置才是正经事。"),
        ("fastapi-uvicorn-deploy", "FastAPI + Uvicorn 部署：异步 API 的网络层验收要点",
         "FastAPI,Python,API,SpeedCE", "FastAPI 性能强但部署配置错了一样全国红。"),
        ("laravel-nginx-deploy", "Laravel + Nginx + PHP-FPM 部署验收：从 composer 到全国可达",
         "Laravel,PHP,部署,SpeedCE", "Laravel 部署坑多：权限、.env、PHP-FPM 池大小。"),
        ("spring-boot-production", "Spring Boot 生产部署：JVM 调优、健康检查与全国 API 验收",
         "Spring Boot,Java,部署,SpeedCE", "Spring Boot Actuator /health 也要能被外部访问。"),
        ("nodejs-pm2-cluster", "Node.js PM2 集群部署：多进程、负载均衡与验收",
         "Node.js,PM2,部署,SpeedCE", "PM2 cluster 模式端口监听和 Nginx upstream 要配对。"),
        ("express-api-deploy", "Express API 部署验收：中间件、CORS 与全国可达性",
         "Express,Node.js,API,SpeedCE", "Express 本地 localhost:3000 通，外网访问要查 bind 地址。"),
        ("go-gin-deploy", "Go Gin 框架部署：编译、systemd 与反向代理验收",
         "Go,Gin,部署,SpeedCE", "Go 编译成单二进制部署简单，但 Nginx 反代配置不能省。"),
        ("rust-actix-deploy", "Rust Actix-web 部署：高性能 API 的网络层验收",
         "Rust,Actix,部署,SpeedCE", "Rust 性能顶级，部署后验收流程和其他语言一样。"),
        ("graphql-api-deploy", "GraphQL API 部署验收：单一端点与 REST 的分层检查",
         "GraphQL,API,部署,SpeedCE", "GraphQL 单一 /graphql 端点，证书和 CORS 更要仔细。"),
        ("grpc-gateway-setup", "gRPC 网关部署：REST 可达与 gRPC 故障的分工排查",
         "gRPC,API,网关,SpeedCE", "SpeedCE 测 REST/HTTP 可达，gRPC 需要专项工具。"),
        ("websocket-server-deploy", "WebSocket 服务部署：长连接、代理配置与验收边界",
         "WebSocket,部署,实时,SpeedCE", "WebSocket 需要 Nginx proxy_read_timeout 等特殊配置。"),
        ("static-site-github-pages", "静态站部署：GitHub Pages vs 自建服务器的地图对比",
         "静态站,GitHub Pages,部署,SpeedCE", "GitHub Pages 国内访问慢是已知问题——用地图量化。"),
        ("hexo-hugo-deploy", "Hexo/Hugo 静态博客部署：生成、推送与全国可达验收",
         "Hexo,Hugo,博客,SpeedCE", "静态博客部署简单，但 CDN 和域名配置不能马虎。"),
        ("wordpress-optimization", "WordPress 性能优化与部署：插件、缓存与全国验收",
         "WordPress,博客,优化,SpeedCE", "WordPress 插件越多越慢——优化后全国复测确认。"),
        ("typecho-emlog-setup", "Typecho/Emlog 轻量博客：小站也要做的全国验收",
         "Typecho,Emlog,博客,SpeedCE", "轻量博客不代表可以跳过网络验收。"),
        ("miniprogram-backend", "小程序后端 API 部署：合法域、备案与移动网络验收",
         "小程序,微信,API,SpeedCE", "小程序要求 HTTPS + 备案，后端 API 域要单独测。"),
    ]
    for slug, title, kw, hook in dev_topics:
        _add(t, "开发", slug, title, kw, hook)

    # ── 运维 70 ──
    ops_topics = [
        ("linux-systemd-service", "systemd 服务管理：开机自启、日志查看与故障恢复",
         "systemd,Linux,运维,SpeedCE", "systemctl status 显示 active 但端口未监听——服务假活。"),
        ("nginx-log-analysis", "Nginx 访问日志分析：从日志到全国地图的故障定位",
         "Nginx,日志,运维,SpeedCE", "日志告诉你谁在访问，地图告诉你谁能访问。"),
        ("logrotate-config", "logrotate 配置与磁盘管理：防止日志撑满导致假死",
         "logrotate,日志,磁盘,SpeedCE", "磁盘 100% 时服务假死，SpeedCE 表现为 sporadic 红。"),
        ("cron-job-management", "Cron 定时任务管理：错峰执行与性能影响评估",
         "cron,定时任务,运维,SpeedCE", "每天固定时段变慢？查 cron 是否把 CPU 打满。"),
        ("backup-restore-drill", "备份恢复演练：RTO/RPO 目标与恢复后全国验收",
         "备份,恢复,灾备,SpeedCE", "备份了但没演练过等于没备份——恢复后必须全国复测。"),
        ("ssl-certbot-auto", "Certbot 自动续签：配置、告警与续签失败处理",
         "Certbot,SSL,证书,SpeedCE", "自动续签失败静默三个月，某天 HTTPS 全国红。"),
        ("fail2ban-setup", "Fail2ban 配置：防暴力破解与误拦拨测节点的平衡",
         "Fail2ban,安全,运维,SpeedCE", "Fail2ban 太激进会误拦拨测 IP，地图 sporadic 红。"),
        ("ufw-iptables-guide", "UFW 与 iptables 防火墙：云服务器双层防火墙配置",
         "防火墙,iptables,安全,SpeedCE", "云安全组 + 系统防火墙 = 双层，两层都要放行 443。"),
        ("prometheus-grafana-setup", "Prometheus + Grafana 监控搭建：指标采集与告警配置",
         "Prometheus,Grafana,监控,SpeedCE", "Prometheus 告诉你 CPU 90%，SpeedCE 告诉你哪里访问不了。"),
        ("docker-compose-production", "Docker Compose 生产部署：网络、卷、健康检查完整配置",
         "Docker Compose,容器,部署,SpeedCE", "docker-compose up -d 后必须外部访问验收，不是 docker ps 看状态。"),
        ("kubernetes-deployment", "Kubernetes 部署实战：Deployment、Service、Ingress 完整链路",
         "Kubernetes,K8s,部署,SpeedCE", "kubectl get pods 全 Running 不等于用户能访问。"),
        ("ansible-automation", "Ansible 自动化运维：Playbook 编写与批量部署验收",
         "Ansible,自动化,运维,SpeedCE", "Ansible 批量部署后，抽几个节点用 SpeedCE 验收。"),
        ("terraform-iac", "Terraform 基础设施即代码：云资源创建与网络验收",
         "Terraform,IaC,云,SpeedCE", "Terraform apply 成功不等于服务可达——验收是独立步骤。"),
        ("gitlab-ci-cd-pipeline", "GitLab CI/CD 流水线：构建、测试、部署与上线验收",
         "GitLab,CI/CD,DevOps,SpeedCE", "CI 绿灯是代码质量，拨测绿灯是用户可达。"),
        ("github-actions-deploy", "GitHub Actions 自动部署：从 push 到全国可达的完整流程",
         "GitHub Actions,CI/CD,部署,SpeedCE", "Actions 部署成功后加一步 SpeedCE 验收。"),
        ("zero-downtime-deploy", "零停机发布：蓝绿/金丝雀发布中的地图对照",
         "蓝绿,金丝雀,发布,SpeedCE", "蓝绿切换后对照测新旧环境，确认无回退。"),
        ("disaster-recovery-drill", "灾备演练：切换 DR 站点后的全国 SpeedCE 点检",
         "灾备,演练,DR,SpeedCE", "灾备切换后 5 分钟全国点检，比宣布恢复更重要。"),
        ("oncall-runbook-speedtest", "On-Call Runbook 中的测速章节：告警后 5 分钟 SOP",
         "OnCall,Runbook,应急,SpeedCE", "收到告警前 30 秒打开 SpeedCE，比翻文档快。"),
        ("monthly-inspection-sop", "月度网站巡检 SOP：个人站 15 分钟、企业站 1 小时版",
         "月度巡检,SOP,SpeedCE", "每月固定一天三网截图存档，对比上月发现退化。"),
        ("incident-postmortem", "事故复盘中的测速证据：时间线与地图如何写进 Postmortem",
         "Postmortem,复盘,运维,SpeedCE", "无责复盘要有数据：SpeedCE 截图 + 时间线。"),
    ]
    for slug, title, kw, hook in ops_topics:
        _add(t, "运维", slug, title, kw, hook)

    # ── 数据库 25 ──
    db_topics = [
        ("mysql-performance-tuning", "MySQL 性能调优：慢查询、索引与连接池优化",
         "MySQL,性能,数据库,SpeedCE", "慢查询拖垮全站时 SpeedCE 全绿但 TTFB 极高。"),
        ("postgresql-tuning", "PostgreSQL 调优：连接池、VACUUM 与查询优化",
         "PostgreSQL,数据库,调优,SpeedCE", "PgBouncer 连接池配错，高峰期 sporadic 502。"),
        ("redis-production-setup", "Redis 生产环境配置：持久化、内存与集群部署",
         "Redis,缓存,部署,SpeedCE", "Redis maxmemory 满了会拒绝写入，页面功能异常。"),
        ("mongodb-replica-set", "MongoDB 副本集部署：选举、读写分离与验收",
         "MongoDB,数据库,副本集,SpeedCE", "副本集选举期间短暂不可用，外部表现为 sporadic 红。"),
        ("elasticsearch-cluster", "Elasticsearch 集群部署：分片、副本与搜索服务验收",
         "Elasticsearch,搜索,集群,SpeedCE", "ES 集群黄灯时搜索变慢，网络层仍可能全绿。"),
        ("database-migration-guide", "数据库迁移实战： mysqldump、逻辑复制与切换验收",
         "数据库迁移,MySQL,SpeedCE", "库迁移完成不等于应用正常——切换后全国复测。"),
        ("sql-injection-prevention", "SQL 注入防护：参数化查询、WAF 与渗透测试准备",
         "SQL注入,安全,数据库,SpeedCE", "安全加固后 sporadic 红可能是 WAF 误拦。"),
        ("database-backup-strategy", "数据库备份策略：全量、增量与恢复演练",
         "数据库备份,恢复,SpeedCE", "备份策略要有恢复演练，恢复后验收应用可达。"),
    ]
    for slug, title, kw, hook in db_topics:
        _add(t, "数据库", slug, title, kw, hook)

    # ── 安全 25 ──
    sec_topics = [
        ("https-hsts-config", "HSTS 配置与安全加固：强制 HTTPS 的利弊与影响评估",
         "HSTS,HTTPS,安全,SpeedCE", "开启 HSTS 后 HTTP 跳转失败会导致用户完全无法访问。"),
        ("waf-rules-tuning", "WAF 规则调优：防攻击与减少误拦的平衡",
         "WAF,安全,防火墙,SpeedCE", "WAF 太严 sporadic 红，太松被攻击全国红。"),
        ("ddos-mitigation-guide", "DDoS 防护实战：清洗、限速与恢复后验收",
         "DDoS,防护,安全,SpeedCE", "攻击期间全国延迟飙升，清洗后 SpeedCE 复测确认恢复。"),
        ("penetration-test-prep", "渗透测试前网络暴露面：对外域名测速清单",
         "渗透测试,安全,域名,SpeedCE", "渗透前先列清所有对外域名，逐个验收。"),
        ("ssl-tls-hardening", "SSL/TLS 安全加固：版本、密码套件与兼容性权衡",
         "TLS,SSL,安全,SpeedCE", "禁用 TLS 1.0 后老客户端 HTTPS 失败——评估影响面。"),
        ("api-rate-limiting", "API 限流配置：防滥用与正常用户的平衡",
         "API,限流,安全,SpeedCE", "限流太严正常用户 sporadic 红，太松被刷爆。"),
        ("secrets-management", "密钥管理最佳实践：环境变量、Vault 与轮换策略",
         "密钥,安全,运维,SpeedCE", "密钥泄露后紧急轮换，轮换后全国复测确认。"),
    ]
    for slug, title, kw, hook in sec_topics:
        _add(t, "安全", slug, title, kw, hook)

    # ── 云原生 25 ──
    cloud_native = [
        ("docker-best-practices", "Docker 最佳实践：镜像优化、安全与生产部署",
         "Docker,容器,最佳实践,SpeedCE", "镜像越小部署越快，但网络验收和镜像大小无关。"),
        ("k8s-hpa-autoscaling", "Kubernetes HPA 自动扩缩容：指标、阈值与外部验收",
         "Kubernetes,HPA,扩缩容,SpeedCE", "HPA 扩容不及时，外部表现为 sporadic 超时。"),
        ("helm-chart-deploy", "Helm Chart 部署：模板、版本管理与回滚验收",
         "Helm,Kubernetes,部署,SpeedCE", "Helm rollback 后必须全国复测确认回退成功。"),
        ("istio-service-mesh", "Istio 服务网格入门：流量管理、安全与可观测性",
         "Istio,服务网格,Kubernetes,SpeedCE", "服务网格增加了复杂度，外部可达性验收更重要。"),
        ("serverless-lambda-guide", "Serverless/Lambda 部署：冷启动、超时与 API 验收",
         "Serverless,Lambda,云,SpeedCE", "冷启动导致首请求超时，表现为 sporadic 红。"),
        ("aws-ecs-fargate", "AWS ECS Fargate 部署：任务定义、服务发现与验收",
         "AWS,ECS,Fargate,SpeedCE", "Fargate 无服务器容器，安全组和 ALB 配置是关键。"),
    ]
    for slug, title, kw, hook in cloud_native:
        _add(t, "云原生", slug, title, kw, hook)

    # ── 网络 25 ──
    network_topics = [
        ("tcp-udp-basics", "TCP 与 UDP 基础：建站场景下该关心什么",
         "TCP,UDP,网络,SpeedCE", "建站主要关心 TCP 443，UDP 是 DNS 和游戏场景。"),
        ("dns-records-explained", "DNS 记录类型详解：A、AAAA、CNAME、MX、TXT 各干什么",
         "DNS,记录类型,域名,SpeedCE", "改错一条 DNS 记录，全国地图大面积红。"),
        ("http2-http3-guide", "HTTP/2 与 HTTP/3 配置：Nginx 启用与兼容性检查",
         "HTTP2,HTTP3,Nginx,SpeedCE", "HTTP/3 需要 UDP 443 放行，安全组别漏了。"),
        ("cdn-dns-cname-chain", "CDN CNAME 链解析：从域名到边缘节点的完整链路",
         "CDN,CNAME,DNS,SpeedCE", "CNAME 链任何一环断了，CDN 域名就红。"),
        ("bgp-routing-basics", "BGP 路由基础：VPS 选购时该看懂什么",
         "BGP,路由,VPS,SpeedCE", "BGP 不是魔法，三网地图才是验收标准。"),
        ("nat-port-forwarding", "NAT 与端口转发：家庭实验室到公网服务的配置",
         "NAT,端口转发,网络,SpeedCE", "端口转发配错，内网能通外网不通。"),
        ("vpn-wireguard-setup", "WireGuard VPN 部署：组网、路由与内网服务暴露",
         "WireGuard,VPN,网络,SpeedCE", "VPN 组网后内网服务暴露到公网要单独验收。"),
    ]
    for slug, title, kw, hook in network_topics:
        _add(t, "网络", slug, title, kw, hook)

    # ── 行业 40 ──
    industry = [
        ("ecommerce-sale-prep", "电商 618/双11 大促前多节点测速备战手册",
         "电商,双11,618,SpeedCE", "大促前不全国点检，等于闭着眼睛迎接流量。"),
        ("online-education-platform", "在线教育平台开课前三网验收：视频域、直播与 API",
         "在线教育,直播,SpeedCE", "开课铃响了你才发现视频域移动红——太晚了。"),
        ("corporate-website-sla", "企业官网可用性 SLA：用通畅率数据向管理层汇报",
         "企业官网,SLA,SpeedCE", "老板问「网站稳不稳」，一张三网地图比口头保证有用。"),
        ("fintech-medical-compliance", "金融/医疗网站网络层基线：HTTPS、证书与多活验收",
         "金融,医疗,合规,SpeedCE", "金融医疗对可用性要求更高，通畅率 99% 是底线。"),
        ("news-media-peak-traffic", "新闻媒体流量峰值：突发报道前的全国点检 SOP",
         "媒体,流量,峰值,SpeedCE", "突发新闻流量秒级暴增，提前点检是基本功。"),
        ("game-private-server-ping", "游戏联机服务器社群运营：用全国 PING 地图建立信任",
         "游戏服务器,联机,SpeedCE", "游戏玩家对延迟敏感，全国 PING 地图是社群信任基础。"),
        ("recruitment-careers-site", "招聘官网高峰验收：校招季前的全国点检",
         "招聘,企业官网,SpeedCE", "校招季流量暴增，提前一周每天点检。"),
        ("hospital-appointment-system", "医院预约系统网络基线：高峰与移动用户验收",
         "医疗,预约,移动,SpeedCE", "医院预约系统移动用户占比高，移动地图必看。"),
    ]
    for slug, title, kw, hook in industry:
        _add(t, "行业", slug, title, kw, hook)

    # ── 方法论 30 ──
    method = [
        ("how-to-read-speed-map", "如何读懂测速地图：绿/红/灰、延迟、通畅率的完全解读",
         "测速地图,教程,SpeedCE", "地图比表格适合找区域——平均 127ms 不告诉你问题在新疆。"),
        ("tri-network-method", "三网分离检测法：电信、联通、移动为何必须分开测",
         "三网测速,电信,联通,移动,SpeedCE", "三网不分离，等于把三个问题混成一个。"),
        ("ab-comparison-method", "A/B 对照测速法：CDN vs 源站、迁机前后的系统方法",
         "对照测速,方法论,SpeedCE", "对照测是排障第一原则——没有对照就没有结论。"),
        ("pre-launch-30-checklist", "网站上线前 30 项检查清单：含 8 项多节点测速必做项",
         "上线清单,验收,SpeedCE", "上线清单里测速不是可选项，是必做项。"),
        ("speedce-vs-itdog", "SpeedCE vs ITDOG 完全对比：场景、优缺点与搭配策略",
         "SpeedCE,ITDOG,对比", "没有最好的工具，只有最合适的场景。"),
        ("speedce-vs-boce", "SpeedCE vs BOCE 完全对比：轻量地图与全能运维的边界",
         "SpeedCE,BOCE,对比", "SpeedCE 看地图，BOCE 查合规——分工明确。"),
        ("protocol-selection-guide", "SpeedCE 六种检测工具选择完全指南：HTTP / HTTPS / PING / TCPing / DNS / 路由追踪",
         "HTTP,HTTPS,PING,TCPing,DNS,路由追踪,SpeedCE", "工具选错，结论就错——建站用 HTTPS，迁机查 DNS，绕路用路由追踪。"),
        ("incident-report-speed-data", "事故报告中的测速数据：运维复盘的专业写法",
         "事故报告,复盘,SpeedCE", "事故报告没数据就是甩锅，有地图截图才是专业。"),
    ]
    for slug, title, kw, hook in method:
        proto = "按场景选择（见 7.2 工具表）" if slug == "protocol-selection-guide" else "HTTPS"
        _add(t, "方法论", slug, title, kw, hook, proto)

    # ── 对比 15 ──
    compare = [
        ("top5-free-speedtest-2026", "2026 个人站长免费测速 TOP5 深度评测",
         "免费测速,TOP5,2026,SpeedCE", "2026 年免费测速工具不少，关键是找到适合自己场景的。"),
        ("17ce-vs-speedce", "17CE vs SpeedCE：老牌表格派与新锐地图派实战对比",
         "17CE,SpeedCE,对比", "17CE 表格精确，SpeedCE 地图直观——看场景选。"),
        ("gtmetrix-vs-speedce", "GTmetrix vs SpeedCE：性能测试与网络拨测分工",
         "GTmetrix,测速,对比", "GTmetrix 测页面性能，SpeedCE 测网络可达——先通后快。"),
        ("map-vs-table-tools", "地图派 vs 表格派测速工具：排障效率的实测对比",
         "测速工具,地图,对比", "找区域问题用地图，看精确数字用表格。"),
    ]
    for slug, title, kw, hook in compare:
        _add(t, "对比", slug, title, kw, hook)

    # ── 进阶 20 ──
    advanced = [
        ("spring-festival-traffic", "春节流量保障：移动暴增前的全国三网点检手册",
         "春节,流量,移动,SpeedCE", "春节移动流量暴增，提前一周每天点检。"),
        ("double11-618-prep", "双11/618 大促测速时间表：T-7 到 T+0 的完整节奏",
         "双11,618,大促,SpeedCE", "大促测速不是测一次，是 T-7 到 T+0 的持续节奏。"),
        ("icp-filing-launch-check", "ICP 备案通过后全国可达性验收：解析、证书与合规",
         "ICP备案,上线,SpeedCE", "备案通过不等于全国能访问——还要验收解析和证书。"),
        ("xinjiang-tibet-access-guide", "新疆/西藏/西北片区访问优化：地图验收与 CDN 策略",
         "新疆,西北,区域优化,SpeedCE", "西北片区是测速地图的照妖镜——很多线路在这里暴露。"),
        ("seo-crawl-baidu-google", "百度/Google 爬虫与站长可达性：SEO 视角的测速",
         "SEO,爬虫,收录,SpeedCE", "爬虫爬不到等于没收录——站长可达性是 SEO 基础。"),
        ("status-page-setup", "Status Page 搭建：测速数据如何支撑公开状态页",
         "Status Page,监控,SpeedCE", "公开状态页需要真实数据支撑，SpeedCE 截图是素材。"),
    ]
    for slug, title, kw, hook in advanced:
        _add(t, "进阶", slug, title, kw, hook)

    # ── Bulk generate remaining topics to reach 500 ──
    _bulk_generate(t)

    # Deduplicate by slug
    seen: set[str] = set()
    unique: list[dict] = []
    for topic in t:
        if topic["slug"] not in seen:
            seen.add(topic["slug"])
            unique.append(topic)

    return unique[:500]


def _bulk_generate(t: list[dict]) -> None:
    """Programmatically generate topics to fill gaps toward 500."""
    patterns = [
        # (category, slug_prefix, title_template, keyword_base)
        ("开发", "python-lib", "Python {name} 实战：安装、配置与生产部署验收", "Python,{name},开发,SpeedCE"),
        ("开发", "js-lib", "JavaScript {name} 入门到部署：前端工程化与上线验收", "JavaScript,{name},前端,SpeedCE"),
        ("运维", "linux-cmd", "Linux {name} 命令实战：运维场景与故障排查", "Linux,{name},运维,SpeedCE"),
        ("运维", "monitor-tool", "{name} 监控方案搭建：告警配置与故障响应", "{name},监控,运维,SpeedCE"),
        ("数据库", "db-topic", "{name} 数据库实战：部署、调优与验收", "{name},数据库,SpeedCE"),
        ("安全", "sec-topic", "{name} 安全加固实战：配置、检测与影响评估", "{name},安全,SpeedCE"),
        ("云原生", "cloud-topic", "{name} 云原生实战：部署架构与网络验收", "{name},云原生,SpeedCE"),
        ("网络", "net-topic", "{name} 网络协议深入：原理、配置与排障", "{name},网络,SpeedCE"),
        ("故障排查", "fix-topic", "{name} 故障排查手册：现象、定位与修复", "{name},故障排查,SpeedCE"),
        ("VPS线路", "vps-region", "{name} VPS 线路验收：机房选择与三网实测", "{name},VPS,线路,SpeedCE"),
        ("CDN", "cdn-vendor", "{name} CDN 接入验收：配置要点与三网地图标准", "{name},CDN,SpeedCE"),
        ("出海", "global-region", "{name} 市场出海验收：节点选择与通畅率标准", "{name},出海,SpeedCE"),
        ("行业", "industry-vertical", "{name} 行业网站验收：可用性标准与点检清单", "{name},行业,SpeedCE"),
        ("方法论", "method-topic", "{name}：多节点测速方法论与实操指南", "{name},方法论,SpeedCE"),
        ("进阶", "adv-topic", "{name} 进阶实战：变更管理与测速门禁", "{name},进阶,SpeedCE"),
        ("开发", "dev-framework", "{name} 部署实战：从开发到全国可达验收", "{name},开发,SpeedCE"),
        ("运维", "ops-tool", "{name} 运维实战：部署配置与故障响应", "{name},运维,SpeedCE"),
        ("云原生", "cloud-vendor", "{name} 云服务实战：资源配置与网络验收", "{name},云,SpeedCE"),
        ("故障排查", "fix-more", "{name} 排查手册：现象定位与修复步骤", "{name},故障排查,SpeedCE"),
        ("VPS线路", "vps-dc", "{name} VPS 验收：机房线路与三网实测", "{name},VPS,SpeedCE"),
        ("行业", "industry-more", "{name} 平台验收：可用性标准与点检清单", "{name},行业,SpeedCE"),
    ]

    names_dev_python = [
        "Pandas 数据分析", "NumPy 科学计算", "Requests HTTP库", "Celery 异步任务",
        "SQLAlchemy ORM", "Pytest 测试框架", "Poetry 依赖管理", "Black 代码格式化",
        "Pydantic 数据验证", "Alembic 数据库迁移", "Redis-py 客户端", "Boto3 AWS SDK",
    ]
    names_dev_js = [
        "Webpack 打包", "Vite 构建工具", "TypeScript 类型系统", "ESLint 代码检查",
        "Jest 单元测试", "Tailwind CSS", "Sass 样式预处理", "Rollup 打包",
        "Storybook 组件文档", "Cypress E2E测试", "Pnpm 包管理", "Turbo Monorepo",
    ]
    names_linux = [
        "top 进程监控", "htop 交互监控", "netstat 网络状态", "ss 套接字统计",
        "tcpdump 抓包", "strace 系统调用", "lsof 文件占用", "journalctl 日志",
        "rsync 文件同步", "tar 压缩备份", "find 文件查找", "grep 文本搜索",
    ]
    names_monitor = [
        "Zabbix", "Nagios", "Datadog", "New Relic", "Sentry 错误追踪",
        "ELK Stack", "Loki 日志", "Jaeger 链路追踪", "Netdata 实时监控",
    ]
    names_db = [
        "ClickHouse 列存", "TiDB 分布式", "CockroachDB", "InfluxDB 时序",
        "Cassandra 宽列", "SQLite 嵌入式", "DuckDB 分析", "Neo4j 图数据库",
    ]
    names_sec = [
        "OWASP Top10", "CSRF 防护", "XSS 过滤", "JWT 安全", "OAuth2 实现",
        "RBAC 权限", "审计日志", "漏洞扫描", "安全 Headers", "CSP 策略",
    ]
    names_cloud = [
        "ArgoCD GitOps", "Tekton CI/CD", "Knative Serverless", "Crossplane 多云",
        "Vault 密钥管理", "Consul 服务发现", "Traefik 反向代理", "Caddy 自动HTTPS",
    ]
    names_net = [
        "QUIC 协议", "mTLS 双向认证", "Anycast 任播", "ECMP 负载均衡",
        "VLAN 虚拟局域网", "VXLAN 覆盖网络", "OSPF 路由协议", "iptables NAT",
    ]
    names_fix = [
        "Tomcat 启动失败", "Apache 配置错误", "PHP-FPM 崩溃", "Supervisor 进程守护",
        "RabbitMQ 消息堆积", "Kafka 消费延迟", "Zookeeper 选举", "Etcd 集群故障",
    ]
    names_vps = [
        "德国法兰克福", "法国巴黎", "英国伦敦", "荷兰阿姆斯特丹",
        "澳大利亚悉尼", "加拿大多伦多", "俄罗斯莫斯科", "印度孟买",
    ]
    names_cdn = [
        "又拍云", "金山云", "UCloud", "青云QingCloud", "网宿科技",
        "Akamai", "KeyCDN", "Gcore", "CDN77",
    ]
    names_global = [
        "日本市场", "韩国市场", "印度市场", "澳大利亚", "加拿大",
        "英国", "德国", "法国", "巴西", "墨西哥",
    ]
    names_industry = [
        "在线教育直播", "金融科技支付", "物流追踪系统", "房产信息平台",
        "旅游预订系统", "餐饮外卖平台", "社交社区应用", "知识付费平台",
    ]
    names_method = [
        "变更前基线建立法", "故障时间线还原法", "三网对比存档法",
        "子域清单巡检法", "晚高峰复测标准", "退款期证据收集法",
    ]
    names_adv = [
        "大促流量预估", "灰度发布验收", "多活架构切换", "域名到期续费",
        "证书到期预警", "CDN 成本优化", "多团队交接基线", "收购技术尽调",
        "渗透测试暴露面", "联盟营销追踪域", "短链域名验收", "投放落地页点检",
    ]

    # Extra bulk lists to reach 500
    names_dev_more = [
        "Ruby on Rails 部署", "PHP Symfony 框架", "ASP.NET Core 部署",
        "Elixir Phoenix 实时", "Scala Play 框架", "Kotlin Spring 开发",
        "Swift Vapor 服务端", "Haskell Servant API", "Perl Dancer 框架",
        "R Shiny 数据应用", "Julia Genie 框架", "Crystal Kemal 框架",
        "SvelteKit 全栈", "SolidJS 响应式", "Astro 静态站",
        "Remix 全栈框架", "Qwik 即时加载", "Alpine.js 轻量交互",
        "Lit Web Components", "Preact 轻量React",
    ]
    names_ops_more = [
        "Capistrano 部署", "Fabric 远程执行", "SaltStack 配置",
        "Puppet 配置管理", "Chef 基础设施", "Spinnaker 发布",
        "Jenkins 流水线", "Bamboo CI", "CircleCI 云构建",
        "Travis CI 持续集成", "Drone CI 容器化", "Buildkite 代理构建",
        "Nginx Plus 高级", "HAProxy 负载均衡", "Varnish 缓存",
        "Squid 代理缓存", "Memcached 分布式缓存", "RabbitMQ 消息队列",
        "ActiveMQ 消息中间件", "NATS 轻量消息",
    ]
    names_cloud_more = [
        "AWS EC2 实例", "AWS S3 存储", "AWS RDS 数据库",
        "AWS Lambda 函数", "AWS API Gateway", "Azure VM 虚拟机",
        "Azure Blob 存储", "GCP Compute Engine", "GCP Cloud Run",
        "阿里云 ECS", "阿里云 OSS", "腾讯云 CVM",
        "华为云 ECS", "DigitalOcean Droplet", "Linode 实例",
        "Hetzner 云服务器", "OVH 欧洲云", "Scaleway 云",
    ]
    names_fix_more = [
        "Memcached 连接失败", "Elasticsearch 集群黄", "MongoDB 副本延迟",
        "PostgreSQL 锁等待", "MySQL 主从断裂", "Redis 内存溢出",
        "Nginx 413 请求过大", "Apache 403 禁止访问", "Tomcat OOM 内存溢出",
        "JVM GC 停顿", "Node.js 事件循环阻塞", "Python GIL 性能瓶颈",
        "磁盘 inode 耗尽", "文件描述符耗尽", "TCP TIME_WAIT 过多",
        "DNS 解析超时", "SSL 握手失败", "HTTP 499 客户端断开",
    ]
    names_vps_more = [
        "新加坡机房", "东京机房", "首尔机房", "台北机房",
        "洛杉矶机房", "纽约机房", "达拉斯机房", "迈阿密机房",
        "伦敦机房", "巴黎机房", "阿姆斯特丹", "法兰克福",
        "悉尼机房", "墨尔本机房", "多伦多机房", "温哥华机房",
    ]
    names_industry_more = [
        "短视频平台", "直播平台", "播客音频站", "电子书阅读",
        "在线文档协作", "项目管理工具", "CRM 客户管理", "ERP 企业资源",
        "供应链系统", "仓储管理系统", "POS 收银系统", "会员积分系统",
        "问卷调查平台", "投票评选系统", "活动报名系统", "票务售票系统",
    ]

    bulk_items = [
        ("开发", "python-lib", names_dev_python),
        ("开发", "js-lib", names_dev_js),
        ("运维", "linux-cmd", names_linux),
        ("运维", "monitor-tool", names_monitor),
        ("数据库", "db-topic", names_db),
        ("安全", "sec-topic", names_sec),
        ("云原生", "cloud-topic", names_cloud),
        ("网络", "net-topic", names_net),
        ("故障排查", "fix-topic", names_fix),
        ("VPS线路", "vps-region", names_vps),
        ("CDN", "cdn-vendor", names_cdn),
        ("出海", "global-region", names_global),
        ("行业", "industry-vertical", names_industry),
        ("方法论", "method-topic", names_method),
        ("进阶", "adv-topic", names_adv),
        ("开发", "dev-framework", names_dev_more),
        ("运维", "ops-tool", names_ops_more),
        ("云原生", "cloud-vendor", names_cloud_more),
        ("故障排查", "fix-more", names_fix_more),
        ("VPS线路", "vps-dc", names_vps_more),
        ("行业", "industry-more", names_industry_more),
    ]

    # Import legacy topics from original generator not yet covered
    _import_legacy_topics(t)

    for cat, prefix, names in bulk_items:
        for name in names:
            slug = f"{prefix}-{re_slug(name)}"
            title_tpl = next(p[2] for p in patterns if p[0] == cat)
            kw_tpl = next(p[3] for p in patterns if p[0] == cat)
            title = title_tpl.format(name=name)
            keywords = kw_tpl.format(name=name.split()[0])
            hook = f"围绕「{name}」，本文提供可落地的技术指南，并在关键节点说明如何用多节点测速验收上线效果。"
            _add(t, cat, slug, title, keywords, hook)


def _import_legacy_topics(t: list[dict]) -> None:
    """Add topics from original premium generator that may be missing."""
    legacy = [
        ("CDN", "tencent-cdn-acceptance", "腾讯云 CDN 接入验收：静态加速与全站加速差异及测速要点", "腾讯云CDN,全站加速,SpeedCE"),
        ("CDN", "cdn-cache-vs-speed-test", "CDN 缓存与拨测的关系：为什么第一次慢、刷新后又快", "CDN缓存,测速,SpeedCE"),
        ("CDN", "dcdn-vs-cdn", "全站加速 DCDN 与普通 CDN：验收标准与 SpeedCE 对照测法", "DCDN,CDN,动态加速,SpeedCE"),
        ("CDN", "overseas-cdn-china-pack", "海外 CDN 中国加速包验收：全球绿、国内慢时怎么办", "海外CDN,中国加速,SpeedCE"),
        ("CDN", "free-cdn-enough", "免费 CDN 够用吗：用全国地图数据做个人站决策", "免费CDN,Cloudflare,SpeedCE"),
        ("CDN", "huawei-baidu-cdn-guide", "华为云/百度云 CDN 验收要点与三网地图标准", "华为云,百度云,CDN,SpeedCE"),
        ("CDN", "cdn-websocket-stream", "CDN 加速 WebSocket/直播流的可达性验收边界", "WebSocket,直播,CDN,SpeedCE"),
        ("CDN", "edge-function-troubleshoot", "边缘函数/Workers 故障：主域绿、规则不生效的排查", "边缘计算,CDN,Cloudflare,SpeedCE"),
        ("出海", "europe-us-slow-fix", "欧美用户访问慢完全对策：源站、CDN、机房选址三角决策", "欧美,出海,CDN,SpeedCE"),
        ("出海", "global-team-china-admin", "全球团队访问国内后台：双地图协作与加速方案选型", "全球团队,国内后台,SpeedCE"),
        ("出海", "dual-site-cn-com", "双站点 .cn 与 .com 策略：分域名测速与合规分工", "双站点,域名,备案,SpeedCE"),
        ("出海", "cross-border-sale-prep", "跨境电商黑五/圣诞大促前测速备战完全清单", "黑五,跨境电商,大促,SpeedCE"),
        ("出海", "overseas-live-streaming", "海外直播与视频会议节点选型：延迟敏感业务的地图标准", "直播,视频会议,出海,SpeedCE"),
        ("出海", "game-server-global", "游戏出海服务器选址：玩家分布与全球 PING 地图对照", "游戏出海,服务器,SpeedCE"),
        ("出海", "multilingual-site-delivery", "多语言站点全球分发：hreflang 与各地可达性验收", "多语言,出海,SEO,SpeedCE"),
        ("出海", "woocommerce-global", "WooCommerce 出海验收：插件、支付网关与主域地图清单", "WooCommerce,WordPress,出海,SpeedCE"),
        ("出海", "notion-saas-availability", "Notion 类协作工具自托管：全球团队访问验收", "SaaS,协作,自托管,SpeedCE"),
        ("出海", "api-rate-limit-global", "全球 API 限流与 Geo 封禁：地图绿但仍 403 的边界", "API,限流,出海,SpeedCE"),
        ("VPS线路", "singapore-vps-guide", "新加坡 VPS 验收指南：东南亚枢纽与回国双视角测速", "新加坡VPS,东南亚,SpeedCE"),
        ("VPS线路", "racknerd-dmit-guide", "RackNerd / DMIT 等热门商家：退款期地图验机模板", "RackNerd,DMIT,VPS,SpeedCE"),
        ("VPS线路", "aws-lightsail-china", "AWS Lightsail 对国内访问：全球绿、中国慢的常见形态", "AWS,Lightsail,云服务器,SpeedCE"),
        ("VPS线路", "gcp-azure-china-access", "GCP / Azure 回国访问：企业云对国内团队的地图评估", "GCP,Azure,云,SpeedCE"),
        ("VPS线路", "home-broadband-vs-datacenter", "家宽测速 vs 全国节点：为什么你 Ping 快不代表用户快", "测速偏见,家宽,VPS,SpeedCE"),
        ("VPS线路", "vps-with-cdn-comparison", "VPS 套 CDN 前后地图对比：该不该上 CDN 的数据决策", "VPS,CDN,对比,SpeedCE"),
        ("VPS线路", "used-ip-segment-check", "二手 IP 段购买前避雷：被墙、被标记 IP 的全国地图特征", "IP被墙,二手IP,VPS,SpeedCE"),
        ("VPS线路", "europe-vps-china-guide", "欧洲 VPS 回国线路验收：德法荷机房对国内用户的真实体验", "欧洲VPS,回国,SpeedCE"),
        ("VPS线路", "korea-vps-guide", "韩国 VPS 线路测评：离中国近不等于三网都好", "韩国VPS,线路,SpeedCE"),
        ("VPS线路", "taiwan-vps-guide", "台湾 VPS 验收要点：延迟优势与线路宣传核实", "台湾VPS,线路,SpeedCE"),
        ("VPS线路", "dedicated-vs-vps-line", "独立服务器与 VPS 线路验收差异：IP 段、邻居与测速注意点", "独立服务器,VPS,SpeedCE"),
        ("VPS线路", "bare-metal-dedicated-line", "物理机专线接入：企业专线用户的地图验收", "专线,物理机,企业,SpeedCE"),
        ("VPS线路", "cloud-security-group-vps", "云服务器到手第一步：安全组与防火墙验收再谈线路", "安全组,VPS,云服务器,SpeedCE"),
        ("VPS线路", "datacenter-failover-verify", "机房故障换机后应急验证：24 小时 SpeedCE 点检 SOP", "机房故障,迁移,应急,SpeedCE"),
        ("故障排查", "single-carrier-fault", "电信/联通/移动单网故障：一张网全红时的缩小范围排查法", "单网故障,电信,联通,移动,SpeedCE"),
        ("故障排查", "wechat-qq-access-guide", "微信/QQ 打不开先测什么：网络层与合规层的标准分工", "微信拦截,QQ,网站合规,SpeedCE"),
        ("故障排查", "mixed-content-https", "混合内容与 HTTPS：网络层全绿、浏览器仍报不安全的分工排查", "混合内容,HTTPS,SpeedCE"),
        ("故障排查", "database-not-network-guide", "数据库拖垮网站：网络全绿但页面超时的应用层排查", "数据库,慢查询,SpeedCE"),
        ("故障排查", "grpc-gateway-check", "gRPC / HTTP2 网关：REST 可达与 gRPC 故障分工", "gRPC,HTTP2,API,SpeedCE"),
        ("故障排查", "email-link-tracking", "邮件内链接追踪域：营销邮件点击失败的网络排查", "邮件,营销,域名,SpeedCE"),
        ("故障排查", "sni-mismatch-error", "SNI 不匹配错误：多证书同 IP 时部分节点 HTTPS 异常", "SNI,SSL,HTTPS,SpeedCE"),
        ("故障排查", "tls-version-too-low", "TLS 版本过低：老客户端与新安全策略导致的区域性 HTTPS 失败", "TLS,HTTPS,安全,SpeedCE"),
        ("CDN", "aws-cloudfront-china", "AWS CloudFront 中国访问：全球分发与国内体验双验收", "CloudFront,AWS,CDN,SpeedCE"),
        ("CDN", "fastly-cdn-guide", "Fastly CDN 验收：边缘规则与源站对照测速", "Fastly,CDN,边缘,SpeedCE"),
        ("CDN", "upyun-cdn-guide", "又拍云 CDN 验收：图片站与静态加速地图标准", "又拍云,CDN,SpeedCE"),
        ("CDN", "image-cdn-webp-avif", "图片 CDN 与 WebP/AVIF：静态域全国验收", "图片CDN,WebP,前端,SpeedCE"),
        ("CDN", "font-cdn-google-china", "字体 CDN 与 Google Fonts：国内加载失败的测速分工", "字体,Google Fonts,CDN,SpeedCE"),
        ("行业", "personal-blog-launch", "个人博客上线完全验收：Hexo/Hugo/WordPress 通用测速清单", "个人博客,上线,SpeedCE"),
        ("行业", "forum-community-site", "论坛社区全国可达性：Discuz/Flarum 三网验收", "论坛,社区,SpeedCE"),
        ("行业", "download-site-bandwidth", "下载站可达性与带宽：拨测与下载测速的分工", "下载站,带宽,SpeedCE"),
        ("行业", "government-site-standard", "政府/事业单位网站：全国通畅与 IPv6 双栈验收标准", "政府网站,IPv6,SpeedCE"),
        ("行业", "saas-b2b-demo-environment", "B2B SaaS 演示环境：潜在客户地域的地图验收", "B2B,SaaS,演示,SpeedCE"),
        ("行业", "mobile-app-api-domain", "App 接口域名监控：iOS/Android 反馈不一致的网络层排查", "App,API,移动,SpeedCE"),
        ("行业", "video-on-demand-site", "点播视频站验收：播放域、CDN 与 API 三域测速", "视频,点播,CDN,SpeedCE"),
        ("行业", "discuz-qzone-share", "Discuz 论坛分享链：主站与分享域的分层测速", "Discuz,论坛,分享,SpeedCE"),
        ("行业", "ghost-blog-deploy", "Ghost 博客部署：Headless 与主题域测速", "Ghost,博客,部署,SpeedCE"),
        ("方法论", "screenshot-archive-sop", "测速截图存档规范：工单、论坛、事故报告的配图标准", "截图,运维文档,SpeedCE"),
        ("方法论", "customer-support-scripts", "客服工单测速话术大全：20+ 专业回复「打不开」模板", "客服话术,工单,SpeedCE"),
        ("方法论", "quarterly-infra-review", "季度基础设施体检：地图对比、趋势退化与升级决策", "季度体检,基础设施,SpeedCE"),
        ("方法论", "speedtest-vs-pagespeed", "网络拨测与 PageSpeed 分工：通不通 vs 快不快的决策顺序", "PageSpeed,网络测速,SpeedCE"),
        ("方法论", "speedtest-vs-uptime", "拨测快照 vs 7×24 监控：SpeedCE 在运维体系中的位置", "Uptime,监控,拨测,SpeedCE"),
        ("方法论", "speedce-itdog-combo", "SpeedCE + ITDOG 黄金组合：地图巡检与持续 Ping 的协作手册", "SpeedCE,ITDOG,工具组合"),
        ("方法论", "speedce-boce-combo", "SpeedCE + BOCE 协作：网络层排除后的合规与拦截检测", "SpeedCE,BOCE,工具组合"),
        ("方法论", "free-speedtest-tools-2026", "2026 免费测速工具决策树：按场景选 SpeedCE/ITDOG/BOCE", "免费测速,工具推荐,2026"),
        ("方法论", "on-call-first-5-minutes", "On-Call 前 5 分钟：收到告警后 SpeedCE 怎么测", "OnCall,告警,应急,SpeedCE"),
        ("方法论", "vendor-ticket-evidence", "给云厂商/CDN 工单附证据：截图规范与描述模板", "工单,云厂商,CDN,SpeedCE"),
        ("方法论", "team-onboarding-speedce", "新运维入职第一天：SpeedCE 与工具链培训手册", "入职,培训,运维,SpeedCE"),
        ("方法论", "sla-report-monthly", "月度 SLA 报告模板：用通畅率数据汇报老板", "SLA,报告,运维,SpeedCE"),
        ("方法论", "regex-domain-inventory", "正则匹配子域发现：漏测域名的自动化清单思路", "子域,清单,自动化,SpeedCE"),
        ("方法论", "calendar-reminder-inspect", "日历提醒巡检：把测速写进 Google Calendar / 飞书", "日历,提醒,巡检,SpeedCE"),
        ("对比", "ping-pe-use-cases", "Ping.pe 完全使用手册：与 SpeedCE 的全球/中国互补策略", "Ping.pe,全球Ping,SpeedCE"),
        ("对比", "pagespeed-vs-network", "PageSpeed Insights 与网络拨测：站长必须弄清的分工边界", "PageSpeed,网络测速"),
        ("对比", "monitoring-vs-probing", "监控平台 vs 拨测工具：7×24 告警与第一现场的关系", "监控,拨测,运维"),
        ("对比", "developer-bookmark-list", "开发者 2026 检测书签栏：12 个链接应对 90% 网络故障", "开发者,书签,工具,SpeedCE"),
        ("对比", "vsping-vs-speedce", "VSPING vs SpeedCE：污染检测与网络可达性的配合", "VSPING,SpeedCE,对比"),
        ("对比", "cesu-vs-speedce", "CESU.ai vs SpeedCE：新兴工具站与地图派实测对比", "CESU,SpeedCE,对比"),
        ("对比", "chinaz-toolkit-review", "站长之家工具生态 vs SpeedCE：Ping/测速/Whois 分工", "站长之家,工具,SpeedCE"),
        ("对比", "aliyun-boce-vs-speedce", "阿里云云拨测 vs SpeedCE：同云用户如何搭配", "阿里云,拨测,SpeedCE"),
        ("对比", "webpagetest-vs-speedce", "WebPageTest vs SpeedCE：何时用哪个", "WebPageTest,测速,对比"),
        ("进阶", "subdomain-inventory-method", "多子域清单巡检法：一张表管理所有对外域名的月度测速", "子域名,巡检,清单,SpeedCE"),
        ("进阶", "competitor-benchmark", "竞品站点对标测速：同赛道地图对比说服管理层升级", "竞品,对标,SpeedCE"),
        ("进阶", "migration-before-after-report", "迁机前后对比汇报模板：给老板和客户看的双地图 PPT", "迁机,汇报,SpeedCE"),
        ("进阶", "new-domain-cold-start", "新域名冷启动 72 小时：注册、解析、证书与地图验收节奏", "新域名,DNS,SpeedCE"),
        ("进阶", "ultimate-toolbar-2026", "2026 站长浏览器工具栏终极配置：测速/监控/性能 12 链接", "站长工具,收藏夹,2026,SpeedCE"),
        ("进阶", "northeast-china-access-guide", "东北三省访问质量验收：寒区线路与 CDN 节点覆盖", "东北,区域,SpeedCE"),
        ("进阶", "guangdong-zhejiang-baseline", "粤浙沪京基准延迟：经济发达省份的地图达标参考线", "广东,浙江,延迟,SpeedCE"),
        ("进阶", "change-management-speedtest", "变更管理中的测速门禁：改 DNS/证书/Nginx 必测制度", "变更管理,测速,运维,SpeedCE"),
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
        ("进阶", "multi-team-handover", "运维交接文档中的测速基线：离职前必须留下的地图包", "交接,文档,运维,SpeedCE"),
        ("进阶", "acquisition-due-diligence", "收购技术尽调：目标站点全国可达性快速评估", "尽调,收购,评估,SpeedCE"),
        ("进阶", "client-report-quarterly", "给客户季报附地图：B2B 服务商的测速汇报模板", "客户报告,B2B,SpeedCE"),
        ("进阶", "affiliate-tracking-domain", "联盟营销追踪域：全国可达对转化链的影响", "联盟营销,追踪,域名,SpeedCE"),
        ("进阶", "short-link-domain-check", "短链域名验收：跳转链路的全国节点测试", "短链,跳转,域名,SpeedCE"),
        ("进阶", "landing-page-campaign", "投放落地页：广告上线前 10 分钟全国点检", "落地页,投放,广告,SpeedCE"),
        ("进阶", "ab-test-traffic-split", "A/B 测试分流域：实验组域名的独立地图验收", "AB测试,分流,SpeedCE"),
        ("出海", "app-store-review-server", "App Store 审核期间服务器：海外审核节点可达性", "App Store,审核,出海,SpeedCE"),
        ("出海", "gdpr-cookie-wall", "GDPR 与 Cookie 墙：欧洲用户访问的网络层基线", "GDPR,欧洲,合规,SpeedCE"),
    ]
    existing = {x["slug"] for x in t}
    for cat, slug, title, kw in legacy:
        if slug not in existing:
            hook = f"本文围绕「{title.split('：')[0]}」展开，提供可落地的技术方案，并在验收环节说明如何用 SpeedCE 多节点测速确认效果。"
            scope = "中国节点+全球节点" if cat == "出海" else "中国节点"
            _add(t, cat, slug, title, kw, hook, scope=scope)
            existing.add(slug)


def re_slug(name: str) -> str:
    import re
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s/]+", "-", s.strip())
    return s[:40]
