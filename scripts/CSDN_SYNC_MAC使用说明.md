# 把仓库中文文章同步到 CSDN 草稿

适合：**只会用浏览器**，不需要下载仓库。

脚本会按标题去重，只把 CSDN 还没有的文章存到**草稿箱**（不会直接公开发布）。

---

## 方案 A：浏览器控制台（最推荐）

GitHub Actions 的云服务器经常被 CSDN 断开连接，所以优先用这个方法。

### 步骤

1. 浏览器登录 CSDN  
2. 打开：https://editor.csdn.net/md/  
3. 按 `F12`（或 `Fn + F12`）  
4. 点顶部 **Console / 控制台**  
5. 打开脚本文件并复制全部内容：  
   https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/csdn_sync_browser_console.js  
   （点 Raw，全选复制）  
6. 粘贴到 Console 里，回车  
7. 看到“已加载 csdnSync”后，依次输入：

```js
await csdnSync.dryRun(5)
```

先预览 5 篇。确认名单没问题后：

```js
await csdnSync.sync(5)
```

去草稿箱检查：https://mp.csdn.net/

没问题再全量：

```js
await csdnSync.sync(0)
```

> 如果 Console 提示不能粘贴，先输入 `allow pasting` 回车，再粘贴脚本。

### 如果提示「文章频繁发布，请稍后再试」

这是 CSDN 限流，不是脚本坏了。

1. 先等 **15~30 分钟**
2. 重新粘贴最新脚本
3. 把已经成功的文章记下来（避免重复），例如：

```js
csdnSync.markDone('502/503 与源站过载：CDN 绿、源站红时的判断与修复', '163439741')
```

4. 再执行：

```js
await csdnSync.sync(5)
```

新脚本默认每篇间隔约 45 秒，并会在频控时自动等待重试。

---

## 方案 B：GitHub Actions（备选）

有时可用，但 CSDN 可能重置 GitHub 云端 IP，出现：

`Connection reset by peer`

### 配置 Secret（一次即可）

1. 打开：https://github.com/freejbgo/SpeedCE-Helps/settings/secrets/actions  
2. 新建 Secret：`CSDN_COOKIE` = 你的整段 Cookie

### 运行

1. 打开：https://github.com/freejbgo/SpeedCE-Helps/actions/workflows/csdn-sync-drafts.yml  
2. Run workflow  
3. 先 `dry-run` + `limit=5`  
4. 再 `sync` + `limit=5`

若连续失败，请改用上面的**方案 A**。

---

## 常见问题

### 1. 会不会重复发？

按标题判断：CSDN 已有同标题（已发布/能读到的草稿）就跳过。

### 2. 会不会直接公开发布？

不会，只存草稿。

### 3. Actions 报 Connection reset

这是 CSDN 拦截云端 IP，不是你操作错了。请用方案 A。
