#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_lab.py - C++ 面向对象训练营 统一入口

**最常用的用法就一条**::

    py oop_lab.py         或双击 oop_lab.bat     -> 进交互式主菜单, 所有功能都在里面

菜单里能做的事(也就是下面这些子命令), 想写脚本时直接用子命令即可:

    py oop_lab.py menu               交互式主菜单(不带参数且是终端时默认进这里)
    py oop_lab.py plan               按你的水平安排今天练哪几道(自适应选题)
    py oop_lab.py study b01          先学后练: 打印本题涉及的知识点讲义
    py oop_lab.py study K12          直接看某个知识点
    py oop_lab.py list               题目列表(-l 2 只看进阶, -t 虚函数 按知识点)
    py oop_lab.py show b01           看题面
    py oop_lab.py new b01            生成/补齐这一题并打开统一工作区
    py oop_lab.py judge b01          编译 + 跑全部用例 + 老师式诊断
    py oop_lab.py review b01         面向对象写法审查(自动指正)
    py oop_lab.py diagnose b01       只做诊断讲解(不重新评测)
    py oop_lab.py submit b01         生成提交包(贴给老师/AI 点评)
    py oop_lab.py solution b01       看参考解(通过后才解锁)
    py oop_lab.py run b01 --case 2   编译并跑第 2 组用例
    py oop_lab.py progress           进度与统计
    py oop_lab.py profile            学习画像: 各知识点掌握度
    py oop_lab.py skills [K12]       知识点清单 / 单个知识点讲解
    py oop_lab.py log -n 10          学习日志

    py oop_lab.py search 线段树       多源找题(来源清单可自由增删)
    py oop_lab.py pull P1001         导入洛谷题目(1049=dotcpp, CF4A=Codeforces)
    py oop_lab.py pull <任意网址>     从任意网站的题面页导入(通用抽取)
    py oop_lab.py sources            管理题目来源(增删启停)
    py oop_lab.py selftest           用参考解自检题库(全部内建题真编译一遍)
    py oop_lab.py doctor             环境自检(编译器 / VSCode / 目录)

练习只在一个统一工作区里进行(workspace/, 同时带 VSCode 配置和 oop_lab.sln),
每道题是其中的一个子目录, 里面先看 knowledge.md 再写 main.cpp。

全局开关: --no-color 关闭彩色, -v 输出调试日志。
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_bank
import oop_coach
import oop_common as oc
import oop_judge
import oop_review
import oop_search
import oop_skills
import oop_web
import oop_workspace

XP_PER_LEVEL = {1: 10, 2: 20, 3: 30}


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def _banner() -> List[str]:
    return [
        oc.color("=" * 78, "grey"),
        oc.color("  C++ 面向对象训练营 · OOP Lab", "bold")
        + oc.color("    从类与对象到设计模式, %d 题阶梯式过关" % len(oop_bank.BUILTIN),
                   "grey"),
        oc.color("=" * 78, "grey"),
    ]


def _status_badge(status: str) -> str:
    """兼容旧调用: 真正的实现在 oop_common, 图形界面也要用同一份文案。"""
    return oc.status_badge(status)


def _progress_bar(done: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return ""
    return oc.format_bar(done * 100.0 / total, width)


def _store() -> oc.ProgressStore:
    return oc.ProgressStore()


def _pick_problem(pid: str) -> Optional[Dict[str, Any]]:
    return oop_bank.find(pid)


def _require_problem(pid: str) -> Optional[Dict[str, Any]]:
    problem = _pick_problem(pid)
    if problem is None:
        print(oc.color("找不到题目: %s" % pid, "red"))
        print("用 `py oop_lab.py list` 看看有哪些题目; 或者先 `py oop_lab.py pull <洛谷题号>` 导入。")
    return problem


def _toolchain_or_hint() -> Optional[oop_judge.Toolchain]:
    chain = oop_judge.find_toolchain()
    if chain is None:
        print(oc.color("没有找到 C++ 编译器, 无法编译。", "red"))
        print("运行 `py oop_lab.py doctor` 查看安装建议。")
    return chain


# ---------------------------------------------------------------------------
# 各子命令
# ---------------------------------------------------------------------------
def cmd_overview(args: argparse.Namespace) -> int:
    store = _store()
    for row in _banner():
        print(row)
    print()

    problems = oop_bank.all_problems()
    order = oop_bank.id_order(problems)
    passed = [pid for pid in order if store.status(pid) == "passed"]
    print("总进度  %s  %d/%d" % (_progress_bar(len(passed), len(order)), len(passed), len(order)))

    counts = oop_bank.level_counts()
    for level in (1, 2, 3):
        total = counts.get(level, 0)
        done = sum(1 for pid in order
                   if store.status(pid) == "passed"
                   and int(oop_bank.find(pid)["level"]) == level)
        print("  %s %s  %-4s  %d/%d" % (
            oc.LEVEL_STARS.get(level, "???"), oc.LEVEL_NAMES.get(level, ""),
            _progress_bar(done, total, 18), done, total))
    print()

    coach = oop_coach.LearnerProfile()
    if coach.practised():
        print("你的档位: %s   %s" % (
            oc.color(coach.level_label(), "yellow"),
            oc.color("(评测 %d 次 · 学习 %d 天)" % (
                coach.count("judge"), len(coach.data.get("days", []))), "grey")))
        weak = coach.weakest(2)
        if weak:
            print("薄弱点:   %s" % " / ".join(
                "%s %s(%.0f%%)" % (sid, oop_skills.skill_name(sid), value * 100)
                for sid, value in weak))
        print()

    assignments = oop_coach.local_plan(coach, count=1)
    if assignments:
        item = assignments[0]
        print("教练推荐:  %s  %s  %s" % (
            oc.color(item.problem["id"].upper(), "bold"), item.problem["title"],
            oc.color("[%s]" % oc.LEVEL_STARS.get(int(item.problem["level"]), ""), "grey")))
        for reason in item.reasons[:2]:
            print("           " + oc.color("· " + reason, "grey"))
        print("           py oop_lab.py new %s" % item.problem["id"])
        print("           想看完整安排: py oop_lab.py plan")
    else:
        print(oc.color("本地题库都练熟了, 用 `py oop_lab.py search <关键词>` 去洛谷/dotcpp 找新题。", "green"))
    print()

    chain = oop_judge.find_toolchain()
    print("编译器: %s" % (chain.describe() if chain else oc.color("未找到(先跑 doctor)", "red")))
    print("练习目录: %s" % oc.WORKSPACE_DIR)
    return 0


def _next_problem(store: oc.ProgressStore) -> Optional[Dict[str, Any]]:
    for pid in oop_bank.id_order():
        if store.status(pid) != "passed":
            return oop_bank.find(pid)
    return None


def cmd_list(args: argparse.Namespace) -> int:
    store = _store()
    problems = oop_bank.filter_problems(level=args.level, tag=args.tag, keyword=args.keyword)
    if not problems:
        print("没有匹配的题目。")
        return 0
    by_level: Dict[int, List[Dict[str, Any]]] = {}
    for problem in problems:
        by_level.setdefault(int(problem["level"]), []).append(problem)

    for level in sorted(by_level):
        print(oc.color("── 第 %d 档 · %s  %s" % (level, oc.LEVEL_NAMES.get(level, ""),
                                                oc.LEVEL_STARS.get(level, "")), "bold"))
        print(oc.color("   " + oc.LEVEL_TOPICS.get(level, ""), "grey"))
        for problem in by_level[level]:
            tags = ",".join(problem.get("topics", [])[:3])
            print("   %-5s %s %s %s" % (
                problem["id"],
                oc.pad_end(oc.truncate(problem["title"], 36), 36),
                oc.pad_end(oc.truncate(tags, 26), 26),
                _status_badge(store.status(problem["id"]))))
        print()
    print(oc.color("共 %d 题(内建 %d + 在线导入 %d)。" % (
        len(problems), len(oop_bank.BUILTIN), len(oop_bank.load_user())), "grey"))
    print("看题面: py oop_lab.py show <编号>    开练: py oop_lab.py new <编号>")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    for row in oop_coach.render_problem(problem):
        print(row)
    info = oop_workspace.summary(problem)
    if info["source_exists"]:
        print("你的代码: %s" % oop_workspace.student_source_path(problem))
    else:
        print("还没开工。运行: py oop_lab.py new %s" % problem["id"])
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    chain = oop_judge.find_toolchain()
    info = oop_workspace.ensure_workspace(problem, force=args.force, toolchain=chain)
    store = _store()
    store.record(problem["id"], kind="new", detail="生成练习工程", opened=True)
    coach = oop_coach.LearnerProfile()
    coach.bump("new")
    coach.save()
    oop_coach.log_event(
        "new", "开始练 **%s %s**" % (problem["id"].upper(), problem["title"]),
        ["- 知识点: " + ", ".join("%s %s" % (s, oop_skills.skill_name(s))
                                  for s in (oop_skills.classify(problem.get("topics", [])) or ["K01"])),
         "- 目录: %s" % info["dir"],
         "- 用例: %d 组" % len(problem.get("tests") or [])],
        pid=problem["id"], detail="生成练习工程")

    print(oc.color("这一题已经在工作区里就绪", "green"))
    print("  题目目录: %s" % info["dir"])
    print("  先读这个: %s  ← 知识点讲义(先学后练)" % oop_workspace.KNOWLEDGE_NAME)
    print("  然后写:   %s" % oop_workspace.SOURCE_NAME)
    print("  用例:     %d 组在 %s\\" % (len(problem.get("tests") or []),
                                        oop_workspace.TESTS_DIRNAME))
    print("  统一工作区: %s" % info["workspace"])
    print("  知识点: %s" % "、".join("%s %s" % (s, oop_skills.skill_name(s))
                                     for s in info["skills"]))
    if info.get("solution"):
        print("  VS 解决方案: %s" % os.path.basename(info["solution"]))
    if not info["files"]:
        print(oc.color("  (文件已存在, 没有覆盖你的 main.cpp)", "grey"))
    print()
    print(oc.color("接下来", "cyan"))
    print("  0. 先花 5~10 分钟读 %s, 或者终端里看: py oop_lab.py study %s"
          % (oop_workspace.KNOWLEDGE_NAME, problem["id"]))
    print("  1. VSCode: 打开工作区 %s（只需打开一次, 所有题目共享同一套配置）" % info["workspace"])
    print("     打开 workspace\\%s 后 Ctrl+Shift+B 构建、F5 调试 —— 它会编译**当前打开的那个文件**"
          % os.path.basename(info["dir"]))
    print("  2. Visual Studio: 打开 workspace\\%s, 把本工程设为启动项目后 F5"
          % oop_workspace.SOLUTION_NAME)
    print("  3. 回终端: py oop_lab.py judge %s" % problem["id"])
    print("  4. 想要点评: py oop_lab.py submit %s" % problem["id"])

    if args.open:
        print()
        if oop_workspace.open_in_vscode(info["workspace"]):
            print(oc.color("已用 VSCode 打开统一工作区(在左侧找到 %s 即可开练)。"
                           % os.path.basename(info["dir"]), "green"))
        elif oop_workspace.open_in_visual_studio(info["solution"]):
            print(oc.color("没找到 code 命令, 已改用 Visual Studio 打开解决方案。", "green"))
        else:
            print(oc.color("没找到 code / devenv 命令, 请手动打开工作区目录: %s"
                           % info["workspace"], "yellow"))
    return 0


def cmd_study(args: argparse.Namespace) -> int:
    """先学后练: 打印知识点讲义(支持题目编号或知识点编号)。"""
    target = (args.id or "").strip()
    if not target:
        return cmd_skills(argparse.Namespace(id=None))

    upper = target.upper()
    if upper.startswith("K") and upper[1:].isdigit():
        skill_id = "K%02d" % int(upper[1:])
    else:
        skill_id = ""

    if skill_id:
        if oop_skills.skill(skill_id) is None:
            print(oc.color("没有这个知识点: %s" % target, "red"))
            print("可用: %s" % ", ".join(oop_skills.all_skill_ids()))
            return 1
        for row in oop_skills.teach_lines(skill_id):
            print(row)
        return 0

    problem = _require_problem(target)
    if problem is None:
        return 1
    ids = oop_workspace.problem_skills(problem)
    print(oc.color("先学后练 · %s %s" % (problem["id"].upper(), problem["title"]), "bold"))
    print(oc.color("本题涉及 %d 个知识点: %s" % (
        len(ids), "、".join("%s %s" % (s, oop_skills.skill_name(s)) for s in ids)), "grey"))
    print(oc.hr("=", 78))
    print()
    for skill_id in ids:
        for row in oop_skills.teach_lines(skill_id):
            print(row)
    info = oop_workspace.summary(problem)
    print(oc.color("读完了就去写代码: py oop_lab.py new %s" % problem["id"], "green"))
    if info["knowledge_exists"]:
        print(oc.color("讲义也在这里(可以边写边看): %s" % os.path.join(
            info["dir"], oop_workspace.KNOWLEDGE_NAME), "grey"))
    return 0


def _compile_and_judge(problem: Dict[str, Any], timeout: float) -> Optional[oop_judge.JudgeReport]:
    chain = _toolchain_or_hint()
    if chain is None:
        return None
    source = oop_workspace.student_source_path(problem)
    if not os.path.isfile(source):
        print(oc.color("还没有 main.cpp, 先运行: py oop_lab.py new %s" % problem["id"], "yellow"))
        return None
    report = oop_judge.judge(problem, source, toolchain=chain, timeout=timeout)
    return report


def cmd_judge(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    report = _compile_and_judge(problem, args.timeout)
    if report is None:
        return 1

    print(oc.color("评测 %s %s" % (problem["id"].upper(), problem["title"]), "bold"))
    print(oc.hr("-", 78))
    for row in oop_judge.render_report(report, show_output=args.verbose):
        print(row)

    profile = oop_coach.LearnerProfile()
    source = oop_workspace.student_source_path(problem)
    findings = oop_review.review_file(source, problem)
    # 收尾逻辑与图形界面共用同一份(见 oop_coach.record_result)
    outcome = oop_coach.record_result(problem, report, findings, profile=profile)
    review_score = outcome["review_score"]
    record = outcome["record"]
    entry = outcome["entry"]

    # ---- 老师式诊断 ----
    diag = oop_coach.diagnose(problem, report=report, findings=findings, profile=profile)
    print()
    for row in oop_coach.render_diagnosis(diag):
        print(row)

    if entry.get("best"):
        print(oc.color("历史最好成绩: %s" % entry["best"], "grey"))
    print(oc.color("知识点掌握度变化: " + " / ".join(
        "%s %.0f%%" % (sid, profile.mastery(sid) * 100) for sid in record["skills"]), "grey"))

    log_lines = ["- 评测: %s, 通过 %d/%d 个用例, 规范分 %d/100, 耗时 %s" % (
        report.verdict, report.passed, report.total, review_score,
        oc.human_duration(report.seconds))]
    log_lines.append("- 涉及知识点: " + ", ".join(
        "%s %s (%.0f%%)" % (sid, oop_skills.skill_name(sid), profile.mastery(sid) * 100)
        for sid in record["skills"]))
    if findings:
        log_lines.append("- 写法问题: " + "; ".join(
            "%s %s" % (f.rule, f.title) for f in findings[:5]))
    log_lines.append("")
    log_lines.extend(oop_coach.render_diagnosis(diag))
    oop_coach.log_event(
        "judge", "**%s %s** —— %s" % (problem["id"].upper(), problem["title"], report.verdict),
        log_lines, pid=problem["id"],
        detail="%s %d/%d, 规范分 %d" % (report.verdict, report.passed, report.total, review_score))
    print(oc.color("已写入学习日志: py oop_lab.py log", "grey"))
    return 0 if report.all_passed else 1


def cmd_run(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    chain = _toolchain_or_hint()
    if chain is None:
        return 1
    source = oop_workspace.student_source_path(problem)
    if not os.path.isfile(source):
        print("还没有 main.cpp, 先运行: py oop_lab.py new %s" % problem["id"])
        return 1
    build_dir = os.path.join(os.path.dirname(source), oop_workspace.BUILD_DIRNAME)
    built = oop_judge.compile_file(chain, source, build_dir)
    if not built.ok:
        print(oc.color("编译失败:", "red"))
        print(built.log)
        return 1

    tests = problem.get("tests") or []
    if args.case > 0 and args.case <= len(tests):
        stdin_text = tests[args.case - 1].get("in", "")
    elif tests:
        stdin_text = tests[0].get("in", "")
    else:
        stdin_text = ""
    print(oc.color("-- 输入 --", "grey"))
    print(stdin_text.rstrip("\n") or "(无输入)")
    run = oop_judge.run_binary(built.exe, stdin_text, timeout=args.timeout, cwd=build_dir)
    print(oc.color("-- 输出 --", "grey"))
    print(run.stdout, end="" if run.stdout.endswith("\n") else "\n")
    if run.stderr.strip():
        print(oc.color("-- stderr --", "yellow"))
        print(run.stderr.strip())
    if run.timed_out:
        print(oc.color("程序运行超时，可能有死循环。", "red"))
    return run.code


def cmd_review(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    source = oop_workspace.student_source_path(problem)
    if not os.path.isfile(source):
        print("还没有 main.cpp, 先运行: py oop_lab.py new %s" % problem["id"])
        return 1

    findings = oop_review.review_file(source, problem)
    print(oc.color("写法审查 %s %s" % (problem["id"].upper(), problem["title"]), "bold"))
    print(oc.color("文件: %s" % source, "grey"))
    print(oc.hr("-", 78))
    rows = oop_review.render_findings(findings)
    for row in rows:
        print(row)
    value = oop_review.score(findings)
    color = "green" if value >= 90 else ("yellow" if value >= 70 else "red")
    print("OOP 规范分: %s" % oc.color("%d/100" % value, color))
    errors = sum(1 for f in findings if f.severity == "error")
    warns = sum(1 for f in findings if f.severity == "warn")
    print(oc.color("错误 %d 条 / 警告 %d 条 / 提示 %d 条" % (
        errors, warns, len(findings) - errors - warns), "grey"))
    _store().record(problem["id"], kind="review", detail="规范分 %d" % value)

    profile = oop_coach.LearnerProfile()
    skill_ids = profile.note_review(problem, findings, score=value)
    if findings:
        print()
        print(oc.color("按知识点看, 这些地方要补:", "yellow"))
        for sid in skill_ids:
            related = [f for f in findings if oop_skills.map_review_rule(f.rule) == sid]
            if related:
                print("  · %s %s —— 掌握度 %.0f%%  %s" % (
                    sid, oop_skills.skill_name(sid), profile.mastery(sid) * 100,
                    profile.bar(profile.mastery(sid))))
        print(oc.color("看讲解: py oop_lab.py skills %s" % skill_ids[0], "grey"))
    oop_coach.log_event(
        "review", "**%s %s** —— 写法审查 %d/100" % (
            problem["id"].upper(), problem["title"], value),
        ["- 问题: " + ("; ".join("%s %s" % (f.rule, f.title) for f in findings) or "无")]
        + [""] + oop_review.render_findings(findings, show_ok=False),
        pid=problem["id"], detail="规范分 %d, %d 条意见" % (value, len(findings)))
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    source = oop_workspace.student_source_path(problem)
    if not os.path.isfile(source):
        print("还没有 main.cpp, 先运行: py oop_lab.py new %s" % problem["id"])
        return 1

    report = None
    if not args.no_judge:
        report = _compile_and_judge(problem, args.timeout)
    findings = oop_review.review_file(source, problem)
    path, error = oop_workspace.write_submission(problem, report=report, findings=findings,
                                                 extra_note=args.note or "")
    if path is None:
        print(oc.color(error, "red"))
        return 1

    print(oc.color("提交包已生成", "green"))
    print("  %s" % path)
    if report is not None:
        print("  评测: %s  通过 %d/%d" % (report.verdict, report.passed, report.total))
    print("  规范分: %d/100" % oop_review.score(findings))
    print()
    print("把它整个贴给 AI 或老师, 对方不用任何额外上下文就能开始点评。")
    print("比如在对话里说: 帮我按 OOP 角度点评这个提交, 指出最该改的三处。")
    _store().record(problem["id"], kind="submit", detail="生成提交包")
    coach = oop_coach.LearnerProfile()
    coach.bump("submit")
    coach.save()
    oop_coach.log_event(
        "submit", "**%s %s** —— 生成点评申请" % (problem["id"].upper(), problem["title"]),
        ["- 提交包: %s" % path,
         "- 规范分: %d/100" % oop_review.score(findings)] +
        (["- 评测: %s %d/%d" % (report.verdict, report.passed, report.total)] if report else []),
        pid=problem["id"], detail="生成提交包")
    return 0


def cmd_solution(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    store = _store()
    status = store.status(problem["id"])
    if status != "passed" and not args.force:
        print(oc.color("这一题还没通过, 先自己写。", "yellow"))
        print("确实想直接看参考解, 加 --force: py oop_lab.py solution %s --force" % problem["id"])
        return 1
    solution = problem.get("solution") or ""
    if not solution.strip():
        print("这题(在线导入的题目)没有参考解, 可以自己去 %s 提交验证。" % problem.get("url", "原站"))
        return 1
    print(oc.color("参考解 %s %s" % (problem["id"].upper(), problem["title"]), "bold"))
    print(oc.hr("-", 78))
    print(solution.rstrip("\n"))
    print(oc.hr("-", 78))
    if problem.get("checklist"):
        print(oc.color("对着再看一遍这几个点:", "cyan"))
        for item in problem["checklist"]:
            print("  [ ] %s" % item)
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """推荐下一题 —— 走的和 plan 同一套自适应逻辑。"""
    profile = oop_coach.LearnerProfile()
    assignments = oop_coach.local_plan(profile, count=1)
    if not assignments:
        store = _store()
        problem = _next_problem(store)
        if problem is None:
            print(oc.color("本地题库都练熟了。用 `py oop_lab.py search <关键词>` 去找新题。", "green"))
            return 0
        print("下一题: %s  %s" % (problem["id"].upper(), problem["title"]))
        return cmd_new(argparse.Namespace(id=problem["id"], force=False, open=not args.no_open))

    item = assignments[0]
    problem = item.problem
    print(oc.color("教练推荐下一题", "bold"))
    print("  %s  %s  [%s]" % (problem["id"].upper(), problem["title"],
                              oc.LEVEL_STARS.get(int(problem["level"]), "")))
    for reason in item.reasons:
        print("  · " + oc.color(reason, "grey"))
    print()
    return cmd_new(argparse.Namespace(id=problem["id"], force=False, open=not args.no_open))


def cmd_progress(args: argparse.Namespace) -> int:
    store = _store()
    order = oop_bank.id_order()
    stats = store.stats()

    print(oc.color("练习进度", "bold"))
    print(oc.hr("-", 78))
    xp = 0
    for pid in order:
        problem = oop_bank.find(pid)
        status = store.status(pid)
        entry = store.get(pid)
        level = int(problem["level"])
        if status == "passed":
            xp += XP_PER_LEVEL.get(level, 10)
        elif status == "doing":
            xp += 2
        mark = {"passed": "[√]", "doing": "[~]", "todo": "[ ]"}.get(status, "[?]")
        extra = ""
        if entry.get("best"):
            extra = "%s  %d 次提交" % (entry["best"], entry.get("attempts", 0))
        print("  %s %-5s %s %s %s" % (
            mark, pid,
            oc.pad_end(oc.truncate(problem["title"], 34), 34),
            oc.pad_end(extra, 16),
            _status_badge(status)))

    print(oc.hr("-", 78))
    print("通过 %d 题   进行中 %d 题   提交 %d 次   累计练习 %s" % (
        stats["passed"], stats["doing"], stats["attempts"],
        oc.human_duration(stats["seconds"])))
    print("经验值 %s" % oc.color("%d XP" % xp, "yellow"))
    print(_progress_bar(stats["passed"], len(order)))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    profile = oop_coach.LearnerProfile()
    result = oop_coach.plan(profile, count=args.count, local_only=args.local_only)
    for row in oop_coach.render_plan(result):
        print(row)

    weakest = profile.weakest(3)
    if profile.practised():
        print(oc.hr("-", 78))
        print(oc.color("为什么这么安排", "bold"))
        for sid, value in weakest:
            ev = profile.evidence(sid)
            print("  · %s %s 掌握度 %.0f%%  %s  练习 %d 次(通过 %d 次)" % (
                sid, oc.pad_end(oop_skills.skill_name(sid), 20), value * 100,
                profile.bar(value), ev.get("attempts", 0), ev.get("full", 0)))
        wins, losses = profile.streak()
        if wins >= 2:
            print(oc.color("  最近连续通过 %d 次, 所以本次难度往上加了半档。" % wins, "green"))
        elif losses >= 2:
            print(oc.color("  最近连续 %d 次没通过, 所以本次难度退回了半档, 先把手感找回来。" % losses, "yellow"))
    else:
        print(oc.hr("-", 78))
        print("这是你第一次练习, 安排的顺序是“类与封装 → 构造函数 → 生命周期”这条主线。")

    print()
    print(oc.color("练完一道就 judge 一次, 记录会写进学习日志与画像。", "grey"))
    oop_coach.log_event(
        "plan", "安排练习(%d 道)" % len(result.get("assignments") or []),
        ["- " + "%s %s [%s]" % (a.problem["id"], a.problem["title"], a.kind)
         for a in (result.get("assignments") or [])],
        detail="当前档位 %d, 目标难度 %d" % (result.get("profile_level", 1),
                                            result.get("target_level", 1)))
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    problem = _require_problem(args.id)
    if problem is None:
        return 1
    source = oop_workspace.student_source_path(problem)
    if not os.path.isfile(source):
        print("还没有 main.cpp, 先运行: py oop_lab.py new %s" % problem["id"])
        return 1

    profile = oop_coach.LearnerProfile()
    report = None
    if not args.no_judge:
        print(oc.color("正在重新编译并跑一遍用例…", "grey"))
        report = _compile_and_judge(problem, args.timeout)
    findings = oop_review.review_file(source, problem)

    if report is not None:
        print(oc.color("评测摘要", "bold"))
        print("  %s  通过 %d/%d 个用例" % (
            oop_judge.verdict_badge(report.verdict), report.passed, report.total))
        print()

    diag = oop_coach.diagnose(problem, report=report, findings=findings, profile=profile)
    for row in oop_coach.render_diagnosis(diag):
        print(row)

    ids = diag.skills[:2]
    if ids and not args.no_teach:
        print()
        print(oc.hr("=", 78))
        print(oc.color("针对性讲解", "bold"))
        for sid in ids:
            print()
            for row in oop_skills.teach_lines(sid):
                print(row)
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    profile = oop_coach.LearnerProfile()
    for row in profile.render():
        print(row)
    print(oc.hr("-", 78))
    print(oc.color("建议", "bold"))
    assignments = oop_coach.local_plan(profile, count=2)
    if not assignments:
        print("  本地题库都练熟了, 用 `py oop_lab.py search <关键词>` 去洛谷/dotcpp 找新题。")
    else:
        print("  下一步推荐: %s %s（py oop_lab.py new %s）" % (
            assignments[0].problem["id"], assignments[0].problem["title"],
            assignments[0].problem["id"]))
    if profile.records:
        last = profile.records[-1]
        print("  最近一次: %s %s -> %s %d/%d" % (
            last.get("ts") and time.strftime("%m-%d %H:%M", time.localtime(last["ts"])),
            last.get("pid"), last.get("verdict"), last.get("passed"), last.get("total")))
    print()
    print(oc.color("看知识点讲解: py oop_lab.py skills K12", "grey"))
    return 0


def cmd_skills(args: argparse.Namespace) -> int:
    if not args.id:
        print(oc.color("面向对象知识点图谱(%d 个)" % len(oop_skills.SKILLS), "bold"))
        print(oc.hr("-", 78))
        for level in (1, 2, 3):
            print(oc.color("第 %d 档 · %s" % (level, oc.LEVEL_NAMES.get(level, "")), "cyan"))
            for item in oop_skills.skills_by_level(level):
                print("  %s %s %s" % (
                    item["id"], oc.pad_end(item["name"], 22),
                    oc.color(oc.truncate(item["summary"], 40), "grey")))
            print()
        print("看某个知识点的完整讲解: py oop_lab.py skills K12")
        return 0

    skill_id = args.id.upper()
    if not skill_id.startswith("K") or len(skill_id) == 1:
        skill_id = "K%02d" % int(skill_id[1:]) if skill_id[1:].isdigit() else skill_id
    if oop_skills.skill(skill_id) is None:
        print(oc.color("没有这个知识点: %s" % args.id, "red"))
        print("可用: %s" % ", ".join(oop_skills.all_skill_ids()))
        return 1
    for row in oop_skills.teach_lines(skill_id):
        print(row)
    related = [p for p in oop_bank.all_problems()
               if skill_id in oop_skills.classify(p.get("topics", []))]
    if related:
        print()
        print(oc.color("覆盖这个知识点的题:", "cyan"))
        for problem in related[:8]:
            print("  %-5s %s" % (problem["id"], problem["title"]))
    return 0


# ---------------------------------------------------------------------------
# 集中式主菜单(什么都不用记, 双击 oop_lab.bat 就是它)
# ---------------------------------------------------------------------------
MENU_ITEMS: List[Tuple[str, str, str]] = [
    ("1", "教练安排今天的题", "plan"),
    ("2", "学知识点(先学后练)", "study"),
    ("3", "题目列表", "list"),
    ("4", "看某道题(题面)", "show"),
    ("5", "开练某道题(生成工程并打开编辑器)", "new"),
    ("6", "评测当前题(编译 + 用例 + 老师式诊断)", "judge"),
    ("7", "写法审查(12 条 OOP 规则)", "review"),
    ("8", "我的学习画像(%d 个知识点掌握度)" % len(oop_skills.SKILLS), "profile"),
    ("9", "学习日志", "log"),
    ("10", "联网找题 / 导入题目", "search"),
    ("11", "只看某道题的参考解", "solution"),
    ("12", "打开练习工作区", "open"),
    ("13", "环境自检", "doctor"),
    ("14", "题库自检(%d 题参考解真编译)" % len(oop_bank.BUILTIN), "selftest"),
    ("0", "退出", "quit"),
]
_MENU_NEEDS_ID = {"show", "new", "judge", "review", "solution", "study"}


def _ask(prompt: str, default: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default or "__quit__"


def _menu_header() -> List[str]:
    store = _store()
    coach = oop_coach.LearnerProfile()
    order = oop_bank.id_order()
    passed = sum(1 for pid in order if store.status(pid) == "passed")
    chain = oop_judge.find_toolchain()
    lines = [
        oc.color("=" * 72, "grey"),
        oc.color("  C++ 面向对象训练营 · OOP Lab", "bold")
        + oc.color("    统一工作区 + 先学后练 + 老师式诊断", "grey"),
        oc.color("=" * 72, "grey"),
        "  进度 %d/%d   %s   档位 %s   %s" % (
            passed, len(order), _progress_bar(passed, len(order), 16),
            coach.level_label(),
            oc.color(chain.label if chain else "未找到编译器", "green" if chain else "red")),
        "  练习工作区: %s" % oc.WORKSPACE_DIR,
        oc.color("-" * 72, "grey"),
    ]
    return lines


def cmd_menu(args: argparse.Namespace) -> int:
    """交互式主菜单 —— 所有功能都从这里进去, 不需要记命令。"""
    print()
    for row in _menu_header():
        print(row)
    for key, label, _cmd in MENU_ITEMS:
        print("  %-3s %s" % (key + ")", label))
    print()

    while True:
        choice = _ask("请选择 [0-14]: ")
        if choice in ("0", "q", "Q", "quit", "exit", "__quit__"):
            print(oc.color("再见, 下次直接从 `py oop_lab.py` 或 oop_lab.bat 进来。", "grey"))
            return 0
        if choice == "":
            continue

        item = next((entry for entry in MENU_ITEMS if entry[0] == choice), None)
        if item is None:
            print(oc.color("没有这个选项, 重新选。", "yellow"))
            continue
        _, label, command = item

        if command == "quit":
            return 0
        if command == "open":
            workspace = oc.ensure_dir(oc.WORKSPACE_DIR)
            oop_workspace.ensure_lab(workspace)
            if oop_workspace.open_in_vscode(workspace):
                print(oc.color("已用 VSCode 打开工作区: %s" % workspace, "green"))
            elif oop_workspace.open_in_visual_studio(
                    os.path.join(workspace, oop_workspace.SOLUTION_NAME)):
                print(oc.color("已用 Visual Studio 打开解决方案。", "green"))
            else:
                print(oc.color("请手动打开: %s" % workspace, "yellow"))
            print()
            continue

        tokens = [command]
        if command in _MENU_NEEDS_ID:
            coach = oop_coach.LearnerProfile()
            suggestion = ""
            planned = oop_coach.local_plan(coach, count=1)
            if planned:
                suggestion = planned[0].problem["id"]
            hint = "(回车用推荐题目 %s)" % suggestion if suggestion else "(例如 b01)"
            answer = _ask("请输入题目编号 %s: " % hint)
            if answer == "__quit__":
                return 0
            answer = answer or suggestion
            if not answer:
                print(oc.color("需要题目编号。", "yellow"))
                continue
            tokens.append(answer)
        elif command == "list":
            pass
        elif command == "search":
            answer = _ask("搜索关键词(回车跳过, 直接看来源清单): ")
            if answer == "__quit__":
                return 0
            if answer:
                tokens.append(answer)
            else:
                for row in oop_web.render_sources():
                    print(row)
                print()
                continue

        print()
        print(oc.color("─" * 72, "grey"))
        try:
            main(tokens)
        except SystemExit:
            pass
        except KeyboardInterrupt:
            print()
        print(oc.color("─" * 72, "grey"))
        _ask("回车回到菜单... ", " ")
        print()


def cmd_sources(args: argparse.Namespace) -> int:
    """题目来源管理: 列出 / 新增 / 启用 / 停用 / 删除。"""
    if args.add:
        if args.kind == "generic" and (not args.search_url or not args.item_regex):
            print(oc.color("generic 来源必须同时给 --search-url 和 --item-regex", "red"))
            for row in oop_web.GENERIC_HELP:
                print("  · " + row)
            return 1
        entry = {
            "name": args.add,
            "label": args.label or args.add,
            "kind": args.kind,
            "hosts": [h.strip() for h in (args.hosts or "").split(",") if h.strip()],
            "search_url": args.search_url or "",
            "item_regex": args.item_regex or "",
            "enabled": True,
            "note": args.note or "用户自定义来源",
        }
        oop_web.add_source(entry)
        print(oc.color("已添加来源 %s (%s)" % (args.add, args.kind), "green"))
        return 0
    if args.enable:
        print("已启用 %s" % args.enable if oop_web.set_enabled(args.enable, True)
              else oc.color("没有这个来源: %s" % args.enable, "red"))
        return 0
    if args.disable:
        print("已停用 %s" % args.disable if oop_web.set_enabled(args.disable, False)
              else oc.color("没有这个来源: %s" % args.disable, "red"))
        return 0
    if args.remove:
        print("已删除 %s" % args.remove if oop_web.remove_source(args.remove)
              else oc.color("没有这个来源: %s" % args.remove, "red"))
        return 0

    for row in oop_web.render_sources():
        print(row)
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    for row in oop_coach.render_log(args.count):
        print(row)
    print(oc.color("完整 markdown 日志: %s" % oop_coach.LOG_FILE, "grey"))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    keyword = " ".join(args.keyword)
    local = oop_bank.filter_problems(keyword=keyword)
    if local:
        print(oc.color("本地题库命中 %d 题:" % len(local), "cyan"))
        for problem in local:
            skills = oop_skills.classify(problem.get("topics", []))
            print("  %-5s %s %s" % (
                problem["id"], oc.pad_end(oc.truncate(problem["title"], 36), 36),
                oc.color(", ".join(oop_skills.skill_name(s) for s in skills), "grey")))
        print()

    entries = oop_web.enabled_sources()
    if args.source != "auto":
        entries = [e for e in entries
                   if str(e.get("name", "")).lower() == args.source.lower()]
        if not entries:
            print(oc.color("没有这个来源: %s" % args.source, "red"))
            print("看看有哪些已配置的来源: py oop_lab.py sources")
            return 1
    names = " + ".join(str(e.get("label") or e.get("name")) for e in entries)
    print(oc.color("正在联网找题(%s)…" % (names or "无"), "grey"))
    result = oop_search.search_all(keyword, limit=args.limit,
                                   sources=[str(e.get("name")) for e in entries])
    for row in oop_search.render_search(result):
        print(row)
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    """支持任意链接: 认得出来的站点走专用解析, 认不出来走通用抽取。"""
    target = args.target
    kind = args.source if args.source != "auto" else oop_search.detect_source(target)
    label = oop_search.source_label(kind)
    is_url = target.lower().startswith(("http://", "https://"))
    if is_url and kind == "web":
        print(oc.color("正在用通用模式抽取这个链接的题面…", "grey"))
    else:
        print(oc.color("正在从 %s 抓取题面…" % label, "grey"))

    problem, error = oop_search.import_problem(target, source=args.source, level=args.level)
    if problem is None:
        print(oc.color("导入失败: %s" % error, "red"))
        if is_url:
            print("可以直接打开链接自己看: %s" % target)
        elif kind == "dotcpp":
            print("可以直接打开链接自己看: %s" % oop_search.dotcpp_problem_url(
                oop_search.extract_dotcpp_id(target) or target))
        elif kind == "codeforces":
            cid, index = oop_search.parse_cf_id(target)
            if cid:
                print("可以直接打开链接自己看: %s" % oop_search.cf_problem_url(cid, index))
        else:
            print("可以直接打开链接自己看: %s" % oop_search.luogu_problem_url(
                oop_search.extract_pid(target) or target))
        return 1
    print(oc.color("导入成功", "green"))
    print("  %s  %s" % (problem["id"], problem["title"]))
    print("  难度档位: 第 %d 档 %s %s" % (
        problem["level"], oc.LEVEL_NAMES.get(int(problem["level"]), ""),
        oc.LEVEL_STARS.get(int(problem["level"]), "")))
    tags = [t for t in problem.get("topics", []) if t != "在线导入"]
    if tags:
        print("  标签: %s" % " / ".join(tags))
    if problem.get("samples"):
        print("  题面样例: %d 组(已写进 problem.md)" % len(problem["samples"]))
    print("  来源: %s (%s)" % (problem.get("url", ""),
                              oop_search.source_label(problem.get("origin", ""))))
    print()
    print("接下来: py oop_lab.py new %s" % problem["id"])
    print(oc.color("提示: 在线导入的题目没有内建用例, 请自己补 tests/ 下的数据。", "grey"))
    return 0


def cmd_selftest(args: argparse.Namespace) -> int:
    chain = _toolchain_or_hint()
    if chain is None:
        return 1
    problems = ([oop_bank.find(args.id)] if args.id else oop_bank.BUILTIN)
    problems = [p for p in problems if p]
    print(oc.color("题库自检: 用每题自带的参考解跑一遍用例", "bold"))
    print("编译器: %s" % chain.describe())
    print(oc.hr("-", 78))

    failed: List[str] = []
    for problem in problems:
        report = oop_judge.verify_solution(problem, chain)
        mark = oc.color("OK ", "green") if report.all_passed else oc.color("BAD", "red")
        print("  %s %-5s %-34s %d/%d  %s" % (
            mark, problem["id"], oc.truncate(problem["title"], 34),
            report.passed, report.total,
            oc.color(report.verdict if not report.all_passed else "", "grey")))
        if not report.all_passed:
            failed.append(problem["id"])
            for row in oop_judge.render_report(report, max_diff=2)[:24]:
                print("      " + row)
    print(oc.hr("-", 78))
    if failed:
        print(oc.color("有 %d 题的参考解或答案有问题: %s" % (len(failed), ", ".join(failed)), "red"))
        return 1
    print(oc.color("全部 %d 题的参考解都能通过各自的用例。题库是干净的。" % len(problems), "green"))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    ok, rows = oop_judge.doctor()
    for row in rows:
        print(row)
    print()
    print(oc.color("== 题库健康度 ==", "bold"))
    errors = oop_bank.validate_all()
    if errors:
        ok = False
        for item in errors:
            print("  " + oc.color("×", "red") + " " + item)
    else:
        print("  %s %d 题结构自检通过" % (oc.color("[OK]", "green"), len(oop_bank.all_problems())))
    user = oop_bank.load_user()
    print("  在线导入题目: %d 题" % len(user))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# 命令行解析
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    parent.add_argument("-v", "--verbose", action="store_true", help="输出调试日志")

    parser = argparse.ArgumentParser(
        prog="oop_lab", description="C++ 面向对象训练营",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parent])
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("menu", parents=[parent], help="交互式主菜单(不带参数时默认进这里)")
    sub.add_parser("overview", parents=[parent], help="总览面板")

    p_study = sub.add_parser("study", parents=[parent], help="先学后练: 知识点讲义")
    p_study.add_argument("id", nargs="?", help="题目编号(b01)或知识点编号(K12)")

    p_list = sub.add_parser("list", parents=[parent], help="列出题目")
    p_list.add_argument("-l", "--level", type=int, choices=[1, 2, 3], help="只看某一档")
    p_list.add_argument("-t", "--tag", help="按知识点过滤")
    p_list.add_argument("-k", "--keyword", help="按关键字过滤")

    p_show = sub.add_parser("show", parents=[parent], help="查看题面")
    p_show.add_argument("id")

    p_new = sub.add_parser("new", parents=[parent], help="生成 VSCode 练习工程")
    p_new.add_argument("id")
    p_new.add_argument("--force", action="store_true", help="覆盖已有的 main.cpp")
    p_new.add_argument("--no-open", dest="open", action="store_false", help="不自动打开 VSCode")
    p_new.set_defaults(open=True)

    p_judge = sub.add_parser("judge", parents=[parent], help="编译并跑全部用例")
    p_judge.add_argument("id")
    p_judge.add_argument("--timeout", type=float, default=oop_judge.DEFAULT_TIMEOUT)

    p_run = sub.add_parser("run", parents=[parent], help="编译并跑一组用例")
    p_run.add_argument("id")
    p_run.add_argument("--case", type=int, default=0, help="第几组用例(默认第 1 组)")
    p_run.add_argument("--timeout", type=float, default=oop_judge.DEFAULT_TIMEOUT)

    p_review = sub.add_parser("review", parents=[parent], help="面向对象写法审查")
    p_review.add_argument("id")

    p_submit = sub.add_parser("submit", parents=[parent], help="生成提交包(贴给 AI/老师)")
    p_submit.add_argument("id")
    p_submit.add_argument("-m", "--note", help="附上你想问的问题")
    p_submit.add_argument("--no-judge", action="store_true", help="不跑评测, 只打包代码")
    p_submit.add_argument("--timeout", type=float, default=oop_judge.DEFAULT_TIMEOUT)

    p_sol = sub.add_parser("solution", parents=[parent], help="查看参考解")
    p_sol.add_argument("id")
    p_sol.add_argument("--force", action="store_true", help="没通过也强行查看")

    p_next = sub.add_parser("next", parents=[parent], help="推荐下一题并开工程")
    p_next.add_argument("--no-open", dest="no_open", action="store_true", help="不自动打开 VSCode")

    sub.add_parser("progress", parents=[parent], help="进度与统计")

    p_plan = sub.add_parser("plan", parents=[parent], help="按你的水平安排今天练哪几道")
    p_plan.add_argument("-n", "--count", type=int, default=3, help="安排几道(默认 3)")
    p_plan.add_argument("--local-only", action="store_true", help="只用本地题库, 不联网")

    p_diag = sub.add_parser("diagnose", parents=[parent], help="老师式诊断(错在哪/补什么)")
    p_diag.add_argument("id")
    p_diag.add_argument("--no-judge", action="store_true", help="不重新编译评测, 只做写法诊断")
    p_diag.add_argument("--no-teach", action="store_true", help="不展开知识点讲解")
    p_diag.add_argument("--timeout", type=float, default=oop_judge.DEFAULT_TIMEOUT)

    sub.add_parser("profile", parents=[parent], help="学习画像: 知识点掌握度与档位")

    p_skills = sub.add_parser("skills", parents=[parent], help="知识点讲解")
    p_skills.add_argument("id", nargs="?", help="知识点编号, 例如 K12; 不填则列出全部")

    p_log = sub.add_parser("log", parents=[parent], help="学习日志")
    p_log.add_argument("-n", "--count", type=int, default=8, help="显示最近几条")

    p_search = sub.add_parser("search", parents=[parent],
                              help="多源找题(来源清单见 sources 命令)")
    p_search.add_argument("keyword", nargs="+")
    p_search.add_argument("--limit", type=int, default=8)
    p_search.add_argument("--source", default="auto",
                          help="只查某一个来源(名字见 py oop_lab.py sources)")

    p_pull = sub.add_parser("pull", parents=[parent],
                            help="导入题目: 题号或任意题面链接")
    p_pull.add_argument("target", help="P1001 / 1049 / CF4A / 或者任意题面 URL")
    p_pull.add_argument("--level", type=int, choices=[1, 2, 3], help="强制指定档位")
    p_pull.add_argument("--source", default="auto", help="强制按某个来源解析(默认自动识别)")

    p_sources = sub.add_parser("sources", parents=[parent],
                               help="题目来源管理(增删启停, 题目不绑定固定网站)")
    p_sources.add_argument("--add", metavar="NAME", help="新增来源, 例如 --add hdu")
    p_sources.add_argument("--kind", default="generic",
                           help="来源类型: luogu/dotcpp/codeforces/github/bing/generic")
    p_sources.add_argument("--label", help="显示名")
    p_sources.add_argument("--hosts", help="域名(逗号分隔), 用来识别链接属于哪个站点")
    p_sources.add_argument("--search-url", dest="search_url",
                           help="搜索地址模板, 用 {q} 占位关键词")
    p_sources.add_argument("--item-regex", dest="item_regex",
                           help="条目正则: 第 1 组=链接, 第 2 组=标题")
    p_sources.add_argument("--note", help="备注")
    p_sources.add_argument("--enable", metavar="NAME", help="启用某个来源")
    p_sources.add_argument("--disable", metavar="NAME", help="停用某个来源")
    p_sources.add_argument("--remove", metavar="NAME", help="删除某个来源")

    p_self = sub.add_parser("selftest", parents=[parent], help="用参考解自检题库")
    p_self.add_argument("--id", help="只检查某一题")

    sub.add_parser("doctor", parents=[parent], help="环境自检")
    return parser


HANDLERS = {
    "menu": cmd_menu,
    "study": cmd_study,
    "overview": cmd_overview,
    "list": cmd_list,
    "show": cmd_show,
    "new": cmd_new,
    "judge": cmd_judge,
    "run": cmd_run,
    "review": cmd_review,
    "submit": cmd_submit,
    "solution": cmd_solution,
    "next": cmd_next,
    "progress": cmd_progress,
    "plan": cmd_plan,
    "diagnose": cmd_diagnose,
    "profile": cmd_profile,
    "skills": cmd_skills,
    "log": cmd_log,
    "search": cmd_search,
    "pull": cmd_pull,
    "sources": cmd_sources,
    "selftest": cmd_selftest,
    "doctor": cmd_doctor,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if getattr(args, "no_color", False):
        oc.set_color_enabled(False)
    else:
        oc.enable_ansi()
    oc.setup_logging(verbose=getattr(args, "verbose", False))
    # 打包成 --windowed 的 exe 时没有标准输出, 这里必须判空(否则启动即崩)
    if sys.stdout is not None:
        try:
            if not sys.stdout.isatty():
                sys.stdout.reconfigure(encoding="utf-8")
            else:
                sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass

    # 不带参数时: 在真实终端里进交互菜单, 被重定向/管道时退回总览面板(可脚本化)
    command = args.command
    if not command:
        interactive = False
        try:
            interactive = sys.stdin is not None and sys.stdin.isatty()
        except Exception:
            interactive = False
        command = "menu" if interactive else "overview"
    handler = HANDLERS.get(command)
    if handler is None:
        parser.print_help()
        return 2
    try:
        return handler(args)
    except KeyboardInterrupt:
        print()
        print(oc.color("已中断。", "yellow"))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
