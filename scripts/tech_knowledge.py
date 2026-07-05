"""Deep technical knowledge base for 15k-20k char long-form articles."""

from __future__ import annotations

import hashlib
import random
from typing import Any

# Each domain entry: principles, terms, architecture, pitfalls, advanced, ops_steps
DOMAIN_KB: dict[str, dict[str, Any]] = {}

def _kb(domain: str, **kwargs: Any) -> None:
    DOMAIN_KB[domain] = kwargs


_kb("dns",
principles=[
    """**DNS（Domain Name System，域名系统）** 是互联网的「电话簿」。人类记住 `example.com`，
    路由器却只认 IP 地址。DNS 的职责，就是在用户输入域名后，通过分层查询把域名翻译成 IP。
    整个过程涉及：浏览器缓存 → 操作系统缓存 → 本地递归解析器（通常是运营商 DNS）→
    根域名服务器 → 顶级域（.com）→ 权威 DNS（你的域名服务商）。""",
    """**TTL（Time To Live，生存时间）** 是 DNS 记录里最重要的数字之一，单位是秒。
    TTL=300 表示解析结果可被缓存 5 分钟；TTL=86400 表示 24 小时。迁机前把 TTL 调低到 300，
    能大幅缩短全球各地「还指着旧 IP」的时间窗口。很多人迁机后投诉不断，根因就是迁机前没降 TTL。""",
    """**递归解析 vs 权威解析**：你电脑上的 `dig` 或 `nslookup` 问的是递归解析器（如 223.5.5.5），
    它替你跑完整条链路；权威 DNS 只回答「这个域名归我管，记录是 xxx」。排障时两者都要查：
    权威记录错了，全球都错；权威对了但递归缓存旧值，表现为「部分地区、逐渐恢复」。""",
    """**分线路解析（智能 DNS / GeoDNS）** 让同一域名在不同运营商或地区返回不同 IP。
    电信用户走电信优化线路，联通走联通，海外走海外源站——这是 CDN 和跨国业务的常见架构。
    但若某条线路配错，地图上会呈现「仅电信红」或「仅某省红」，而不是全国红。""",
],
terms=[
    ("A 记录", "把域名直接指向 IPv4 地址", "最基础的记录类型。`www.example.com → 1.2.3.4`。改 A 记录后，受 TTL 和各级缓存影响，全球生效需要时间。"),
    ("AAAA 记录", "把域名指向 IPv6 地址", "双栈站点必须同时维护 A 和 AAAA。只改 A 不改 AAAA，IPv6 用户会打到错误地址。"),
    ("CNAME 记录", "域名别名，指向另一个域名", "CDN 接入典型做法：`www` CNAME 到 `xxx.cdn.com`。注意 CNAME 链不能循环，且 CNAME 与 MX 等记录互斥。"),
    ("NS 记录", "指定域名的权威 DNS 服务器", "换 DNS 服务商本质是改 NS。NS 变更生效慢，通常 24-48 小时，期间可能出现「新旧 DNS 交替」。"),
    ("MX 记录", "邮件服务器地址", "不影响网站访问，但迁 DNS 时漏配 MX 会导致邮件收不到。"),
    ("TXT 记录", "文本记录，常用于 SPF/DKIM/域名验证", "Let's Encrypt DNS-01 验证、Google Search Console 验证都靠 TXT。"),
    ("TTL", "缓存存活时间（秒）", "迁机、切 CDN 前调到 300；稳定后可调回 3600 或更高以减少查询压力。"),
    ("DNSSEC", "DNS 安全扩展，防劫持篡改", "配置错误会导致部分解析器验证失败，表现为 sporadic 解析异常。"),
],
architecture="""```
用户浏览器
    ↓ 查询 example.com
本地缓存（浏览器/OS）→ 命中则直接返回
    ↓ 未命中
递归 DNS（运营商 223.5.5.5 / 8.8.8.8）
    ↓
根 DNS（.）→ 顶级域 DNS（.com）→ 权威 DNS（你的服务商）
    ↓ 返回 A/AAAA/CNAME
递归 DNS 缓存（受 TTL 约束）→ 返回给用户
```""",
pitfalls=[
    "迁机前未降低 TTL，导致 24-48 小时内各地缓存不一致",
    "CNAME 链过长或指向错误，CDN 接入后部分省份解析失败",
    "分线路 DNS 某条线路 IP 配错，表现为单运营商或单省异常",
    "只验证了本地 dig，未用全国多节点验证真实用户视角",
    "权威 DNS 改了但 CDN 控制台未同步，回源指向旧 IP",
    "DNS 与 SSL 证书不同步改，子域漏配导致 HTTPS 红",
    "把 DNS 问题当服务器问题，盲目重启或迁机",
    "忽略 DNS 传播的时间维度，测一次就宣布成功",
],
advanced=[
    "使用 `dig +trace` 追踪完整解析链路，定位哪一层返回了错误结果",
    "对比多个公共 DNS（223.5.5.5、119.29.29.29、8.8.8.8）的结果差异",
    "建立 DNS 变更 Runbook：降 TTL → 改记录 → 每 10min 多节点复测 → 72h 后恢复 TTL",
    "对关键域名配置 DNS 监控（UptimeRobot DNS 监控或自建脚本）",
],
)

_kb("ssl",
principles=[
    """**HTTPS = HTTP + TLS（Transport Layer Security，传输层安全）**。
    TLS 在 TCP 连接建立后、HTTP 请求发出前，先完成握手：协商加密算法、验证服务器证书、
    交换会话密钥。用户看到的「小锁」代表 TLS 握手成功且证书被浏览器信任。""",
    """**证书链（Certificate Chain）** 结构：叶子证书（你的域名）→ 中间证书（CA 签发）→ 根证书（内置在浏览器）。
    若 Nginx 只配了叶子证书没配中间证书，部分浏览器/拨测节点会报链不完整——
    表现为 HTTPS 红、HTTP 绿。`fullchain.pem` 应包含叶子+中间。""",
    """**SNI（Server Name Indication）** 让同一 IP 上多个 HTTPS 站点各用各的证书。
    客户端在 TLS 握手时告诉服务器「我要访问 api.example.com」，服务器据此选择对应证书。
    老设备或不发 SNI 的客户端可能拿到错误证书。""",
    """**Let's Encrypt** 提供免费 90 天证书，通过 ACME 协议自动续签。HTTP-01 验证需要 80 端口可达；
    DNS-01 验证需要添加 TXT 记录。续签失败若未告警，90 天后 HTTPS 突然全国红。""",
],
terms=[
    ("SAN", "Subject Alternative Name，证书覆盖的域名列表", "一张证书可覆盖 www、api、*.example.com。漏了 api 子域，api 就会 HTTPS 失败。"),
    ("CN", "Common Name，证书主域名（旧标准）", "现在以 SAN 为准，CN 仅作兼容。"),
    ("OV/EV/DV", "证书验证级别", "DV 域名验证最常见（Let's Encrypt）；EV 显示绿色公司名，多用于金融。"),
    ("HSTS", "HTTP Strict Transport Security", "强制浏览器只用 HTTPS。开启后若证书出问题，用户无法通过 HTTP 回退访问。"),
    ("OCSP Stapling", "在线证书状态协议装订", "Nginx 可预取 OCSP 响应，加快握手、减轻 CA 压力。"),
    ("TLS 1.2/1.3", "传输层安全协议版本", "TLS 1.0/1.1 已废弃。过严配置会导致老客户端失败。"),
    ("mTLS", "双向 TLS，客户端也出示证书", "常见于服务网格、金融 API，配置复杂。"),
    ("证书透明度 CT", "Certificate Transparency 日志", "Let's Encrypt 自动满足。企业内网证书可能不需要。"),
],
architecture="""```
TCP 三次握手（IP:443）
    ↓
TLS ClientHello（含 SNI: api.example.com）
    ↓
TLS ServerHello + 证书链 + ServerKeyExchange
    ↓
客户端验证证书（有效期、域名匹配、链完整、CRL/OCSP）
    ↓
密钥交换 → 加密通道建立
    ↓
HTTP 请求/响应（已加密）
```""",
pitfalls=[
    "证书过期未告警，凌晨 HTTPS 全国红",
    "只配 cert.pem 没配 fullchain.pem，链不完整",
    "通配符证书 *.example.com 不覆盖 api.staging.example.com",
    "CDN 证书和源站证书混淆，只修了一边",
    "开启 HSTS 后证书故障无法 HTTP 回退",
    "TLS 版本配太严，老 Android 客户端失败",
    "SNI 未正确配置，多域同 IP 时拿错证书",
    "用自签证书未导入客户端信任，拨测全红",
],
advanced=[
    "用 `openssl s_client -connect host:443 -servername host` 检查证书链和 SNI",
    "配置 certbot 续签失败邮件/webhook 告警",
    "生产环境启用 OCSP Stapling 和 TLS 1.3",
    "证书变更纳入变更管理，改完立即 SpeedCE 复测",
],
)

_kb("nginx",
principles=[
    """**Nginx** 是高性能 Web 服务器和反向代理。事件驱动（epoll/kqueue）架构使其能用极少内存
    处理数万并发连接。作为反向代理时，Nginx 接收客户端请求，转发给后端（PHP-FPM、Node、Java），
    再把响应返回客户端——用户看到的是 Nginx 的 IP 和证书，后端可以藏在内部网络。""",
    """**server_name** 决定哪个 server 块处理请求。请求头里的 `Host` 与 `server_name` 匹配。
    若 `api.example.com` 没有对应 server 块，会落入 default_server——可能用错证书或返回 404。
    每个对外子域都应有独立 server 块。""",
    """**proxy_pass 末尾斜杠陷阱**：`proxy_pass http://backend/;`（有斜杠）会剥掉 location 前缀；
    `proxy_pass http://backend;`（无斜杠）会保留完整 URI。配错导致 404 或路径重复。""",
    """**upstream 健康检查**：多台后端时，一台挂掉若未及时摘除，用户会 sporadic 502。
    配合 `max_fails` 和 `fail_timeout`，或上层负载均衡探活。""",
],
terms=[
    ("worker_processes", "工作进程数", "通常 = CPU 核数。每进程可处理数千连接。"),
    ("worker_connections", "单进程最大连接数", "与系统 ulimit 有关，需一并调大。"),
    ("location", "URL 路径匹配规则", "最长前缀匹配。正则 location 用 `~` 或 `~*`。"),
    ("try_files", "按顺序尝试文件", "SPA 常用 `try_files $uri /index.html`。"),
    ("proxy_buffering", "代理缓冲", "关闭可减少延迟，但增加后端压力。"),
    ("gzip", "响应压缩", "文本类资源可压缩 70%+，显著降低传输时间。"),
    ("limit_req", "请求速率限制", "防 CC 攻击，但阈值太低会误伤正常用户。"),
    ("access_log / error_log", "访问日志与错误日志", "502/504 第一时间看 error.log 的 upstream 信息。"),
],
architecture="""```
客户端 → Nginx:443（SSL 终结）
              ↓ proxy_pass
         upstream 池
         ├─ 127.0.0.1:3000 (Node)
         ├─ 127.0.0.1:9000 (PHP-FPM)
         └─ 10.0.1.5:8080 (Java)
              ↓
         响应原路返回
```""",
pitfalls=[
    "server_name 漏配子域，请求落入 default_server",
    "proxy_pass 斜杠导致 URI 路径错误",
    "SSL 证书路径写错，reload 不报错但 HTTPS 失败",
    "upstream 一台后端挂了导致 sporadic 502",
    "client_max_body_size 太小，上传大文件 413",
    "未配置 proxy_set_header Host，后端拿到错误 Host",
    "日志磁盘满导致 Nginx 无法写日志进而异常",
    "改配置未 nginx -t 测试就 reload",
],
advanced=[
    "用 `nginx -T` 查看完整生效配置",
    "配置 stub_status 或 nginx-prometheus-exporter 监控",
    "大流量站点调优 worker、keepalive、open_file_cache",
    "每个对外域名独立 access/error log 便于排障",
],
)

_kb("docker",
principles=[
    """**Docker 容器** 是轻量级隔离进程，共享宿主机内核但拥有独立文件系统、网络和进程空间。
    与虚拟机不同，容器不包含完整 OS，启动秒级、资源占用小。但「容器内正常」不等于「外部可访问」——
    端口映射、网络模式、安全组是三层独立检查。""",
    """**网络模式**：`bridge`（默认，需端口映射 `-p 8080:80`）、`host`（直接用宿主机网络）、
    `none`（无网络）。生产常用 bridge + 端口映射或 docker-compose 网络。""",
    """**数据卷（Volume）** 持久化数据，容器删除后数据仍在。数据库容器必须挂载 volume，
    否则重建容器数据丢失。""",
    """**健康检查（HEALTHCHECK）** 让 Docker 知道容器内服务是否真正就绪。
    仅 `docker ps` 显示 Up 不够——进程在但端口未监听、应用死锁，外部仍会超时。""",
],
terms=[
    ("镜像 Image", "只读模板，含应用和依赖", "分层存储，相同层可复用。`docker build` 构建。"),
    ("容器 Container", "镜像的运行实例", "`docker run` 创建。可启停删，不应当虚拟机长期 SSH 进去改。"),
    ("Dockerfile", "构建镜像的脚本", "FROM/COPY/RUN/CMD/EXPOSE 等指令。多阶段构建可减小镜像体积。"),
    ("docker-compose", "多容器编排 YAML", "定义 services、networks、volumes，一键启停整套环境。"),
    ("端口映射 -p", "宿主机端口:容器端口", "`-p 443:443` 把容器 443 映射到宿主机 443。"),
    ("ENTRYPOINT vs CMD", "容器启动命令", "ENTRYPOINT 固定，CMD 可覆盖。理解两者区别避免启动失败。"),
    ("registry", "镜像仓库", "Docker Hub、阿里云 ACR、Harbor 私有仓库。"),
    ("namespace/cgroups", "内核隔离机制", "容器隔离的底层原理，资源限制靠 cgroups。"),
],
architecture="""```
docker run -p 443:443 myapp
    ↓
宿主机 iptables NAT 规则（DNAT 443→容器IP:443）
    ↓
容器网络栈（bridge veth）
    ↓
容器内进程监听 0.0.0.0:443
    ↓
（若进程只监听 127.0.0.1:443，外部映射也无效）
```""",
pitfalls=[
    "容器内 curl localhost 通过，但未做端口映射",
    "安全组未放行映射的宿主机端口",
    "应用 bind 127.0.0.1 而非 0.0.0.0",
    "docker-compose ports 写错（容器端口与监听端口不一致）",
    "镜像过大导致部署慢，但未影响网络（别和连通性混淆）",
    "未配置健康检查，负载均衡打到未就绪容器",
    "容器日志撑满磁盘",
    "生产用 latest 标签，版本不可追溯",
],
advanced=[
    "多阶段 Dockerfile 减小镜像，加快部署",
    "docker-compose 配置 healthcheck 和 restart policy",
    "用 `docker inspect` 查端口映射和 IP",
    "部署后从外部 SpeedCE 验收，不只 docker ps",
],
)

_kb("k8s",
principles=[
    """**Kubernetes（K8s）** 是容器编排平台，自动调度 Pod、服务发现、滚动更新、自愈。
    外部流量路径：Ingress → Service → Pod。任何一层断了，公网域名就红——
    即使 `kubectl get pods` 全 Running。""",
    """**Pod** 是最小调度单元，可含一个或多个容器。Pod IP 在重建后会变，
    因此不直接对外暴露 Pod，而是通过 Service 提供稳定虚拟 IP（ClusterIP）或负载均衡。""",
    """**Service** 通过 Label Selector 关联 Pod。Selector 与 Pod label 不匹配时，
    Endpoints 为空，Ingress 转发无目标 → 502。""",
    """**Ingress** 是七层路由入口，需 Ingress Controller（如 nginx-ingress、traefik）实际生效。
    只创建 Ingress 资源而不装 Controller，规则不会执行。""",
],
terms=[
    ("Deployment", "无状态应用部署", "管理 ReplicaSet，支持滚动更新和回滚。"),
    ("StatefulSet", "有状态应用", "Pod 有固定网络标识和持久卷，适合数据库。"),
    ("ConfigMap/Secret", "配置和密钥", "注入环境变量或挂载文件，Secret 存证书等敏感信息。"),
    ("Ingress", "HTTP/HTTPS 路由规则", "按 host/path 转发到不同 Service。"),
    ("Namespace", "资源隔离", "dev/staging/prod 分命名空间。"),
    ("HPA", "水平自动扩缩容", "按 CPU/自定义指标增减 Pod 数。"),
    ("Probe", "存活/就绪探针", "liveness 失败重启 Pod；readiness 失败从 Service 摘除。"),
    ("PV/PVC", "持久卷声明", "Pod 重启后数据不丢。"),
],
architecture="""```
Internet → LoadBalancer / NodePort
              ↓
         Ingress Controller
              ↓ Ingress rules (host/path)
         Service (ClusterIP)
              ↓ kube-proxy / iptables
         Pod(s) → Container:port
```""",
pitfalls=[
    "Ingress Controller 未安装或未运行",
    "Service selector 与 Pod label 不匹配，Endpoints 空",
    "readinessProbe 配置错误，Pod 永不 Ready",
    "镜像 pull 失败但旧 Pod 还在，表现为间歇异常",
    "Resource limit 太低导致 OOMKilled",
    "只测集群内 curl，未测公网域名",
    "TLS Secret 与 Ingress 域名不匹配",
    "滚动更新时 maxUnavailable 导致短暂不可用",
],
advanced=[
    "`kubectl describe ingress/service/endpoints` 三板斧",
    "配置 PodDisruptionBudget 保障可用性",
    "用 Helm 管理复杂应用发布",
    "公网域名 SpeedCE 验收纳入 CI/CD 流水线",
],
)

_kb("vps",
principles=[
    """**VPS（Virtual Private Server）** 是虚拟化的服务器实例，与物理机相比共享硬件但隔离资源。
    选购 VPS 时，CPU/内存/磁盘是明面上的参数，**线路质量**才是影响用户体验的关键——
    而线路由机房位置、上游运营商、是否 CN2/CMI 优化决定，不能只看 ping 数字。""",
    """**CN2（China Telecom Next Generation Network）** 是电信下一代承载网，分 GT（普通）和 GIA（Global Internet Access，精品）。
    GT 晚高峰可能拥堵；GIA 延迟低且稳定但贵且稀缺。商家说「CN2」要追问是 GT 还是 GIA。""",
    """**BGP（Border Gateway Protocol）** 在多线机房表示电信/联通/移动各有入口。
    真 BGP 三网延迟应较均衡；假 BGP 可能只有电信能看，移动全红。""",
    """**CMI（China Mobile International）** 移动国际出口优化。中国移动用户占比超 50%，
    不单独测移动地图等于放弃一半潜在用户。CMI/CMIN2 是否真优化，地图说了算。""",
    """**国际出口拥堵**：晚高峰（20:00-22:00）国际带宽打满，延迟飙升、丢包增加。
    商家下午给的测试 IP 往往最美——你必须在晚高峰复测。""",
],
terms=[
    ("CN2 GT", "电信普通 CN2 线路", "性价比尚可，晚高峰可能堵。"),
    ("CN2 GIA", "电信精品 CN2", "延迟稳、丢包低，贵且商家常虚假宣传。"),
    ("CMI", "移动国际优化", "移动用户验收必看。"),
    ("BGP 多线", "多运营商接入", "三网应均衡，用地图验证而非文案。"),
    ("ICMP 禁 Ping", "云厂商默认屏蔽 Ping", "验机改看 HTTPS 通畅率，别被 Ping 超时吓到。"),
    ("带宽计费", "按流量或固定带宽", "「不限流量」可能有速度上限或超量限速。"),
    ("IP 被墙", "GFW 封锁", "典型特征：全球绿、中国红。"),
    ("超售", "宿主机过载", "邻居吵闹导致延迟抖动，地图表现为 sporadic 红。"),
],
architecture="""```
你的 VPS (IP: x.x.x.x)
    ↓ 机房上游
机房出口 → 国际骨干 / CN2 / CMI
    ↓ 跨境链路
中国电信/联通/移动 各省城域网
    ↓
终端用户（家宽/4G/5G）
```""",
pitfalls=[
    "只看本地 ping，未用全国三网地图验收",
    "下午测完美，晚高峰移动全红",
    "信商家「三网直连」文案，未实测",
    "测试 IP 与正式 IP 线路不同",
    "被墙 IP 付款后才发现",
    "禁 Ping 误判线路差",
    "不买移动优化却面向国内全用户",
    "过了退款期才发现问题",
],
advanced=[
    "退款期三次测速：到账日、第3天、第7天晚高峰",
    "三网截图 + 通畅率数字存档",
    "对照测试 IP 与正式 IP",
    "HostLoc 发帖用地图说话，比吵架有效",
],
)

_kb("cdn",
principles=[
    """**CDN（Content Delivery Network，内容分发网络）** 在全球/全国部署边缘节点，
    把静态资源（甚至动态内容）缓存到离用户近的节点，减少回源距离和源站压力。
    用户访问 `cdn.example.com` 时，DNS 解析到最近边缘节点，边缘有缓存则直接返回，无缓存则回源拉取。""",
    """**回源（Origin Pull）** 是边缘节点向你的源站请求内容的过程。回源失败（源站 502、
    超时、安全组拦 CDN IP）表现为 CDN 域名红而源站 IP 可能绿。排障必须对照测。""",
    """**缓存键（Cache Key）** 决定什么算「同一份缓存」。通常含 URL、部分 Header。
    带 Cookie 的请求可能不被缓存。`?v=hash` 可强制刷新静态资源缓存。""",
    """**切量** 是把 DNS 从源站 IP 改到 CDN CNAME 的过程。全球 DNS 缓存不同步，
    切量后 72 小时内要持续多节点复测，不能半小时宣布成功。""",
],
terms=[
    ("边缘节点 Edge", "CDN 分布的缓存服务器", "离用户近，降低延迟。"),
    ("源站 Origin", "你的真实服务器", "CDN 只是代理层，源站挂了 CDN 也救不了。"),
    ("CNAME 接入", "域名 CNAME 到 CDN", "最常见接入方式。"),
    ("回源 Host", "回源时带的 Host 头", "配错会导致源站虚拟主机不匹配。"),
    ("缓存刷新 Purge", "主动清除边缘缓存", "发版后必做，否则用户看旧内容。"),
    ("HTTPS 证书", "边缘证书", "可与源站证书不同，分别管理。"),
    ("DCDN/全站加速", "动态内容也走 CDN", "适合 API 加速，比纯静态 CDN 贵。"),
    ("预热 Preload", "提前把资源推到边缘", "大促前减少首发回源压力。"),
],
architecture="""```
用户 → DNS 解析到 CDN 边缘 IP
         ↓
    边缘节点查缓存
    ├─ 命中 → 直接返回（快）
    └─ 未命中 → 回源到 Origin
                  ↓
              源站生成/返回内容
                  ↓
              边缘缓存 + 返回用户
```""",
pitfalls=[
    "只测 CDN 域不测源站，无法区分故障层",
    "切量后未做 72 小时点检",
    "回源 IP 未加源站白名单",
    "CDN 证书过期",
    "缓存脏数据未刷新",
    "WebSocket 走了不支持 WS 的 CDN",
    "源站慢导致 CDN 更慢",
    "切量半小时就宣布成功",
],
advanced=[
    "源站 IP 与 CDN 域名对照测速",
    "建立 T+0 到 T+72 点检表",
    "静态资源文件名加 content hash",
    "大促前预热关键 URL",
],
)

_kb("linux",
principles=[
    """**Linux 服务器运维** 核心能力：进程管理、网络诊断、日志分析、权限与安全。
    网站「打不开」时，标准顺序：进程是否运行 → 端口是否监听 → 防火墙是否放行 →
    外部网络是否可达。很多新手在第一步就卡住——SSH 能登不代表 Web 服务正常。""",
    """**systemd** 是现代 Linux 的服务管理器。`systemctl status nginx` 看状态，
    `journalctl -u nginx` 看日志。`enabled` 表示开机自启，`active (running)` 才是真的在跑。""",
    """**防火墙双层**：云安全组（控制台）+ 系统防火墙（ufw/iptables/firewalld）。
    两层都要放行 80/443，漏任何一层都表现为全国红。""",
],
terms=[
    ("ss / netstat", "查看端口监听", "`ss -tlnp` 看 TCP 监听端口和进程。"),
    ("journalctl", "systemd 日志", "`journalctl -u nginx -f` 实时跟踪。"),
    ("ulimit", "进程资源限制", "文件描述符不够会导致 too many open files。"),
    ("iptables/nftables", "内核防火墙", "与安全组独立，都要查。"),
    ("cron", "定时任务", "错配可能导致定时把 CPU 打满。"),
    ("logrotate", "日志轮转", "配置失败会导致磁盘满。"),
    ("load average", "系统负载", "高负载时响应变慢，可能表现为超时。"),
    ("OOM Killer", "内存不足杀进程", "内存耗尽时内核杀进程，服务突然挂。"),
],
architecture="""```
外部请求 → 云安全组（入站规则）
              ↓ 放行
         iptables/ufw
              ↓ 放行
         进程监听 0.0.0.0:443
              ↓
         应用处理请求
```""",
pitfalls=[
    "SSH 能登就以为服务正常",
    "只配了安全组忘了系统防火墙",
    "磁盘满导致服务假死",
    "日志撑满磁盘",
    "cron 任务打满 CPU",
    "OOM 后进程被杀未告警",
    "改配置未测试就重启",
    "未配置 logrotate",
],
advanced=[
    "On-Call Runbook 第一步：SpeedCE 测影响面",
    "变更管理加「测速截图已附」",
    "月度三网截图存档对比",
    "磁盘/内存/CPU 告警与网络告警联动",
],
)

# Generic fallback for domains without specific KB
_kb("default",
principles=[
    """技术运维的核心方法论：**观测 → 假设 → 验证 → 修复 → 复测**。
    不要跳步。用户说「打不开」时，你的第一反应应是确认影响范围——是全国还是局部？
    是持续还是间歇？是单运营商还是三网？数据比直觉可靠。""",
    """**多节点拨测** 解决的是「单点偏见」：你在上海办公室测正常，不代表新疆移动用户正常。
    全国地图把每个省份、每个运营商的可达性可视化，是网络层验收的客观标准。""",
],
terms=[
    ("多节点拨测", "从多地发起真实访问", "SpeedCE 核心能力。"),
    ("通畅率", "成功探测/总探测", "≥95% 为国内主站建议达标线。"),
    ("三网分离", "电信/联通/移动独立看", "定位运营商级问题。"),
    ("对照测", "两目标同时测", "CDN vs 源站、迁机前后。"),
],
architecture="""```
变更/故障 → SpeedCE 多节点测速
    ↓
判断影响面（全国/局部/单网）
    ↓
缩小层级（DNS/证书/CDN/源站/应用）
    ↓
修复 → 复测 → 存档
```""",
pitfalls=[
    "单点测试下结论",
    "跳步骤盲目换服务器",
    "不看地图只看平均延迟",
    "变更后不复测",
    "不截图存档",
    "忽视移动用户",
    "不区分网络层和应用层",
    "测一次就宣布成功",
],
advanced=[
    "建立变更必测门禁",
    "月度三网体检",
    "事故复盘附地图时间线",
    "工具栏固定 SpeedCE 书签",
],
)


def detect_domain(slug: str, title: str, category: str) -> str:
    text = f"{slug} {title} {category}".lower()
    rules = [
        ("dns", "dns"), ("domain", "dns"), ("解析", "dns"), ("geodns", "dns"),
        ("ssl", "ssl"), ("tls", "ssl"), ("https", "ssl"), ("certificate", "ssl"), ("证书", "ssl"),
        ("nginx", "nginx"), ("apache", "nginx"), ("proxy", "nginx"), ("反向代理", "nginx"),
        ("docker", "docker"), ("container", "docker"), ("compose", "docker"),
        ("k8s", "k8s"), ("kubernetes", "k8s"), ("ingress", "k8s"), ("helm", "k8s"),
        ("vps", "vps"), ("cn2", "vps"), ("bgp", "vps"), ("线路", "vps"), ("机房", "vps"),
        ("cdn", "cdn"), ("cloudflare", "cdn"), ("回源", "cdn"), ("边缘", "cdn"),
        ("linux", "linux"), ("systemd", "linux"), ("firewall", "linux"), ("iptables", "linux"),
    ]
    for kw, dom in rules:
        if kw in text:
            return dom
    cat_map = {
        "VPS线路": "vps", "CDN": "cdn", "故障排查": "dns", "网络": "linux",
        "运维": "linux", "云原生": "docker", "开发": "nginx",
    }
    return cat_map.get(category, "default")


def get_kb(slug: str, title: str, category: str) -> dict[str, Any]:
    dom = detect_domain(slug, title, category)
    return DOMAIN_KB.get(dom, DOMAIN_KB["default"])


def pick_items(slug: str, pool: list, count: int) -> list:
    rng = random.Random(int(hashlib.md5(slug.encode()).hexdigest()[:8], 16))
    if len(pool) <= count:
        return list(pool)
    return rng.sample(pool, count)
