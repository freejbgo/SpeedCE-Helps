# 仓库中文文章同步到 CSDN 草稿 — 使用说明

本文档供下次同步时直接照做。  
**推荐只用浏览器**，不需要下载仓库，也不需要会命令行。

---

## 1. 做什么

把本仓库 `articles/` 下的中文 Markdown 文章，同步到你的 CSDN **草稿箱**。

规则：

- 只存草稿，不直接公开发布
- 按**标题**去重：CSDN 已发布过的同标题文章会跳过
- 浏览器方式还会把「本次已成功存草稿」的标题记在本地，避免重复提交
- 不修改仓库 `articles/` 原文结构

---

## 2. 相关文件一览

| 文件 | 作用 |
|------|------|
| [`scripts/csdn_sync_browser_console.js`](./csdn_sync_browser_console.js) | **主推**：浏览器控制台脚本 |
| [`scripts/csdn_sync_drafts.py`](./csdn_sync_drafts.py) | Python 脚本（供 GitHub Actions / 本机使用） |
| [`.github/workflows/csdn-sync-drafts.yml`](../.github/workflows/csdn-sync-drafts.yml) | GitHub Actions 工作流（备选，云端常被 CSDN 断开） |
| 本文档 | 完整操作步骤与排错 |

在线直达（`main` 分支）：

- 浏览器脚本：https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/csdn_sync_browser_console.js  
- 本说明：https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/CSDN同步到草稿使用说明.md  

---

## 3. 推荐方案：浏览器控制台（下次优先用这个）

### 3.1 准备

1. 用 Chrome / Edge 登录你的 CSDN 账号  
2. 打开 Markdown 编辑器页面：  
   https://editor.csdn.net/md/  
3. 按键盘 `F12`（笔记本可能是 `Fn + F12`）  
4. 点顶部 **Console / 控制台**

### 3.2 加载脚本

1. 打开脚本页面：  
   https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/csdn_sync_browser_console.js  
2. 点右上角 **Raw**  
3. `Cmd + A` 全选，`Cmd + C` 复制  
4. 回到 CSDN 页面的 Console，粘贴，回车  

如果 Console 提示不能粘贴，先输入下面这句并回车，再粘贴脚本：

```text
allow pasting
```

看到类似提示即表示加载成功：

```text
已加载 csdnSync。
先预览: await csdnSync.dryRun(5)
再同步: await csdnSync.sync(5)
...
```

### 3.3 先预览（不写入）

```js
await csdnSync.dryRun(5)
```

关注输出里的：

- `已发布标题: xxx`
- `本地已同步记录: xxx`
- `待同步到草稿: xxx`
- 待同步文章标题列表

### 3.4 小批量写入草稿

确认名单无误后：

```js
await csdnSync.sync(5)
```

默认每篇大约间隔 45 秒；若触发 CSDN「频繁发布」会自动等待重试。

写完后打开草稿箱检查：

https://mp.csdn.net/

### 3.5 继续分批 / 全量

继续下一批：

```js
await csdnSync.sync(5)
```

或一次多一点：

```js
await csdnSync.sync(20)
```

确认稳定后再考虑全量：

```js
await csdnSync.sync(0)
```

> `0` 表示不限制数量。全量耗时较长，且更容易触发频控，建议优先分批。

### 3.6 常用命令

| 命令 | 含义 |
|------|------|
| `await csdnSync.dryRun(5)` | 只预览 5 篇，不写入 |
| `await csdnSync.sync(5)` | 同步 5 篇到草稿 |
| `await csdnSync.sync(20)` | 同步 20 篇到草稿 |
| `await csdnSync.sync(0)` | 同步全部待处理文章 |
| `csdnSync.listDone()` | 查看本地已成功记录 |
| `csdnSync.markDone('标题', '文章ID')` | 手动标记某篇已同步，避免重复 |

手动标记示例：

```js
csdnSync.markDone('API 接口可达性检测：Postman 能通、全国用户不通的真相', '163439956')
```

---

## 4. 实战经验（很重要）

### 4.1 CSDN 频控

如果出现：

```text
文章频繁发布，请稍后再试
```

处理办法：

1. 停下来，等 **15~30 分钟**
2. 重新打开编辑器页，重新粘贴最新脚本  
3. 如有已成功但未记入本地的文章，先 `markDone`  
4. 再执行 `await csdnSync.sync(5)`

当前脚本已内置：

- 篇与篇之间默认等待约 45 秒  
- 遇到频控自动等待后重试  

### 4.2 去重说明

当前可靠去重来源：

1. CSDN **已发布**文章标题  
2. 浏览器 `localStorage` 里本次/历史成功记录（`csdnSync.listDone()`）

说明：

- 创作中心「草稿列表」接口签名不稳定，脚本默认跳过  
- 所以：**仅存在于草稿箱、且本机没有 `markDone` 记录的文章**，理论上仍可能再存一份  
- 同浏览器、同域名下，`localStorage` 记录会保留；换浏览器 / 清站点数据后记录会丢，需要重新 `markDone` 或依赖已发布标题

### 4.3 第一次成功后的标准节奏

1. `dryRun(5)` 看名单  
2. `sync(5)` 验证草稿箱  
3. 反复 `sync(5)` 或 `sync(20)`  
4. 最后视情况 `sync(0)` 收尾  

---

## 5. 备选方案：GitHub Actions

> 注意：GitHub 云端 IP 经常被 CSDN 重置（`Connection reset by peer`）。  
> **只在浏览器方案不可用时再试。**

### 5.1 配置 Cookie Secret（一次）

1. 浏览器登录 CSDN，打开 https://editor.csdn.net/md/  
2. `F12` → Network → 刷新 → 点任意请求 → 复制请求头里的整段 `Cookie`  
3. 打开：https://github.com/freejbgo/SpeedCE-Helps/settings/secrets/actions  
4. New repository secret  
   - Name：`CSDN_COOKIE`  
   - Secret：粘贴整段 Cookie  
5. Add secret  

Cookie 是登录凭证，不要发到聊天里，不要提交进仓库。

### 5.2 运行工作流

1. 打开：https://github.com/freejbgo/SpeedCE-Helps/actions/workflows/csdn-sync-drafts.yml  
2. Run workflow  
3. 建议参数：  
   - 先：`mode=dry-run`，`limit=5`  
   - 再：`mode=sync`，`limit=5`  
4. 分支选 `main`

对应实现：

- 工作流：`.github/workflows/csdn-sync-drafts.yml`  
- 脚本：`scripts/csdn_sync_drafts.py`

---

## 6. 常见问题

### Q1：Console 里粘贴不了？

先输入 `allow pasting` 回车，再粘贴脚本。

### Q2：提示未检测到登录？

请确认已登录 CSDN，并且当前页面是：  
https://editor.csdn.net/md/

### Q3：创作中心列表报 HMAC signature does not match？

可忽略。浏览器方案默认已跳过该接口，不影响按「已发布标题 + 本地记录」去重后存草稿。

### Q4：会不会直接公开发布？

不会。脚本写入的是草稿（`pubStatus: draft`）。

### Q5：换电脑 / 清了浏览器数据后怎么办？

重新加载脚本。已公开发布的文章仍会按标题跳过；仅草稿且无本地记录的，可能需人工看一眼草稿箱，必要时 `markDone`。

### Q6：Actions 一直 Connection reset？

改用本文第 3 节浏览器方案。

---

## 7. 下次同步速查清单

- [ ] 登录 CSDN，打开 https://editor.csdn.net/md/  
- [ ] F12 → Console  
- [ ] 如需粘贴权限：输入 `allow pasting`  
- [ ] 打开 Raw 并粘贴 `scripts/csdn_sync_browser_console.js`  
- [ ] `await csdnSync.dryRun(5)`  
- [ ] `await csdnSync.sync(5)`  
- [ ] 打开 https://mp.csdn.net/ 检查草稿  
- [ ] 继续 `sync(5)` / `sync(20)`，最后按需 `sync(0)`  
- [ ] 若遇频控：等待 15~30 分钟后再继续  

---

## 8. 安全提醒

- 不要把 Cookie 发到公开聊天或提交到 Git  
- GitHub Secret `CSDN_COOKIE` 仅用于 Actions 备选方案  
- 浏览器方案不需要把 Cookie 复制出来，最安全也最稳  
