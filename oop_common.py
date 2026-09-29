#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_common.py - C++ 面向对象训练营(OOP Lab)共用基础设施

沿用同作者的 cleaner 项目的工程约定:
  * 纯标准库, 不引入任何第三方依赖(不用 pip install)
  * 与平台相关的能力(ANSI 颜色/文件替换)在非 Windows 上自动降级
  * 所有"对外输出"集中在这里, 方便统一格式与做单元测试

职责:
  * 目录常量           BASE_DIR / DATA_DIR / WORKSPACE_DIR
  * 终端输出           ANSI 颜色 / 中文宽度计算 / 自动换行 / 分隔线
  * JSON 持久化        原子写(先写临时文件再 os.replace)
  * 输出归一化         normalize_output() 供评测比对
  * 进度存储           ProgressStore (data/progress.json)
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
import time
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

APP_NAME = "cpp-oop-lab"
IS_WINDOWS = os.name == "nt"


def _detect_base_dir() -> str:
    """程序"数据目录": 开发时是源码目录, 打包后是 exe 所在目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _detect_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
USER_BANK_FILE = os.path.join(DATA_DIR, "user_problems.json")

LEVEL_NAMES: Dict[int, str] = {1: "基础", 2: "进阶", 3: "高级"}
LEVEL_STARS: Dict[int, str] = {1: "★☆☆", 2: "★★☆", 3: "★★★"}
LEVEL_TOPICS: Dict[int, str] = {
    1: "类与对象 / 封装 / 构造与析构 / const / static / 运算符重载入门",
    2: "拷贝控制 / 继承与派生 / 虚函数多态 / 抽象类 / 友元 / 运算符重载进阶",
    3: "模板与特化 / RAII 与智能指针 / 设计模式 / 多重继承与虚继承",
}

LOG = logging.getLogger(APP_NAME)

STATUS_TEXT: Dict[str, Tuple[str, str]] = {
    "todo": ("未开始", "grey"),
    "doing": ("进行中", "yellow"),
    "passed": ("已通过", "green"),
}


def status_badge(status: str) -> str:
    """把进度状态渲染成带色的中文短标签(CLI 与 GUI 共用一份文案)。"""
    text, tint = STATUS_TEXT.get(status, ("未知", "grey"))
    return color(text, tint)


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
def default_log_path() -> str:
    return os.path.join(BASE_DIR, "oop_lab.log")


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """配置日志: 始终写文件(便于事后排查), verbose 时同时输出到 stderr。"""
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers.clear()
    LOG.propagate = False
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    try:
        handler = logging.FileHandler(default_log_path(), encoding="utf-8")
        handler.setFormatter(fmt)
        handler.setLevel(logging.DEBUG)
        LOG.addHandler(handler)
    except OSError:
        pass  # 日志写不了不应该让主流程失败
    # --windowed 模式下 sys.stderr 是 None: 此时只能写文件, 不能加控制台 handler
    # (StreamHandler(None) 会在真正 emit 时才炸, 属于最难查的那类问题)
    if verbose and not quiet and sys.stderr is not None:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(fmt)
        LOG.addHandler(console)


# ---------------------------------------------------------------------------
# 终端输出: 颜色 / 宽度
# ---------------------------------------------------------------------------
_ANSI: Dict[str, str] = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "grey": "\033[90m",
}

_COLOR_ENABLED = False


def enable_ansi() -> bool:
    """打开 Windows 控制台的 VT 转义支持; 返回最终是否可用颜色。"""
    global _COLOR_ENABLED
    if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
        _COLOR_ENABLED = False
        return False
    if not IS_WINDOWS:
        _COLOR_ENABLED = os.environ.get("TERM", "") != "dumb"
        return _COLOR_ENABLED
    try:
        import ctypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            _COLOR_ENABLED = False
            return False
        if mode.value & 0x0004:  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            _COLOR_ENABLED = True
            return True
        _COLOR_ENABLED = bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        _COLOR_ENABLED = False
    return _COLOR_ENABLED


def set_color_enabled(flag: bool) -> None:
    """供 --no-color / 单元测试关闭颜色。"""
    global _COLOR_ENABLED
    _COLOR_ENABLED = bool(flag)


def color_enabled() -> bool:
    return _COLOR_ENABLED


def color(text: object, name: str) -> str:
    """按名字着色; 颜色不可用时原样返回。"""
    text = str(text)
    if not _COLOR_ENABLED:
        return text
    code = _ANSI.get(name)
    if not code or name == "reset":
        return text
    return "%s%s%s" % (code, text, _ANSI["reset"])


def display_width(text: str) -> int:
    """终端显示宽度: 中日韩全角字符按 2 列算。"""
    width = 0
    for ch in str(text):
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def pad_end(text: str, width: int, fill: str = " ") -> str:
    """按显示宽度右侧补齐(用于对齐中文表格)。"""
    text = str(text)
    diff = width - display_width(text)
    return text + fill * diff if diff > 0 else text


def wrap_text(text: str, width: int = 78, indent: str = "",
              subsequent_indent: Optional[str] = None) -> List[str]:
    """按显示宽度自动换行(中英文混排都算得对)。"""
    if subsequent_indent is None:
        subsequent_indent = indent
    out: List[str] = []
    for paragraph in str(text).split("\n"):
        if not paragraph.strip():
            out.append("")
            continue
        prefix = indent
        cur = prefix
        cur_w = display_width(prefix)
        for ch in paragraph:
            w = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            if cur_w + w > width and cur != prefix:
                # 英文单词不要被劈成两半: 能找到靠后的空格就断在空格处
                cut = cur.rfind(" ")
                if cut > len(prefix) + max(4, (width - len(prefix)) // 3):
                    head, tail = cur[:cut], cur[cut + 1:]
                else:
                    head, tail = cur, ""
                out.append(head.rstrip())
                prefix = subsequent_indent
                cur = prefix + tail
                cur_w = display_width(cur)
            cur += ch
            cur_w += w
        out.append(cur.rstrip())
    return out


def hr(char: str = "-", width: int = 78) -> str:
    return char * width


_ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(text: object) -> str:
    """去掉 ANSI 颜色转义 —— 写日志/写 markdown 文件时必须用。"""
    return _ANSI_PATTERN.sub("", str(text))


def format_bar(percent: float, width: int = 24) -> str:
    """生成文本进度条, 例如 "[######......]  40.0%"。"""
    percent = max(0.0, min(100.0, float(percent)))
    width = max(0, int(width))
    filled = int(round(percent / 100.0 * width))
    filled = max(0, min(width, filled))
    return "[%s%s] %5.1f%%" % ("#" * filled, "." * (width - filled), percent)


def truncate(text: str, width: int = 40, suffix: str = "…") -> str:
    """按显示宽度截断(给表格列用)。"""
    text = str(text)
    if display_width(text) <= width:
        return text
    limit = width - display_width(suffix)
    cur = 0
    out = []
    for ch in text:
        w = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if cur + w > limit:
            break
        out.append(ch)
        cur += w
    return "".join(out) + suffix


# ---------------------------------------------------------------------------
# 文件 / JSON
# ---------------------------------------------------------------------------
def ensure_dir(path: str) -> str:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    return path


def load_json(path: str, default: Any = None) -> Any:
    """读 JSON; 文件不存在/损坏时返回 default(绝不抛异常)。"""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save_json(path: str, payload: Any) -> bool:
    """原子写 JSON: 先写同目录临时文件再 os.replace, 避免中途崩溃留下半个文件。"""
    try:
        ensure_dir(os.path.dirname(path))
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
        os.close(fd)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            os.remove(tmp)  # type: ignore[possibly-undefined]
        except Exception:
            pass
        return False


def read_text(path: str, default: str = "") -> str:
    """读文本, 自动兼容 UTF-8 / GBK(学生用记事本另存过的文件经常是 GBK)。"""
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
        except OSError:
            return default
    return default


def write_text(path: str, text: str, newline: str = "\n") -> bool:
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\r\n", "\n").replace("\n", newline))
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# 输出归一化(评测比对用)
# ---------------------------------------------------------------------------
def normalize_output(text: str) -> str:
    """归一化程序输出, 让评测只看"有效内容":

    * 统一换行符
    * 去掉每行行尾空白(学生常常多打一个空格)
    * 去掉首尾空行
    """
    if text is None:
        return ""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def first_difference(expected: str, actual: str) -> Tuple[int, str, str]:
    """返回 (行号从1开始, 期望行, 实际行); 完全一致返回 (0, "", "")。"""
    exp = normalize_output(expected).split("\n")
    act = normalize_output(actual).split("\n")
    if expected == "" and actual == "":
        return 0, "", ""
    for idx in range(max(len(exp), len(act))):
        e = exp[idx] if idx < len(exp) else "<没有这一行>"
        a = act[idx] if idx < len(act) else "<没有这一行>"
        if e != a:
            return idx + 1, e, a
    return 0, "", ""


def human_duration(seconds: float) -> str:
    seconds = float(seconds or 0.0)
    if seconds < 1:
        return "%.0f ms" % (seconds * 1000)
    if seconds < 60:
        return "%.2f 秒" % seconds
    return "%d 分 %02d 秒" % (int(seconds // 60), int(seconds % 60))


# ---------------------------------------------------------------------------
# 进度存储
# ---------------------------------------------------------------------------
class ProgressStore:
    """把每个题目的练习状态落盘到 data/progress.json。

    结构::

        {
          "version": 1,
          "problems": {
            "b01": {"status": "passed", "attempts": 3, "best": "6/6",
                    "first_seen": 1690000000, "last_seen": 1690000123,
                    "seconds": 12.5, "open_count": 2}
          },
          "events": [{"ts": ..., "pid": "b01", "kind": "judge", "detail": "..."}]
        }

    status 取值: ``todo``(未开始) / ``doing``(已打开工程) / ``passed``(全用例通过)。
    """

    MAX_EVENTS = 500

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or PROGRESS_FILE
        payload = load_json(self.path, default=None)
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("version", 1)
        payload.setdefault("problems", {})
        payload.setdefault("events", [])
        if not isinstance(payload["problems"], dict):
            payload["problems"] = {}
        if not isinstance(payload["events"], list):
            payload["events"] = []
        self.data: Dict[str, Any] = payload

    # -- 查询 ---------------------------------------------------------------
    def get(self, pid: str) -> Dict[str, Any]:
        entry = self.data["problems"].get(pid)
        return dict(entry) if isinstance(entry, dict) else {}

    def status(self, pid: str) -> str:
        return str(self.get(pid).get("status", "todo"))

    # -- 修改 ---------------------------------------------------------------
    def record(self, pid: str, *, status: Optional[str] = None, passed: Optional[int] = None,
               total: Optional[int] = None, seconds: Optional[float] = None,
               kind: str = "judge", detail: str = "", opened: bool = False) -> Dict[str, Any]:
        now = time.time()
        entry = self.data["problems"].setdefault(pid, {})
        entry.setdefault("status", "todo")
        entry.setdefault("attempts", 0)
        entry.setdefault("open_count", 0)
        entry.setdefault("first_seen", now)
        entry["last_seen"] = now

        if opened:
            entry["open_count"] = int(entry.get("open_count", 0)) + 1
            if entry["status"] == "todo":
                entry["status"] = "doing"
        if passed is not None:
            entry["attempts"] = int(entry.get("attempts", 0)) + 1
            entry["last_result"] = "%d/%d" % (passed, total or 0)
            if total:
                entry["best"] = self._better(entry.get("best"), "%d/%d" % (passed, total))
        if seconds is not None:
            entry["seconds"] = round(float(entry.get("seconds", 0.0)) + float(seconds), 3)
        if status:
            if status == "passed" or entry["status"] != "passed":
                entry["status"] = status
            elif status == "doing" and entry["status"] == "todo":
                entry["status"] = "doing"

        self.data["events"].append({
            "ts": round(now, 3), "pid": pid, "kind": kind, "detail": detail[:200],
        })
        if len(self.data["events"]) > self.MAX_EVENTS:
            self.data["events"] = self.data["events"][-self.MAX_EVENTS:]
        self.save()
        return dict(entry)

    @staticmethod
    def _better(old: Optional[str], new: str) -> str:
        """保留历史最好成绩(比较通过用例数)。"""
        def score(value: str) -> Tuple[int, int]:
            try:
                a, b = str(value).split("/")
                return int(a), int(b)
            except (ValueError, AttributeError):
                return -1, 0
        return new if score(new) >= score(old or "") else str(old)

    def save(self) -> bool:
        return save_json(self.path, self.data)

    def clear(self, pid: Optional[str] = None) -> None:
        if pid:
            self.data["problems"].pop(pid, None)
        else:
            self.data["problems"] = {}
            self.data["events"] = []
        self.save()

    def stats(self) -> Dict[str, Any]:
        problems = self.data["problems"]
        passed = [p for p, v in problems.items() if v.get("status") == "passed"]
        doing = [p for p, v in problems.items() if v.get("status") == "doing"]
        attempts = sum(int(v.get("attempts", 0)) for v in problems.values())
        seconds = sum(float(v.get("seconds", 0.0)) for v in problems.values())
        return {
            "passed": len(passed),
            "doing": len(doing),
            "touched": len(problems),
            "attempts": attempts,
            "seconds": seconds,
            "passed_ids": passed,
        }


def resolve_problem_dir(problem: Dict[str, Any], root: Optional[str] = None) -> str:
    """练习工程目录: workspace/<id>-<slug>。"""
    base = root or WORKSPACE_DIR
    return os.path.join(base, "%s-%s" % (problem["id"], problem.get("slug") or problem["id"]))


def slugify(text: str, maxlen: int = 24) -> str:
    """把中文标题转成短目录名后缀(ASCII 字母数字/连字符, 其余丢掉)。"""
    out: List[str] = []
    for ch in str(text):
        if ch.isascii() and (ch.isalnum() or ch in "-_"):
            out.append(ch.lower())
        elif out and out[-1] != "-":
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:maxlen].strip("-") or "problem"
