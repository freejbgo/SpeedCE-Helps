/**
 * 在浏览器里同步 SpeedCE-Helps 中文文章到 CSDN 草稿（适合只会用浏览器的情况）
 *
 * 完整操作文档：
 *   scripts/CSDN同步到草稿使用说明.md
 *   https://github.com/freejbgo/SpeedCE-Helps/blob/main/scripts/CSDN同步到草稿使用说明.md
 *
 * 使用步骤：
 * 1. 浏览器登录 CSDN
 * 2. 打开：https://editor.csdn.net/md/
 * 3. 按 F12 → 点 Console / 控制台
 * 4. 如提示不能粘贴，先输入 allow pasting 回车
 * 5. 粘贴本文件全部内容，回车
 * 6. 先预览： await csdnSync.dryRun(5)
 * 7. 再小批量写入草稿： await csdnSync.sync(5)
 * 8. 确认无误后分批继续，或 await csdnSync.sync(0)
 *
 * 说明：
 * - 只会存草稿，不会公开发布
 * - 按标题去重：已发布标题 + 本地 markDone 记录
 * - 文章内容从 GitHub 仓库读取，不需要你下载仓库
 * - 遇「频繁发布」会自动等待重试；仍失败则停 15~30 分钟再继续
 * - 已移除 GitHub Actions / Python 同步方案，日常只用本脚本
 */
(() => {
  const REPO = "freejbgo/SpeedCE-Helps";
  const BRANCH = "main";
  const CA_KEY = "203803574";
  const CA_SECRET = "9znpamsyl2c7cdrr9sas0le9vbc3r6ba";
  const BLOG = "https://blog.csdn.net";
  const BIZ = "https://bizapi.csdn.net";

  function normalizeTitle(title) {
    return String(title || "")
      .replace(/[\u3000\u00a0]/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .replace(/[。．.！!？?；;：:]+$/g, "");
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  async function hmacSign(method, pathWithQuery, contentType = "") {
    const nonce = crypto.randomUUID();
    const stringToSign =
      `${method}\n*/*\n\n${contentType}\n\n` +
      `x-ca-key:${CA_KEY}\nx-ca-nonce:${nonce}\n${pathWithQuery}`;
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(CA_SECRET),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sigBuf = await crypto.subtle.sign(
      "HMAC",
      key,
      new TextEncoder().encode(stringToSign)
    );
    let binary = "";
    const bytes = new Uint8Array(sigBuf);
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    const signature = btoa(binary);
    return {
      "x-ca-key": CA_KEY,
      "x-ca-nonce": nonce,
      "x-ca-signature": signature,
      "x-ca-signature-headers": "x-ca-key,x-ca-nonce",
      Accept: "*/*",
    };
  }

  const DONE_KEY = "csdnSyncDoneTitles";

  function loadDoneMap() {
    try {
      return JSON.parse(localStorage.getItem(DONE_KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }

  function saveDoneMap(map) {
    localStorage.setItem(DONE_KEY, JSON.stringify(map));
  }

  function markDone(title, articleId) {
    const map = loadDoneMap();
    map[normalizeTitle(title)] = {
      title,
      articleId: articleId || "",
      at: new Date().toISOString(),
    };
    saveDoneMap(map);
    console.log("已记录到本地去重列表:", title);
    return map;
  }

  function listDone() {
    return loadDoneMap();
  }

  async function fetchJson(url, options = {}) {
    const resp = await fetch(url, {
      credentials: "include",
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
    });
    const text = await resp.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(`非 JSON 响应 (${resp.status}): ${text.slice(0, 200)}`);
    }
    if (!resp.ok) {
      const msg = (data && (data.msg || data.message)) || text.slice(0, 200);
      const err = new Error(`HTTP ${resp.status}: ${msg}`);
      err.status = resp.status;
      err.payload = data;
      throw err;
    }
    return data;
  }

  async function listGithubArticles() {
    // 优先从 README 提取标题和路径，避免预览时逐个下载 500 篇文章
    const readmeUrl = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/README.md`;
    const resp = await fetch(readmeUrl, { credentials: "omit" });
    if (!resp.ok) throw new Error(`读取 README 失败: ${resp.status}`);
    const readme = await resp.text();
    const items = [];
    const re = /\[(?:\*\*)?(.+?)(?:\*\*)?\]\((articles\/[^)\s]+\.md)\)/g;
    let m;
    const seen = new Set();
    while ((m = re.exec(readme))) {
      const title = m[1].trim();
      const path = m[2].trim();
      if (seen.has(path)) continue;
      seen.add(path);
      items.push({ path, title });
    }
    if (items.length) return items;

    // 备用：GitHub tree API
    const treeUrl = `https://api.github.com/repos/${REPO}/git/trees/${BRANCH}?recursive=1`;
    const tree = await fetchJson(treeUrl, { credentials: "omit" });
    const files = (tree.tree || [])
      .filter((x) => x.type === "blob" && /^articles\/[^/]+\.md$/.test(x.path))
      .map((x) => ({
        path: x.path,
        title: x.path.replace(/^articles\//, "").replace(/\.md$/, ""),
      }));
    if (!files.length) throw new Error("GitHub 上没有找到 articles/*.md");
    return files.sort((a, b) => a.path.localeCompare(b.path));
  }

  async function loadArticleContent(path) {
    const url = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${path}`;
    const resp = await fetch(url, { credentials: "omit" });
    if (!resp.ok) throw new Error(`读取 ${path} 失败: ${resp.status}`);
    return await resp.text();
  }

  async function fetchPublishedTitles(username) {
    const titles = new Map();
    let page = 1;
    let total = null;
    while (page <= 50) {
      const qs = new URLSearchParams({
        page: String(page),
        size: "100",
        businessType: "blog",
        username,
      });
      const url = `${BLOG}/community/home-api/v1/get-business-list?${qs}`;
      const data = await fetchJson(url);
      const payload = data.data || {};
      const rows = payload.list || [];
      if (total == null) total = payload.total;
      for (const row of rows) {
        const key = normalizeTitle(row.title || "");
        if (key) titles.set(key, row);
      }
      if (!rows.length) break;
      if (total != null && page * 100 >= total) break;
      if (rows.length < 100) break;
      page += 1;
      await sleep(200);
    }
    return titles;
  }

  async function fetchConsoleTitles() {
    const titles = new Map();
    for (const status of ["all_v3", "all", "draft", "enable"]) {
      let page = 1;
      let got = false;
      while (page <= 40) {
        const params = { page: String(page), pageSize: "50", status };
        const qs = Object.keys(params)
          .sort()
          .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
          .join("&");
        const path = `/blog/phoenix/console/v1/article/list?${qs}`;
        const sign = await hmacSign("GET", path, "");
        try {
          const data = await fetchJson(`${BIZ}${path}`, {
            headers: {
              ...sign,
              Origin: "https://mp.csdn.net",
              Referer: "https://mp.csdn.net/",
            },
          });
          if (!(data.code === 200 || data.code === 0 || data.code === "200")) break;
          const rows = (data.data && (data.data.list || data.data.articles)) || [];
          if (!rows.length) break;
          got = true;
          for (const row of rows) {
            const key = normalizeTitle(row.title || row.articleTitle || "");
            if (key) titles.set(key, row);
          }
          const total = data.data.total || data.data.count;
          if (total != null && page * 50 >= total) break;
          if (rows.length < 50) break;
          page += 1;
          await sleep(250);
        } catch (e) {
          console.warn(`创作中心列表 status=${status} 失败:`, e.message || e);
          break;
        }
      }
      if (got) break;
    }
    return titles;
  }

  function mdToHtml(src) {
    const esc = (s) =>
      String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    const inline = (s) =>
      esc(s)
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    return String(src || "")
      .split(/\n\s*\n/)
      .map((block) => {
        const t = block.trim();
        if (!t) return "";
        const hm = t.match(/^(#{1,6})\s+(.*)$/);
        if (hm && !t.includes("\n")) {
          const lv = hm[1].length;
          return `<h${lv}>${inline(hm[2])}</h${lv}>`;
        }
        return `<p>${inline(t.replace(/\n/g, " "))}</p>`;
      })
      .filter(Boolean)
      .join("\n");
  }

  function makeDescription(md) {
    const text = md
      .replace(/^#\s+.*$/m, "")
      .replace(/```[\s\S]*?```/g, " ")
      .replace(/[>#*_`\[\]\(\)!-]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    return text.length > 180 ? text.slice(0, 179) + "…" : text;
  }

  function isRateLimited(err) {
    const msg = String((err && err.message) || err || "");
    return msg.includes("频繁发布") || msg.includes("请稍后再试");
  }

  async function saveDraft(title, markdown, { retries = 6, waitSec = 60 } = {}) {
    const path = "/blog-console-api/v3/mdeditor/saveArticle";
    const body = {
      title,
      markdowncontent: markdown,
      content: mdToHtml(markdown),
      readType: "public",
      status: 2,
      categories: "",
      tags: "SpeedCE,网络测速,运维",
      type: "original",
      original_link: "",
      authorized_status: false,
      Description: makeDescription(markdown),
      not_auto_saved: "1",
      source: "pc_mdeditor",
      cover_images: [],
      cover_type: 0,
      is_new: 1,
      vote_id: 0,
      pubStatus: "draft",
    };

    let lastErr;
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const sign = await hmacSign("POST", path, "application/json");
        const data = await fetchJson(`${BIZ}${path}`, {
          method: "POST",
          headers: {
            ...sign,
            Origin: "https://editor.csdn.net",
            Referer: "https://editor.csdn.net/",
          },
          body: JSON.stringify(body),
        });
        if (data.code !== 200) {
          throw new Error(data.msg || data.message || JSON.stringify(data));
        }
        return data.data || {};
      } catch (e) {
        lastErr = e;
        if (isRateLimited(e) && attempt < retries) {
          console.warn(
            `  触发 CSDN 频控，${waitSec} 秒后重试 (${attempt}/${retries})...`
          );
          await sleep(waitSec * 1000);
          continue;
        }
        throw e;
      }
    }
    throw lastErr;
  }

  async function plan(limit = 5, { skipConsole = true } = {}) {
    const username = getCookie("UserName") || getCookie("UN");
    if (!username) {
      throw new Error("未检测到 CSDN 登录 Cookie，请先登录并打开 https://editor.csdn.net/md/");
    }
    console.log("CSDN 账号:", username);

    console.log("读取 GitHub 文章列表...");
    const files = await listGithubArticles();
    console.log("仓库文章数:", files.length);

    console.log("拉取 CSDN 已发布标题...");
    const existing = await fetchPublishedTitles(username);
    console.log("已发布标题:", existing.size);

    const doneMap = loadDoneMap();
    const doneCount = Object.keys(doneMap).length;
    console.log("本地已同步记录:", doneCount);
    for (const key of Object.keys(doneMap)) existing.set(key, doneMap[key]);

    if (!skipConsole) {
      console.log("尝试拉取创作中心/草稿标题...");
      const consoleTitles = await fetchConsoleTitles();
      console.log("创作中心标题:", consoleTitles.size);
      for (const [k, v] of consoleTitles) existing.set(k, v);
    } else {
      console.log("已跳过创作中心列表（签名不稳定）；草稿去重改用本地记录。");
    }

    const pending = [];
    let skipped = 0;
    for (const art of files) {
      const key = normalizeTitle(art.title);
      if (existing.has(key)) {
        skipped += 1;
      } else {
        pending.push(art);
        if (limit > 0 && pending.length >= limit) break;
      }
    }

    console.log("======== 对比结果 ========");
    console.log("跳过（已发布/本地已同步）:", skipped);
    console.log("待同步到草稿:", pending.length);
    pending.slice(0, 20).forEach((a, i) => {
      console.log(`${i + 1}. ${a.title}  <=  ${a.path}`);
    });
    return { username, skipped, pending };
  }

  async function dryRun(limit = 5) {
    const result = await plan(limit);
    console.log("预览完成，没有写入 CSDN。确认后执行: await csdnSync.sync(5)");
    return result;
  }

  async function sync(limit = 5, options = {}) {
    const delaySec = options.delaySec != null ? options.delaySec : 45;
    const waitSec = options.waitSec != null ? options.waitSec : 90;
    const { pending } = await plan(limit, options);
    if (!pending.length) {
      console.log("没有需要同步的文章");
      return [];
    }
    console.log(`开始同步：每篇间隔约 ${delaySec} 秒，遇频控自动等待重试`);
    const results = [];
    for (let i = 0; i < pending.length; i++) {
      const art = pending[i];
      console.log(`[${i + 1}/${pending.length}] 存草稿: ${art.title}`);
      try {
        const content = await loadArticleContent(art.path);
        const hm = content.match(/^#\s+(.+?)\s*$/m);
        const title = (hm ? hm[1].trim() : art.title) || art.title;
        const data = await saveDraft(title, content, { waitSec });
        const id = data.id || data.art_id || data.articleId;
        const editUrl = id ? `https://editor.csdn.net/md/?articleId=${id}` : "";
        markDone(title, id);
        console.log("  成功:", editUrl || id);
        results.push({ ok: true, title, path: art.path, id, editUrl });
      } catch (e) {
        console.error("  失败:", e.message || e);
        results.push({
          ok: false,
          title: art.title,
          path: art.path,
          error: String(e.message || e),
        });
        if (isRateLimited(e)) {
          console.warn("仍被频控，停止本轮。请过 10~30 分钟后再执行 await csdnSync.sync(5)");
          break;
        }
      }
      if (i < pending.length - 1) {
        console.log(`  等待 ${delaySec} 秒后继续...`);
        await sleep(delaySec * 1000);
      }
    }
    console.log("本轮结束。请打开草稿箱检查: https://mp.csdn.net/");
    return results;
  }

  window.csdnSync = { dryRun, sync, plan, markDone, listDone };
  console.log(
    [
      "已加载 csdnSync。",
      "先预览: await csdnSync.dryRun(5)",
      "再同步: await csdnSync.sync(5)",
      "全量同步: await csdnSync.sync(0)",
      "记录已成功文章: csdnSync.markDone('标题', '文章ID')",
    ].join("\n")
  );
})();
