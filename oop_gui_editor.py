#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_editor.py - 代码编辑控件

分成两层, 是刻意的:

  * 纯函数 highlight_spans() / indent_after() —— 不碰 Tk, 可以直接单测;
  * CodeEditor 控件 —— 行号栏 + 高亮 + 自动缩进 + Ctrl+S。

"算什么要变色"和"怎么画到界面上"分开之后, 前者在无显示环境的机器上也能验证,
而 Tk 控件在那种环境里根本建不起来。
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, List, Optional, Tuple

INDENT = "    "

CXX_KEYWORDS = {
    "alignas", "alignof", "auto", "break", "case", "catch", "class", "const",
    "constexpr", "continue", "decltype", "default", "delete", "do", "else",
    "enum", "explicit", "export", "extern", "false", "final", "for", "friend",
    "goto", "if", "inline", "mutable", "namespace", "new", "noexcept", "nullptr",
    "operator", "override", "private", "protected", "public", "return", "sizeof",
    "static", "static_cast", "struct", "switch", "template", "this", "throw",
    "true", "try", "typedef", "typeid", "typename", "using", "virtual", "volatile",
    "while",
}

CXX_TYPES = {
    "bool", "char", "double", "float", "int", "long", "short", "signed",
    "size_t", "string", "unsigned", "void", "wchar_t",
    "ostream", "istream", "vector", "map", "set", "pair", "unique_ptr",
    "shared_ptr", "cout", "cin", "cerr", "endl", "std",
}

# 顺序很重要: 注释 / 字符串 / 预处理指令必须排在关键字前面,
# 否则 "// 这里写 int" 里的 int 会被当成类型高亮出来。
_TOKEN_RE = re.compile(
    r"(?P<block>/\*.*?\*/)"
    r"|(?P<comment>//[^\n]*)"
    r"|(?P<preproc>^[ \t]*\#[^\n]*)"
    r"|(?P<string>\"(?:[^\"\\\n]|\\.)*\")"
    r"|(?P<char>'(?:[^'\\\n]|\\.)*')"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>[A-Za-z_]\w*)",
    re.MULTILINE | re.DOTALL,
)

_TAG_OF_GROUP = {
    "block": "comment",
    "comment": "comment",
    "preproc": "preproc",
    "string": "string",
    "char": "string",
    "number": "number",
}


def highlight_spans(text: str) -> List[Tuple[int, int, str]]:
    """算出源码里需要变色的区间: [(start, end, tag)], 按位置升序。

    tag 取值: comment / string / preproc / number / keyword / type
    """
    spans: List[Tuple[int, int, str]] = []
    for match in _TOKEN_RE.finditer(text or ""):
        group = match.lastgroup or ""
        tag = _TAG_OF_GROUP.get(group)
        if tag is None and group == "word":
            word = match.group()
            if word in CXX_KEYWORDS:
                tag = "keyword"
            elif word in CXX_TYPES:
                tag = "type"
        if tag is not None:
            spans.append((match.start(), match.end(), tag))
    return spans


def indent_after(line: str) -> str:
    """回车换行时, 新行该用多少缩进(由**上一行**决定)。

    - 上一行以 `}` 开头(如 `}` / `};` / `} else {`) -> 先退一级;
    - 上一行以 `{` 结尾 -> 再进一级;
    - 其余情况 -> 原样继承缩进。
    """
    stripped = line.strip()
    indent = line[:len(line) - len(line.lstrip())]
    if stripped.startswith("}"):
        indent = indent[:-len(INDENT)] if indent.endswith(INDENT) else ""
    if stripped.endswith("{"):
        indent += INDENT
    return indent


CODE_FONT_FAMILY = "Consolas"
CODE_FONT_SIZE = 11

_TAG_COLORS = {
    "comment": "#6a9955",
    "string": "#ce9178",
    "preproc": "#c586c0",
    "number": "#b5cea8",
    "keyword": "#569cd6",
    "type": "#4ec9b0",
}


class CodeEditor(tk.Frame):
    """带行号栏与高亮的代码编辑框。

    行号栏是一个独立的、禁用的 Text 控件, 与主 Text 用同一个字体保证行高一致,
    靠 yview 同步滚动。高亮做了 120ms 防抖 —— 否则每敲一个字符就全量重新着色会明显卡顿。
    """

    def __init__(self, master, on_save: Optional[Callable[[], None]] = None,
                 **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.on_save = on_save
        self.dirty = False
        self._highlight_job: Optional[str] = None

        code_font = tkfont.Font(family=CODE_FONT_FAMILY, size=CODE_FONT_SIZE)
        self.text = tk.Text(self, undo=True, wrap="none", font=code_font,
                            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
                            selectbackground="#264f78", relief="flat", padx=6, pady=4)
        self.gutter = tk.Text(self, width=5, padx=4, pady=4, takefocus=0,
                              font=code_font, bg="#252526", fg="#858585",
                              relief="flat", state="disabled", cursor="arrow")
        scroll = tk.Scrollbar(self, orient="vertical", command=self._on_scroll)
        self.text.configure(yscrollcommand=self._on_yscroll)

        self.gutter.pack(side="left", fill="y")
        scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for tag, tint in _TAG_COLORS.items():
            self.text.tag_configure(tag, foreground=tint)

        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Control-s>", self._on_ctrl_s)

    # ---- 滚动同步 ------------------------------------------------------
    def _on_scroll(self, *args) -> None:
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_yscroll(self, first, last) -> None:
        self.gutter.yview_moveto(first)

    # ---- 文本读写 ------------------------------------------------------
    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, content: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content or "")
        self.text.edit_reset()
        self.dirty = False
        self.apply_highlight()
        self.refresh_gutter()

    def insert_for_test(self, content: str) -> None:
        """给测试用的最小插入接口(真实输入走键盘事件)。"""
        self.text.insert("insert", content)
        self._on_key(None)

    # ---- 行号 ----------------------------------------------------------
    def refresh_gutter(self) -> None:
        total = int(self.text.index("end-1c").split(".")[0])
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", "\n".join(str(i) for i in range(1, total + 1)))
        self.gutter.configure(state="disabled")

    def gutter_line_count(self) -> int:
        return int(self.gutter.index("end-1c").split(".")[0])

    # ---- 高亮 ----------------------------------------------------------
    def apply_highlight(self) -> None:
        self._highlight_job = None
        content = self.get_text()
        for tag in _TAG_COLORS:
            self.text.tag_remove(tag, "1.0", "end")
        for start, end, tag in highlight_spans(content):
            self.text.tag_add(tag, "1.0 + %dc" % start, "1.0 + %dc" % end)

    # ---- 事件 ----------------------------------------------------------
    def _on_key(self, event) -> None:
        self.dirty = True
        self.refresh_gutter()
        if self._highlight_job is not None:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(120, self.apply_highlight)

    def _on_tab(self, event):
        self.text.insert("insert", INDENT)
        self._on_key(None)
        return "break"

    def _on_return(self, event):
        line = self.text.get("insert linestart", "insert")
        self.text.insert("insert", "\n" + indent_after(line))
        self._on_key(None)
        return "break"

    def _on_ctrl_s(self, event):
        if self.on_save is not None:
            self.on_save()
        self.dirty = False
        return "break"
