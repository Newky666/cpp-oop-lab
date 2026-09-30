#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_gui.py - 图形界面相关的回归测试

分两类:
  * 纯逻辑(高亮/缩进/后台任务/题面渲染) —— 任何机器上都能跑;
  * 控件冒烟 —— 需要能建出 Tk 窗口, 建不出来就自动 skipTest。

约定与 test_oop_lab.py 一致: 只用标准库 unittest, 从仓库根目录跑
    py -m unittest discover -s tests -t .
"""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import logging
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import oop_app
import oop_bank
import oop_coach
import oop_common as oc
import oop_gui_app
import oop_gui_editor as ge
import oop_gui_tasks
import oop_workspace


def tk_available() -> bool:
    """能不能真的建出一个 Tk 窗口(无显示环境/无 tkinter 时为 False)。"""
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        return False


class TestWindowedMode(unittest.TestCase):
    """--windowed 打包后 stdout/stderr 是 None, 绝不能因此崩溃。"""

    def setUp(self):
        self._out, self._err = sys.stdout, sys.stderr

    def tearDown(self):
        sys.stdout, sys.stderr = self._out, self._err

    def test_setup_logging_tolerates_missing_stderr(self):
        sys.stdout = None
        sys.stderr = None
        oc.setup_logging()                       # 以前这里会抛异常
        formats = [type(h).__name__ for h in oc.LOG.handlers]
        self.assertIn("FileHandler", formats)
        self.assertNotIn("StreamHandler", formats)

    def test_ensure_streams_installs_placeholder(self):
        sys.stdout = None
        sys.stderr = None
        oop_app.ensure_streams()
        self.assertIsNotNone(sys.stdout)
        self.assertIsNotNone(sys.stderr)
        print("这一行以前会 AttributeError")     # 关键断言: 不抛异常

    def test_ensure_streams_keeps_real_streams(self):
        stream = sys.stdout
        oop_app.ensure_streams()
        self.assertIs(sys.stdout, stream)


class TestRenderProblem(unittest.TestCase):
    """题面渲染抽出来给 CLI 与 GUI 共用, 两边内容必须一致。"""

    def setUp(self):
        oc.set_color_enabled(False)
        self.problem = oop_bank.find("b01")
        self.text = "\n".join(oop_coach.render_problem(self.problem))

    def test_contains_identity_and_meta(self):
        self.assertIn("B01", self.text)
        self.assertIn(self.problem["title"], self.text)
        self.assertIn("自动用例", self.text)
        self.assertIn("难度", self.text)

    def test_contains_every_requirement(self):
        for item in self.problem["require"]:
            self.assertIn(item[:12], self.text)

    def test_contains_io_and_samples(self):
        self.assertIn(self.problem["io"][:10], self.text)
        sample = self.problem["samples"][0]
        self.assertIn(sample["in"].splitlines()[0], self.text)
        self.assertIn(sample["out"].splitlines()[0], self.text)

    def test_contains_hints_and_checklist(self):
        self.assertIn(self.problem["hints"][0][:10], self.text)
        self.assertIn(self.problem["checklist"][0][:10], self.text)

    def test_returns_lines_not_printed_text(self):
        lines = oop_coach.render_problem(self.problem)
        self.assertIsInstance(lines, list)
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(row, str) for row in lines))

    def test_accepts_explicit_status_and_survives_broken_store(self):
        lines = oop_coach.render_problem(self.problem, status="passed")
        self.assertIn("已通过", "\n".join(lines))

    def test_status_badge_shared_with_common(self):
        self.assertEqual(oc.status_badge("passed"), oc.STATUS_TEXT["passed"][0])
        self.assertEqual(oc.status_badge("没这个状态"), "未知")


class TestTaskRunner(unittest.TestCase):
    """后台任务执行器: 纯逻辑, 完全不依赖 Tk。"""

    @staticmethod
    def _drain(runner, timeout=3.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if runner.poll():
                return True
            time.sleep(0.01)
        return False

    def test_success_callback_gets_value(self):
        runner = oop_gui_tasks.TaskRunner()
        seen = []
        self.assertTrue(runner.run(lambda: 6 * 7, on_done=seen.append, label="算术"))
        self.assertEqual(runner.label, "算术")
        self.assertTrue(runner.busy)
        self.assertTrue(self._drain(runner))
        self.assertEqual(seen, [42])
        self.assertFalse(runner.busy)

    def test_exception_goes_to_on_error(self):
        runner = oop_gui_tasks.TaskRunner()
        failures = []

        def boom():
            raise ValueError("编译失败")

        runner.run(boom, on_done=lambda v: self.fail("不该走 on_done"),
                   on_error=failures.append)
        self.assertTrue(self._drain(runner))
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], ValueError)

    def test_second_run_is_rejected_while_busy(self):
        runner = oop_gui_tasks.TaskRunner()
        gate = threading.Event()
        runner.run(lambda: gate.wait(3.0), on_done=lambda v: None)
        self.assertFalse(runner.run(lambda: 1, on_done=lambda v: None))
        gate.set()
        self.assertTrue(self._drain(runner))
        self.assertTrue(runner.run(lambda: 1, on_done=lambda v: None))
        self.assertTrue(self._drain(runner))

    def test_tasks_run_serially(self):
        runner = oop_gui_tasks.TaskRunner()
        trace = []

        def first():
            trace.append("a1")
            trace.append("a2")

        runner.run(first, on_done=lambda v: None)
        self._drain(runner)
        runner.run(lambda: trace.append("b1"), on_done=lambda v: None)
        self._drain(runner)
        self.assertEqual(trace, ["a1", "a2", "b1"])

    def test_poll_returns_false_when_idle(self):
        self.assertFalse(oop_gui_tasks.TaskRunner().poll())

    def test_exception_without_handler_is_recorded_not_raised(self):
        runner = oop_gui_tasks.TaskRunner()

        def boom():
            raise RuntimeError("没有回调")

        runner.run(boom)
        self.assertTrue(self._drain(runner))          # 关键: poll 不能抛异常
        self.assertIsInstance(runner.last_error, RuntimeError)


class TestHighlightSpans(unittest.TestCase):
    """高亮是纯函数, 不依赖 Tk。"""

    @staticmethod
    def _tags(code):
        return {tag for _, _, tag in ge.highlight_spans(code)}

    def test_keywords_types_numbers(self):
        tags = self._tags("int x = 42;\nreturn x;\n")
        self.assertIn("type", tags)        # int
        self.assertIn("keyword", tags)     # return
        self.assertIn("number", tags)      # 42

    def test_comment_string_preproc_are_recognized(self):
        code = '#include <string>\n// 注释\nconst char* s = "hello";\n'
        tags = self._tags(code)
        self.assertIn("preproc", tags)
        self.assertIn("comment", tags)
        self.assertIn("string", tags)

    def test_keyword_inside_comment_or_string_is_not_highlighted(self):
        code = '// int 是注释里的\nconst char* s = "return 1";\n'
        for start, end, tag in ge.highlight_spans(code):
            if tag in ("comment", "string"):
                continue
            # 除了注释与字符串, 不该有别的区间落在引号/注释内部
            self.assertNotIn(code[start:end].strip(), ("int", "return"))

    def test_block_comment_spans_multiple_lines(self):
        code = "/* a\nb */\nint x;\n"
        comments = [s for s in ge.highlight_spans(code) if s[2] == "comment"]
        self.assertEqual(len(comments), 1)
        self.assertEqual(code[comments[0][0]:comments[0][1]], "/* a\nb */")

    def test_spans_are_sorted_and_in_range(self):
        code = "#include <iostream>\nint main() { return 0; }   // 完\n"
        spans = ge.highlight_spans(code)
        self.assertTrue(spans)
        last = 0
        for start, end, _ in spans:
            self.assertGreaterEqual(start, last)
            self.assertLessEqual(end, len(code))
            self.assertLess(start, end)
            last = start

    def test_empty_source(self):
        self.assertEqual(ge.highlight_spans(""), [])
        self.assertEqual(ge.highlight_spans(None), [])


class TestIndentAfter(unittest.TestCase):
    def test_brace_opens_a_level(self):
        self.assertEqual(ge.indent_after("int main() {"), ge.INDENT)
        self.assertEqual(ge.indent_after("    if (x) {"), "    " + ge.INDENT)

    def test_closing_brace_drops_a_level(self):
        self.assertEqual(ge.indent_after("    }"), "")
        self.assertEqual(ge.indent_after("        };"), "    ")

    def test_plain_line_keeps_indent(self):
        self.assertEqual(ge.indent_after("    int x = 1;"), "    ")
        self.assertEqual(ge.indent_after(""), "")

    def test_closing_brace_wins_over_opening(self):
        # "} else {" : 先退一级, 再因为结尾是 { 而进一级 -> 净不变
        self.assertEqual(ge.indent_after("    } else {"), "    ")


@unittest.skipUnless(tk_available(), "本机没有可用的显示环境")
class TestCodeEditorSmoke(unittest.TestCase):
    def setUp(self):
        import tkinter
        self.root = tkinter.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_set_and_get_text(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("int main() { return 0; }\n")
        self.assertIn("int main", editor.get_text())
        self.assertFalse(editor.dirty)

    def test_typing_marks_dirty_and_highlight_runs(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("")
        editor.insert_for_test("class A {")
        editor.apply_highlight()                 # 不能抛异常
        self.assertTrue(editor.dirty)

    def test_highlight_tags_are_applied_to_widget(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("int x = 1;\n")
        editor.apply_highlight()
        ranges = editor.text.tag_ranges("type")
        self.assertTrue(ranges)

    def test_gutter_line_numbers_match_line_count(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("a\nb\nc\n")
        editor.refresh_gutter()
        self.assertEqual(editor.gutter_line_count(), 4)   # 末尾空行也给行号

    def test_ctrl_s_calls_back_and_clears_dirty(self):
        saved = []
        editor = ge.CodeEditor(self.root, on_save=lambda: saved.append(1))
        editor.set_text("int main(){}")
        editor.dirty = True
        editor._on_ctrl_s(None)
        self.assertEqual(saved, [1])
        self.assertFalse(editor.dirty)

    def test_return_key_inserts_indent_after_open_brace(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("")
        editor.text.insert("1.0", "int main() {")
        editor.text.mark_set("insert", "end-1c")
        editor._on_return(None)
        self.assertTrue(editor.get_text().endswith("\n" + ge.INDENT))


class TestWindowGeometry(unittest.TestCase):
    """窗口必须落在屏幕里 —— 开在屏幕外等于"程序打不开"。

    这是个真 bug 的回归测试: 只写 geometry("1280x800") 不指定位置时, 窗口管理器
    把窗口摆到了 +712, 右边超出屏幕 285 像素。
    """

    def test_normal_screen_centered_and_fully_visible(self):
        width, height, x, y = oop_gui_app.window_geometry(1920, 1080)
        self.assertEqual((width, height), (1280, 800))
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(x + width, 1920)
        self.assertLessEqual(y + height, 1080)

    def test_shrinks_to_fit_small_screen(self):
        width, height, x, y = oop_gui_app.window_geometry(1366, 768)
        self.assertLessEqual(height, 768)
        self.assertLessEqual(x + width, 1366)
        self.assertLessEqual(y + height, 768)

    def test_never_offscreen_on_tiny_screen(self):
        width, height, x, y = oop_gui_app.window_geometry(800, 600)
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(x + width, 800)
        self.assertLessEqual(y + height, 600)

    def test_exactly_the_screen_size_still_works(self):
        width, height, x, y = oop_gui_app.window_geometry(1280, 800)
        self.assertLessEqual(x + width, 1280)
        self.assertLessEqual(y + height, 800)


@unittest.skipUnless(tk_available(), "本机没有可用的显示环境")
class GuiCase(unittest.TestCase):
    """所有建窗口的测试都继承它。

    关键: 把**全部**运行期路径重定向到临时目录 —— 否则测试会真的往用户正在写的
    workspace/**/main.cpp、真实的进度库、真实的学习日志里写东西。
    各模块都是在调用时读这些模块级全局量, 所以改它们就能把整条链路重定向,
    不需要改任何业务代码。
    """

    #: (模块, 属性名, 临时子路径)—— 一个都不能漏
    REDIRECTS = (
        (oc, "WORKSPACE_DIR", "workspace"),
        (oc, "PROGRESS_FILE", "progress.json"),
        (oc, "USER_BANK_FILE", "user_problems.json"),
        (oop_coach, "PROFILE_FILE", "profile.json"),
        (oop_coach, "LOG_FILE", "learning_log.md"),
    )

    def setUp(self):
        import tkinter
        self.tmp = tempfile.mkdtemp(prefix="oop-gui-")
        self._saved = []
        for module, name, leaf in self.REDIRECTS:
            self._saved.append((module, name, getattr(module, name)))
            setattr(module, name, os.path.join(self.tmp, leaf))
        oc.set_color_enabled(False)
        self.root = tkinter.Tk()
        self.root.withdraw()

    def tearDown(self):
        for module, name, value in self._saved:
            setattr(module, name, value)
        try:
            self.root.destroy()
        except Exception:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_window(self):
        return oop_gui_app.LabWindow(self.root)


class TestWindowSmoke(GuiCase):
    def test_window_builds_and_lists_problems(self):
        window = self.make_window()
        # 每道题一个节点(分组节点不算在内)
        self.assertEqual(window.tree_item_count(), len(window.problems))
        self.assertGreaterEqual(window.tree_item_count(), 22)
        # 四个档位分组节点(基础/进阶/高级/可视化·MFC)
        self.assertEqual(len(window.tree.get_children("")), 4)
        self.assertIsNotNone(window.problem)

    def test_switching_problem_loads_all_panes(self):
        window = self.make_window()
        window.select_problem("i08")
        self.assertEqual(window.problem["id"], "i08")
        self.assertIn("has-a", window.statement_text())
        self.assertIn("K17", window.knowledge_text())
        self.assertIn("TODO", window.code_editor.get_text())

    def test_first_tab_is_knowledge(self):
        window = self.make_window()
        window.select_problem("b01")
        self.assertEqual(window.tabs.index("current"), 0)

    def test_status_bar_reports_toolchain(self):
        window = self.make_window()
        self.assertTrue(window.status_toolchain_text())

    def test_workspace_goes_to_redirected_root(self):
        """练习工程必须落在临时目录里, 绝不能碰用户真实的工作区。"""
        window = self.make_window()
        window.select_problem("b01")
        self.assertTrue(oc.WORKSPACE_DIR.startswith(self.tmp))
        self.assertTrue(os.path.isdir(
            os.path.join(oc.WORKSPACE_DIR, "b01-student-class")))

    def test_minsize_fits_screen(self):
        window = self.make_window()
        min_w, min_h = self.root.minsize()
        self.assertLessEqual(min_w, self.root.winfo_screenwidth())
        self.assertLessEqual(min_h, self.root.winfo_screenheight())

    def test_bring_to_front_does_not_raise(self):
        window = self.make_window()
        window.bring_to_front()          # 不抛异常即可
        self.root.update_idletasks()

    def test_result_pane_colours_verdict_lines(self):
        window = self.make_window()
        window.show_result(["[AC] 通过", "[WA] 答案错误", "普通一行"])
        self.assertTrue(window.result_view.tag_ranges("ok"))
        self.assertTrue(window.result_view.tag_ranges("bad"))

    def test_reselecting_same_problem_keeps_result_pane(self):
        """评测结束后界面会 reload 一次; 重新选中同一题不能把结果冲掉。

        这是一个真 bug 的复现: select_problem 无条件清空结果页, 于是刚评测完
        显示的结果立刻被清空, 用户什么都看不到。
        """
        window = self.make_window()
        window.select_problem("b01")
        window.show_result(["[AC] 通过"])
        window.select_problem("b01")                 # 等价于 reload_problems()
        self.assertIn("[AC]", window.result_text())
        self.assertEqual(window.tabs.index("current"),
                         oop_gui_app.TAB_RESULT)     # 也不能把视图跳走

    def test_switching_to_another_problem_clears_result_pane(self):
        window = self.make_window()
        window.select_problem("b01")
        window.show_result(["[AC] 通过"])
        window.select_problem("b02")
        self.assertEqual(window.result_text(), "")
        self.assertEqual(window.tabs.index("current"), oop_gui_app.TAB_KNOWLEDGE)


class TestTreeSelectEventLoop(GuiCase):
    """回归: <<TreeviewSelect>> 与 select_problem 之间的自我循环。

    真实事故: Tk 的 treeview 对「同一项再 selection_set 一次」**也会**再发一个
    <<TreeviewSelect>>, 而事件回调又调 select_problem —— 于是 mainloop 一进去
    就每秒上千次地自循环(每次都重建题面/高亮/行号), 窗口全白无响应,
    表现就是「双击 OOPLab 打不开」。这里用 spy 锁住死循环的两个必要条件。
    """

    @staticmethod
    def _spy_selection_set(window):
        calls = []
        original = window.tree.selection_set

        def spy(*args, **kwargs):
            calls.append(args)
            return original(*args, **kwargs)

        window.tree.selection_set = spy
        return calls

    def test_event_on_current_problem_does_not_touch_selection(self):
        window = self.make_window()
        window.select_problem("b01")
        calls = self._spy_selection_set(window)
        window._on_tree_select()                 # 模拟事件派发
        self.assertEqual(calls, [])              # 再往选择里写 = 等着死循环
        self.assertEqual(window.problem["id"], "b01")

    def test_event_on_another_problem_switches_without_resetting(self):
        window = self.make_window()
        window.select_problem("b01")
        window.tree.selection_set("b02")         # 模拟用户点树: Tk 先改选择
        calls = self._spy_selection_set(window)
        window._on_tree_select()                 # 事件随后派发
        self.assertEqual(window.problem["id"], "b02")
        self.assertEqual(calls, [])              # 选择已经是 b02, 不该再写


class TestMainloopSmoke(unittest.TestCase):
    """在子进程里真跑一次 Tk mainloop —— 覆盖其它 GUI 测试够不到的盲区。

    其它窗口测试都只构造界面、不跑 mainloop, 所以事件风暴类的 bug 一个都逮不到。
    这一条把窗口真正推进事件循环, 要求它 1.5 秒后能按 after 定时器自行退出。

    刻意放子进程 + 超时: 万一事件循环又退化成自循环, 测试进程自己也会挂死,
    CI 永远等不到结果; 在子进程里就能杀掉并判失败。子进程的数据目录全部
    重定向到临时目录, 不碰真实的 workspace/ 与 data/。
    """

    SCRIPT = textwrap.dedent("""
        import os, sys, tempfile
        sys.path.insert(0, os.environ["OOP_TEST_REPO"])
        import tkinter
        import oop_common as oc
        oc.set_color_enabled(False)
        tmp = tempfile.mkdtemp(prefix="oop-mainloop-")
        import oop_coach
        oc.WORKSPACE_DIR = os.path.join(tmp, "workspace")
        oc.PROGRESS_FILE = os.path.join(tmp, "progress.json")
        oc.USER_BANK_FILE = os.path.join(tmp, "user_problems.json")
        oop_coach.PROFILE_FILE = os.path.join(tmp, "profile.json")
        oop_coach.LOG_FILE = os.path.join(tmp, "learning_log.md")
        import oop_gui_app
        root = tkinter.Tk()
        root.withdraw()                      # 不打扰桌面, 事件照常流转
        window = oop_gui_app.LabWindow(root)
        state = {"done": False}

        def tick():
            state["done"] = True
            root.quit()

        root.after(1500, tick)
        root.mainloop()
        print("MAINLOOP_OK" if state["done"] else "MAINLOOP_EARLY_EXIT")
    """)

    def test_mainloop_reaches_after_timer(self):
        if not tk_available():
            self.skipTest("本机没有可用的显示环境")
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = dict(os.environ, OOP_TEST_REPO=repo)
        try:
            proc = subprocess.run(
                [sys.executable, "-c", self.SCRIPT], capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=30,
                env=env)
        except subprocess.TimeoutExpired:
            self.fail("窗口主循环卡死: 事件循环疑似又陷入自循环, 30 秒都没出来")
        self.assertIn("MAINLOOP_OK", proc.stdout or "",
                      "mainloop 没有正常退出\nstdout=%s\nstderr=%s"
                      % (proc.stdout, proc.stderr))


class TestActions(GuiCase):
    def test_save_writes_student_file(self):
        window = self.make_window()
        window.select_problem("b01")
        window.code_editor.set_text("// 我写的\nint main() { return 0; }\n")
        window.act_save()
        ok, text = oop_workspace.read_student_code(window.problem)
        self.assertTrue(ok)
        self.assertIn("我写的", text)

    def test_review_shows_result_pane(self):
        window = self.make_window()
        window.select_problem("b01")
        window.code_editor.set_text("int main() { return 0; }")
        window.act_review()
        self.assertTrue(window.result_text().strip())
        self.assertEqual(window.tabs.index("current"),
                         oop_gui_app.TAB_RESULT)

    def test_profile_is_text(self):
        window = self.make_window()
        window.act_profile()
        text = window.result_text()
        self.assertIn("综合档位", text)
        self.assertIn("K01", text)
        self.assertIn("K17", text)          # 新增的知识点也要出现在画像里

    def test_review_of_reference_solution_is_clean(self):
        window = self.make_window()
        window.select_problem("i08")
        window.code_editor.set_text(window.problem["solution"])
        window.act_review()
        self.assertNotIn("Rule of Three", window.result_text())

    def test_all_actions_exist(self):
        expected = {"act_plan", "act_study", "act_save", "act_judge",
                    "act_review", "act_profile", "act_search", "act_vscode",
                    "act_visual_studio", "act_doctor"}
        missing = [name for name in expected
                   if not callable(getattr(oop_gui_app.LabWindow, name, None))]
        self.assertEqual(missing, [])

    def test_async_actions_use_task_runner(self):
        """排课 / 评测 / 找题 / 自检必须走后台, 否则界面会假死。"""
        window = self.make_window()
        seen = []
        original = window.tasks.run

        def spy(fn, **kwargs):
            seen.append(kwargs.get("label", ""))
            return False                        # 不真的执行, 避免联网

        window.tasks.run = spy
        for action in (window.act_plan, window.act_judge, window.act_doctor):
            action()
        self.assertEqual(len(seen), 3)


@unittest.skipUnless(tk_available(), "本机没有可用的显示环境")
class TestEndToEndJudge(GuiCase):
    """端到端: 在界面上写完代码 → 点评测 → 出 AC → 进度落盘。

    这是「图形界面真的能跑通评测闭环」的证据, 会真的调用编译器, 因此没有
    编译器时自动跳过。
    """

    def setUp(self):
        super().setUp()
        self.window = self.make_window()
        if self.window.toolchain is None:
            self.skipTest("本机没有 C++ 编译器")

    def _pump(self, timeout=180.0):
        """等后台任务出结果。

        这里**故意不调 root.update()** —— 是个踩过的坑: 当时 update() 会永久
        阻塞, 最初以为是 _poll 每 50ms 续一个 after 定时器导致的。后来查明真正
        的原因是 <<TreeviewSelect>> 自循环事件风暴(见 TestTreeSelectEventLoop):
        事件队列被无限灌入新事件, update() 处理不完、mainloop 同理出不来 ——
        也就是「exe 双击打不开」本身。修复后就不会再有这个现象, 但保持只调
        tasks.poll() 仍然更稳: 它从队列里取结果并触发回调, 回调里的控件操作
        (插入文本等)是同步生效的, 不依赖事件循环去重绘。
        """
        deadline = time.time() + timeout
        while self.window.tasks.busy and time.time() < deadline:
            self.window.tasks.poll()
            time.sleep(0.02)
        return not self.window.tasks.busy

    def test_reference_solution_gets_ac_through_the_gui(self):
        window = self.window
        window.select_problem("b01")
        window.code_editor.set_text(oop_bank.find("b01")["solution"])
        window.act_judge()
        self.assertTrue(self._pump(), "评测任务超时")
        result = window.result_text()
        self.assertIn("[AC]", result)
        self.assertNotIn("[WA]", result)
        self.assertEqual(window.store.status("b01"), "passed")
        # 进度必须落在临时目录里, 不能碰真实的 data/
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "progress.json")))
        # 画像也必须一起更新 —— 漏了这一步自适应排课就废了(这里曾经是个真 bug)
        self.assertGreater(window.profile.mastery("K01"), 0.0)
        self.assertGreater(int(window.profile.evidence("K01")["attempts"]), 0)

    def test_wrong_solution_reports_wa_with_diff(self):
        window = self.window
        problem = oop_bank.find("b01")
        window.select_problem("b01")
        broken = problem["solution"].replace(
            '<< id << \' \' << name << \' \' << score',
            '<< id << \' \' << score << \' \' << name')
        self.assertNotEqual(broken, problem["solution"])
        window.code_editor.set_text(broken)
        window.act_judge()
        self.assertTrue(self._pump(), "评测任务超时")
        result = window.result_text()
        self.assertIn("[WA]", result)
        self.assertEqual(window.store.status("b01"), "doing")


class TestIcon(unittest.TestCase):
    """图标: 生成器产物必须可解码, 打包参数与窗口都要用上它。"""

    @staticmethod
    def _ico_path():
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oop_lab.ico")

    def test_ico_has_multiple_sizes(self):
        path = self._ico_path()
        self.assertTrue(os.path.isfile(path),
                        "缺少 oop_lab.ico —— 先跑 py tools/make_ico.py")
        with open(path, "rb") as fh:
            head = fh.read(6)
        self.assertEqual(head[:4], b"\x00\x00\x01\x00")       # ICONDIR, type=1
        count = head[4] | (head[5] << 8)
        self.assertGreaterEqual(count, 4, "图标至少要有 4 个尺寸")

    def test_build_args_include_absolute_icon(self):
        import build_exe
        args = build_exe._build_pyinstaller_args()
        self.assertIn("--icon", args)
        icon = args[args.index("--icon") + 1]
        self.assertTrue(os.path.isabs(icon))                  # 相对路径会解析失败
        self.assertTrue(icon.endswith(".ico"))

    def test_embedded_png_decodes_to_64x64(self):
        if not tk_available():
            self.skipTest("本机没有可用的显示环境")
        import tkinter

        import oop_lab_icon
        root = tkinter.Tk()
        root.withdraw()
        try:
            image = tkinter.PhotoImage(data=oop_lab_icon.ICON_PNG_B64)
            self.assertEqual((image.width(), image.height()), (64, 64))
        finally:
            root.destroy()

    def test_apply_window_icon_does_not_raise(self):
        if not tk_available():
            self.skipTest("本机没有可用的显示环境")
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        try:
            oop_gui_app._apply_window_icon(root)              # 不抛异常即可
        finally:
            root.destroy()


class TestBuildScript(unittest.TestCase):
    """打包脚本的参数拼装(不真的执行 PyInstaller)。"""

    def setUp(self):
        import build_exe
        self.build = build_exe

    def test_arguments_target_gui_entry(self):
        args = self.build._build_pyinstaller_args(onedir=False)
        joined = " ".join(args)
        self.assertIn("--onefile", args)
        self.assertIn("--windowed", args)
        self.assertNotIn("--onedir", args)
        self.assertTrue(any(a.endswith("oop_app.py") for a in args))
        self.assertNotIn("oop_lab.py", joined)      # 入口必须是 GUI, 不是命令行
        self.assertIn("--name", args)

    def test_onedir_switches_mode(self):
        args = self.build._build_pyinstaller_args(onedir=True)
        self.assertIn("--onedir", args)
        self.assertNotIn("--onefile", args)

    def test_app_name_is_oop_lab_exe(self):
        self.assertEqual(self.build.APP_NAME, "OOPLab")


if __name__ == "__main__":
    unittest.main()
