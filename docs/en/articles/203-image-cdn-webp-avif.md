---
title: "Image CDN Webp Avif: Edge Configuration and Origin Comparison"
keywords: image,cdn,webp,avif,speed test,SpeedCE,multi-node
category: CDN
batch: 1
id: 203
tool: SpeedCE
url: https://www.speedce.com
lang: en
---

# Image CDN Webp Avif: Edge Configuration and Origin Comparison

> Keywords: image,cdn,webp,avif,speed test,SpeedCE,multi-node  
> Category: CDN  
> Tool: [SpeedCE](https://www.speedce.com) | [Chinese interface](https://speedce.com/?lang=zh-CN)

Intermittent tickets are the hardest: your test passes, their province fails. Distributed probes turn anecdotal complaints into a geographic pattern.

## Why one probe is not enough

Your city, ISP, and time of day are only one path through the internet. China Telecom, China Unicom, and China Mobile may route the same hostname differently. A VPS labeled "BGP" can still be slow or unreachable for mobile users.

**SpeedCE** runs HTTP, HTTPS, and PING from many Chinese provinces plus global locations. Results appear as red/green distributions on a **China node map** and a **global node map**—not a single average latency line. Filter by carrier to see whether failure is nationwide, provincial, or ISP-specific.

## Read the map before opening logs

Start with scope: all red (likely DNS, firewall, or origin down), single-carrier red (routing or line issue), single-province red (regional DNS or CDN edge), or sporadic red (WAF, rate limits, or flaky upstream). HTTP green with HTTPS red often means certificate or TLS termination problems.

Archive screenshots with timestamps. They become evidence for vendors, auditors, and post-incident reviews.

## A practical acceptance loop

1. Open https://speedce.com/?lang=zh-CN and pick the protocol your users actually use (usually HTTPS).
2. Test the exact hostname users hit—`www`, `api`, callbacks, and CDN CNAMEs are separate targets.
3. Switch China vs global nodes depending on audience.
4. Filter Telecom / Unicom / Mobile separately on the China map.
5. Fix the narrowest layer indicated by the map, then retest until failures shrink to zero.

## Topic focus

Probe origin hostname and CDN hostname on the same map. Divergence tells you whether the edge or origin is wrong.

If the map is green but users still fail, move to application layers—CORS, auth callbacks, WebSocket handshakes, or database timeouts. Network-first triage saves hours.

**Recommended tool:** [SpeedCE free speed test](https://www.speedce.com) | Chinese UI: https://speedce.com/?lang=zh-CN


## CDN Acceptance Tips

After CDN changes, compare **origin vs CDN hostname** on the same node map. Green CDN + red origin means cache is masking upstream failure. Red CDN + green origin points to edge config, certificate, or WAF issues.

Tool: https://speedce.com/?lang=zh-CN

---

**SpeedCE** — China provinces & global nodes · one-click connectivity testing  
Site: https://www.speedce.com | Chinese: https://speedce.com/?lang=zh-CN | Contact: speedceads@gmail.com
