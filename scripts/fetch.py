# -*- coding: utf-8 -*-
"""从 GitHub API 刷新 data.json 里的元数据（星标、Fork、语言、许可证、提交时间等）。

用法：
    GITHUB_TOKEN=ghp_xxx python scripts/fetch.py          # 有 token 最好，配额 5000 次/小时
    python scripts/fetch.py                               # 无 token，配额 60 次/小时
    python scripts/fetch.py --check                       # 只报告变化，不写文件
    python scripts/fetch.py --add owner/repo              # 追加一个新仓库（元数据先抓，标注仍需手写）

只更新「机器能抓的字段」，不碰 scripts/annotations.json 里的中文标注。
抓不到的仓库不会从 data.json 里删掉，只在最后汇总里列出来，避免一次网络抖动毁掉数据。
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.json"
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# 仓库改名很频繁，核心 API 报 404 时用它兜底（旧名 → 新名）
ALIAS = {
    "geekan/metagpt": "FoundationAgents/MetaGPT",
    "all-hands-ai/openhands": "OpenHands/OpenHands",
    "block/goose": "aaif-goose/goose",
    "jlowin/fastmcp": "PrefectHQ/fastmcp",
    "modelscope/agentscope": "agentscope-ai/agentscope",
    "openinterpreter/open-interpreter": "openinterpreter/openinterpreter",
    "gpt-engineer-org/gpt-engineer": "AntonOsika/gpt-engineer",
    "sst/opencode": "anomalyco/opencode",
    "strands-agents/sdk-python": "strands-agents/harness-sdk",
    "volcengine/verl": "verl-project/verl",
    "microsoft/autogen": "microsoft/agent-framework",
    "microsoft/semantic-kernel": "microsoft/agent-framework",
}


def _req(url, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": "agent-landscape-fetch"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return urllib.request.Request(url, headers=headers)


def get_json(url):
    """返回 (数据, 错误说明)。限流时等一分钟重试一次。"""
    for attempt in range(2):
        try:
            with urllib.request.urlopen(_req(url), timeout=25) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt == 0:
                reset = e.headers.get("X-RateLimit-Reset")
                wait = 60
                if reset and reset.isdigit():
                    wait = max(5, min(90, int(reset) - int(time.time()) + 1))
                print(f"    限流，等 {wait}s 后重试…")
                time.sleep(wait)
                continue
            body = e.read().decode("utf-8", "ignore")[:120]
            return None, f"HTTP {e.code} {body}"
        except Exception as e:  # 网络超时 / DNS / 连接重置
            if attempt == 0:
                time.sleep(3)
                continue
            return None, f"{type(e).__name__}: {e}"
    return None, "重试后仍失败"


def shape(r):
    """把 GitHub 的返回裁成 data.json 用的字段。"""
    lic = (r.get("license") or {}).get("spdx_id") or "-"
    return {
        "full_name": r["full_name"],
        "url": r["html_url"],
        "homepage": r.get("homepage") or "",
        "desc": r.get("description") or "",
        "stars": r.get("stargazers_count", 0),
        "forks": r.get("forks_count", 0),
        "lang": r.get("language") or "-",
        "license": lic,
        "topics": r.get("topics") or [],
        "pushed_at": (r.get("pushed_at") or "")[:10],
        "created_at": (r.get("created_at") or "")[:7],
        "archived": bool(r.get("archived")),
        "open_issues": r.get("open_issues_count", 0),
    }


def fetch_one(full_name):
    """先打核心 API；404 时查别名，再不行就走 search API（改名后的仓库也能找到）。"""
    data, err = get_json(f"{API}/repos/{full_name}")
    if data:
        return shape(data), None

    alias = ALIAS.get(full_name.lower())
    if alias and alias.lower() != full_name.lower():
        data, err2 = get_json(f"{API}/repos/{alias}")
        if data:
            out = shape(data)
            out["aliased_from"] = full_name
            return out, None

    if err and "404" in err:
        q = urllib.parse.quote(f"repo:{full_name}")
        found, err3 = get_json(f"{API}/search/repositories?q={q}")
        items = (found or {}).get("items") or []
        if items:
            out = shape(items[0])
            if out["full_name"].lower() != full_name.lower():
                out["aliased_from"] = full_name
            return out, None
        return None, f"404（search 也没找到）"
    return None, err


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    add = None
    if "--add" in args:
        add = args[args.index("--add") + 1]

    old = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else []
    order = [x["full_name"] for x in old]
    if add:
        if add.lower() in {o.lower() for o in order}:
            sys.exit(f"{add} 已经在 data.json 里了")
        order.append(add)

    if not TOKEN:
        print("提示：没设 GITHUB_TOKEN，未认证配额只有 60 次/小时，仓库多了会被限流。\n")

    t0 = time.time()
    results, problems = {}, []
    with ThreadPoolExecutor(max_workers=1 if not TOKEN else 6) as pool:
        futures = {pool.submit(fetch_one, fn): fn for fn in order}
        for i, fut in enumerate(futures, 1):
            fn = futures[fut]
            meta, err = fut.result()
            if meta:
                results[fn] = meta
            else:
                problems.append(f"{fn}：{err}")
            if i % 10 == 0 or i == len(order):
                print(f"  已抓 {i}/{len(order)}（{time.time() - t0:.0f}s）")

    # 保持原顺序；抓失败的沿用旧数据
    old_by_name = {x["full_name"].lower(): x for x in old}
    merged, changes = [], []
    for fn in order:
        new = results.get(fn) or old_by_name.get(fn.lower())
        if not new:
            continue
        prev = old_by_name.get(fn.lower())
        if prev:
            d_star = new["stars"] - prev["stars"]
            if d_star:
                changes.append(f"  {new['full_name']:<45} ★ {prev['stars']:>7,} → {new['stars']:>7,}  ({d_star:+,})")
            if new["pushed_at"] != prev["pushed_at"]:
                changes.append(f"  {new['full_name']:<45} 最后提交 {prev['pushed_at']} → {new['pushed_at']}")
            if new["full_name"].lower() != fn.lower():
                changes.append(f"  {fn} → {new['full_name']}（改名，data.json 已更新）")
        else:
            changes.append(f"  + 新增 {new['full_name']}  ★ {new['stars']:,}")
        merged.append(new)

    print(f"\n抓到 {len(results)}/{len(order)} 个仓库，用时 {time.time() - t0:.0f}s")
    if changes:
        print(f"变化 {len(changes)} 处：")
        print("\n".join(changes[:40]))
        if len(changes) > 40:
            print(f"  …还有 {len(changes) - 40} 处")
    else:
        print("没有任何变化。")
    if problems:
        print(f"\n{len(problems)} 个没抓到（已保留旧数据）：")
        print("\n".join("  " + p for p in problems))

    if check_only:
        print("\n--check：未写入 data.json")
        return
    DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n已写入 data.json（{len(merged)} 条）。下一步：补标注 → python scripts/build.py")


if __name__ == "__main__":
    main()
