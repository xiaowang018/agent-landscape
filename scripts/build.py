# -*- coding: utf-8 -*-
"""把 data.json（机器抓的元数据）+ annotations.json（人工标注）渲染成 index.html。

用法：
    python scripts/build.py            # 生成 index.html
    python scripts/build.py --check    # 只校验，不写文件

规则：
- 每个仓库都必须在 annotations.json 里有标注，否则报错退出（宁可不生成，也不生成半张卡）。
- data.json 里有、annotations.json 里没有的仓库 → 报错；反之 → 报错。
- 组内按星数降序；赛道顺序以 tracks.json 为准。
"""
import json
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP_DATE = datetime.date(2026, 11, 24)   # 快照日期：维护状态与「近 45 天」都按它算

LANG_COLOR = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Rust": "#dea584", "Go": "#00ADD8", "C#": "#68217a",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "-": "#94a3b8",
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


def status(pushed):
    days = (SNAP_DATE - datetime.date.fromisoformat(pushed)).days
    if days <= 45:
        return "活跃", "s-on"
    if days <= 210:
        return "维护中", "s-mid"
    return "沉寂", "s-off"


def card(meta, ann):
    fn = meta["full_name"]
    owner, _, name = fn.partition("/")
    lang = meta["lang"]
    diff = ann["diff"]
    st, cls = status(meta["pushed_at"])
    topics = " ".join(meta.get("topics") or [])
    # 搜索用的可见文案；topics 单独放 data-topics，避免同一个词存两份
    data_name = " ".join(x for x in (fn, ann["pitch"], ann["aud"], ann["note"]) if x).lower()
    color = LANG_COLOR.get(lang, "#94a3b8")
    act = 1 if st == "活跃" else 0
    return f"""    <article class="card" data-cat="{ann['cat']}" data-lang="{lang}"
             data-name="{data_name}"
             data-diff="{diff}" data-act="{act}" data-topics="{topics}"
             data-stars="{meta['stars']}" data-upd="{meta['pushed_at']}">
      <div class="card-top">
        <a class="repo" href="{meta['url']}" target="_blank" rel="noopener">
          <span class="owner">{owner}/</span><span class="name">{name}</span>
        </a>
        <span class="stars" title="{meta['stars']:,} stars">★ {wan(meta['stars'])}</span>
      </div>
      <h3 class="pitch">{ann['pitch']}</h3>
      <p class="note">{ann['note']}</p>
      <div class="fit"><span class="fitk">适合</span><span class="fitv">{ann['aud']}</span></div>
      <div class="topics"><span>⑂ Fork {fork_fmt(meta['forks'])}</span><span>创建于 {meta['created_at']}</span></div>
      <div class="card-foot">
        <span class="meta-item lang"><i class="ldot" style="background:{color}"></i>{lang}</span>
        <span class="meta-item">{ann['lic']}</span>
        <span class="meta-item diff">门槛 <b>{diff}</b>{DOTS[DIFF_N[diff]]}</span>
        <span class="meta-item upd"><span class="s {cls}">{st}</span>{meta['pushed_at']}</span>
      </div>
    </article>"""


def main():
    check_only = "--check" in sys.argv
    tracks = json.loads((ROOT / "scripts/tracks.json").read_text(encoding="utf-8"))
    anns = json.loads((ROOT / "scripts/annotations.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    meta = {x["full_name"].lower(): x for x in data}

    problems = []
    for key in meta:
        if key not in anns:
            problems.append(f"缺少标注：{meta[key]['full_name']}（请补到 scripts/annotations.json）")
    for key in anns:
        if key not in meta:
            problems.append(f"标注找不到仓库：{anns[key]['name']}（data.json 里没有，先跑 scripts/fetch.py）")
    valid_cats = {t["cat"] for t in tracks}
    for key, a in anns.items():
        if a["cat"] not in valid_cats:
            problems.append(f"未知赛道：{a['name']} → {a['cat']}")
        if a["diff"] not in DIFF_N:
            problems.append(f"门槛只能是 易/中/难：{a['name']} → {a['diff']}")
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
                 if (SNAP_DATE - datetime.date.fromisoformat(m["pushed_at"])).days <= 45)

    stats = "\n".join([
        f'    <div class="stat"><b>{len(meta)}</b><span>收录项目</span></div>',
        f'    <div class="stat"><b>{wan(total)}</b><span>累计星标</span></div>',
        f'    <div class="stat"><b>{len(by_cat)}</b><span>赛道分类</span></div>',
        f'    <div class="stat"><b>{active}</b><span>近 45 天有提交</span></div>',
    ])

    chips = [f'<button class="chip on" data-cat="all">全部<i>{len(meta)}</i></button>']
    for t in tracks:
        if t["cat"] in by_cat:
            chips.append(f'<button class="chip" data-cat="{t["cat"]}">{t["title"]}<i>{len(by_cat[t["cat"]])}</i></button>')

    langs = {}
    for m in meta.values():
        langs[m["lang"]] = langs.get(m["lang"], 0) + 1
    lang_opts = ['<option value="">全部语言</option>']
    for lang, n in sorted(langs.items(), key=lambda kv: (-kv[1], kv[0] == "-", kv[0])):
        lang_opts.append(f'<option value="{lang}">{lang} ({n})</option>')

    groups = []
    for t in tracks:
        items = by_cat.get(t["cat"], [])
        if not items:
            continue
        star_sum = sum(m["stars"] for m in items)
        body = "\n".join(card(m, anns[m["full_name"].lower()]) for m in items)
        groups.append(f"""  <section class="group" data-cat="{t['cat']}">
    <div class="group-head">
      <h2>{t['title']}</h2>
      <span class="gsub">{t['sub']}</span>
      <span class="gcount"><b class="gc-n">{len(items)}</b> 个项目 · ★ <span class="gc-s">{wan(star_sum)}</span></span>
    </div>
    <div class="grid">
{body}
    </div>
  </section>""")

    html = (ROOT / "scripts/template.html").read_text(encoding="utf-8")
    html = html.replace("\r\n", "\n")
    for ph, val in [
        ("{{STATS}}", stats), ("{{CHIPS}}", "".join(chips)), ("{{LANGS}}", "".join(lang_opts)),
        ("{{GROUPS}}", "\n".join(groups)), ("{{N_REPOS}}", str(len(meta))),
        ("{{N_TRACKS}}", str(len(by_cat))), ("{{DATE}}", SNAP_DATE.isoformat()),
    ]:
        assert ph in html, f"模板缺少占位符 {ph}"
        html = html.replace(ph, val)

    print(f"项目 {len(meta)} / 赛道 {len(by_cat)} / 星标 {total:,}（{wan(total)}） / 近45天 {active}")
    for t in tracks:
        n = len(by_cat.get(t["cat"], []))
        print(f"  {t['title']:<18} {n:>3}")
    if check_only:
        print("校验通过（--check 未写入）")
        return
    (ROOT / "index.html").write_text(html.rstrip("\n") + "\n", encoding="utf-8")
    print("已写入 index.html")


if __name__ == "__main__":
    main()
