#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_html.py - 底层网页工具(HTTP / 编码 / HTML 转文本)

单独抽出来是为了避免循环依赖:
    oop_search.py ──┐
    oop_web.py    ──┴──> oop_html.py

这里只放与具体网站无关的东西:
  * http_get()        一次 GET, 任何异常都转成 HttpResult(不抛)
  * decode_body()     猜编码(中文站点 utf-8 / gbk 都常见, 必应还出现过声明与实际不符)
  * html_to_text()    HTML 片段 -> 纯文本(带换行)
  * normalize_spaces() 各种 Unicode 空白(全角空格/窄空格/零宽字符)统一成普通空格
    —— 不做这一步的话, 从某些站点抓来的题面写进 markdown 没问题,
       但往 GBK 控制台一 print 就会 UnicodeEncodeError。
"""

from __future__ import annotations

import gzip
import html as html_mod
import re
import urllib.error
import urllib.request
import zlib
from typing import Dict, Optional

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

DEFAULT_TIMEOUT = 15.0


class HttpResult:
    def __init__(self, ok: bool, text: str = "", url: str = "",
                 status: int = 0, error: str = "") -> None:
        self.ok = ok
        self.text = text
        self.url = url
        self.status = status
        self.error = error

    def __repr__(self) -> str:  # pragma: no cover
        return "<HttpResult ok=%s status=%s len=%d %s>" % (
            self.ok, self.status, len(self.text), self.error)


# ---------------------------------------------------------------------------
# 文本规范化
# ---------------------------------------------------------------------------
_UNICODE_SPACES = "\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007" \
                  "\u2008\u2009\u200a\u202f\u205f\u3000"
_ZERO_WIDTH = "\u200b\u200c\u200d\ufeff\u2060"


def normalize_spaces(text: str) -> str:
    """把各种 Unicode 空白压成普通空格, 删掉零宽字符。

    这些字符在网页里很常见(排版空格), 但会让终端输出在某些代码页下直接抛异常。
    """
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    table = {ord(ch): " " for ch in _UNICODE_SPACES}
    table.update({ord(ch): None for ch in _ZERO_WIDTH})
    return text.translate(table)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
_META_CHARSET = re.compile(rb'<meta[^>]+charset=["\']?([A-Za-z0-9_-]+)', re.I)
_XML_CHARSET = re.compile(rb'<\?xml[^>]+encoding=["\']([A-Za-z0-9_-]+)', re.I)
_HEADER_CHARSET = re.compile(r"charset=([A-Za-z0-9_-]+)", re.I)


def decode_body(raw: bytes, content_type: str = "") -> str:
    """按 Content-Type / meta 声明猜编码, 猜不出来按 utf-8 → gbk 依次尝试。"""
    raw = raw or b""
    candidates = []
    match = _HEADER_CHARSET.search(content_type or "")
    if match:
        candidates.append(match.group(1))
    head = raw[:4096]
    for pattern in (_META_CHARSET, _XML_CHARSET):
        found = pattern.search(head)
        if found:
            candidates.append(found.group(1).decode("ascii", "ignore"))
    candidates.extend(["utf-8", "gbk", "latin-1"])

    seen = []
    for enc in candidates:
        enc = (enc or "").lower()
        if enc and enc not in seen:
            seen.append(enc)
    for enc in seen:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def http_get(url: str, timeout: float = DEFAULT_TIMEOUT,
             headers: Optional[Dict[str, str]] = None) -> HttpResult:
    """发起 GET 请求; 任何异常都转成 HttpResult(ok=False)。"""
    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }
    if headers:
        request_headers.update(headers)

    request = urllib.request.Request(url, headers=request_headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            encoding = (response.headers.get("Content-Encoding") or "").lower()
            if "gzip" in encoding:
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
            elif "deflate" in encoding:
                try:
                    raw = zlib.decompress(raw, -zlib.MAX_WBITS)
                except zlib.error:
                    pass
            text = decode_body(raw, response.headers.get("Content-Type") or "")
            return HttpResult(True, text, url, int(getattr(response, "status", 200)))
    except urllib.error.HTTPError as exc:
        return HttpResult(False, "", url, int(exc.code), "HTTP %s" % exc.code)
    except urllib.error.URLError as exc:
        return HttpResult(False, "", url, 0, "网络不可达: %s" % (exc.reason,))
    except (OSError, ValueError) as exc:
        return HttpResult(False, "", url, 0, "请求失败: %s" % exc)


# ---------------------------------------------------------------------------
# HTML -> 文本
# ---------------------------------------------------------------------------
# 整块丢弃: 脚本/样式, 以及纯 UI 元素。
# 丢 UI 元素很关键 —— 例如 dotcpp 的「复制」按钮文字会被当成样例输出。
_DROP_BLOCKS = re.compile(
    r"(?is)<(script|style|noscript|template|svg|canvas|button|select|option|"
    r"nav|aside|footer|header|form|iframe|textarea)\b[^>]*>.*?</\1\s*>")
# 注意不要在这里干掉 <br>/<hr>: 它们要留给下面的 _BR 转成换行
_SELF_CLOSING_UI = re.compile(
    r"(?is)<(input|button|select|option|textarea|img|svg|iframe|meta|link|"
    r"nav|aside|footer|header|form)\b[^>]*/?>")
_BR = re.compile(r"(?i)<(br|/p|/div|/li|/tr|/h[1-6]|/pre|/td|/section|/article)\s*/?>")


def strip_scripts(raw: str) -> str:
    """去掉 script/style 与纯 UI 元素, 只留下有阅读价值的内容。"""
    text = _DROP_BLOCKS.sub("", raw or "")
    return _SELF_CLOSING_UI.sub(" ", text)


def strip_tags(raw: str) -> str:
    return re.sub(r"(?s)<[^>]+>", "", raw or "")


def html_to_text(raw: str, keep_newlines: bool = True) -> str:
    """把 HTML 片段转成可读纯文本。"""
    if not raw:
        return ""
    text = strip_scripts(raw)
    if keep_newlines:
        text = _BR.sub("\n", text)
    text = strip_tags(text)
    text = html_mod.unescape(text)
    text = normalize_spaces(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def squash_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text or "").strip()
