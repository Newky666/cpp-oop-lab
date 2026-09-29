#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_web.py - 通用题面抽取 + 可配置的题目来源

题目不绑定任何固定网站, 这里负责两件事:

一、**通用题面抽取** ``extract_problem(html, url)``
    不依赖具体站点的 DOM 结构, 而是用「小标题切段落」的策略, 对绝大多数 OJ
    与题解博客都有效(实测洛谷 / dotcpp / Codeforces / OpenJudge / 牛客都能抽出来):

      1. 先去 script/style/noscript, 再把 <pre> 块单独收起来(样例通常在里面);
      2. HTML 转纯文本, 逐行看是不是「小节标题」: 整行文字很短, 且等于/以
         题面小标题开头(题目描述/输入格式/输出格式/样例输入/提示…… 中英文都认);
      3. 按小标题把正文切进 description / inputFormat / outputFormat / hint;
      4. 样例优先用「样例输入/样例输出」标记; 没有标记就用 <pre> 块配对
         (多块时取最后两块 —— 前面的往往是格式说明而不是样例);
      5. 一个都没切到时, 退化成「第一个标题之前的正文」, 并剔掉时间/内存限制这类元信息。

二、**来源注册表** ``load_sources()``
    ``data/sources.json`` 里列出所有可用的题目来源, 用户随时可以增删改。
    内置 5 种 kind(专用解析) + 1 种 generic(任意站点, 只要给出搜索 URL 模板与条目正则):

      kind=luogu / dotcpp / codeforces / github / bing    -> 内置专用 provider
      kind=generic  ->  search_url 里的 {q} 会被替换成 URL 编码后的关键词,
                        再用 item_regex(第 1 组=链接, 第 2 组=标题)解析条目

    抓不到也没关系: 任何来源失败都只影响它自己, search_all 会把错误汇总给用户。
"""

from __future__ import annotations

import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_common as oc
import oop_html as oh
from oop_html import html_to_text, normalize_spaces

SOURCES_FILE = os.path.join(oc.DATA_DIR, "sources.json")

# ---------------------------------------------------------------------------
# 题面小标题(中英文都认)
# ---------------------------------------------------------------------------
SECTIONS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("background", ("题目背景", "背景描述", "题目来源", "题目出处")),
    ("description", ("题目描述", "问题描述", "问题陈述", "题目大意", "题目",
                     "描述", "problem statement", "statement", "description", "task")),
    ("inputFormat", ("输入格式", "输入描述", "输入说明", "输入要求", "输入",
                     "input format", "input description", "input")),
    ("outputFormat", ("输出格式", "输出描述", "输出说明", "输出要求", "输出",
                      "output format", "output description", "output")),
    ("hint", ("提示", "说明", "数据范围", "数据规模", "注意", "样例说明", "评分说明",
              "hint", "note", "constraints", "scoring")),
)

SAMPLE_IN = ("样例输入", "输入样例", "输入示例", "输入样例1", "样例1输入",
             "sample input", "example input", "input example")
SAMPLE_OUT = ("样例输出", "输出样例", "输出示例", "输出样例1", "样例1输出",
              "sample output", "example output", "output example")

# 页面里的元信息行(时间限制/内存限制/输入输出设备), 抽取正文时要剔除
_META_LINE = re.compile(
    r"(time limit|memory limit|per test|input file|output file|standard input|"
    r"standard output|^\s*(input|output)\s*[:：]|时间限制|内存限制|输入文件|输出文件|"
    r"题目来源[:：]|查看|提交|收藏|难度[:：]|通过率)", re.I)

# 明显不是题目名的文本
_NOISE_TITLES = {
    "problem", "problems", "enter", "register", "log in", "sign in", "login",
    "首页", "主页", "题库", "题目", "题目列表", "题解", "提交", "排名", "比赛", "讨论",
    "登录", "注册", "帮助", "关于", "javascript", "undefined", "null",
}


# ---------------------------------------------------------------------------
# 通用题面抽取
# ---------------------------------------------------------------------------
_PRE = re.compile(r"(?is)<pre[^>]*>(.*?)</pre>")
_TITLE_TAG = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
_CLASS_ATTR = re.compile(r"""class\s*=\s*["']([^"']*)["']""", re.I)
_OPEN_TAG = re.compile(r"(?is)<(h1|h2|div)\b([^>]*)>")

# 单独的“时间/内存数值”行, 在正文兜底时要剔掉
_VALUE_LINE = re.compile(r"^\s*[\d.]+\s*(seconds?|megabytes?|gigabytes?|kilobytes?|bytes?|"
                         r"ms|MB|KB|GB|秒|毫秒)\s*$", re.I)


def _clean_title(text: str) -> str:
    text = html_to_text(text, keep_newlines=False).strip(" \t·:：|-—_")
    return re.sub(r"\s{2,}", " ", text)


def _immediate_text(html: str, position: int, window: int = 240) -> str:
    """取某个开标签之后的第一段可见文字(允许跨过一层嵌套标签)。

    不能直接用 `<(div)>(.*?)</\\1>`, 因为嵌套的 div 会让外层把内层一起吞掉 ——
    Codeforces 的题名就在 <div class="ttypography"><div class="title">… 里面。
    """
    fragment = (html or "")[position:position + window]
    for part in re.split(r"<[^>]*>", fragment, maxsplit=2):
        text = html_to_text(part, keep_newlines=False)
        if text:
            return text
    return ""


def pick_title(html: str) -> str:
    """猜题目名: 先看 h1/h2 与 class 正好是 title 的块, 再退到 <title> 标签。"""
    candidates: List[str] = []
    for match in _OPEN_TAG.finditer(html or ""):
        tag, attrs = match.group(1).lower(), match.group(2)
        if tag == "div":
            found = _CLASS_ATTR.search(attrs)
            classes = found.group(1).split() if found else []
            # 必须是独立的 title 类, 不能是 property-title / problem-title 这种
            if "title" not in classes:
                continue
        text = _clean_title(_immediate_text(html, match.end()))
        if not _usable_title(text):
            continue
        candidates.append(text)
    if candidates:
        return max(candidates, key=len)

    match = _TITLE_TAG.search(html or "")
    if match:
        text = _clean_title(match.group(1))
        text = re.split(r"\s+[-–|_]\s+", text)[0].strip()
        if _usable_title(text):
            return text
    return ""


def _usable_title(text: str) -> bool:
    if not text or not (3 <= len(text) <= 90):
        return False
    low = text.lower().strip(" .:：")
    if low in _NOISE_TITLES or low.isdigit():
        return False
    if _META_LINE.search(low):
        return False
    return True


def classify_line(line: str) -> Optional[str]:
    """整行是不是一个小节标题? 返回归一化后的字段名。"""
    key = line.strip().strip(":：*#·-—>「」[]()（） ")
    if not key or len(key) > 18:
        return None
    low = key.lower()
    for word in SAMPLE_IN:
        if low == word or low.startswith(word):
            return "sampleIn"
    for word in SAMPLE_OUT:
        if low == word or low.startswith(word):
            return "sampleOut"
    for name, words in SECTIONS:
        for word in words:
            if low == word or low.startswith(word + ":") or low.startswith(word + "："):
                return name
    return None


def normalize_sample(text: str) -> str:
    """样例文本清理: 去掉「（无）」这类占位, 压掉多余空行。"""
    text = normalize_spaces(text or "").strip()
    if text in ("（无）", "(无)", "无", "none", "None", "N/A"):
        return ""
    return oh.squash_blank_lines(text)


_TAG_TOKEN = re.compile(r"(?is)<(/?)([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>")
_VOID_TAGS = {"br", "img", "input", "hr", "meta", "link", "source", "area",
              "base", "col", "embed", "param", "track", "wbr"}
_CONTAINER_TAGS = {"div", "article", "section", "main", "td", "li", "p",
                   "blockquote", "body", "dl", "dd"}
_LINK_BLOCK = re.compile(r"(?is)<a\b[^>]*>.*?</a\s*>")


def _pair_tags(html: str) -> Tuple[List[Any], Dict[int, Tuple[int, int]]]:
    """给 HTML 里的标签配对, 返回 (标签列表, {开标签下标: (闭标签下标, 深度)})。"""
    tokens = list(_TAG_TOKEN.finditer(html or ""))
    pairs: Dict[int, Tuple[int, int]] = {}
    stack: List[Tuple[int, str, int]] = []
    for index, token in enumerate(tokens):
        name = token.group(2).lower()
        if name in _VOID_TAGS:
            continue
        if token.group(1):
            for depth in range(len(stack) - 1, -1, -1):
                if stack[depth][1] == name:
                    pairs[stack[depth][0]] = (index, stack[depth][2])
                    del stack[depth:]
                    break
        else:
            stack.append((index, name, len(stack)))
    return tokens, pairs


def elements_by_class(html: str, class_token: str) -> List[Tuple[int, int, str]]:
    """找出 class 里含指定词的元素的 (内容起点, 内容终点, 标签名)。"""
    tokens, pairs = _pair_tags(html)
    found: List[Tuple[int, int, str]] = []
    for open_index, (close_index, _depth) in pairs.items():
        attrs = tokens[open_index].group(3)
        match = _CLASS_ATTR.search(attrs)
        classes = match.group(1).split() if match else []
        if class_token in classes:
            found.append((tokens[open_index].end(), tokens[close_index].start(),
                          tokens[open_index].group(2).lower()))
    return found


def find_content_container(html: str, min_text: int = 250) -> str:
    """readability 的精简版: 找出“文本多、链接少”的那个容器。

    页面顶栏/侧边栏的特征是链接密度高, 正文的特征是纯文本多。
    评分 = 正文长度 − 3 × 链接文字长度, 然后在接近最高分的候选里取嵌套最深的那个。
    这样站点导航、侧边栏会被自动排除, 不需要为每个站点写规则 ——
    这是“题目可以来自任何网站”的关键一步。
    """
    tokens, pairs = _pair_tags(html)
    if not tokens:
        return html or ""

    candidates: List[Tuple[float, int, int, int, int]] = []
    for open_index, (close_index, depth) in pairs.items():
        name = tokens[open_index].group(2).lower()
        if name not in _CONTAINER_TAGS:
            continue
        start, end = tokens[open_index].end(), tokens[close_index].start()
        inner = html[start:end]
        if len(inner) < 200:
            continue
        text_len = len(html_to_text(inner, keep_newlines=False))
        if text_len < min_text:
            continue
        link_len = 0
        for block in _LINK_BLOCK.findall(inner):
            link_len += len(html_to_text(block, keep_newlines=False))
        candidates.append((text_len - 3.0 * link_len, depth, text_len, start, end))

    if not candidates:
        return html or ""
    best_score = max(item[0] for item in candidates)
    near = [item for item in candidates if item[0] >= 0.85 * best_score]
    chosen = max(near, key=lambda item: (item[1], item[2]))
    return html[chosen[3]:chosen[4]]


def _is_meta(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return bool(_META_LINE.search(stripped) or _VALUE_LINE.match(stripped))


def _paragraph_fallback(lines: Sequence[str], title: str = "") -> str:
    """没有「题目描述」小标题时, 从正文里挑出一段像题干的内容。

    做法: 剔除明显是导航/时间内存限制的行, 找到最长的一行当锚点,
    再向前后扩展成段落 —— 页面顶部的导航栏都是短行, 自然被隔在外面。
    """
    cleaned: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if _is_meta(stripped):
            continue
        cleaned.append(stripped)

    best_index, best_len = -1, 0
    for index, item in enumerate(cleaned):
        if len(item) > best_len:
            best_index, best_len = index, len(item)
    if best_index < 0 or best_len < 20:
        return ""

    start = best_index
    while start > 0 and cleaned[start - 1] and len(cleaned[start - 1]) >= 15:
        start -= 1

    block = [item for item in cleaned[start:] if item]
    text = "\n\n".join(block)
    if title and text.startswith(title):
        text = text[len(title):].lstrip()
    return oh.squash_blank_lines(text)


# 页面上到处存在的按钮/交互文案, 会污染样例与正文
_UI_NOISE = {"复制", "复制代码", "copy", "copy code", "展开", "收起",
             "返回顶部", "更多", "查看更多", "上一题", "下一题"}


class _Analysis:
    def __init__(self) -> None:
        self.sections: Dict[str, str] = {}
        self.preamble: List[str] = []
        self.samples: List[Dict[str, str]] = []

    def quality(self, title: str) -> float:
        """粗略评价一次抽取结果好不好, 用来在“容器版”与“整页版”之间二选一。"""
        desc = self.sections.get("description") or _paragraph_fallback(self.preamble, title)
        size = len(desc)
        score = 0.0
        if 60 <= size <= 8000:
            score += 3.0
        elif size > 0:
            score += 1.0
        for key in ("inputFormat", "outputFormat", "hint"):
            if self.sections.get(key):
                score += 1.0
        if self.samples:
            score += 2.0
        if any(word in desc for word in _UI_NOISE):
            score -= 2.0
        return score


def _analyze(fragment: str) -> _Analysis:
    """把一段 HTML 切成段落并抽出样例。"""
    result = _Analysis()
    pre_texts = [normalize_sample(html_to_text(b)) for b in _PRE.findall(fragment or "")]
    pre_texts = [t for t in pre_texts if t and t.lower() not in _UI_NOISE]

    body = _PRE.sub("\n\n", fragment or "")
    buckets: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in html_to_text(body).split("\n"):
        kind = classify_line(line)
        if kind:
            current = kind
            buckets.setdefault(kind, [])
            continue
        stripped = line.strip()
        if current is None:
            result.preamble.append(line)
            continue
        if len(stripped) <= 1 and not stripped.isdigit():
            continue
        if stripped.lower() in _UI_NOISE:
            continue
        # 段落内部的短元信息行也要剔掉(如 Codeforces 的 "standard input")
        if _is_meta(stripped) and len(stripped) < 40:
            continue
        buckets[current].append(line)

    result.sections = {key: oh.squash_blank_lines("\n".join(value))
                       for key, value in buckets.items()}

    samples: List[Dict[str, str]] = []
    if result.sections.get("sampleIn") or result.sections.get("sampleOut"):
        samples.append({"in": result.sections.get("sampleIn", ""),
                        "out": result.sections.get("sampleOut", "")})
    elif len(pre_texts) >= 2:
        # 多块时取最后两块: 前面的 <pre> 常常是格式说明而不是样例
        samples.append({"in": pre_texts[-2], "out": pre_texts[-1]})
    result.samples = [s for s in samples if s.get("in") or s.get("out")]
    return result


def extract_problem(html: str, url: str = "",
                    prefer_classes: Sequence[str] = ()) -> Dict[str, Any]:
    """通用题面抽取: 任何网站的题面页都应该能出一个可用的结果。

    会试好几个范围再取最好的那个结果:

      1. ``prefer_classes`` 里点名的容器(例如 Codeforces 的 ttypography);
      2. 自动识别出来的正文容器;
      3. 整页兜底。

    这样既能在结构清晰的站点上避开导航噪声, 又不会因为容器识别失误而一无所获。
    """
    raw_html = html or ""
    title = pick_title(raw_html) or guess_pid(url) or "未命名题目"

    fragments: List[str] = []
    for token in prefer_classes:
        blocks = elements_by_class(raw_html, token)
        if blocks:
            start, end, _tag = max(blocks, key=lambda item: item[1] - item[0])
            fragments.append(raw_html[start:end])
            break
    container = find_content_container(raw_html)
    fragments.append(container)
    fragments.append(raw_html)

    best: Optional[_Analysis] = None
    best_score = -1.0
    seen = set()
    for fragment in fragments:
        if not fragment or fragment in seen:
            continue
        seen.add(fragment)
        parsed = _analyze(fragment)
        score = parsed.quality(title)
        if score > best_score:
            best, best_score = parsed, score
    analysis = best or _Analysis()

    description = analysis.sections.get("description", "")
    if not description:
        description = _paragraph_fallback(analysis.preamble, title)

    return {
        "pid": guess_pid(url),
        "title": title,
        "difficulty": "—",
        "tags": [],
        "background": analysis.sections.get("background", ""),
        "description": description,
        "inputFormat": analysis.sections.get("inputFormat", ""),
        "outputFormat": analysis.sections.get("outputFormat", ""),
        "hint": analysis.sections.get("hint", ""),
        "samples": analysis.samples,
        "source": "web",
        "url": url,
    }


# (正则, 取哪几组拼成题号)
_PID_PATTERNS: Tuple[Tuple[str, Tuple[int, ...]], ...] = (
    (r"/problem/([A-Za-z]{1,6}\d{1,6})", (1,)),
    (r"/problemset/problem/(\d+)/([A-Za-z]\d*)", (1, 2)),
    (r"/contest/(\d+)/problem/([A-Za-z]\d*)", (1, 2)),
    (r"/problem(\d+)\.html", (1,)),
    (r"/acm/problem/(\d+)", (1,)),
    (r"/problem/(\d+)", (1,)),
    (r"/([A-Za-z]{1,4})(\d{2,6})/?$", (1, 2)),
    (r"/(\d{1,6})/?$", (1,)),
)


def guess_pid(url: str) -> str:
    """从 URL 里猜一个短题号, 只用于展示与目录名。"""
    parsed = urllib.parse.urlparse(url or "")
    path = parsed.path or ""
    for pattern, groups in _PID_PATTERNS:
        match = re.search(pattern, path)
        if not match:
            continue
        try:
            return "".join(match.group(index) or "" for index in groups)
        except (IndexError, TypeError):
            continue
    tail = [seg for seg in path.split("/") if seg]
    if tail:
        cleaned = re.sub(r"[^A-Za-z0-9_-]", "", tail[-1])[:16]
        if cleaned:
            return cleaned
    host = parsed.netloc.split(":")[0].replace("www.", "")
    return host.split(".")[0] if host else "web"


def extract_items(html: str, base_url: str, item_regex: str,
                  limit: int = 20) -> List[Dict[str, str]]:
    """用用户给的正则从任意列表页里抓条目(第 1 组=链接, 第 2 组=标题)。"""
    if not item_regex:
        return []
    try:
        pattern = re.compile(item_regex, re.S)
    except re.error:
        return []
    items: List[Dict[str, str]] = []
    seen = set()
    for match in pattern.finditer(html or ""):
        groups = match.groups()
        if not groups:
            continue
        link = groups[0] if len(groups) >= 1 else ""
        title = groups[1] if len(groups) >= 2 else link
        link = urllib.parse.urljoin(base_url, (link or "").strip())
        title = normalize_spaces(re.sub(r"(?s)<[^>]+>", "", title or "")).strip()
        if not link or link in seen:
            continue
        seen.add(link)
        items.append({"title": title or link, "url": link})
        if len(items) >= limit:
            break
    return items


# ---------------------------------------------------------------------------
# 来源注册表(data/sources.json)
# ---------------------------------------------------------------------------
DEFAULT_SOURCES: List[Dict[str, Any]] = [
    {
        "name": "luogu", "label": "洛谷", "kind": "luogu", "enabled": True,
        "hosts": ["luogu.com.cn", "luogu.org"],
        "note": "中文 OJ, 有难度与标签, 题面可完整抓取(专用解析)",
    },
    {
        "name": "dotcpp", "label": "dotcpp", "kind": "dotcpp", "enabled": True,
        "hosts": ["dotcpp.com"],
        "note": "C 语言网, 题名自带 [编程入门] 之类分类前缀",
    },
    {
        "name": "codeforces", "label": "Codeforces", "kind": "codeforces", "enabled": True,
        "hosts": ["codeforces.com"],
        "note": "英文, 有 tag 与 rating, 可以按水平精准挑题(免鉴权 API)",
    },
    {
        "name": "github", "label": "GitHub", "kind": "github", "enabled": True,
        "hosts": ["github.com"],
        "note": "推荐成体系的练习仓库(公开搜索 API, 失败时回退精选清单)",
    },
    {
        "name": "bing", "label": "必应", "kind": "bing", "enabled": True,
        "hosts": ["bing.com"],
        "note": "网页兜底, 也用来在其它站点上找题",
    },
    {
        "name": "nowcoder", "label": "牛客", "kind": "generic", "enabled": False,
        "hosts": ["nowcoder.com"],
        "search_url": "https://ac.nowcoder.com/acm/problem/list?keyword={q}",
        "item_regex": r'href="(https://ac\.nowcoder\.com/acm/problem/\d+)"[^>]*>\s*([^<]{4,90}?)\s*<',
        "note": "generic 示例: 默认关闭, 启用后可直接在牛客搜题",
    },
]

# 用户添加 generic 来源时需要知道的字段说明
GENERIC_HELP = (
    "kind=generic 的必填字段: search_url(用 {q} 占位关键词), item_regex(第1组=链接, 第2组=标题)",
    "可选字段: label(显示名), hosts(用于识别链接属于哪个站点), enabled(true/false), note",
)


def _normalize_source(item: Dict[str, Any]) -> Dict[str, Any]:
    source = dict(item)
    source.setdefault("label", source.get("name", "?"))
    source.setdefault("kind", "generic")
    source.setdefault("enabled", True)
    source.setdefault("hosts", [])
    source.setdefault("note", "")
    source.setdefault("search_url", "")
    source.setdefault("item_regex", "")
    return source


def default_sources() -> List[Dict[str, Any]]:
    return [_normalize_source(item) for item in DEFAULT_SOURCES]


def load_sources(write_if_missing: bool = True) -> List[Dict[str, Any]]:
    """读来源配置; 首次运行会把内置配置写到 data/sources.json 方便用户改。"""
    payload = oc.load_json(SOURCES_FILE, default=None)
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        sources = default_sources()
        if write_if_missing:
            save_sources(sources)
        return sources

    merged: List[Dict[str, Any]] = []
    seen = set()
    for item in payload["sources"]:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        source = _normalize_source(item)
        seen.add(source["name"])
        merged.append(source)
    # 内置来源被用户删掉了也补回来? 不补 —— 用户删掉就是不想用。
    if not merged:
        merged = default_sources()
    return merged


def save_sources(sources: Sequence[Dict[str, Any]]) -> bool:
    return oc.save_json(SOURCES_FILE, {
        "version": 1,
        "hint": "题目来源清单。可以自由增删; kind=generic 的站点只要给 search_url 与 item_regex。",
        "sources": [dict(item) for item in sources],
    })


def enabled_sources(sources: Optional[Sequence[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    items = list(sources) if sources is not None else load_sources()
    return [item for item in items if item.get("enabled", True)]


def source_by_name(name: str,
                   sources: Optional[Sequence[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    key = (name or "").strip().lower()
    for item in (sources if sources is not None else load_sources()):
        if str(item.get("name", "")).lower() == key:
            return item
    return None


def detect_source(url: str,
                  sources: Optional[Sequence[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """按 hosts 判断一个链接属于哪个已配置来源。"""
    host = urllib.parse.urlparse(url or "").netloc.lower()
    if not host:
        return None
    for item in (sources if sources is not None else load_sources()):
        for pattern in item.get("hosts", []):
            if pattern and pattern.lower() in host:
                return item
    return None


def add_source(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """新增或覆盖一个来源配置。"""
    item = _normalize_source(source)
    items = [s for s in load_sources() if s.get("name") != item["name"]]
    items.append(item)
    save_sources(items)
    return items


def set_enabled(name: str, enabled: bool) -> bool:
    items = load_sources()
    hit = False
    for item in items:
        if str(item.get("name", "")).lower() == (name or "").lower():
            item["enabled"] = bool(enabled)
            hit = True
    if hit:
        save_sources(items)
    return hit


def remove_source(name: str) -> bool:
    items = load_sources()
    kept = [s for s in items if str(s.get("name", "")).lower() != (name or "").lower()]
    if len(kept) == len(items):
        return False
    save_sources(kept)
    return True


def render_sources(sources: Optional[Sequence[Dict[str, Any]]] = None) -> List[str]:
    items = list(sources) if sources is not None else load_sources()
    lines = [oc.color("题目来源(data/sources.json)", "bold"), oc.hr("-", 78)]
    for item in items:
        flag = oc.color("启用", "green") if item.get("enabled", True) else oc.color("停用", "grey")
        lines.append("%s %s %s  kind=%s" % (
            flag, oc.pad_end(item.get("name", "?"), 14),
            oc.pad_end(item.get("label", ""), 14), item.get("kind", "generic")))
        if item.get("note"):
            lines.append(oc.color("     " + item["note"], "grey"))
        if item.get("kind") == "generic" and item.get("search_url"):
            lines.append(oc.color("     搜索: " + item["search_url"], "grey"))
    lines.append("")
    lines.append(oc.color("新增来源: py oop_lab.py sources --add 名字 --kind generic "
                          "--search-url <含{q}的地址> --item-regex <正则>", "grey"))
    lines.append(oc.color("启用/停用: py oop_lab.py sources --enable 名字 / --disable 名字", "grey"))
    lines.append(oc.color("直接导入任意链接: py oop_lab.py pull <网址>", "grey"))
    return lines
