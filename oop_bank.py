#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_bank.py - 题库聚合层

把三档内建题库(基础/进阶/高级)与"联网搜到后导入的题目"合并成统一视图, 提供:

    all_problems()                     全部题目
    find(pid)                          按 id 精确查找
    filter_problems(...)               按档位 / 知识点 / 关键字过滤
    validate(problem)                  结构自检(单元测试与 selftest 都会用)
    save_user_problems()/load_user()   在线导入题目的读写

在线导入的题目保存在 data/user_problems.json, 与内建题库完全隔离,
即使文件损坏也不会影响内建题库(load_json 失败即返回空列表)。
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import oop_bank_adv
import oop_bank_basic
import oop_bank_pro
import oop_bank_visual
from oop_common import LEVEL_NAMES, USER_BANK_FILE, load_json, save_json, slugify

BUILTIN: List[Dict[str, Any]] = (
    list(oop_bank_basic.PROBLEMS)
    + list(oop_bank_adv.PROBLEMS)
    + list(oop_bank_pro.PROBLEMS)
    + list(oop_bank_visual.PROBLEMS)      # 第 4 档: 教材第 5 版(MFC 可视化)
)

_REQUIRED_KEYS = ("id", "level", "title", "desc", "skeleton", "solution", "tests")

# 每题必须给到的字段(缺省值由 _normalize 补齐, 这里只列语义必填项)
_LIST_KEYS = ("topics", "require", "hints", "checklist", "tests", "samples",
              "defines", "libs", "checks")


def _normalize(problem: Dict[str, Any], source: str = "builtin") -> Dict[str, Any]:
    """补齐缺省字段, 保证后续代码可以无脑访问。"""
    p: Dict[str, Any] = dict(problem)
    p.setdefault("id", "u000")
    p.setdefault("level", 3)
    p.setdefault("title", p["id"])
    p.setdefault("desc", "")
    p.setdefault("io", "")
    p.setdefault("skeleton", "// TODO: 在这里写你的代码\n")
    p.setdefault("solution", "")
    for key in _LIST_KEYS:
        value = p.get(key)
        p[key] = list(value) if isinstance(value, (list, tuple)) else []
    p.setdefault("framework", "console")    # console 控制台题 | mfc 可视化题(教材第 2~8 章)
    p.setdefault("subsystem", "")           # windows / console; 空 = 按 framework 默认
    p.setdefault("slug", slugify(p.get("title") or p["id"]))
    p["source"] = p.get("source", source)
    return p


def load_user() -> List[Dict[str, Any]]:
    """读取在线导入的题目(文件不存在或损坏时返回空列表)。"""
    payload = load_json(USER_BANK_FILE, default=[])
    if not isinstance(payload, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict) and item.get("id"):
            out.append(_normalize(item, source="user"))
    return out


def save_user(problems: List[Dict[str, Any]]) -> bool:
    return save_json(USER_BANK_FILE, problems)


def add_user(problem: Dict[str, Any]) -> Dict[str, Any]:
    """把一题追加进用户题库(同 id 覆盖), 返回归一化后的题目。"""
    item = _normalize(problem, source="user")
    items = [p for p in load_user() if p["id"] != item["id"]]
    items.append(item)
    save_user(items)
    return item


def next_user_id() -> str:
    """给在线导入的题目分配一个不冲突的 id: u01 / u02 / ..."""
    used = {p["id"] for p in load_user()}
    index = 1
    while ("u%02d" % index) in used:
        index += 1
    return "u%02d" % index


def all_problems(include_user: bool = True) -> List[Dict[str, Any]]:
    problems = [_normalize(p) for p in BUILTIN]
    if include_user:
        problems.extend(load_user())
    return problems


def find(pid: str, include_user: bool = True) -> Optional[Dict[str, Any]]:
    """按 id(忽略大小写)或 slug 查找, 也支持 "b1"/"b01" 这种宽松写法。"""
    if not pid:
        return None
    key = str(pid).strip().lower()
    problems = all_problems(include_user)
    for p in problems:
        if p["id"].lower() == key or p.get("slug", "").lower() == key:
            return p
    # 宽松匹配: b1 -> b01, i2 -> i02, a3 -> a03
    for p in problems:
        pid_low = p["id"].lower()
        if len(pid_low) == 3 and pid_low[0] + pid_low[2] == key:
            return p
        if len(pid_low) == 2 and pid_low == key:
            return p
    for p in problems:
        if p["id"].lower().startswith(key):
            return p
    return None


def filter_problems(level: Optional[int] = None,
                    tag: Optional[str] = None,
                    keyword: Optional[str] = None,
                    include_user: bool = True) -> List[Dict[str, Any]]:
    """按档位 / 知识点 / 关键字(标题+描述)过滤。"""
    result: List[Dict[str, Any]] = []
    for p in all_problems(include_user):
        if level is not None and int(p.get("level", 0)) != int(level):
            continue
        if tag:
            tags = [str(t).lower() for t in p.get("topics", [])]
            needle = str(tag).lower()
            if not any(needle in t for t in tags):
                continue
        if keyword:
            haystack = " ".join([
                str(p.get("id", "")), str(p.get("title", "")),
                str(p.get("desc", "")), " ".join(str(t) for t in p.get("topics", [])),
            ]).lower()
            if str(keyword).lower() not in haystack:
                continue
        result.append(p)
    return result


def level_counts(include_user: bool = True) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for p in all_problems(include_user):
        lv = int(p.get("level", 3))
        counts[lv] = counts.get(lv, 0) + 1
    return counts


def all_topics(include_user: bool = True) -> List[str]:
    seen: List[str] = []
    for p in all_problems(include_user):
        for t in p.get("topics", []):
            if t not in seen:
                seen.append(str(t))
    return seen


def id_order(problems: Optional[List[Dict[str, Any]]] = None) -> List[str]:
    """按 档位 → 题库内顺序 返回 id 列表(用于进度条与 next 命令)。"""
    items = problems if problems is not None else all_problems()
    ordered = sorted(items, key=lambda p: (int(p.get("level", 3)), items.index(p)))
    return [p["id"] for p in ordered]


def validate(problem: Dict[str, Any]) -> List[str]:
    """结构自检: 返回问题列表(空列表 = 通过)。单元测试直接用它。"""
    errors: List[str] = []
    pid = problem.get("id", "<无 id>")
    framework = str(problem.get("framework") or "console").lower()
    for key in _REQUIRED_KEYS:
        if problem.get(key):
            continue
        # 在线导入的题目允许没有参考解与用例
        if problem.get("source") == "user" and key in ("solution", "tests"):
            continue
        # MFC 窗口题没有控制台用例(靠 checks 把关)
        if framework == "mfc" and key == "tests":
            continue
        errors.append("%s: 缺少字段 %s" % (pid, key))
    if not isinstance(problem.get("level"), int) or problem["level"] not in LEVEL_NAMES:
        errors.append("%s: level 必须是 %s"
                      % (pid, "/".join(str(k) for k in sorted(LEVEL_NAMES))))

    if framework not in ("console", "mfc"):
        errors.append("%s: framework 必须是 console/mfc, 现在是 %r" % (pid, framework))
    if framework == "mfc" and not (problem.get("checks") or []):
        errors.append("%s: MFC 题必须至少写一条 checks 规则(缺编译环境时靠它把关)" % pid)
    for index, rule in enumerate(problem.get("checks") or [], start=1):
        if not isinstance(rule, dict) or not rule.get("pattern"):
            errors.append("%s: 第 %d 条 checks 缺少 pattern" % (pid, index))
            continue
        try:
            re.compile(str(rule["pattern"]))
        except re.error as exc:
            errors.append("%s: 第 %d 条 checks 正则非法: %s" % (pid, index, exc))

    for i, test in enumerate(problem.get("tests", [])):
        if not isinstance(test, dict) or "in" not in test or "out" not in test:
            errors.append("%s: 第 %d 个用例缺少 in/out" % (pid, i + 1))
    requires_main = framework == "console"
    for name in ("skeleton", "solution"):
        text = problem.get(name) or ""
        if not text:
            continue
        if requires_main and "int main" not in text:
            errors.append("%s: %s 缺少 int main()" % (pid, name))
        # 头文件不允许省略 —— 用户明确要求每道题都把 #include 写全
        if "#include" not in text:
            errors.append("%s: %s 缺少 #include —— 题目的头文件不允许省略" % (pid, name))
    if pid != "<无 id>":
        m = problem.get("skeleton") or ""
        if m and "TODO" not in m:
            errors.append("%s: skeleton 里没有 TODO 标记, 学生不知道该改哪里" % pid)
    return errors


def validate_all(include_user: bool = True) -> List[str]:
    errors: List[str] = []
    seen: Dict[str, int] = {}
    for p in all_problems(include_user):
        errors.extend(validate(p))
        pid = p["id"]
        seen[pid] = seen.get(pid, 0) + 1
    for pid, count in seen.items():
        if count > 1:
            errors.append("%s: 题目 id 重复 %d 次" % (pid, count))
    return errors
