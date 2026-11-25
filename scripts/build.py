# -*- coding: utf-8 -*-
"""把 data.json（机器抓的元数据）+ annotations.json（人工标注）渲染成 index.html。

用法：
    python scripts/build.py                    # 生成 index.html
    python scripts/build.py --check            # 只校验，不写文件
    python scripts/build.py --check-generated  # 校验并检查 index.html 是否为最新产物

规则：
- 每个仓库都必须在 annotations.json 里有标注，否则报错退出（宁可不生成，也不生成半张卡）。
- data.json 里有、annotations.json 里没有的仓库 → 报错；反之 → 报错。
- 组内按星数降序；赛道顺序以 tracks.json 为准。
"""
import datetime
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_FILE = ROOT / "scripts/snapshot.json"


def get_snapshot_date():
    """快照日期由 fetch.py 写入；测试时可用 SNAPSHOT_DATE 环境变量覆盖。"""
    raw = os.environ.get("SNAPSHOT_DATE")
    if not raw:
        raw = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))["date"]
    return datetime.date.fromisoformat(raw)


SNAP_DATE = get_snapshot_date()

LANG_COLOR = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Rust": "#dea584", "Go": "#00ADD8", "C#": "#68217a",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "MDX": "#fcb32c", "-": "#94a3b8",
}
DOTS = {
    1: '<span class="dots"><i class="dot on"></i><i class="dot "></i><i class="dot "></i></span>',
    2: '<span class="dots"><i class="dot on"></i><i class="dot on"></i><i class="dot "></i></span>',
    3: '<span class="dots"><i class="dot on"></i><i class="dot on"></i><i class="dot on"></i></span>',
}
DIFF_N = {"易": 1, "中": 2, "难": 3}


def wan(n):
    """星标/总计的展示格式：10000 以上折成「万」，保留一位小数。"""
    if n >= 10000:
        s = f"{n / 10000:.1f}".rstrip("0").rstrip(".")
        return s + "万"
    return f"{n:,}"


def fork_fmt(n):
    """Fork 数三档：≥1 万用「万」，≥1000 用「k」，再小就原样带千分位。"""
    if n >= 10000:
        return wan(n)
    if n >= 1000:
        s = f"{n / 1000:.1f}".rstrip("0").rstrip(".")
        return s + "k"
    return f"{n:,}"


def status(meta):
    """归档优先级高于提交日期：刚归档的仓库也可能有很新的最后一次提交。"""
    if meta.get("archived"):
        return "已归档", "s-off"
    days = (SNAP_DATE - datetime.date.fromisoformat(meta["pushed_at"])).days
    if days <= 45:
        return "活跃", "s-on"
    if days <= 210:
        return "维护中", "s-mid"
    return "沉寂", "s-off"


def esc(value):
    """标注是人工写的自由文本，进 HTML 文本和属性前都必须转义。"""
    return html.escape(str(value), quote=True)


def license_label(value):
    if value == "NOASSERTION":
        return "许可未识别", "GitHub 未识别许可证，商用前请查看仓库 LICENSE"
    if value == "-":
        return "未声明许可", "仓库未声明许可证，并不代表可以自由使用"
    return value, ""


def card(meta, ann):
    fn = meta["full_name"]
    owner, _, name = fn.partition("/")
    lang = meta["lang"]
    diff = ann["diff"]
    st, cls = status(meta)
    topics = " ".join(meta.get("topics") or [])
    # 搜索用的可见文案；topics 单独放 data-topics，避免同一个词存两份
    data_name = " ".join(x for x in (fn, ann["pitch"], ann["aud"], ann["note"]) if x).lower()
    color = LANG_COLOR.get(lang, "#94a3b8")
    act = 1 if st == "活跃" else 0
    lic, lic_title = license_label(ann["lic"])
    lic_title_attr = f' title="{esc(lic_title)}"' if lic_title else ""
    return f"""    <article class="card" data-cat="{esc(ann['cat'])}" data-lang="{esc(lang)}"
             data-name="{esc(data_name)}"
             data-diff="{esc(diff)}" data-act="{act}" data-topics="{esc(topics)}"
             data-stars="{meta['stars']}" data-upd="{esc(meta['pushed_at'])}">
      <div class="card-top">
        <a class="repo" href="{esc(meta['url'])}" target="_blank" rel="noopener">
          <span class="owner">{esc(owner)}/</span><span class="name">{esc(name)}</span>
        </a>
        <span class="stars" title="{meta['stars']:,} stars">★ {wan(meta['stars'])}</span>
      </div>
      <h3 class="pitch">{esc(ann['pitch'])}</h3>
      <p class="note">{esc(ann['note'])}</p>
      <div class="fit"><span class="fitk">适合</span><span class="fitv">{esc(ann['aud'])}</span></div>
      <div class="topics"><span>⑂ Fork {fork_fmt(meta['forks'])}</span><span>创建于 {esc(meta['created_at'])}</span></div>
      <div class="card-foot">
        <span class="meta-item lang"><i class="ldot" style="background:{color}"></i>{esc(lang)}</span>
        <span class="meta-item"{lic_title_attr}>{esc(lic)}</span>
        <span class="meta-item diff">门槛 <b>{esc(diff)}</b>{DOTS[DIFF_N[diff]]}</span>
        <span class="meta-item upd"><span class="s {cls}">{st}</span>{esc(meta['pushed_at'])}</span>
      </div>
    </article>"""


def main():
    check_only = "--check" in sys.argv
    check_generated = "--check-generated" in sys.argv
    tracks = json.loads((ROOT / "scripts/tracks.json").read_text(encoding="utf-8"))
    anns = json.loads((ROOT / "scripts/annotations.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))

    problems = []
    meta = {}
    for item in data:
        fn = item.get("full_name", "")
        key = fn.lower()
        if not fn:
            problems.append("data.json 里有缺少 full_name 的记录")
        elif key in meta:
            problems.append(f"仓库重复：{fn}（与 {meta[key]['full_name']} 仅大小写不同或完全重复）")
        else:
            meta[key] = item
        try:
            datetime.date.fromisoformat(item.get("pushed_at", ""))
        except (ValueError, TypeError):
            problems.append(f"最后提交日期无效：{fn or '(未命名)'} → {item.get('pushed_at')!r}")

    track_names = [t.get("cat", "") for t in tracks]
    if len(track_names) != len(set(track_names)):
        problems.append("tracks.json 里有重复的赛道 cat")
    valid_cats = set(track_names)
    for key in meta:
        if key not in anns:
            problems.append(f"缺少标注：{meta[key]['full_name']}（请补到 scripts/annotations.json）")
    for key, a in anns.items():
        name = a.get("name", key)
        if key != key.lower():
            problems.append(f"标注 key 必须小写：{key}")
        if key not in meta:
            problems.append(f"标注找不到仓库：{name}（data.json 里没有，先跑 scripts/fetch.py）")
        for field in ("name", "cat", "pitch", "aud", "note", "diff", "lic"):
            if not isinstance(a.get(field), str) or not a.get(field):
                problems.append(f"标注字段缺失或不是字符串：{key} → {field}")
        if a.get("cat") not in valid_cats:
            problems.append(f"未知赛道：{name} → {a.get('cat')}")
        if a.get("diff") not in DIFF_N:
            problems.append(f"门槛只能是 易/中/难：{name} → {a.get('diff')}")
    if problems:
        print("\n".join(problems))
        sys.exit(f"\n{len(problems)} 处问题，未生成页面。")

    by_cat = {}
    for key, a in anns.items():
        by_cat.setdefault(a["cat"], []).append(meta[key])
    for cat in by_cat:
        by_cat[cat].sort(key=lambda m: (-m["stars"], m["full_name"].lower()))

    total = sum(m["stars"] for m in meta.values())
    active = sum(1 for m in meta.values()
                 if not m.get("archived")
                 and (SNAP_DATE - datetime.date.fromisoformat(m["pushed_at"])).days <= 45)

    stats = "\n".join([
        f'    <div class="stat"><b>{len(meta)}</b><span>收录项目</span></div>',
        f'    <div class="stat"><b>{wan(total)}</b><span>累计星标</span></div>',
        f'    <div class="stat"><b>{len(by_cat)}</b><span>赛道分类</span></div>',
        f'    <div class="stat"><b>{active}</b><span>近 45 天有提交</span></div>',
    ])

    chips = [f'<button type="button" class="chip on" data-cat="all" aria-pressed="true">全部<i>{len(meta)}</i></button>']
    for t in tracks:
        if t["cat"] in by_cat:
            chips.append(f'<button type="button" class="chip" data-cat="{esc(t["cat"])}" aria-pressed="false">{esc(t["title"])}<i>{len(by_cat[t["cat"]])}</i></button>')

    langs = {}
    for m in meta.values():
        langs[m["lang"]] = langs.get(m["lang"], 0) + 1
    lang_opts = ['<option value="">全部语言</option>']
    for lang, n in sorted(langs.items(), key=lambda kv: (-kv[1], kv[0] == "-", kv[0])):
        lang_opts.append(f'<option value="{esc(lang)}">{esc(lang)} ({n})</option>')

    groups = []
    for t in tracks:
        items = by_cat.get(t["cat"], [])
        if not items:
            continue
        star_sum = sum(m["stars"] for m in items)
        body = "\n".join(card(m, anns[m["full_name"].lower()]) for m in items)
        groups.append(f"""  <section class="group" data-cat="{esc(t['cat'])}">
    <div class="group-head">
      <h2>{esc(t['title'])}</h2>
      <span class="gsub">{esc(t['sub'])}</span>
      <span class="gcount"><b class="gc-n">{len(items)}</b> 个项目 · ★ <span class="gc-s">{wan(star_sum)}</span></span>
    </div>
    <div class="grid">
{body}
    </div>
  </section>""")

    page = (ROOT / "scripts/template.html").read_text(encoding="utf-8").replace("\r\n", "\n")
    for ph, val in [
        ("{{STATS}}", stats), ("{{CHIPS}}", "".join(chips)), ("{{LANGS}}", "".join(lang_opts)),
        ("{{GROUPS}}", "\n".join(groups)), ("{{N_REPOS}}", str(len(meta))),
        ("{{N_TRACKS}}", str(len(by_cat))), ("{{DATE}}", SNAP_DATE.isoformat()),
    ]:
        assert ph in page, f"模板缺少占位符 {ph}"
        page = page.replace(ph, val)
    page = page.rstrip("\n") + "\n"

    print(f"项目 {len(meta)} / 赛道 {len(by_cat)} / 星标 {total:,}（{wan(total)}） / 近45天 {active}")
    for t in tracks:
        n = len(by_cat.get(t["cat"], []))
        print(f"  {t['title']:<18} {n:>3}")
    if check_generated:
        output = ROOT / "index.html"
        current = output.read_text(encoding="utf-8").replace("\r\n", "\n") if output.exists() else ""
        if current != page:
            sys.exit("index.html 与源文件不一致，请运行 python scripts/build.py 重新生成。")
        print("index.html 与源文件一致（--check-generated 未写入）")
        return
    if check_only:
        print("校验通过（--check 未写入）")
        return
    output = ROOT / "index.html"
    old_bytes = output.read_bytes() if output.exists() else b""
    eol = "\r\n" if b"\r\n" in old_bytes else "\n"
    output.write_bytes(page.replace("\n", eol).encode("utf-8"))
    print(f"已写入 index.html（保留 {eol!r} 换行）")


if __name__ == "__main__":
    main()
