# Mac 小白版：把仓库中文文章同步到 CSDN 草稿

这个脚本会：

1. 读取仓库 `articles/` 里的中文文章  
2. 对照你 CSDN 账号里**已经有的标题**（已发布 + 尽量包含草稿）  
3. 把还没有的文章复制到临时文件夹 `/tmp/csdn-pending/`  
4. 再同步到 CSDN **草稿箱**（不会直接公开发布）  
5. 成功后删除临时文件夹  

**不会修改** `articles/` 里的原文，也不会改仓库目录结构。

---

## 准备工作（只做一次）

### 1. 确认电脑有 Python

打开「终端」，输入：

```bash
python3 --version
```

能看到类似 `Python 3.x.x` 就可以。

### 2. 准备 Cookie 文件

1. 浏览器登录 CSDN  
2. 打开：https://editor.csdn.net/md/  
3. 按 `F12`（或 `Fn + F12`）→ 点 **Network / 网络**  
4. 刷新页面，点任意一个请求  
5. 在 Headers 里找到 `Cookie:`，复制后面**整段长内容**  
6. 打开「文本编辑」，粘贴进去，保存为：

```text
/Users/你的用户名/csdn_cookie.txt
```

不知道用户名时，在终端执行：

```bash
echo $HOME
```

例如输出 `/Users/zhangsan`，文件就保存成：

```text
/Users/zhangsan/csdn_cookie.txt
```

> Cookie 是登录凭证，只放你自己电脑，不要发给别人，不要提交到 GitHub。

### 3. 下载 / 打开本仓库

如果你已经用 GitHub Desktop 或命令行把仓库放到本地，记下仓库路径。  
例如：

```text
/Users/zhangsan/SpeedCE-Helps
```

---

## 怎么运行

先进入仓库目录（把路径换成你自己的）：

```bash
cd /Users/你的用户名/SpeedCE-Helps
```

### 第一步：先预览（强烈建议）

```bash
python3 scripts/csdn_sync_drafts.py
```

这一步**不会写入 CSDN**，只会告诉你：

- 跳过多少篇（标题已存在）  
- 将同步多少篇  
- 并把待同步文章复制到 `/tmp/csdn-pending/`

你也可以打开 Finder，按 `Cmd + Shift + G`，输入：

```text
/tmp/csdn-pending
```

查看即将同步的文件。

### 第二步：先小批量真正同步（推荐）

先只同步 5 篇试试：

```bash
python3 scripts/csdn_sync_drafts.py --sync --limit 5
```

然后去 CSDN 草稿箱检查：

https://mp.csdn.net/

### 第三步：确认没问题后，同步剩余文章

```bash
python3 scripts/csdn_sync_drafts.py --sync
```

---

## 常见问题

### 1. 提示找不到 Cookie 文件

检查文件是否叫 `csdn_cookie.txt`，并且放在你的用户目录下（`~/csdn_cookie.txt`）。

### 2. 提示 Cookie 过期 / 403

重新登录 CSDN，重新复制 Cookie，覆盖保存到 `csdn_cookie.txt`，再运行。

### 3. 会不会重复发？

脚本按**标题**判断：  
CSDN 里已经有同标题（已发布或草稿），就会跳过，不会再存一份。

### 4. 会不会直接公开发布？

不会。脚本只会存到**草稿**。

### 5. 临时文件夹会不会留着？

- 预览模式：会保留 `/tmp/csdn-pending/`，方便你检查  
- 同步全部成功：会自动删除临时文件夹  
- 如果有失败：会保留，方便你核对  
- 同步结果还会保存在：`~/csdn_sync_result.json`

### 6. 想自定义 Cookie 文件路径

```bash
python3 scripts/csdn_sync_drafts.py --cookie-file /Users/你的用户名/Desktop/csdn_cookie.txt
```

---

## 安全提醒

- 不要把 `csdn_cookie.txt` 发到聊天工具或上传到仓库  
- 之前如果不小心把 Cookie 发过给别人，请退出 CSDN 重新登录，再换一份新 Cookie  
