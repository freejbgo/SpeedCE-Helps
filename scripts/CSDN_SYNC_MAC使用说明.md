# 把仓库中文文章同步到 CSDN 草稿

适合：**只会用浏览器**，不需要把仓库下载到电脑。

脚本会：

1. 读取仓库 `articles/` 里的中文文章  
2. 对照你 CSDN 账号里已经有的标题（已发布 + 尽量包含草稿）  
3. 把还没有的文章先放到临时目录  
4. 同步到 CSDN **草稿箱**（不会直接公开发布）  

---

## 方案 A：只用浏览器（推荐给你）

你不需要下载仓库，也不需要会命令行。

### 第 1 步：准备 Cookie

1. 浏览器登录 CSDN  
2. 打开：https://editor.csdn.net/md/  
3. 按 `F12`（或 `Fn + F12`）→ 点 **Network / 网络**  
4. 刷新页面，点任意一个请求  
5. 在 Headers 里找到 `Cookie:`，复制后面**整段长内容**

> Cookie 是登录凭证。只粘贴到 GitHub Secrets，不要发到聊天里。

### 第 2 步：把 Cookie 存进 GitHub（一次即可）

1. 打开仓库：https://github.com/freejbgo/SpeedCE-Helps  
2. 点 **Settings**  
3. 左侧点 **Secrets and variables** → **Actions**  
4. 点 **New repository secret**  
5. Name 填：

```text
CSDN_COOKIE
```

6. Secret 框里粘贴整段 Cookie  
7. 点 **Add secret**

### 第 3 步：在网页上点一下运行

1. 打开：https://github.com/freejbgo/SpeedCE-Helps/actions/workflows/csdn-sync-drafts.yml  
2. 右侧点 **Run workflow**  
3. 建议第一次这样选：
   - `mode`：`dry-run`（只预览，不写入）
   - `limit`：`5`
4. 点绿色 **Run workflow**
5. 等运行结束后，点进去看日志，确认“待同步”名单

### 第 4 步：真正同步到草稿

1. 再点一次 **Run workflow**  
2. 这次选：
   - `mode`：`sync`
   - `limit`：`5`（先只同步 5 篇）
3. 运行完成后，打开 CSDN 草稿箱检查：https://mp.csdn.net/  
4. 没问题后，再运行一次：
   - `mode`：`sync`
   - `limit`：`0`（0 表示不限制，同步剩余全部）

---

## 方案 B：本机运行（可选，你会用电脑终端时才需要）

1. 把 Cookie 保存为 `~/csdn_cookie.txt`  
2. 在仓库目录执行：

```bash
python3 scripts/csdn_sync_drafts.py
python3 scripts/csdn_sync_drafts.py --sync --limit 5
python3 scripts/csdn_sync_drafts.py --sync
```

---

## 常见问题

### 1. Settings 点不开？

你需要是这个仓库的管理员/有权限的协作者。如果没有权限，让仓库所有者帮你添加 `CSDN_COOKIE` Secret。

### 2. 运行失败，提示 Cookie 过期 / 403

重新登录 CSDN，复制新 Cookie，更新 GitHub 里的 `CSDN_COOKIE` Secret，再重新 Run workflow。

### 3. 会不会重复发？

按标题判断：CSDN 已有同标题（已发布或草稿）就会跳过。

### 4. 会不会直接公开发布？

不会，只会存草稿。

### 5. 公开仓库安全吗？

可以。Secret 内容不会显示在网页上；只要日志里不打印 Cookie 就行（脚本不会打印 Cookie）。  
但 Cookie 仍是登录凭证，过期后请及时更新，不要分享给别人。
