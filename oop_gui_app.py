#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_app.py - 图形界面主窗口

三栏工作台: 左边是题目树, 中间是 讲义 / 题面 / 我的代码 / 评测结果 四个选项卡,
上下分别是工具栏与状态栏。

这个文件只负责"摆放与接线" —— 所有业务逻辑都调现有模块:
    oop_bank(题库) oop_skills(讲义) oop_coach(排课/诊断/画像)
    oop_judge(编译评测) oop_review(写法审查) oop_search(找题) oop_workspace(工作区)
凡是会卡住界面的操作(编译 / 联网 / 自检)一律交给 oop_gui_tasks.TaskRunner 放到后台。
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

import oop_bank
import oop_coach
import oop_common as oc
import oop_gui_editor
import oop_gui_tasks
import oop_judge
import oop_review
import oop_search
import oop_skills
import oop_workspace

POLL_MS = 50
UI_FONT = ("Microsoft YaHei UI", 10)
TREE_WIDTH = 260
TAB_KNOWLEDGE, TAB_STATEMENT, TAB_CODE, TAB_RESULT = 0, 1, 2, 3


def enable_dpi_awareness() -> None:
    """高 DPI 屏上不设这个, 字体和控件会发虚。"""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class LabWindow:
    """整个界面。对外只需要 root 一个参数, 方便测试里直接 new 出来。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.tasks = oop_gui_tasks.TaskRunner()
        self.store = oc.ProgressStore()
        self.problem: Optional[Dict[str, Any]] = None
        self.problems: List[Dict[str, Any]] = []
        self.toolchain = oop_judge.find_toolchain()
        self.profile = oop_coach.LearnerProfile()   # 画像读一次即可, 评测后不必重建
        self._prepared: set = set()                 # 已经生成过工程目录的题目 id

        root.title("OOP Lab — C++ 面向对象训练营")
        root.geometry("1280x800")
        root.minsize(960, 640)
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self.reload_problems()
        self._poll()

    # ------------------------------------------------------------------ 构建
    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self.root, padding=(8, 6))
        bar.pack(side="top", fill="x")
        self.buttons: List[ttk.Button] = []
        for text, command, slow in (
            ("教练排课", self.act_plan, True),
            ("学知识点", self.act_study, False),
            ("保存", self.act_save, False),
            ("评测  F5", self.act_judge, True),
            ("写法审查", self.act_review, False),
            ("学习画像", self.act_profile, False),
            ("找题", self.act_search, True),
            ("打开VSCode", self.act_vscode, False),
            ("自检", self.act_doctor, True),
        ):
            button = ttk.Button(bar, text=text, command=command, width=11)
            button.pack(side="left", padx=3)
            if slow:
                self.buttons.append(button)     # 只有走 TaskRunner 的按钮需要置灰
        self.root.bind("<F5>", lambda event: self.act_judge())

    def _build_body(self) -> None:
        panes = ttk.PanedWindow(self.root, orient="horizontal")
        panes.pack(side="top", fill="both", expand=True)

        left = ttk.Frame(panes, width=TREE_WIDTH)
        panes.add(left, weight=0)
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.tag_configure("passed", foreground="#2e7d32")
        self.tree.tag_configure("doing", foreground="#f9a825")
        self.tree.tag_configure("todo", foreground="#666666")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        right = ttk.Frame(panes)
        panes.add(right, weight=1)
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)
        self.knowledge_view = self._make_text_tab("讲义")
        self.statement_view = self._make_text_tab("题面")
        self.code_editor = oop_gui_editor.CodeEditor(self.tabs, on_save=self.act_save)
        self.tabs.add(self.code_editor, text="我的代码")
        self.result_view = self._make_text_tab("评测结果")

    def _make_text_tab(self, title: str) -> tk.Text:
        """建一个只读文本框挂到选项卡上, 返回控件本身。"""
        frame = ttk.Frame(self.tabs)
        widget = tk.Text(frame, wrap="word", font=UI_FONT, bg="#fbfbfb",
                         relief="flat", padx=10, pady=8)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=widget.yview)
        widget.configure(yscrollcommand=scroll.set, state="disabled")
        scroll.pack(side="right", fill="y")
        widget.pack(side="left", fill="both", expand=True)
        self.tabs.add(frame, text=title)
        return widget

    def _build_statusbar(self) -> None:
        ttk.Separator(self.root, orient="horizontal").pack(side="bottom", fill="x")
        bar = ttk.Frame(self.root, padding=(8, 4))
        bar.pack(side="bottom", fill="x")
        chain = self.toolchain.describe() if self.toolchain else "没找到 C++ 编译器(点「自检」看建议)"
        self.status_chain = ttk.Label(bar, text="编译器: %s" % chain)
        self.status_problem = ttk.Label(bar, text="当前: —")
        self.status_task = ttk.Label(bar, text="就绪")
        self.status_chain.pack(side="left")
        ttk.Label(bar, text=" │ ").pack(side="left")
        self.status_problem.pack(side="left")
        self.status_task.pack(side="right")

    # ------------------------------------------------------------------ 数据
    def reload_problems(self) -> None:
        """重建题目树, 并尽量保持当前选中项。"""
        self.problems = oop_bank.all_problems()
        keep = self.problem["id"] if self.problem else ""
        self.profile = oop_coach.LearnerProfile()
        self.tree.delete(*self.tree.get_children())
        for level in (1, 2, 3):
            rows = [p for p in self.problems if int(p["level"]) == level]
            if not rows:
                continue
            done = sum(1 for p in rows if self.store.status(p["id"]) == "passed")
            node = self.tree.insert(
                "", "end", iid="level%d" % level, open=True,
                text="%s %s (%d/%d)" % (oc.LEVEL_STARS[level], oc.LEVEL_NAMES[level],
                                        done, len(rows)))
            for problem in rows:
                status = self.store.status(problem["id"])
                glyph, tag = {"passed": ("●", "passed"),
                              "doing": ("◐", "doing")}.get(status, ("○", "todo"))
                self.tree.insert(node, "end", iid=problem["id"], tags=(tag,),
                                 text="%s %s  %s" % (glyph, problem["id"],
                                                     problem["title"]))
        fallback = self.problems[0]["id"] if self.problems else ""
        self.select_problem(keep or fallback)

    def select_problem(self, pid: str, ask_save: bool = True) -> None:
        """切换当前题目: 先处理未保存的修改, 再加载讲义 / 题面 / 代码。"""
        if not pid or pid.startswith("level"):
            return
        if ask_save and self.problem is not None and self.code_editor.dirty \
                and self.problem["id"] != pid:
            if not messagebox.askyesno("还没保存", "当前代码有未保存的修改, 要保存吗?"):
                return
            self.act_save()
        problem = oop_bank.find(pid)
        if problem is None:
            return
        previous = self.problem["id"] if self.problem else ""
        switching = previous != problem["id"]
        self.problem = problem
        if problem["id"] not in self._prepared:
            oop_workspace.ensure_workspace(problem, toolchain=self.toolchain)
            self._prepared.add(problem["id"])
        self._set_readonly(self.statement_view,
                           "\n".join(oop_coach.render_problem(problem)))
        self._set_readonly(self.knowledge_view, oop_skills.teach_markdown(
            oop_workspace.problem_skills(problem)))
        exists, source = oop_workspace.read_student_code(problem)
        self.code_editor.set_text(source if exists else problem["skeleton"])
        # 只有真的换了一道题才清空结果页 / 跳回讲义。
        # 评测结束后会 reload 一次(重新选中同一题), 那时必须保住刚出的结果。
        if switching:
            self._set_readonly(self.result_view, "")
            self.tabs.select(TAB_KNOWLEDGE)
        if self.tree.exists(problem["id"]):
            # 只有选择真的不同才改: Tk 的 treeview 对「同一项再选一次」也会
            # 触发 <<TreeviewSelect>>, 而本函数正是被那个事件驱动的 ——
            # 无条件 selection_set 会形成「事件 → 选题 → 再触发事件」的死循环,
            # 窗口在 mainloop 里永远出不来(实测每秒上千次, 界面全部卡死)。
            if self.tree.selection() != (problem["id"],):
                self.tree.selection_set(problem["id"])
            self.tree.see(problem["id"])
        status = self.store.status(problem["id"])
        self.status_problem.configure(text="当前: %s %s   掌握度: %s" % (
            problem["id"].upper(),
            oc.STATUS_TEXT.get(status, ("未知", ""))[0],
            self._mastery_brief(problem)))

    def _on_tree_select(self, event=None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        # 选中的已经是当前题: 直接返回。否则又会走一遍 select_problem,
        # 而它结尾的 selection_set 会再发一次本事件 —— 第二道防死循环保险。
        if self.problem is not None and selection[0] == self.problem["id"]:
            return
        self.select_problem(selection[0])

    def _mastery_brief(self, problem: Dict[str, Any]) -> str:
        """状态栏里显示这道题相关知识点的最低掌握度。"""
        scores = [self.profile.mastery(sid)
                  for sid in oop_workspace.problem_skills(problem)]
        if not scores:
            return "—"
        return "最低 %.0f%%" % (min(scores) * 100)

    def tree_item_count(self) -> int:
        return sum(len(self.tree.get_children(node))
                   for node in self.tree.get_children(""))

    # -------------------------------------------------------- 只读文本框读写
    @staticmethod
    def _set_readonly(widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content or "")
        widget.configure(state="disabled")

    @staticmethod
    def _get_readonly(widget: tk.Text) -> str:
        return widget.get("1.0", "end-1c")

    def knowledge_text(self) -> str:
        return self._get_readonly(self.knowledge_view)

    def statement_text(self) -> str:
        return self._get_readonly(self.statement_view)

    def result_text(self) -> str:
        return self._get_readonly(self.result_view)

    def status_toolchain_text(self) -> str:
        return self.status_chain.cget("text")

    def show_result(self, lines: List[str]) -> None:
        """把结果写进评测结果页, 并把 [AC] / [WA] 之类染上色。"""
        self._set_readonly(self.result_view, "\n".join(lines))
        self.result_view.tag_configure("ok", foreground="#2e7d32")
        self.result_view.tag_configure("bad", foreground="#c62828")
        for index, row in enumerate(lines, start=1):
            text = row.strip()
            tag = None
            if text.startswith("[AC]"):
                tag = "ok"
            elif text.startswith(("[WA]", "[RE]", "[CE]", "[TLE]")):
                tag = "bad"
            if tag:
                self.result_view.tag_add(tag, "%d.0" % index, "%d.end" % index)
        self.tabs.select(TAB_RESULT)

    # ------------------------------------------------------------------ 动作
    def act_save(self) -> None:
        problem = self.problem
        if problem is None:
            return
        path = oop_workspace.student_source_path(problem)
        oc.ensure_dir(os.path.dirname(path))
        oc.write_text(path, self.code_editor.get_text())
        self.code_editor.dirty = False
        self._set_status("已保存 %s" % os.path.basename(os.path.dirname(path)))

    def act_review(self) -> None:
        problem = self.problem
        if problem is None:
            return
        findings = oop_review.review_source(self.code_editor.get_text(),
                                           problem=problem)
        self.show_result(oop_review.render_findings(findings, show_ok=True))
        self._set_status("写法审查: %d 条提示" % len(findings))

    def act_profile(self) -> None:
        self.show_result(self.profile.render())
        self._set_status("学习画像已刷新")

    def act_vscode(self) -> None:
        if oop_workspace.open_in_vscode(oc.WORKSPACE_DIR):
            self._set_status("已用 VSCode 打开工作区")
        else:
            messagebox.showinfo("手动打开",
                                "没找到 VSCode, 请手动打开:\n%s" % oc.WORKSPACE_DIR)

    def _chooser(self, title: str, narrative: List[str],
                 rows: List[Tuple[str, Any]], on_pick: Callable[[Any], None]) -> None:
        """通用选择弹窗: 上面是老师口吻的说明文字, 下面是可双击的候选行。"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("760x520")
        win.transient(self.root)
        text = tk.Text(win, wrap="word", font=UI_FONT, height=14, bg="#fbfbfb",
                       relief="flat", padx=10, pady=8)
        text.insert("1.0", "\n".join(narrative))
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        box = tk.Listbox(win, font=UI_FONT, height=6)
        for label, _ in rows:
            box.insert("end", label)
        box.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        def pick(event=None):
            selection = box.curselection()
            if selection:
                on_pick(rows[selection[0]][1])

        box.bind("<Double-Button-1>", pick)
        ttk.Button(win, text="就用这一条", command=pick).pack(pady=(0, 8))

    def act_plan(self) -> None:
        def work():
            return oop_coach.plan(self.profile, count=3)

        def done(result):
            rows = [("%s  %s   [%s]" % (item.problem["id"], item.problem["title"],
                                        item.kind), item.problem["id"])
                    for item in result.get("assignments", [])]
            self._chooser("教练安排今天的题", oop_coach.render_plan(result),
                          rows, self.select_problem)

        self._run_task(work, done, "正在排课…")

    def act_study(self) -> None:
        rows = [("%s %s   [第 %d 档]" % (item["id"], item["name"], int(item["level"])),
                 item["id"]) for item in oop_skills.SKILLS]
        self._chooser("知识点(先学后练)",
                      ["先读讲义再动手。双击下面任意一条, 看完整讲解。"],
                      rows, lambda sid: self.show_result(oop_skills.teach_lines(sid)))

    def act_search(self) -> None:
        keyword = simpledialog.askstring("联网找题", "关键词(如 运算符重载 / 虚函数):",
                                        parent=self.root)
        if not keyword:
            return

        def work():
            return oop_search.search_all(keyword)

        def done(result):
            rows = []
            for name in result.get("order", []):        # order = 已启用的来源名
                for item in result.get(name) or []:
                    pid = item.get("pid") or item.get("title") or ""
                    rows.append(("%-10s %-10s %-34s %s" % (
                        name, pid, (item.get("title") or "")[:34],
                        item.get("difficulty") or ""), (name, pid)))
            if not rows:
                self.show_result(oop_search.render_search(result))
                self._set_status("没搜到题目(看看结果页里的链接)")
                return
            self._chooser("搜到的题目(双击一行导入)",
                          oop_search.render_search(result), rows,
                          lambda payload: self._import_from_search(*payload))

        self._run_task(work, done, "正在联网找题…")

    def _import_from_search(self, source: str, pid: str) -> None:
        if not pid:
            return

        def work():
            return oop_search.import_problem(pid, source=source)

        def done(payload):
            problem, error = payload
            if problem is None:
                messagebox.showerror("导入失败", error or "没能解析出题面")
                return
            saved = oop_bank.add_user(problem)
            self.reload_problems()
            self.select_problem(saved["id"])
            self._set_status("已导入 %s" % saved["id"])

        self._run_task(work, done, "正在导入题目…")

    def act_doctor(self) -> None:
        def work():
            ok, rows = oop_judge.doctor()
            return ok, rows, oop_bank.validate_all()

        def done(payload):
            ok, rows, errors = payload
            lines = list(rows)
            lines.append("")
            lines.append("题库结构自检: %s" % (
                "通过" if not errors else "有 %d 个问题" % len(errors)))
            lines.extend("  · %s" % item for item in errors)
            self.show_result(lines)
            self._set_status("自检%s" % ("通过" if ok and not errors else "发现问题"))

        self._run_task(work, done, "正在自检…")

    def act_judge(self) -> None:
        problem = self.problem
        if problem is None:
            return
        self.act_save()
        chain = self.toolchain
        if chain is None:
            messagebox.showerror("没有编译器",
                                 "没找到 C++ 编译器, 先点「自检」看安装建议。")
            return
        source = oop_workspace.student_source_path(problem)
        _ok, source_text = oop_workspace.read_student_code(problem)

        def work():
            report = oop_judge.judge(problem, source, toolchain=chain)
            findings = oop_review.review_source(source_text, problem=problem)
            diag = oop_coach.diagnose(problem, source_text=source_text,
                                      report=report, findings=findings,
                                      profile=self.profile)
            return report, findings, diag

        def done(payload):
            report, findings, diag = payload
            lines = oop_judge.render_report(report, max_diff=2)
            lines.append("")
            lines.extend(oop_coach.render_diagnosis(diag))
            if findings:
                lines.append("")
                lines.extend(oop_review.render_findings(findings, show_ok=False))
            self.show_result(lines)
            if report.total == 0:
                messagebox.showinfo("没有自动用例",
                                    "这道题是网上导入的, 没有内建用例, 请去原站提交验证。")
            # 与命令行 judge 共用同一份收尾: 画像 + 进度库一起更新
            oop_coach.record_result(problem, report, findings, profile=self.profile,
                                    store=self.store)
            oop_coach.log_event("judge", "评测 %s" % problem["id"], lines,
                                pid=problem["id"])
            self.reload_problems()

        self._run_task(work, done, "正在编译与评测…")

    # -------------------------------------------------------------- 后台任务
    def _run_task(self, fn: Callable[[], Any], on_done: Callable[[Any], None],
                  label: str) -> None:
        if not self.tasks.run(fn, on_done=on_done,
                              on_error=self._on_task_error, label=label):
            self._set_status("上一个任务还没结束, 请稍等…")
            return
        self._set_busy_buttons(False)
        self._set_status(label)

    def _poll(self) -> None:
        if self.tasks.poll():
            self._set_busy_buttons(True)
            self._set_status("就绪")
        self.root.after(POLL_MS, self._poll)

    def _set_status(self, text: str) -> None:
        self.status_task.configure(text=text)

    def _set_busy_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in self.buttons:
            button.configure(state=state)

    def _on_task_error(self, exc: BaseException) -> None:
        detail = "%s: %s" % (type(exc).__name__, exc)
        self.show_result(["任务失败", "", detail])
        self._set_status("任务失败")
        messagebox.showerror("任务失败", detail)


def main(argv=None) -> int:
    enable_dpi_awareness()
    oc.set_color_enabled(False)      # 界面上不需要 ANSI 转义, 复用 render_* 的纯文本
    # 首次运行就在旁边建好 data\ —— 兑现 README 「exe 旁边会出现 data\ 与 workspace\」
    # 的承诺; workspace\ 由 LabWindow 构造时的 ensure_workspace 负责。
    oc.ensure_dir(oc.DATA_DIR)
    oc.LOG.info("图形界面启动: 数据目录 %s", oc.BASE_DIR)
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    window = LabWindow(root)
    oc.LOG.info("窗口就绪: %d 道题, 编译器 %s", len(window.problems),
                window.toolchain.describe() if window.toolchain else "无")
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
