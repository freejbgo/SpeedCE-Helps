# 仓库中文文章同步到 CSDN 草稿 — 使用说明

本文档供下次同步时直接照做。  
**只用浏览器即可**，不需要下载仓库，也不需要 GitHub Actions。

---

## 1. 做什么

把本仓库 `articles/` 下的中文 Markdown 文章，同步到你的 CSDN **草稿箱**。

规则：

- 只存草稿，不直接公开发布
- 按**标题**去重：CSDN 已发布过的同标题文章会跳过
- 还会把「本次已成功存草稿」的标题记在浏览器本地，避免重复提交
- 不修改仓库 `articles/` 原文结构

---

## 2. 相关文件

| 文件 | 作用 |
|------|------|
| [`scripts/csdn_sync_browser_console.js`](./csdn_sync_browser_console.js) | 浏览器控制台同步脚本（唯一推荐方式） |
| 本文档 | 完整操作步骤与排错 |

在线直达（`main` 分支）：

- 脚本：https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/csdn_sync_browser_console.js  
- 说明：https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/CSDN同步到草稿使用说明.md  

> 说明：以前试过的 GitHub Actions / Python 同步方案，因云端访问 CSDN 经常被断开，已移除。日常只用浏览器脚本。

---

## 3. 操作步骤

### 3.1 准备

1. 用 Chrome / Edge 登录你的 CSDN 账号  
2. 打开：https://editor.csdn.net/md/  
3. 按 `F12`（笔记本可能是 `Fn + F12`）  
4. 点顶部 **Console / 控制台**

### 3.2 加载脚本

1. 打开：https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/csdn_sync_browser_console.js  
2. 点右上角 **Raw**  
3. `Cmd + A` 全选，`Cmd + C` 复制  
4. 回到 CSDN Console，粘贴，回车  

如果提示不能粘贴，先输入下面这句并回车，再粘贴脚本：

```text
allow pasting
```

看到“已加载 csdnSync”即成功。

### 3.3 先预览（不写入）

```js
await csdnSync.dryRun(5)
```

### 3.4 小批量写入草稿

```js
await csdnSync.sync(5)
```

然后打开草稿箱检查：https://mp.csdn.net/

### 3.5 继续分批 / 全量

```js
await csdnSync.sync(5)
```

或：

```js
await csdnSync.sync(20)
```

确认稳定后再考虑：

```js
await csdnSync.sync(0)
```

> `0` = 不限制数量。全量更容易触发频控，建议优先分批。

### 3.6 常用命令

| 命令 | 含义 |
|------|------|
| `await csdnSync.dryRun(5)` | 只预览 5 篇，不写入 |
| `await csdnSync.sync(5)` | 同步 5 篇到草稿 |
| `await csdnSync.sync(20)` | 同步 20 篇到草稿 |
| `await csdnSync.sync(0)` | 同步全部待处理文章 |
| `csdnSync.listDone()` | 查看本地已成功记录 |
| `csdnSync.markDone('标题', '文章ID')` | 手动标记已同步，避免重复 |

示例：

```js
csdnSync.markDone('API 接口可达性检测：Postman 能通、全国用户不通的真相', '163439956')
```

---

## 4. 实战经验

### 4.1 遇到「文章频繁发布，请稍后再试」

1. 停下来，等 **15~30 分钟**
2. 重新打开编辑器页，重新粘贴最新脚本  
3. 如有已成功但未记入本地的文章，先 `markDone`  
4. 再执行 `await csdnSync.sync(5)`

脚本已内置：

- 每篇默认间隔约 45 秒  
- 遇频控自动等待重试  

### 4.2 去重说明

可靠去重来源：

1. CSDN **已发布**文章标题  
2. 浏览器本地成功记录（`csdnSync.listDone()`）

注意：

- 仅在草稿箱、且本机没有记录的文章，理论上仍可能再存一份  
- 换浏览器 / 清站点数据后，本地记录会丢失  

### 4.3 推荐节奏

1. `dryRun(5)`  
2. `sync(5)`  
3. 反复 `sync(5)` / `sync(20)`  
4. 最后按需 `sync(0)`  

---

## 5. 常见问题

### Q1：Console 粘贴不了？

先输入 `allow pasting` 回车，再粘贴脚本。

### Q2：提示未检测到登录？

确认已登录，并且当前页面是：https://editor.csdn.net/md/

### Q3：会不会直接公开发布？

不会，只存草稿。

### Q4：换电脑后怎么办？

重新加载脚本。已发布文章仍会按标题跳过；仅草稿且无本地记录时，必要时手动 `markDone`。

---

## 6. 下次同步速查清单

- [ ] 登录 CSDN，打开 https://editor.csdn.net/md/  
- [ ] F12 → Console  
- [ ] 如需：输入 `allow pasting`  
- [ ] Raw 复制并粘贴 `csdn_sync_browser_console.js`  
- [ ] `await csdnSync.dryRun(5)`  
- [ ] `await csdnSync.sync(5)`  
- [ ] 打开 https://mp.csdn.net/ 检查草稿  
- [ ] 继续分批同步；遇频控则等待后再继续  

---

## 7. 安全提醒

- 浏览器方案不需要复制 Cookie，最安全  
- 若仓库 Settings 里还留着旧的 `CSDN_COOKIE` Secret，可手动删掉（已不再使用）  
