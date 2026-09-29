#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_review.py - 面向对象代码的静态审查(自动“指正”)

评测只回答“答案对不对”, 审查回答的是“写法对不对”。
这里用一组针对 OOP 的启发式检查, 在提交给老师/AI 点评之前先自己过一遍:

    R01 规则三缺项        有析构却没有拷贝构造 / 拷贝赋值
    R02 虚析构缺失        有虚函数但没有虚析构
    R03 自赋值未处理      operator= 里没有 this == &other 判断
    R04 new/delete 不配对
    R05 const 正确性      带 const X& 形参的成员函数没加 const
    R06 非 public 继承    class A : B / class A : private B
    R07 TODO 未清理
    R08 using namespace std（.cpp 可接受, 头文件禁止）
    R09 C 风格 IO / 不安全字符串函数
    R10 缺少 override
    R11 <bits/stdc++.h> 不可移植

检查全部基于文本启发式, 会保守(宁可漏报不要误报)。
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_common as oc

SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}
SEVERITY_COLOR = {"error": "red", "warn": "yellow", "info": "cyan"}
SEVERITY_TEXT = {"error": "错误", "warn": "警告", "info": "提示"}


class Finding:
    """一条审查意见。"""

    def __init__(self, rule: str, severity: str, title: str, detail: str = "",
                 line: int = 0, advice: str = "", snippet: str = "") -> None:
        self.rule = rule
        self.severity = severity
        self.title = title
        self.detail = detail
        self.line = line
        self.advice = advice
        self.snippet = snippet

    @property
    def color(self) -> str:
        return SEVERITY_COLOR.get(self.severity, "grey")

    def __repr__(self) -> str:  # pragma: no cover
        return "<Finding %s %s %s>" % (self.rule, self.severity, self.title)


# ---------------------------------------------------------------------------
# 预处理: 去掉注释与字符串, 让正则不会被它们干扰
# ---------------------------------------------------------------------------
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT = re.compile(r"//[^\n]*")
_STRING_LITERAL = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
_CHAR_IN_STRING = "\x00"


def strip_comments(text: str) -> str:
    """把注释换成等量空白(保持行号不变)。"""

    def blank(match: "re.Match[str]") -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = _BLOCK_COMMENT.sub(blank, text)
    text = _LINE_COMMENT.sub(lambda m: " " * len(m.group(0)), text)
    return text


def strip_literals(text: str) -> str:
    """把字符串/字符字面量替换成占位符(用于统计关键字次数)。"""

    def blank(match: "re.Match[str]") -> str:
        return '"' + _CHAR_IN_STRING * (len(match.group(0)) - 2) + '"'

    return _STRING_LITERAL.sub(blank, text)


def prepare(text: str) -> str:
    """审查前统一预处理: 去注释、去字面量内容, 保留行号。"""
    return strip_literals(strip_comments(text))


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


# ---------------------------------------------------------------------------
# 类扫描
# ---------------------------------------------------------------------------
class ClassInfo:
    def __init__(self, name: str, header: str, body: str, start: int, end: int,
                 bases: List[str], is_struct: bool) -> None:
        self.name = name
        self.header = header
        self.body = body
        self.start = start
        self.end = end
        self.bases = bases
        self.is_struct = is_struct


_CLASS_HEAD = re.compile(r"\b(class|struct)\s+([A-Za-z_]\w*)\s*([^;{}]*?)\{")


def find_classes(prepared: str) -> List[ClassInfo]:
    """扫描源码里所有类/结构体定义(带花括号配对)。"""
    result: List[ClassInfo] = []
    for match in _CLASS_HEAD.finditer(prepared):
        kind, name, tail = match.group(1), match.group(2), match.group(3)
        head_end = match.end()
        depth = 1
        idx = head_end
        while idx < len(prepared) and depth > 0:
            ch = prepared[idx]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            idx += 1
        body = prepared[head_end:idx - 1] if depth == 0 else prepared[head_end:]
        bases: List[str] = []
        if ":" in tail:
            for part in tail.split(":", 1)[1].split(","):
                token = part.strip().split()
                if token:
                    bases.append(token[-1].strip())
        result.append(ClassInfo(name, match.group(0), body, match.start(), idx,
                                bases, kind == "struct"))
    return result


# ---------------------------------------------------------------------------
# 具体规则
# ---------------------------------------------------------------------------
def _has_dtor(cls: ClassInfo) -> bool:
    return re.search(r"~\s*" + re.escape(cls.name) + r"\s*\(", cls.body) is not None


def _has_copy_ctor(cls: ClassInfo) -> bool:
    pattern = (r"\b" + re.escape(cls.name) + r"\s*\(\s*(?:const\s+)?"
               + re.escape(cls.name) + r"\s*&")
    return re.search(pattern, cls.body) is not None


def _has_copy_assign(cls: ClassInfo) -> bool:
    return re.search(r"operator\s*=\s*\(", cls.body) is not None


def _has_virtual(cls: ClassInfo) -> bool:
    return re.search(r"\bvirtual\b", cls.body) is not None


def _has_virtual_dtor(cls: ClassInfo) -> bool:
    return re.search(r"virtual\s+~\s*" + re.escape(cls.name), cls.body) is not None


def _owns_resource(cls: ClassInfo) -> bool:
    """粗略判断这个类是否自己管理资源(指针成员 / new / delete)。"""
    return (re.search(r"\bnew\b", cls.body) is not None
            or re.search(r"\bdelete\b", cls.body) is not None
            or re.search(r"\*\s*\w+\s*;", cls.body) is not None)


def review_source(text: str, problem: Optional[Dict[str, Any]] = None) -> List[Finding]:
    """对一份 C++ 源码做 OOP 静态审查。"""
    findings: List[Finding] = []
    raw = text or ""
    prepared = prepare(raw)
    classes = find_classes(prepared)
    want_class = bool(problem and any("类" in str(t) or "模板" in str(t)
                                      for t in problem.get("topics", [])))

    # ---- R07 TODO 未清理 ---------------------------------------------------
    # 注意: TODO 通常写在注释里, 所以这里用“只去字面量、保留注释”的版本扫描。
    todo_source = strip_literals(raw)
    for match in re.finditer(r"TODO", todo_source):
        findings.append(Finding(
            "R07", "warn", "还有 TODO 没有处理",
            "第 %d 行仍留有待办标记。" % _line_of(todo_source, match.start()),
            line=_line_of(todo_source, match.start()),
            advice="把 TODO 处补完, 或删掉这行提示, 避免提交时忘记。"))
        break

    # ---- 类相关规则 -------------------------------------------------------
    if not classes and want_class:
        findings.append(Finding(
            "R00", "error", "还没有定义类",
            "本题要求用类/模板解决, 但代码里没有找到 class / struct 定义。",
            advice="先想清楚要有哪些数据成员、哪些成员函数, 再把类骨架写出来。"))

    for cls in classes:
        line = _line_of(prepared, cls.start)
        has_dtor = _has_dtor(cls)
        has_copy_ctor = _has_copy_ctor(cls)
        has_copy_assign = _has_copy_assign(cls)
        owns = _owns_resource(cls)

        # R01 Rule of Three
        if has_dtor and not has_copy_ctor and owns:
            findings.append(Finding(
                "R01", "warn", "%s: 有析构函数却没有拷贝构造函数" % cls.name,
                "类自己管理了资源, 但拷贝时会退回默认的逐成员拷贝, 两个对象会指向同一块内存。",
                line=line,
                advice="补上 %s(const %s& other) 做深拷贝; 或者干脆禁用拷贝(= delete)。"
                       % (cls.name, cls.name)))
        if (has_dtor or has_copy_ctor) and not has_copy_assign and owns:
            findings.append(Finding(
                "R01", "warn", "%s: 有析构/拷贝构造却没有拷贝赋值运算符" % cls.name,
                "a = b 时会退回默认的逐成员赋值, 同样会造成重复释放。",
                line=line,
                advice="补上 %s& operator=(const %s& other)，并在里面处理自赋值。"
                       % (cls.name, cls.name)))

        # R02 虚析构
        if _has_virtual(cls) and not _has_virtual_dtor(cls) and has_dtor:
            findings.append(Finding(
                "R02", "warn", "%s: 有虚函数, 析构函数却不是 virtual" % cls.name,
                "通过基类指针 delete 派生对象时, 派生类的析构函数不会被调用, 资源会泄漏。",
                line=line,
                advice="把析构写成 virtual ~%s();" % cls.name))

        # R03 自赋值
        assign = re.search(r"operator\s*=\s*\([^)]*\)\s*\{", cls.body)
        if assign:
            body_start = assign.end()
            depth, idx = 1, body_start
            while idx < len(cls.body) and depth > 0:
                if cls.body[idx] == "{":
                    depth += 1
                elif cls.body[idx] == "}":
                    depth -= 1
                idx += 1
            body = cls.body[body_start:idx - 1]
            if re.search(r"this\s*==\s*&|this\s*!=\s*&|&\s*\w+\s*==\s*this", body) is None:
                findings.append(Finding(
                    "R03", "warn", "%s::operator= 没有处理自赋值" % cls.name,
                    "a = a 时如果先释放了自己的资源再去读它, 就会读到已释放的内存。",
                    line=_line_of(prepared, cls.start + assign.start()),
                    advice="在函数开头加: if (this == &other) return *this;"))

        # R06 继承方式(class 默认 private 继承, 很容易写出"看起来是 is-a 其实不是")
        if ":" in cls.header:
            inherit = cls.header.split(":", 1)[1].rstrip("{ \t\r\n").strip()
            for part in inherit.split(","):
                tokens = part.strip().split()
                if not tokens:
                    continue
                cursor = 0
                while cursor < len(tokens) and tokens[cursor] == "virtual":
                    cursor += 1
                explicit = (cursor < len(tokens)
                            and tokens[cursor] in ("public", "protected", "private"))
                base_name = tokens[-1]
                if explicit or cls.is_struct:
                    continue
                findings.append(Finding(
                    "R06", "warn", "%s 的继承方式不明确" % cls.name,
                    "没写访问说明符时 class 默认是 private 继承, 外部无法把派生类当基类用。",
                    line=line,
                    advice="写成 class %s : public %s { ... };" % (cls.name, base_name)))

        # R05 const 正确性(启发式: 形参里出现 const 同类& 但函数自身没 const)
        pattern = re.compile(
            r"\b(?:virtual\s+)?[\w:<>,\s\*&]+?\b(\w+)\s*\(([^;{)]*)\)\s*(const)?\s*(?:override|final)?\s*[{;]")
        hits = 0
        for fn in pattern.finditer(cls.body):
            name, params, is_const = fn.group(1), fn.group(2), fn.group(3)
            if name == cls.name or name.startswith("~") or name == "operator":
                continue
            if is_const or hits >= 2:
                continue
            if "static" in fn.group(0).split(name)[0]:
                continue
            if re.search(r"const\s+" + re.escape(cls.name) + r"\s*&", params):
                hits += 1
                findings.append(Finding(
                    "R05", "warn", "%s::%s 建议加上 const" % (cls.name, name),
                    "它接收 const %s& 形参, 却本身不是 const 成员函数。" % cls.name,
                    line=_line_of(prepared, cls.start + fn.start()),
                    advice="如果函数不修改自身状态, 就在参数表后补上 const, 这样 const 对象也能调用它。"))

    # ---- 全局规则 ---------------------------------------------------------
    def _count(pattern: str) -> int:
        return len(re.findall(pattern, prepared))

    news = _count(r"\bnew\b")
    deletes = _count(r"\bdelete\b")
    if news > deletes:
        first = re.search(r"\bnew\b", prepared)
        findings.append(Finding(
            "R04", "warn", "new 与 delete 数量不匹配",
            "源码里出现 %d 次 new, 但只有 %d 次 delete。" % (news, deletes),
            line=_line_of(prepared, first.start()) if first else 0,
            advice="每 new 一次就要 delete 一次; 更推荐用 std::unique_ptr 或容器自动管理。"))

    if re.search(r"\bnew\s+\w+\s*\[", prepared) and not re.search(r"delete\s*\[\s*\]", prepared):
        findings.append(Finding(
            "R04", "warn", "new[] 与 delete[] 不配对",
            "用 new[] 申请的数组必须用 delete[] 释放, 否则行为未定义。",
            advice="检查析构函数里是否写成了 delete[] ptr_;"))

    mapping = [
        ("R08", r"\busing\s+namespace\s+std\s*;", "warn",
         "使用了 using namespace std;",
         "在 .cpp 里问题不大, 但在头文件里会污染所有包含它的翻译单元, 属于坏习惯。",
         "改成显式写 std::, 或者只在 .cpp 的函数内部局部 using。"),
        ("R09", r"\b(printf|scanf|sprintf|strcpy|strcat|gets)\s*\(", "info",
         "出现了 C 风格输入输出 / 不安全字符串函数",
         "这类函数不检查缓冲区长度, 也是 C++ 里最容易出问题的一族。",
         "输入输出统一用 std::cin / std::cout, 字符串统一用 std::string。"),
        ("R11", r"bits/stdc\+\+\.h", "warn",
         "使用了 <bits/stdc++.h>",
         "这是 GCC 特有的头文件, MSVC / clang 上编译不过。",
         "改成显式包含用到的标准头文件。"),
        ("R12", r"\bstd::endl\b", "info",
         "大量使用 std::endl",
         "std::endl 每次都会刷缓冲区, 在循环里用会明显变慢。",
         "只换行用 '\\n', 确实需要立刻刷新时再用 std::endl。"),
    ]
    for rule, pattern, severity, title, detail, advice in mapping:
        match = re.search(pattern, prepared)
        if match:
            findings.append(Finding(rule, severity, title, detail,
                                    line=_line_of(prepared, match.start()),
                                    advice=advice))

    if re.search(r"\bvirtual\b", prepared) and "override" not in prepared and classes:
        first = re.search(r"\bvirtual\b", prepared)
        findings.append(Finding(
            "R10", "info", "重写虚函数时建议加 override",
            "写了 override 之后, 一旦签名写错编译器会立刻报错, 而不是默默变成一个新函数。",
            line=_line_of(prepared, first.start()) if first else 0,
            advice="在派生类重写的函数后面加上 override。"))

    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.line))
    return findings


def review_file(path: str, problem: Optional[Dict[str, Any]] = None) -> List[Finding]:
    if not os.path.isfile(path):
        return [Finding("R00", "error", "找不到源文件",
                        "文件不存在: %s" % path,
                        advice="先用 `py oop_lab.py new <题目>` 生成练习工程。")]
    return review_source(oc.read_text(path), problem)


def score(findings: Sequence[Finding]) -> int:
    """OOP 规范分(0-100), 只用来给个直观反馈, 不参与评测判定。"""
    value = 100
    for item in findings:
        if item.severity == "error":
            value -= 25
        elif item.severity == "warn":
            value -= 8
        else:
            value -= 2
    return max(0, value)


def render_findings(findings: Sequence[Finding], show_ok: bool = True) -> List[str]:
    lines: List[str] = []
    if not findings:
        if show_ok:
            lines.append(oc.color("没有发现明显的写法问题, 继续保持。", "green"))
        return lines
    for item in findings:
        head = "%s %s %s" % (oc.color("[%s]" % SEVERITY_TEXT.get(item.severity, "?"), item.color),
                             oc.color(item.rule, "bold"), item.title)
        if item.line:
            head += oc.color("  第 %d 行" % item.line, "grey")
        lines.append(head)
        if item.detail:
            for row in oc.wrap_text(item.detail, 74, indent="        "):
                lines.append(row)
        if item.advice:
            for row in oc.wrap_text("建议: " + item.advice, 74, indent="        "):
                lines.append(row)
        lines.append("")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    oc.enable_ansi()
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("用法: py oop_review.py <源文件.cpp>")
        return 2
    findings = review_file(args[0])
    for row in render_findings(findings):
        print(row)
    print("OOP 规范分: %d/100" % score(findings))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
