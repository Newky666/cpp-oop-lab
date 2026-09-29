#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_search.py - 多源找题与题目导入

**题目不绑定任何固定网站。** 来源清单放在 ``data/sources.json``(见 oop_web.py),
用户随时可以增删; 每一种来源只需要满足两件事: 能搜(给出条目) / 能抓(给出题面)。

内置 provider:

  luogu       洛谷       搜题 + 题面    解析页面里的 lentille-context 水合 JSON
  dotcpp      dotcpp     搜题 + 题面    列表页表格行 + 详情页 panel_prob 段落
  codeforces  Codeforces 搜题 + 题面    免鉴权 API 拿 tag/rating, 题面走通用抽取
  github      GitHub     仓库推荐       公开搜索 API, 失败回退精选清单
  bing        必应       网页兜底       RSS
  generic     任意站点   搜题 + 题面    配置里给 search_url 模板 + item_regex

**任意一个链接都能导入**: ``import_problem(url)`` 先按 hosts 认出站点走专用解析,
认不出来就用 ``oop_web.extract_problem`` 的通用小标题切分策略(实测洛谷/dotcpp/
Codeforces/OpenJudge/牛客 都可用)。

设计约定: 网络函数不抛异常, 失败原因放进返回值; 每个来源单独 try, 互不影响。
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_bank
import oop_common as oc
import oop_html as oh
import oop_skills
import oop_web
from oop_html import (HttpResult, decode_body, html_to_text, http_get,  # noqa: F401
                      normalize_spaces, strip_scripts)

USER_AGENT = oh.USER_AGENT
DEFAULT_TIMEOUT = oh.DEFAULT_TIMEOUT

LUOGU_BASE = "https://www.luogu.com.cn"
DOTCPP_BASE = "https://www.dotcpp.com"
BING_BASE = "https://cn.bing.com"
GITHUB_API = "https://api.github.com"
CODEFORCES_BASE = "https://codeforces.com"
CODEFORCES_API = CODEFORCES_BASE + "/api/problemset.problems"

LUOGU_HEADERS = {
    "x-luogu-type": "content-only",
    "x-requested-with": "XMLHttpRequest",
    "Referer": LUOGU_BASE + "/problem/list",
}

LUOGU_DIFFICULTY = {
    0: "暂无评定", 1: "入门", 2: "普及-", 3: "普及/提高-",
    4: "普及+/提高", 5: "提高+/省选-", 6: "省选/NOI-", 7: "NOI/NOI+/CTSC",
}

# Codeforces rating -> 我们的三档(用于跨站点统一难度)
CF_RATING_BANDS = {1: (800, 1100), 2: (1200, 1600), 3: (1700, 2200)}

LEVEL_HINTS = (
    (("模拟", "字符串", "排序", "枚举", "语法", "入门", "implementation", "brute force"), 1),
    (("递归", "递推", "贪心", "二分", "搜索", "图论", "动态规划", "背包", "结构",
      "greedy", "binary search", "dp"), 2),
    (("数据结构", "线段树", "树形dp", "网络流", "计算几何", "平衡树", "后缀",
      "data structures", "graphs", "geometry"), 3),
)

SECTION_KEYS = (
    ("背景", "background"),
    ("描述", "description"),
    ("输入格式", "inputFormat"),
    ("输出格式", "outputFormat"),
    ("说明", "hint"),
    ("提示", "hint"),
)

# 离线时的 GitHub 精选资源(公开搜索里真实存在且与“面向对象练习”强相关的仓库)
GITHUB_CURATED: List[Dict[str, Any]] = [
    {"name": "AndorGunczer/CPP_OOP_Deep_Dive", "stars": 0,
     "description": "Exercises to practice Object Oriented Programming in C++"},
    {"name": "kerolloz/oop-exercises", "stars": 0,
     "description": "Exercises for those who want to learn Object Oriented Programming"},
    {"name": "taovietducofficial/OOP-Beginner", "stars": 0,
     "description": "Beginner-friendly Object-Oriented Programming examples"},
    {"name": "taovietducofficial/OOP-Student", "stars": 0,
     "description": "The next level after OOP-Beginner"},
    {"name": "hsf-training/cpluspluscourse", "stars": 0,
     "description": "A C++ course with exercises"},
]

# 老接口兼容用: 来源名 -> 中文标签
SOURCE_LABELS = {"luogu": "洛谷", "dotcpp": "dotcpp", "codeforces": "Codeforces",
                 "github": "GitHub", "bing": "必应", "web": "网页"}


def source_label(name: str) -> str:
    entry = oop_web.source_by_name(name)
    if entry:
        return str(entry.get("label") or name)
    return SOURCE_LABELS.get(name, name)


# ===========================================================================
# 洛谷
# ===========================================================================
def luogu_problem_url(pid: str) -> str:
    return "%s/problem/%s" % (LUOGU_BASE, (pid or "").strip())


def luogu_search_url(keyword: str) -> str:
    return "%s/problem/list?keyword=%s" % (LUOGU_BASE, urllib.parse.quote(keyword))


def difficulty_text(value: Any) -> str:
    try:
        return LUOGU_DIFFICULTY.get(int(value), "未知")
    except (TypeError, ValueError):
        return str(value or "未知")


def extract_pid(text: str) -> str:
    """从 "P1001" / "CF1A" / 完整链接 里取出洛谷题目编号。"""
    text = (text or "").strip()
    match = re.search(r"/problem/([A-Za-z][A-Za-z0-9_]*\d[A-Za-z0-9_]*)", text)
    if match:
        return match.group(1)
    match = re.search(r"\b([A-Za-z][A-Za-z0-9_]*\d[A-Za-z0-9_]*)\b", text)
    return match.group(1) if match else ""


_LENTILLE = re.compile(
    r'<script id="lentille-context" type="application/json">(.*?)</script>', re.S)
_TAG_ID_NAME = re.compile(r'href="/problem/list\?tag=(\d+)"[^>]*>(.*?)</a>', re.S)
_LIST_ITEM = re.compile(
    r'<li>\s*<h3>\s*<a href="/problem/([A-Za-z0-9_]+)"[^>]*>(.*?)</a>\s*</h3>(.*?)</li>',
    re.S)
_TAG_LINK_NAME = re.compile(r'href="/problem/list\?tag=\d+"[^>]*>(.*?)</a>', re.S)
_SECTION = re.compile(r"<section>(.*?)</section>", re.S)
_SECTION_H2 = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_PRE_PAIR = re.compile(r"<pre[^>]*>(.*?)</pre>", re.S)


def parse_lentille(html: str) -> Optional[Dict[str, Any]]:
    """取洛谷页面里的 lentille-context JSON(前端水合数据)。"""
    match = _LENTILLE.search(html or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def parse_tag_map(html: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for tag_id, name in _TAG_ID_NAME.findall(strip_scripts(html or "")):
        text = html_to_text(name, keep_newlines=False)
        if text:
            mapping[tag_id] = text
    return mapping


def tag_names(ids: Any, mapping: Dict[str, str]) -> List[str]:
    names: List[str] = []
    for item in ids or []:
        name = mapping.get(str(item))
        if name and name not in names:
            names.append(name)
    return names


def normalize_samples(raw: Any) -> List[Dict[str, str]]:
    """样例有两种形态: [[输入, 输出], ...] 或 [{"in":..,"out":..}, ...]。"""
    out: List[Dict[str, str]] = []
    for item in raw or []:
        if isinstance(item, dict):
            text_in = item.get("in", item.get("input", item.get("inputFormat", "")))
            text_out = item.get("out", item.get("output", item.get("outputFormat", "")))
            out.append({"in": str(text_in or ""), "out": str(text_out or "")})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append({"in": str(item[0] or ""), "out": str(item[1] or "")})
    return out


def parse_luogu_list(html: str, limit: int = 10) -> List[Dict[str, Any]]:
    """解析洛谷题目列表页: 优先内嵌 JSON, 退回 HTML 正则。"""
    ctx = parse_lentille(html)
    if ctx and isinstance(ctx.get("data"), dict):
        result = (ctx["data"].get("problems") or {}).get("result")
        if result:
            mapping = parse_tag_map(html)
            items = []
            for row in result:
                if not isinstance(row, dict) or not row.get("pid"):
                    continue
                items.append({
                    "pid": str(row["pid"]),
                    "title": str(row.get("name") or row.get("title") or row["pid"]),
                    "difficulty": difficulty_text(row.get("difficulty")),
                    "tags": tag_names(row.get("tags"), mapping),
                    "url": luogu_problem_url(str(row["pid"])),
                    "source": "luogu",
                })
                if len(items) >= limit:
                    break
            if items:
                return items

    items = []
    seen = set()
    for match in _LIST_ITEM.finditer(strip_scripts(html or "")):
        pid, title, rest = match.group(1), match.group(2), match.group(3)
        if pid in seen:
            continue
        seen.add(pid)
        tags = [html_to_text(t, keep_newlines=False) for t in _TAG_LINK_NAME.findall(rest)]
        items.append({
            "pid": pid, "title": html_to_text(title, keep_newlines=False),
            "difficulty": "—", "tags": [t for t in tags if t],
            "url": luogu_problem_url(pid), "source": "luogu",
        })
        if len(items) >= limit:
            break
    return items


def parse_luogu_problem(html: str, pid: str = "") -> Dict[str, Any]:
    """解析洛谷题面: 优先内嵌 JSON, 退回按 <section><h2> 切段落的 HTML 解析。"""
    info: Dict[str, Any] = {
        "pid": (pid or "").strip(), "title": "", "difficulty": "—", "tags": [],
        "background": "", "description": "", "inputFormat": "", "outputFormat": "",
        "hint": "", "samples": [], "source": "luogu",
        "url": luogu_problem_url(pid) if pid else "",
    }

    ctx = parse_lentille(html)
    problem = ((ctx or {}).get("data") or {}).get("problem") if ctx else None
    if isinstance(problem, dict):
        contenu = problem.get("contenu") if isinstance(problem.get("contenu"), dict) else {}
        info["pid"] = str(problem.get("pid") or info["pid"])
        info["title"] = str(problem.get("name") or contenu.get("name") or info["pid"])
        info["difficulty"] = difficulty_text(problem.get("difficulty"))
        info["tags"] = tag_names(problem.get("tags"), parse_tag_map(html))
        info["background"] = str(contenu.get("background") or "")
        info["description"] = str(contenu.get("description") or "")
        info["inputFormat"] = str(contenu.get("formatI") or "")
        info["outputFormat"] = str(contenu.get("formatO") or "")
        info["hint"] = str(contenu.get("hint") or "")
        samples = problem.get("samples")
        if not samples and isinstance(problem.get("content"), dict):
            samples = problem["content"].get("samples")
        info["samples"] = normalize_samples(samples or contenu.get("samples"))
        info["url"] = luogu_problem_url(info["pid"])
        if not info["title"]:
            info["title"] = info["pid"]
        return info

    clean = strip_scripts(html or "")
    h1 = _H1.search(clean)
    if h1:
        info["title"] = html_to_text(h1.group(1), keep_newlines=False)
    if not info["title"]:
        title_tag = re.search(r"<title>(.*?)</title>", clean, re.S)
        if title_tag:
            info["title"] = html_to_text(title_tag.group(1), keep_newlines=False).split(" - ")[0]
    if not info["pid"] and info["title"]:
        found = re.match(r"([A-Za-z][A-Za-z0-9_]*\d[A-Za-z0-9_]*)\s", info["title"])
        if found:
            info["pid"] = found.group(1)

    for block in _SECTION.findall(clean):
        head_match = _SECTION_H2.search(block)
        if not head_match:
            continue
        heading = html_to_text(head_match.group(1), keep_newlines=False)
        content = html_to_text(block[head_match.end():])
        for needle, key in SECTION_KEYS:
            if needle in heading:
                info[key] = (info[key] + "\n\n" + content) if info.get(key) else content
                break

    info["tags"] = list(parse_tag_map(clean).values())[:8]
    blocks = [html_to_text(b) for b in _PRE_PAIR.findall(clean)]
    blocks = [b for b in blocks if b]
    for index in range(0, len(blocks) - 1, 2):
        info["samples"].append({"in": blocks[index], "out": blocks[index + 1]})
    return info


def luogu_search(keyword: str, limit: int = 10,
                 timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, Any]], str]:
    url = "%s/problem/list?keyword=%s&page=1" % (LUOGU_BASE, urllib.parse.quote(keyword))
    result = http_get(url, timeout=timeout, headers=LUOGU_HEADERS)
    if not result.ok:
        return [], result.error or "请求洛谷失败"
    items = parse_luogu_list(result.text, limit=limit)
    if not items:
        return [], "洛谷没有返回匹配的题目(洛谷按题目名匹配, 换更具体的关键词试试)"
    return items, ""


def enrich_from_search(info: Dict[str, Any],
                       timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """题面页只给了标签 id, 也没有难度 —— 用一次列表搜索把它们补回来。"""
    pid = info.get("pid")
    if not pid:
        return info
    need_tags = not info.get("tags")
    need_diff = info.get("difficulty") in (None, "", "—", "未知")
    if not (need_tags or need_diff):
        return info

    url = "%s/problem/list?keyword=%s&page=1" % (LUOGU_BASE, urllib.parse.quote(pid))
    result = http_get(url, timeout=timeout, headers=LUOGU_HEADERS)
    if not result.ok:
        return info
    for item in parse_luogu_list(result.text, limit=20):
        if item.get("pid") != pid:
            continue
        if need_tags and item.get("tags"):
            info["tags"] = item["tags"]
        if need_diff and item.get("difficulty") not in (None, "", "—"):
            info["difficulty"] = item["difficulty"]
        break
    return info


def luogu_problem(pid: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    pid = extract_pid(pid) or (pid or "").strip()
    if not pid:
        return None, "题目编号为空, 例如 P1001"
    result = http_get("%s/problem/%s" % (LUOGU_BASE, pid),
                      timeout=timeout, headers=LUOGU_HEADERS)
    if not result.ok:
        return None, result.error or "请求洛谷失败"
    info = parse_luogu_problem(result.text, pid=pid)
    if not info.get("description"):
        return None, "没能从洛谷页面里解析出题面"
    if not info["title"]:
        info["title"] = pid
    return enrich_from_search(info, timeout=timeout), ""


# ===========================================================================
# dotcpp
# ===========================================================================
def dotcpp_problem_url(pid: str) -> str:
    return "%s/oj/problem%s.html" % (DOTCPP_BASE, str(pid).strip())


def dotcpp_list_url(page: int = 1, difficulty: Optional[int] = None) -> str:
    url = "%s/oj/problemset.php?page=%d" % (DOTCPP_BASE, max(1, int(page)))
    if difficulty is not None:
        url += "&difficulty=%d" % int(difficulty)
    return url


def extract_dotcpp_id(text: str) -> str:
    text = (text or "").strip()
    match = re.search(r"/oj/problem(\d+)\.html", text)
    if match:
        return match.group(1)
    match = re.search(r"(?:^|[^0-9])(\d{1,5})(?:[^0-9]|$)", text)
    return match.group(1) if match else ""


_DOTCPP_PID = re.compile(r"problem-number'><span class='center'>(\d+)</span>")
_DOTCPP_DIFF = re.compile(r"hard_label_(\d+)[^>]*>\s*([^<]*)</a>")
_DOTCPP_PANEL = '<div class="panel_prob_head">'
_DOTCPP_BODY = re.compile(r'<div class="panel_prob_body">(.*)', re.S)
_DOTCPP_H2 = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
_DOTCPP_SECTIONS = (
    ("题目描述", "description"), ("题目背景", "background"),
    ("输入格式", "inputFormat"), ("输出格式", "outputFormat"),
    ("提示", "hint"), ("数据范围", "hint"),
)


def parse_dotcpp_list(html: str, limit: int = 25,
                      keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    clean = strip_scripts(html or "")
    anchors = list(_DOTCPP_PID.finditer(clean))
    items: List[Dict[str, Any]] = []
    needle = (keyword or "").strip().lower()
    for index, match in enumerate(anchors):
        start = match.start()
        end = anchors[index + 1].start() if index + 1 < len(anchors) else len(clean)
        row = clean[start:end]
        pid = match.group(1)
        title_match = re.search(r"title='([^']*)'", row)
        title = html_to_text(title_match.group(1), keep_newlines=False) if title_match else pid
        diff_match = _DOTCPP_DIFF.search(row)
        difficulty = html_to_text(diff_match.group(2), keep_newlines=False) if diff_match else "—"
        if needle and needle not in title.lower():
            continue
        items.append({"pid": pid, "title": title, "difficulty": difficulty or "—",
                      "tags": [], "url": dotcpp_problem_url(pid), "source": "dotcpp"})
        if len(items) >= limit:
            break
    return items


def parse_dotcpp_problem(html: str, pid: str = "") -> Dict[str, Any]:
    clean = strip_scripts(html or "")
    info: Dict[str, Any] = {
        "pid": (pid or "").strip(), "title": "", "difficulty": "—", "tags": [],
        "background": "", "description": "", "inputFormat": "", "outputFormat": "",
        "hint": "", "samples": [], "source": "dotcpp",
        "url": dotcpp_problem_url(pid) if pid else "",
    }

    title_match = re.search(r"<title>(.*?)</title>", clean, re.S)
    if title_match:
        info["title"] = re.split(r"\s+[-–]\s+",
                                 html_to_text(title_match.group(1), keep_newlines=False))[0].strip()
    if not info["pid"]:
        found = re.search(r"problem(\d+)\.html", html or "")
        if found:
            info["pid"] = found.group(1)
            info["url"] = dotcpp_problem_url(info["pid"])

    sample_inputs: List[str] = []
    sample_outputs: List[str] = []
    for part in clean.split(_DOTCPP_PANEL)[1:]:
        head = _DOTCPP_H2.search(part)
        if not head:
            continue
        heading = html_to_text(head.group(1), keep_newlines=False)
        body_match = _DOTCPP_BODY.search(part)
        body = html_to_text(body_match.group(1)) if body_match else ""
        if "样例输入" in heading:
            sample_inputs.append(body)
            continue
        if "样例输出" in heading:
            sample_outputs.append(body)
            continue
        for needle, key in _DOTCPP_SECTIONS:
            if needle in heading:
                info[key] = (info[key] + "\n\n" + body) if info.get(key) else body
                break

    for index in range(min(len(sample_inputs), len(sample_outputs))):
        info["samples"].append({"in": sample_inputs[index], "out": sample_outputs[index]})
    if not info["title"]:
        info["title"] = "dotcpp %s" % (info["pid"] or "?")
    return info


def dotcpp_search(keyword: str, limit: int = 10, pages: int = 2,
                  timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, Any]], str]:
    """dotcpp 没有关键词搜索接口, 抓前几页列表再本地按题名过滤。"""
    collected: List[Dict[str, Any]] = []
    errors: List[str] = []
    for page in range(1, max(1, pages) + 1):
        result = http_get(dotcpp_list_url(page), timeout=timeout)
        if not result.ok:
            errors.append(result.error or "请求 dotcpp 失败")
            continue
        collected.extend(parse_dotcpp_list(result.text, limit=200, keyword=keyword))
        if len(collected) >= limit:
            break
    if not collected:
        return [], errors[0] if errors else "dotcpp 前 %d 页里没有匹配 “%s” 的题" % (pages, keyword)
    return collected[:limit], ""


def dotcpp_problem(pid: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    pid = extract_dotcpp_id(pid) or (pid or "").strip()
    if not pid:
        return None, "题号为空, 例如 1049"
    result = http_get(dotcpp_problem_url(pid), timeout=timeout)
    if not result.ok:
        return None, result.error or "请求 dotcpp 失败"
    info = parse_dotcpp_problem(result.text, pid=pid)
    if not info.get("description"):
        return None, "没能从 dotcpp 页面里解析出题面"
    return info, ""


# ===========================================================================
# Codeforces(免鉴权 API, 有 tag 与 rating)
# ===========================================================================
CF_CACHE = os.path.join(oc.DATA_DIR, "cache", "codeforces_problems.json")
CF_CACHE_TTL = 86400.0


def cf_problem_url(contest_id: Any, index: Any) -> str:
    return "%s/problemset/problem/%s/%s" % (CODEFORCES_BASE, contest_id, index)


def cf_rating_text(rating: Any) -> str:
    try:
        value = int(rating)
    except (TypeError, ValueError):
        return "未评级"
    if value <= 1000:
        return "入门(%d)" % value
    if value <= 1300:
        return "普及-(%d)" % value
    if value <= 1600:
        return "普及/提高-(%d)" % value
    if value <= 1900:
        return "普及+/提高(%d)" % value
    if value <= 2200:
        return "提高+/省选-(%d)" % value
    return "省选以上(%d)" % value


def cf_rating_band(level: Optional[int]) -> Tuple[int, int]:
    return CF_RATING_BANDS.get(int(level or 2), CF_RATING_BANDS[2])


def parse_codeforces_api(text: str, keyword: str = "", tags: Sequence[str] = (),
                         rating_range: Optional[Tuple[int, int]] = None,
                         limit: int = 10) -> List[Dict[str, Any]]:
    """把 problemset.problems 的 JSON 过滤成题目列表。"""
    try:
        payload = json.loads(text)
    except ValueError:
        return []
    problems = ((payload.get("result") or {}).get("problems")) or []
    needle = (keyword or "").strip().lower()
    tag_filter = [t.lower() for t in tags]
    items: List[Dict[str, Any]] = []
    for row in problems:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "")
        if needle and needle not in name.lower():
            continue
        row_tags = [str(t).lower() for t in (row.get("tags") or [])]
        if tag_filter and not any(t in row_tags for t in tag_filter):
            continue
        rating = row.get("rating")
        if rating_range and rating is not None:
            if not (rating_range[0] <= int(rating) <= rating_range[1]):
                continue
        contest_id, index = row.get("contestId"), row.get("index")
        if contest_id is None or not index:
            continue
        items.append({
            "pid": "CF%s%s" % (contest_id, index),
            "title": name,
            "difficulty": cf_rating_text(rating),
            "tags": [str(t) for t in (row.get("tags") or [])],
            "url": cf_problem_url(contest_id, index),
            "source": "codeforces",
            "rating": rating,
        })
        if len(items) >= limit:
            break
    return items


def codeforces_problemset(timeout: float = DEFAULT_TIMEOUT,
                          use_cache: bool = True) -> Tuple[str, str]:
    """取 Codeforces 全量题目表(约 6MB, 缓存一天)。"""
    if use_cache and os.path.isfile(CF_CACHE):
        payload = oc.load_json(CF_CACHE, default=None)
        if isinstance(payload, dict) and payload.get("text"):
            if time.time() - float(payload.get("ts", 0)) < CF_CACHE_TTL:
                return str(payload["text"]), ""
    result = http_get(CODEFORCES_API, timeout=max(timeout, 30.0))
    if not result.ok:
        return "", result.error or "请求 Codeforces API 失败"
    oc.save_json(CF_CACHE, {"ts": time.time(), "text": result.text})
    return result.text, ""


def codeforces_search(keyword: str, limit: int = 10, level: Optional[int] = None,
                      timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, Any]], str]:
    """搜 Codeforces 题: 先按题目名匹配, 匹配不到就按目标 rating 段给几道。"""
    text, error = codeforces_problemset(timeout=timeout)
    if error:
        return [], error
    items = parse_codeforces_api(text, keyword=keyword, limit=limit)
    if items:
        return items, ""
    lo, hi = cf_rating_band(level)
    items = parse_codeforces_api(text, rating_range=(lo, hi), limit=limit)
    if not items:
        return [], "Codeforces 题目表里没有符合条件的题"
    return items, ""


def cf_lookup(contest_id: Any, index: Any,
              timeout: float = DEFAULT_TIMEOUT) -> Optional[Dict[str, Any]]:
    """在全量题目表里查这一题的 rating 与 tags(用于跨站点统一难度)。"""
    text, error = codeforces_problemset(timeout=timeout)
    if error:
        return None
    try:
        payload = json.loads(text)
    except ValueError:
        return None
    for row in ((payload.get("result") or {}).get("problems") or []):
        if str(row.get("contestId")) == str(contest_id) and \
                str(row.get("index")).upper() == str(index).upper():
            return row
    return None


def codeforces_problem(contest_id: Any, index: Any,
                       timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    url = cf_problem_url(contest_id, index)
    result = http_get(url, timeout=timeout)
    if not result.ok:
        return None, result.error or "请求 Codeforces 失败"
    # Codeforces 的题面都包在 div.ttypography / div.problem-statement 里,
    # 直接点名这两个容器, 就不会把侧边栏和公告混进来
    info = oop_web.extract_problem(result.text, url,
                                   prefer_classes=("ttypography", "problem-statement"))
    info["pid"] = "CF%s%s" % (contest_id, index)
    info["source"] = "codeforces"
    info["url"] = url

    row = cf_lookup(contest_id, index, timeout=timeout)
    if row:
        info["difficulty"] = cf_rating_text(row.get("rating"))
        info["tags"] = [str(t) for t in (row.get("tags") or [])]
        if row.get("name"):
            info["title"] = str(row["name"])
    if not info.get("description"):
        return None, "没能从 Codeforces 页面里解析出题面"
    return info, ""


def parse_cf_id(target: str) -> Tuple[str, str]:
    """从 "4A" / "CF4A" / 链接 里取出 (contestId, index)。"""
    text = (target or "").strip()
    match = re.search(r"/(?:problemset/problem|contest)/(\d+)/problem/([A-Za-z]\d*)|"
                      r"/(?:problemset/problem|contest)/(\d+)/([A-Za-z]\d*)", text)
    if match:
        groups = [g for g in match.groups() if g]
        if len(groups) >= 2:
            return groups[0], groups[1]
    match = re.search(r"\b(?:cf)?(\d{1,5})([A-Za-z]\d?)\b", text, re.I)
    if match:
        return match.group(1), match.group(2).upper()
    return "", ""


# ===========================================================================
# GitHub / 必应 / generic
# ===========================================================================
def github_search(keyword: str, limit: int = 6,
                  timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, Any]], str]:
    query = "%s cpp exercises" % (keyword or "oop").strip()
    url = ("%s/search/repositories?q=%s&sort=stars&order=desc&per_page=%d"
           % (GITHUB_API, urllib.parse.quote(query), max(1, min(20, limit))))
    result = http_get(url, timeout=timeout,
                      headers={"Accept": "application/vnd.github+json"})
    if not result.ok:
        return list(GITHUB_CURATED[:limit]), (result.error or "GitHub 搜索失败") + "(已回退到精选清单)"
    try:
        data = json.loads(result.text)
    except ValueError:
        return list(GITHUB_CURATED[:limit]), "GitHub 返回的不是 JSON(已回退到精选清单)"
    items = []
    for row in (data.get("items") or [])[:limit]:
        if isinstance(row, dict):
            items.append({
                "name": row.get("full_name", ""),
                "url": row.get("html_url", ""),
                "stars": int(row.get("stargazers_count") or 0),
                "description": (row.get("description") or "").strip(),
            })
    if not items:
        return list(GITHUB_CURATED[:limit]), "GitHub 没返回结果(已回退到精选清单)"
    return items, ""


_RSS_ITEM = re.compile(r"<item>(.*?)</item>", re.S)
_RSS_TITLE = re.compile(r"<title>(.*?)</title>", re.S)
_RSS_LINK = re.compile(r"<link>(.*?)</link>", re.S)
_RSS_DESC = re.compile(r"<description>(.*?)</description>", re.S)


def parse_bing_rss(xml_text: str, limit: int = 8) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for block in _RSS_ITEM.findall(xml_text or ""):
        title = _RSS_TITLE.search(block)
        link = _RSS_LINK.search(block)
        desc = _RSS_DESC.search(block)
        if not title or not link:
            continue
        items.append({
            "title": html_to_text(title.group(1), keep_newlines=False),
            "url": html_to_text(link.group(1), keep_newlines=False),
            "snippet": html_to_text(desc.group(1)) if desc else "",
        })
        if len(items) >= limit:
            break
    return items


def bing_search(keyword: str, limit: int = 8,
                timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, str]], str]:
    url = "%s/search?q=%s&format=rss" % (BING_BASE, urllib.parse.quote(keyword))
    result = http_get(url, timeout=timeout)
    if not result.ok:
        return [], result.error or "搜索请求失败"
    items = parse_bing_rss(result.text, limit=limit)
    if not items:
        return [], "搜索结果为空(换个关键词试试)"
    return items, ""


# 兼容旧名字
web_search = bing_search


def generic_search(source: Dict[str, Any], keyword: str, limit: int = 10,
                   timeout: float = DEFAULT_TIMEOUT) -> Tuple[List[Dict[str, Any]], str]:
    """用户自定义来源: search_url 模板 + item_regex。"""
    label = source.get("label") or source.get("name") or "自定义来源"
    template = str(source.get("search_url") or "")
    if not template:
        return [], "%s 没有配置 search_url" % label
    url = template.replace("{q}", urllib.parse.quote(keyword)).replace("{Q}", keyword)
    result = http_get(url, timeout=timeout)
    if not result.ok:
        return [], result.error or "请求 %s 失败" % label
    rows = oop_web.extract_items(result.text, url, str(source.get("item_regex") or ""), limit)
    if not rows:
        return [], "%s: 没从搜索页解析出条目(检查 item_regex 是否匹配当前页面)" % label
    items = [{
        "pid": oop_web.guess_pid(row["url"]),
        "title": row["title"],
        "difficulty": "—",
        "tags": [],
        "url": row["url"],
        "source": source.get("name", "generic"),
    } for row in rows]
    return items, ""


# ===========================================================================
# 统一入口
# ===========================================================================
def suggest_links(keyword: str) -> List[Tuple[str, str]]:
    links = [("洛谷搜题", luogu_search_url(keyword)),
             ("dotcpp题库", dotcpp_list_url(1)),
             ("Codeforces", "%s/problemset" % CODEFORCES_BASE),
             ("GitHub", "https://github.com/search?q=%s&type=repositories"
              % urllib.parse.quote("%s cpp exercises" % keyword)),
             ("必应搜索", "https://www.bing.com/search?q=" + urllib.parse.quote(keyword))]
    for item in oop_web.load_sources():
        if item.get("kind") == "generic" and item.get("search_url"):
            links.append((item.get("label") or item["name"],
                          item["search_url"].replace("{q}", urllib.parse.quote(keyword))))
    return links


def run_provider(kind: str, source: Dict[str, Any], keyword: str, limit: int,
                 level: Optional[int], timeout: float) -> Tuple[List[Dict[str, Any]], str]:
    """按 kind 调用对应的抓取实现。"""
    if kind == "luogu":
        return luogu_search(keyword, limit=limit, timeout=timeout)
    if kind == "dotcpp":
        return dotcpp_search(keyword, limit=limit, timeout=timeout)
    if kind == "codeforces":
        return codeforces_search(keyword, limit=limit, level=level, timeout=timeout)
    if kind == "generic":
        return generic_search(source, keyword, limit=limit, timeout=timeout)
    if kind == "github":
        items, error = github_search(keyword, limit=min(6, limit), timeout=timeout)
        return items, error
    if kind == "bing":
        items, error = bing_search("%s C++ 面向对象 练习题" % keyword,
                                   limit=limit, timeout=timeout)
        return items, error
    return [], "未知的来源类型: %s" % kind


def search_all(keyword: str, limit: int = 8, timeout: float = DEFAULT_TIMEOUT,
               sources: Optional[Sequence[str]] = None,
               level: Optional[int] = None) -> Dict[str, Any]:
    """遍历已启用的来源; 每个来源单独容错, 失败原因汇总在 errors 里。"""
    entries = oop_web.enabled_sources()
    if sources is not None:
        wanted = [str(name).lower() for name in sources]
        entries = [e for e in entries if str(e.get("name", "")).lower() in wanted]

    result: Dict[str, Any] = {
        "keyword": keyword,
        "links": suggest_links(keyword),
        "errors": [],
        "order": [],
    }
    for entry in entries:
        name = str(entry.get("name", "?"))
        kind = str(entry.get("kind", "generic"))
        result[name] = []
        result["order"].append(name)
        items, error = run_provider(kind, entry, keyword, limit, level, timeout)
        result[name] = items
        if error:
            result["errors"].append("%s: %s" % (entry.get("label") or name, error))

    if not result["order"]:
        result["errors"].append("没有任何已启用的题目来源(检查 data/sources.json)")
    return result


def render_search(result: Dict[str, Any]) -> List[str]:
    lines: List[str] = [oc.color("搜索关键词: %s" % result.get("keyword", ""), "bold"), ""]
    for name in result.get("order") or []:
        items = result.get(name) or []
        if not items:
            continue
        label = source_label(name)
        entry = oop_web.source_by_name(name) or {}
        kind = entry.get("kind", "")
        if kind == "github":
            lines.append(oc.color("%s 练习仓库(%d):" % (label, len(items)), "cyan"))
            for item in items:
                stars = ("★%d" % item["stars"]) if item.get("stars") else ""
                lines.append("  %s %s" % (oc.pad_end(item.get("name", ""), 38),
                                          oc.color(stars, "yellow")))
                if item.get("description"):
                    lines.append(oc.color("      " + oc.truncate(item["description"], 70), "grey"))
                lines.append(oc.color("      " + item.get("url", ""), "grey"))
        elif kind == "bing":
            lines.append(oc.color("%s 网页参考(%d, 相关性有限):" % (label, len(items)), "cyan"))
            for item in items[:4]:
                lines.append("  " + oc.truncate(item["title"], 64))
                lines.append(oc.color("      " + oc.truncate(item["url"], 76), "grey"))
        else:
            lines.append(oc.color("%s 题目(%d):" % (label, len(items)), "cyan"))
            for item in items:
                lines.append("  %-10s %s %s  %s" % (
                    item.get("pid", ""),
                    oc.pad_end(oc.truncate(item.get("title", ""), 38), 38),
                    oc.pad_end(item.get("difficulty", "—"), 16),
                    oc.color(",".join(item.get("tags", [])[:3]), "grey")))
            lines.append(oc.color("  导入: py oop_lab.py pull %s" % items[0].get("pid", ""), "grey"))
        lines.append("")

    links = result.get("links") or []
    if links:
        lines.append(oc.color("直接打开:", "cyan"))
        for label, url in links:
            lines.append("  %s %s" % (oc.pad_end(label, 16), url))
        lines.append("")

    errors = result.get("errors") or []
    if errors:
        lines.append(oc.color("联网提示(不影响本地题库使用):", "yellow"))
        for item in errors:
            lines.append("  · " + item)
    return lines


# ===========================================================================
# 导入
# ===========================================================================
def guess_level(tags: Sequence[str], difficulty: str = "", title: str = "") -> int:
    """按难度标签定档; 没有难度标签时退化成关键词匹配(标题也参与)。"""
    if difficulty in ("入门", "普及-", "简单") or difficulty.startswith("入门(") \
            or difficulty.startswith("普及-("):
        return 1
    if difficulty in ("普及/提高-", "普及+/提高", "中等") or difficulty.startswith("普及/"):
        return 2
    if difficulty in ("提高+/省选-", "省选/NOI-", "NOI/NOI+/CTSC", "困难", "较难") \
            or difficulty.startswith(("提高+", "省选")):
        return 3
    joined = " ".join([*tags, difficulty or "", title or ""])
    for words, level in LEVEL_HINTS:
        if any(word in joined for word in words):
            return level
    return 2


def build_imported_problem(info: Dict[str, Any], level: Optional[int] = None) -> Dict[str, Any]:
    """把抓到的题面转成本题库的题目结构(没有自动用例, 作为“参考练习”存在)。"""
    pid = info.get("pid") or "?"
    title = info.get("title") or pid
    tags = list(info.get("tags") or [])
    source = info.get("source", "web")
    label = source_label(source)
    io_parts = []
    if info.get("inputFormat"):
        io_parts.append("输入格式: " + info["inputFormat"])
    if info.get("outputFormat"):
        io_parts.append("输出格式: " + info["outputFormat"])

    desc_parts = [info.get("description", "")]
    if info.get("background"):
        desc_parts.insert(0, info["background"])
    if info.get("hint"):
        desc_parts.append("提示: " + info["hint"])
    desc_parts.append("来源: %s (%s)" % (info.get("url", ""), label))

    # 在线题没有我们统一的知识点标签, 从标题+描述里猜几个, 这样它也能参与画像与选题
    guessed = [oop_skills.skill_name(sid) for sid in oop_skills.classify_text(
        "%s\n%s\n%s" % (title, info.get("description", ""), info.get("inputFormat", "")))]
    topics = ["在线导入"] + guessed + [t for t in tags if t not in guessed]

    # 用 % 格式化而不是 str.format: C++ 代码里满是花括号, format 会当成占位符
    skeleton_tpl = (
        "// %(pid)s —— %(title)s\n"
        "// 来源: %(url)s\n"
        "// 标签: %(tags)s\n"
        "//\n"
        "// TODO: 先想清楚要抽象出哪些类 / 每个类的职责, 再动手写。\n"
        "//       写完用 `py oop_lab.py review %(id)s` 自查面向对象写法。\n"
        "#include <iostream>\n"
        "\n"
        "int main() {\n"
        "    // 在这里实现\n"
        "    return 0;\n"
        "}\n"
    )

    problem = {
        "id": oop_bank.next_user_id(),
        "level": level or guess_level(tags, info.get("difficulty", ""), title),
        "slug": oc.slugify("%s-%s" % (str(pid).lower(), title)),
        "title": title,
        "topics": topics,
        "desc": "\n\n".join(part for part in desc_parts if part),
        "require": [
            "先在纸上写出类图(有哪些类、各自的职责), 再开始写代码。",
            "至少使用 2 个类, 并体现出封装 / 继承 / 多态中的一种。",
            "自己补 2~3 组测试用例放进 tests/ 目录(在线导入的题没有内建用例)。",
        ],
        "io": "\n".join(io_parts) or "见题面。",
        "samples": info.get("samples") or [],
        "hints": ["这是从 %s 导入的题目, 没有内建自动用例, 请自己补测试数据。" % label],
        "checklist": [
            "类与职责的划分是否清晰(有没有一个类什么都在干)?",
            "数据成员是否都 private / protected ?",
            "有没有该用虚函数的地方用了 if-else 硬判断?",
        ],
        "solution": "",
        "tests": [],
        "source": "user",
        "origin": source,
        "url": info.get("url", ""),
    }
    problem["skeleton"] = skeleton_tpl % {
        "pid": pid, "title": title, "url": info.get("url", ""),
        "tags": " / ".join(tags) or "无", "id": problem["id"],
    }
    return problem


def detect_source(target: str) -> str:
    """猜一个题目标识来自哪里: 先看链接的域名, 再看编号格式。"""
    text = (target or "").strip()
    if text.lower().startswith(("http://", "https://")):
        entry = oop_web.detect_source(text)
        if entry:
            return str(entry.get("name"))
        return "web"
    if re.fullmatch(r"\d{1,5}", text):
        return "dotcpp"
    if re.fullmatch(r"(?i)cf?\d{1,5}[a-z]\d?", text) or re.fullmatch(r"(?i)\d{1,5}[a-z]\d?", text):
        return "codeforces"
    return "luogu"


def web_problem(url: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    """任意链接 -> 通用题面抽取(不依赖站点结构)。"""
    result = http_get(url, timeout=timeout)
    if not result.ok:
        return None, result.error or "请求失败"
    entry = oop_web.detect_source(url)
    info = oop_web.extract_problem(result.text, url)
    info["source"] = str(entry.get("name")) if entry else "web"
    if not info.get("description") and not info.get("samples"):
        return None, "没能从这个页面里抽到题面(可能是 JS 渲染, 或者根本不是题面页)"
    return info, ""


def import_problem(target: str, source: str = "auto", level: Optional[int] = None,
                   timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    """抓取并保存一道题 —— 支持任意链接。"""
    target = (target or "").strip()
    if not target:
        return None, "没有给出题目(可以是题号, 也可以是任意题面链接)"
    source = (source or "auto").lower()
    if source == "auto":
        source = detect_source(target)
    kind = source
    entry = oop_web.source_by_name(source)
    if entry:
        kind = str(entry.get("kind") or kind)

    if target.lower().startswith(("http://", "https://")):
        if kind == "luogu":
            info, error = luogu_problem(target, timeout=timeout)
        elif kind == "dotcpp":
            info, error = dotcpp_problem(target, timeout=timeout)
        elif kind == "codeforces":
            contest_id, index = parse_cf_id(target)
            if not contest_id:
                return None, "没法从链接里认出 Codeforces 题号"
            info, error = codeforces_problem(contest_id, index, timeout=timeout)
        else:
            info, error = web_problem(target, timeout=timeout)   # 任意站点
    elif kind == "dotcpp":
        info, error = dotcpp_problem(target, timeout=timeout)
    elif kind == "codeforces":
        contest_id, index = parse_cf_id(target)
        if not contest_id:
            return None, "题号格式应为 4A 或 CF4A"
        info, error = codeforces_problem(contest_id, index, timeout=timeout)
    else:
        info, error = luogu_problem(target, timeout=timeout)

    if info is None:
        return None, error
    info["source"] = kind if kind in SOURCE_LABELS or entry else "web"
    if not info.get("url"):
        info["url"] = target
    return oop_bank.add_user(build_imported_problem(info, level=level)), ""


def import_luogu(pid_or_url: str, level: Optional[int] = None,
                 timeout: float = DEFAULT_TIMEOUT) -> Tuple[Optional[Dict[str, Any]], str]:
    return import_problem(pid_or_url, source="luogu", level=level, timeout=timeout)


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    oc.enable_ansi()
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("用法: py oop_search.py <关键词>   |   py oop_search.py pull <题号或链接>")
        return 2
    if args[0] in ("--pull", "pull") and len(args) >= 2:
        problem, error = import_problem(args[1])
        if problem is None:
            print("导入失败: %s" % error)
            return 1
        print("已导入 %s %s" % (problem["id"], problem["title"]))
        return 0
    for row in render_search(search_all(" ".join(args))):
        print(row)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
