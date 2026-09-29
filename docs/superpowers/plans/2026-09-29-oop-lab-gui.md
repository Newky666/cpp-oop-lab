# OOP Lab 图形界面 + 单文件 exe 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）
> 或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 给已有的 `cpp-oop-lab` 终端工具加一个 tkinter 三栏工作台界面，并打包成一个双击即用的
`OOPLab.exe`；终端版一行不删。

**架构：** GUI 完全构建在现有模块之上，不重写业务逻辑 —— 启动时全局关闭 ANSI 颜色，
于是 `oop_judge.render_report()` / `oop_coach.render_plan()` / `oop_review.render_findings()` 等
现成的「返回行列表」函数可以被界面直接复用。只有「题面渲染」一处缺口，抽成
`oop_coach.render_problem()`。所有耗时操作（编译、联网）走 `oop_gui_tasks.TaskRunner`
在后台线程执行，主线程用 `root.after()` 轮询取结果。

**技术栈：** Python 3.10.5 + tkinter 8.6（标准库）+ PyInstaller 6.22.3（仅打包期）。
零运行时第三方依赖。

**规格：** `docs/superpowers/specs/2026-09-29-oop-lab-gui-design.md`

---

## 文件结构

| 文件 | 动作 | 职责 |
| --- | --- | --- |
| `oop_gui_tasks.py` | 创建 | `TaskRunner`：后台串行执行 + 队列回调。不引用任何控件 |
| `oop_gui_editor.py` | 创建 | `highlight_spans()` / `indent_after()` 两个纯函数 + `CodeEditor` 控件 |
| `oop_gui_app.py` | 创建 | `LabWindow`：三栏布局、工具栏、状态栏、业务接线 |
| `oop_app.py` | 创建 | 入口：stream 兜底 + 启动 GUI |
| `build_exe.py` | 创建 | 组装 PyInstaller 参数并调用 |
| `build_exe.bat` | 创建 | 双击打包 |
| `oop_app.bat` | 创建 | 双击用 GUI 启动（开发期） |
| `tests/test_gui.py` | 创建 | 本次新增的全部测试 |
| `oop_common.py` | 修改 | `setup_logging` 的 stderr 判空；新增 `STATUS_TEXT` / `status_badge()` |
| `oop_lab.py` | 修改 | stdout 判空；`_status_badge` 改用 `oc.status_badge`；`cmd_show` 改用 `oop_coach.render_problem` |
| `oop_coach.py` | 修改 | 新增 `render_problem()` |
| `README.md` | 修改 | 补第 16 节「图形界面与 exe」 |

**已核实的现有接口（实现时直接调用，不要改名）：**

```
oop_judge.judge(problem, source_path, toolchain=None, timeout=10.0, build_dir=None) -> JudgeReport
oop_judge.render_report(report, max_diff=3, show_output=False) -> List[str]
oop_judge.find_toolchain() -> Optional[Toolchain]     Toolchain.describe()
oop_judge.doctor() -> Tuple[bool, List[str]]
oop_coach.diagnose(problem, source_text="", report=None, findings=None, profile=None, width=78) -> Diagnosis
oop_coach.render_diagnosis(diag, width=78) -> List[str]
oop_coach.plan(profile=None, count=3, online=True, local_only=False) -> Dict
oop_coach.render_plan(result) -> List[str]
oop_coach.log_event(kind, title, lines, pid="", detail="")
oop_coach.LearnerProfile().render() -> List[str]
oop_review.review_source(text, problem=None) -> List[Finding]
oop_review.render_findings(findings, show_ok=True) -> List[str]
oop_workspace.ensure_workspace(problem, root=None, force=False, toolchain=None) -> Dict
oop_workspace.student_source_path(problem) -> str
oop_workspace.read_student_code(problem, root=None) -> Tuple[bool, str]
oop_workspace.open_in_vscode(path) -> bool
oop_skills.teach_markdown(skill_ids) -> str
oop_workspace.problem_skills(problem) -> List[str]
oc.ProgressStore() / .status(pid) / .mark(pid, status) / .stats()
```

**约定：** 所有命令都在 `D:\code\cpp-oop-lab` 下执行，Python 一律用 `py`。
测试命令固定为 `py -m unittest discover -s tests -t .`。

---

### 任务 0：初始化 git 仓库（可选但推荐）

**文件：** 创建 `D:\code\cpp-oop-lab\.git`（`git init`）

本目录此前没有版本控制，因此本计划每个任务末尾的 Commit 步骤都需要先做这一步。
**如果不想用 git，跳过任务 0，并跳过后续所有 Commit 步骤** —— 每个任务的
「运行测试验证通过」才是真正的验收关卡，不要因为跳过 commit 就跳过测试。

- [ ] **步骤 1：确认当前没有仓库**

运行：`git -C D:\code\cpp-oop-lab rev-parse --is-inside-work-tree`
预期：报错 `fatal: not a git repository`

- [ ] **步骤 2：初始化并首次提交**

```bash
cd /d D:\code\cpp-oop-lab
git init
git add -A
git commit -m "chore: 导入 OOP Lab 现有代码(22 题题库 + 评测 + 教练)"
```

- [ ] **步骤 3：确认忽略规则生效**

运行：`git status --short`
预期：不出现 `data/`、`workspace/`、`__pycache__/`、`oop_lab.log`

> 若 `workspace/` 被跟踪了，检查 `.gitignore` 里是否为 `workspace/*` + `!workspace/**/main.cpp`。
> 学生的 `main.cpp` 必须被跟踪，其余生成物不跟踪。

---

### 任务 1：windowed 模式兜底（必须先做）

**理由：** `--windowed` 打包后 `sys.stdout` / `sys.stderr` 是 `None`，而 `oop_lab.py:1227`
有一句 `if not sys.stdout.isatty():` —— 直接 AttributeError 崩溃。这个任务必须在
任何 GUI 代码之前完成，否则后面调试时会看到「双击 exe 闪一下就没了」。

**文件：**
- 修改：`oop_common.py:65-81`（`setup_logging`）
- 修改：`oop_lab.py:1227-1236`（stdout 判空）
- 创建：`oop_app.py`（本任务只要 `ensure_streams()` 一个函数）
- 测试：`tests/test_gui.py`

- [ ] **步骤 1：编写失败的测试**

创建 `tests/test_gui.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_gui.py - 图形界面相关的回归测试(纯逻辑部分不依赖 Tk)。"""

import io
import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import oop_app
import oop_common as oc


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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **步骤 2：运行测试验证失败**

运行：`py -m unittest tests.test_gui -v`
预期：ERROR —— `ModuleNotFoundError: No module named 'oop_app'`

- [ ] **步骤 3：创建 `oop_app.py`（最小版）**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_app.py - 图形界面入口

这个文件是打包成 OOPLab.exe 的**入口**。它只做两件事:
  1. 补上被 --windowed 抹掉的 stdout/stderr(否则任何 print 都会崩);
  2. 启动主窗口。

命令行版仍然是 oop_lab.py, 两者互不影响。
"""

from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def ensure_streams() -> None:
    """--windowed 打包后 sys.stdout / sys.stderr 是 None。

    Python 的 print() 遇到 None 会静默丢弃, 但任何 .write() / .isatty() /
    .reconfigure() 都会抛 AttributeError。这里塞一个空壳把它们救回来。
    """
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()


def main(argv=None) -> int:
    ensure_streams()
    import oop_gui_app
    return oop_gui_app.main(argv)


if __name__ == "__main__":
    sys.exit(main())
```

> 注意：这一步 `main()` 还调不通（`oop_gui_app` 尚不存在），但 `ensure_streams()`
> 已经可以被测试。**不要**在这一步顺手把 GUI 也写了。

- [ ] **步骤 4：修改 `oop_common.setup_logging`**

把 `oop_common.py:78-81`：

```python
    if verbose and not quiet:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(fmt)
        LOG.addHandler(console)
```

改为：

```python
    # --windowed 模式下 sys.stderr 是 None: 此时只能写文件, 不能加控制台 handler
    if verbose and not quiet and sys.stderr is not None:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(fmt)
        LOG.addHandler(console)
```

- [ ] **步骤 5：修改 `oop_lab.py` 的 stdout 判空**

把 `oop_lab.py:1227-1236` 整段：

```python
    if not sys.stdout.isatty():
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    else:
        try:
            sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass
```

改为：

```python
    # 打包成 --windowed 的 exe 时没有标准输出, 这里必须判空(否则启动即崩)
    if sys.stdout is not None:
        try:
            if not sys.stdout.isatty():
                sys.stdout.reconfigure(encoding="utf-8")
            else:
                sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass
```

- [ ] **步骤 6：运行测试验证通过**

运行：`py -m unittest tests.test_gui -v`
预期：2 条 PASS

- [ ] **步骤 7：确认终端版没被改坏**

运行：`py oop_lab.py doctor --no-color`
预期：正常输出环境自检（与改动前一致）

- [ ] **步骤 8：Commit**

```bash
git add oop_app.py oop_common.py oop_lab.py tests/test_gui.py
git commit -m "fix: --windowed 模式下 stdout/stderr 为 None 导致启动崩溃"
```

---

### 任务 2：抽出 `oop_coach.render_problem()`

**理由：** 题面渲染目前写死在 `oop_lab.cmd_show` 里直接 `print`。GUI 需要同一份内容，
必须抽出来，否则两边迟早不一致。

**文件：**
- 修改：`oop_coach.py`（新增 `render_problem`）
- 修改：`oop_lab.py:206-266`（`cmd_show` 改为调用它）
- 修改：`oop_common.py`（新增 `STATUS_TEXT` / `status_badge`）
- 测试：`tests/test_gui.py`

- [ ] **步骤 1：先把状态徽章下沉到 `oop_common`**

`oop_lab.py:61-79` 现在有：

```python
STATUS_TEXT = {"todo": ("未开始", "grey"), "doing": ("进行中", "yellow"),
               "passed": ("已通过", "green")}


def _status_badge(status: str) -> str:
    text, color = STATUS_TEXT.get(status, ("未知", "grey"))
    return oc.color(text, color)
```

在 `oop_common.py` 的 `LEVEL_TOPICS` 定义之后新增：

```python
STATUS_TEXT: Dict[str, Tuple[str, str]] = {
    "todo": ("未开始", "grey"),
    "doing": ("进行中", "yellow"),
    "passed": ("已通过", "green"),
}


def status_badge(status: str) -> str:
    """把进度状态渲染成带色的中文短标签(CLI 与 GUI 共用)。"""
    text, color = STATUS_TEXT.get(status, ("未知", "grey"))
    return color_text(text, color)
```

> 实现前先确认 `oop_common.py` 里给文字上色的函数到底叫什么（`color` 还是 `color_text`），
> 用真实名字。上面写的是占位签名，**必须改成实际函数名**。

然后 `oop_lab.py` 里删掉本地的 `STATUS_TEXT` 与 `_status_badge`，把所有
`_status_badge(...)` 调用改成 `oc.status_badge(...)`（先搜索确认调用点数量）。

- [ ] **步骤 2：编写失败的测试**

追加到 `tests/test_gui.py`：

```python
import oop_coach
import oop_bank


class TestRenderProblem(unittest.TestCase):
    """题面渲染抽出来给 CLI 与 GUI 共用, 两边的内容必须一致。"""

    def setUp(self):
        oc.set_color_enabled(False)
        self.problem = oop_bank.find("b01")
        self.text = "\n".join(oop_coach.render_problem(self.problem))

    def test_contains_identity_and_meta(self):
        self.assertIn("B01", self.text)
        self.assertIn(self.problem["title"], self.text)
        self.assertIn("自动用例", self.text)

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
        self.assertTrue(all(isinstance(row, str) for row in lines))
```

- [ ] **步骤 3：运行测试验证失败**

运行：`py -m unittest tests.test_gui.TestRenderProblem -v`
预期：ERROR —— `AttributeError: module 'oop_coach' has no attribute 'render_problem'`

- [ ] **步骤 4：实现 `render_problem`**

在 `oop_coach.py` 里 `render_plan` 之后新增（内容就是 `cmd_show` 的渲染体，
逐行搬过来，只把 `print(...)` 换成 `lines.append(...)`）：

```python
def render_problem(problem: Dict[str, Any], status: str = "",
                   width: int = 78) -> List[str]:
    """把题面渲染成行列表 —— CLI 的 show 与 GUI 的题面页共用这一份。

    status 为空时自动读进度库, 这样调用方不用自己查状态。
    """
    if not status:
        try:
            status = oc.ProgressStore().status(problem["id"])
        except Exception:
            status = "todo"
    level = int(problem.get("level", 1))
    lines: List[str] = []
    lines.append(oc.color("%s  %s" % (problem["id"].upper(), problem["title"]), "bold"))
    lines.append("难度 %s %s   状态 %s   自动用例 %d 组" % (
        oc.LEVEL_STARS.get(level, ""), oc.LEVEL_NAMES.get(level, ""),
        oc.status_badge(status), len(problem.get("tests", []))))
    if problem.get("topics"):
        lines.append("知识点 %s" % " / ".join(problem.get("topics", [])))
    lines.append(oc.hr("-", width))
    for row in oc.wrap_text(problem.get("desc", ""), width):
        lines.append(row)
    lines.append("")
    if problem.get("require"):
        lines.append(oc.color("具体要求", "cyan"))
        for index, item in enumerate(problem["require"], start=1):
            lines.extend(oc.wrap_text("%d. %s" % (index, item), width,
                                      subsequent_indent="   "))
        lines.append("")
    if problem.get("io"):
        lines.append(oc.color("输入输出", "cyan"))
        lines.extend(oc.wrap_text(problem["io"], width))
        lines.append("")
    for index, sample in enumerate((problem.get("samples") or [])[:3], start=1):
        lines.append(oc.color("样例 %d" % index, "cyan"))
        lines.append("  输入:")
        for row in (sample.get("in") or "(无输入)").rstrip("\n").splitlines():
            lines.append("    " + row)
        lines.append("  输出:")
        for row in (sample.get("out") or "").rstrip("\n").splitlines():
            lines.append("    " + row)
        lines.append("")
    if problem.get("hints"):
        lines.append(oc.color("提示", "cyan"))
        for item in problem["hints"]:
            lines.extend(oc.wrap_text("· " + item, width, subsequent_indent="  "))
        lines.append("")
    if problem.get("checklist"):
        lines.append(oc.color("完成前自查(OOP 要点)", "cyan"))
        for item in problem["checklist"]:
            lines.extend(oc.wrap_text("[ ] " + item, width, subsequent_indent="    "))
        lines.append("")
    return lines
```

- [ ] **步骤 5：让 `cmd_show` 改用新函数**

`oop_lab.py:206-266` 的 `cmd_show` 整体替换为：

```python
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
```

- [ ] **步骤 6：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestRenderProblem -v`
预期：5 条 PASS

- [ ] **步骤 7：确认 `show` 命令输出没变**

运行：`py oop_lab.py show b01 --no-color > before.txt`（改动前先存一份对比更稳）
预期：内容与改动前逐行一致（题面 + 你的代码/还没开工 那一行）

- [ ] **步骤 8：跑全量回归**

运行：`py -m unittest discover -s tests -t .`
预期：97 条原有 + 7 条新增，全绿

- [ ] **步骤 9：Commit**

```bash
git add oop_coach.py oop_common.py oop_lab.py tests/test_gui.py
git commit -m "refactor: 抽出 oop_coach.render_problem, CLI 与 GUI 共用题面渲染"
```

---

### 任务 3：`oop_gui_tasks.TaskRunner`

**文件：**
- 创建：`oop_gui_tasks.py`
- 测试：`tests/test_gui.py`

- [ ] **步骤 1：编写失败的测试**

追加到 `tests/test_gui.py`：

```python
import threading
import time

import oop_gui_tasks


class TestTaskRunner(unittest.TestCase):
    """后台任务执行器: 纯逻辑, 不依赖 Tk。"""

    def _drain(self, runner, timeout=3.0):
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
        runner.run(lambda: gate.wait(2.0), on_done=lambda v: None)
        self.assertFalse(runner.run(lambda: 1, on_done=lambda v: None))
        gate.set()
        self.assertTrue(self._drain(runner))
        self.assertTrue(runner.run(lambda: 1, on_done=lambda v: None))
        self.assertTrue(self._drain(runner))

    def test_tasks_run_serially(self):
        runner = oop_gui_tasks.TaskRunner()
        trace = []
        runner.run(lambda: trace.append("a1") or trace.append("a2"),
                   on_done=lambda v: None)
        self._drain(runner)
        runner.run(lambda: trace.append("b1"), on_done=lambda v: None)
        self._drain(runner)
        self.assertEqual(trace, ["a1", "a2", "b1"])

    def test_poll_returns_false_when_idle(self):
        runner = oop_gui_tasks.TaskRunner()
        self.assertFalse(runner.poll())

    def test_exception_without_handler_is_recorded_not_raised(self):
        runner = oop_gui_tasks.TaskRunner()

        def boom():
            raise RuntimeError("没有回调")

        runner.run(boom)
        self.assertTrue(self._drain(runner))          # 关键: poll 不抛异常
        self.assertIsInstance(runner.last_error, RuntimeError)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`py -m unittest tests.test_gui.TestTaskRunner -v`
预期：ERROR —— `ModuleNotFoundError: No module named 'oop_gui_tasks'`

- [ ] **步骤 3：实现 `oop_gui_tasks.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_tasks.py - 后台任务执行器

界面的一条铁律: 编译(2~5 秒)、联网找题(可达 10 秒)、自检(几十秒)绝不能跑在
Tk 主线程里, 否则窗口会变成"未响应"。

这个模块只做三件事: 提交任务 / 在后台线程里执行 / 把结果投进队列等主线程来取。
它**不引用任何控件**, 所以能脱离 Tk 单独做单元测试。
"""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable, Optional, Tuple

import oop_common as oc

Callback = Optional[Callable[[Any], None]]


class TaskRunner:
    """串行后台任务: 同一时刻只跑一个, 结果由主线程 poll() 取走。

    刻意不做并发 —— 避免同时编译两份, 也避免用户连点把状态搞乱。
    """

    def __init__(self) -> None:
        self._queue: "queue.Queue[Tuple[bool, Any, Callback]]" = queue.Queue()
        self._busy = False
        self._label = ""
        self.last_error: Optional[BaseException] = None

    # ---- 状态 ---------------------------------------------------------
    @property
    def busy(self) -> bool:
        return self._busy

    @property
    def label(self) -> str:
        return self._label

    # ---- 提交 ---------------------------------------------------------
    def run(self, fn: Callable[[], Any], on_done: Callback = None,
            on_error: Callback = None, label: str = "") -> bool:
        """提交任务。已有任务在跑时**拒绝**并返回 False(不排队)。"""
        if self._busy:
            return False
        self._busy = True
        self._label = label or getattr(fn, "__name__", "task")
        self.last_error = None

        def worker() -> None:
            try:
                value = fn()
            except BaseException as exc:      # 必须捕获一切, 否则异常会让线程静默死掉
                self._queue.put((False, exc, on_error))
            else:
                self._queue.put((True, value, on_done))

        threading.Thread(target=worker, name="oop-gui-task", daemon=True).start()
        return True

    # ---- 主线程侧轮询 -------------------------------------------------
    def poll(self) -> bool:
        """在主线程里调用(配合 root.after): 取走一个已完成任务并触发回调。

        返回 True 表示这次处理了一个任务 —— 界面据此刷新状态栏。
        没有任务时返回 False, 永不阻塞。
        """
        try:
            ok, value, callback = self._queue.get_nowait()
        except queue.Empty:
            return False
        self._busy = False
        self._label = ""
        if ok:
            if callback is not None:
                callback(value)
        elif callback is not None:
            callback(value)
        else:
            self.last_error = value
            oc.LOG.warning("后台任务失败: %s", value)
        return True
```

- [ ] **步骤 4：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestTaskRunner -v`
预期：6 条 PASS

- [ ] **步骤 5：Commit**

```bash
git add oop_gui_tasks.py tests/test_gui.py
git commit -m "feat: 新增 TaskRunner 后台任务执行器(编写中遇到的坑: 异常必须捕获否则线程静默死)"
```

---

### 任务 4：`oop_gui_editor` 的两个纯函数

**文件：**
- 创建：`oop_gui_editor.py`（本任务只放常量与两个纯函数）
- 测试：`tests/test_gui.py`

- [ ] **步骤 1：编写失败的测试**

```python
import oop_gui_editor as ge


class TestHighlightSpans(unittest.TestCase):
    def _tags(self, code):
        return {tag for _, _, tag in ge.highlight_spans(code)}

    def test_keywords_types_numbers(self):
        tags = self._tags("int x = 42;\nreturn x;\n")
        self.assertIn("type", tags)        # int
        self.assertIn("keyword", tags)     # return
        self.assertIn("number", tags)      # 42

    def test_comment_and_string_and_preproc(self):
        code = '#include <string>\n// 注释里有 int\nconst char* s = "int 42";\n'
        spans = ge.highlight_spans(code)
        tags = {tag for _, _, tag in spans}
        self.assertIn("preproc", tags)
        self.assertIn("comment", tags)
        self.assertIn("string", tags)
        # 字符串与注释里的 int 不能被当成类型高亮
        text = code
        for start, end, tag in spans:
            if tag in ("string", "comment"):
                self.assertNotEqual(text[start:end].strip(), "int")

    def test_block_comment_spans_multiple_lines(self):
        spans = ge.highlight_spans("/* a\nb */\nint x;\n")
        comments = [text for text in spans if text[2] == "comment"]
        self.assertEqual(len(comments), 1)
        self.assertIn("b", "/* a\nb */"[comments[0][0]:comments[0][1]])

    def test_spans_sorted_and_in_range(self):
        code = "#include <iostream>\nint main() { return 0; }   // 完\n"
        spans = ge.highlight_spans(code)
        self.assertTrue(spans)
        last = 0
        for start, end, _ in spans:
            self.assertGreaterEqual(start, last)
            self.assertLessEqual(end, len(code))
            last = start

    def test_empty_source(self):
        self.assertEqual(ge.highlight_spans(""), [])


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

    def test_closing_brace_wins_over_plain(self):
        # "} else {" 这种行: 先退一级, 再因为结尾是 { 而进一级 -> 净不变
        self.assertEqual(ge.indent_after("    } else {"), "    ")
```

> 最后一条是**行为规定**：`} else {` 的净缩进不变。实现必须让这条测试通过。

- [ ] **步骤 2：运行测试验证失败**

运行：`py -m unittest tests.test_gui.TestHighlightSpans tests.test_gui.TestIndentAfter -v`
预期：ERROR —— `ModuleNotFoundError: No module named 'oop_gui_editor'`

- [ ] **步骤 3：实现两个纯函数**

创建 `oop_gui_editor.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_editor.py - 代码编辑控件

分两层:
  * 纯函数 highlight_spans() / indent_after() —— 不碰 Tk, 可以单测;
  * CodeEditor 控件 —— 行号栏 + 高亮 + 自动缩进 + Ctrl+S。

把"算什么要变色"和"怎么画到界面上"分开, 是为了让前者可测:
Tk 控件在无显示器环境里根本建不起来。
"""

from __future__ import annotations

import re
from typing import List, Tuple

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

# 顺序很重要: 注释、字符串、预处理指令必须排在关键字前面,
# 否则 "// 这是 int" 里的 int 会被当成类型高亮。
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

    tag: comment / string / preproc / number / keyword / type
    """
    spans: List[Tuple[int, int, str]] = []
    for match in _TOKEN_RE.finditer(text):
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
    """回车换行时, 新行应该用多少缩进(由**上一行**决定)。

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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestHighlightSpans tests.test_gui.TestIndentAfter -v`
预期：9 条 PASS

- [ ] **步骤 5：Commit**

```bash
git add oop_gui_editor.py tests/test_gui.py
git commit -m "feat: 代码高亮与自动缩进的纯函数(可单测, 不依赖 Tk)"
```

---

### 任务 5：`CodeEditor` 控件

**文件：**
- 修改：`oop_gui_editor.py`（追加 `CodeEditor` 类）
- 测试：`tests/test_gui.py`（冒烟，无 Tk 时跳过）

- [ ] **步骤 1：编写冒烟测试**

```python
import unittest


def tk_available():
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        return False


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

    def test_gutter_line_numbers_match_line_count(self):
        editor = ge.CodeEditor(self.root)
        editor.set_text("a\nb\nc\n")
        editor.refresh_gutter()
        self.assertEqual(editor.gutter_line_count(), 4)   # 末尾空行也给行号
```

- [ ] **步骤 2：运行测试验证失败**

运行：`py -m unittest tests.test_gui.TestCodeEditorSmoke -v`
预期：ERROR —— `AttributeError: module 'oop_gui_editor' has no attribute 'CodeEditor'`

- [ ] **步骤 3：实现 `CodeEditor`**

追加到 `oop_gui_editor.py`：

```python
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

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

    行号栏是一个独立的、禁用的 Text 控件, 与主 Text 行高一致, 靠 yview 同步滚动。
    高亮用 after() 做了防抖(120ms), 否则每敲一个字符就全量重新着色会很卡。
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

        yscroll = tk.Scrollbar(self, orient="vertical", command=self._on_scroll)
        self.text.configure(yscrollcommand=self._on_yscroll)

        self.gutter.pack(side="left", fill="y")
        yscroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for tag, color in _TAG_COLORS.items():
            self.text.tag_configure(tag, foreground=color)

        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<Control-s>", self._on_ctrl_s)

    # ---- 滚动同步 ------------------------------------------------------
    def _on_scroll(self, *args) -> None:
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_yscroll(self, first, last) -> None:
        self.gutter.yview_moveto(first)

    # ---- 文本 ----------------------------------------------------------
    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, content: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
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
        lines = "\n".join(str(i) for i in range(1, total + 1))
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", lines)
        self.gutter.configure(state="disabled")

    def gutter_line_count(self) -> int:
        return int(self.gutter.index("end-1c").split(".")[0])

    # ---- 高亮 ----------------------------------------------------------
    def apply_highlight(self) -> None:
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

    def _on_modified(self, event) -> None:
        self.text.edit_modified(False)

    def _on_tab(self, event):
        self.text.insert("insert", INDENT)
        return "break"

    def _on_return(self, event):
        line = self.text.get("insert linestart", "insert")
        self.text.insert("insert", "\n" + indent_after(line))
        return "break"

    def _on_ctrl_s(self, event):
        if self.on_save is not None:
            self.on_save()
        self.dirty = False
        return "break"
```

- [ ] **步骤 4：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestCodeEditorSmoke -v`
预期：3 条 PASS（会短暂弹出一个隐藏窗口）

- [ ] **步骤 5：Commit**

```bash
git add oop_gui_editor.py tests/test_gui.py
git commit -m "feat: CodeEditor 控件(行号栏 + C++ 高亮 + 自动缩进 + Ctrl+S)"
```

---

### 任务 6：`oop_gui_app` 主窗口骨架

**文件：**
- 创建：`oop_gui_app.py`
- 测试：`tests/test_gui.py`（冒烟）

- [ ] **步骤 1：编写冒烟测试**

```python
class TestWindowSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not tk_available():
            raise unittest.SkipTest("本机没有可用的显示环境")
        os.environ["OOP_LAB_NO_OPEN"] = "1"      # 冒烟测试绝不真的去开编辑器

    def setUp(self):
        import tkinter
        self.root = tkinter.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_window_builds_and_lists_problems(self):
        window = oop_gui_app.LabWindow(self.root)
        self.assertGreater(window.tree_item_count(), 22)     # 分组节点 + 22 题
        self.assertIsNotNone(window.problem)                # 自动选中第一题

    def test_switching_problem_loads_all_three_panes(self):
        window = oop_gui_app.LabWindow(self.root)
        window.select_problem("i08")
        self.assertEqual(window.problem["id"], "i08")
        self.assertIn("i08", window.code_editor.get_text()
                      or window.problem["id"])              # 已生成骨架
        self.assertIn("组合", window.knowledge_text())
        self.assertIn("has-a", window.statement_text())

    def test_status_bar_reports_toolchain_or_hint(self):
        window = oop_gui_app.LabWindow(self.root)
        self.assertTrue(window.status_toolchain_text())
```

> `knowledge_text()` / `statement_text()` / `status_toolchain_text()` 是这三个
> 只读文本框的取内容方法，**实现时必须提供**（测试依赖它们）。

- [ ] **步骤 2：运行测试验证失败**

运行：`py -m unittest tests.test_gui.TestWindowSmoke -v`
预期：ERROR —— `ModuleNotFoundError: No module named 'oop_gui_app'`

- [ ] **步骤 3：实现 `oop_gui_app.py`**

要点（完整代码按此结构写，文件名 `oop_gui_app.py`）：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_app.py - 图形界面主窗口

三栏工作台: 左边题目树, 中间 讲义/题面/我的代码/评测结果 四个选项卡, 上下是工具栏与状态栏。
所有耗时操作走 TaskRunner; 所有业务逻辑都调现有模块, 这个文件只负责"摆放与接线"。
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


def enable_dpi_awareness() -> None:
    """高 DPI 屏上不设这个, 字体和控件会发虚。"""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class LabWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.tasks = oop_gui_tasks.TaskRunner()
        self.store = oc.ProgressStore()
        self.problem: Optional[Dict[str, Any]] = None
        self.problems: List[Dict[str, Any]] = []
        self.toolchain = oop_judge.find_toolchain()
        self.profile = oop_coach.LearnerProfile()   # 画像只读一次, 评测后不必重建

        root.title("OOP Lab — C++ 面向对象训练营")
        root.geometry("1280x800")
        root.minsize(960, 640)
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self.reload_problems()
        self._poll()

    # ---- 构建 ---------------------------------------------------------
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
                self.buttons.append(button)   # 只有走 TaskRunner 的按钮需要置灰
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
        self.status_chain = ttk.Label(bar, text="编译器: 检测中…")
        self.status_problem = ttk.Label(bar, text="当前: —")
        self.status_task = ttk.Label(bar, text="就绪")
        self.status_chain.pack(side="left")
        ttk.Label(bar, text=" │ ").pack(side="left")
        self.status_problem.pack(side="left")
        self.status_task.pack(side="right")

    # ---- 数据 ---------------------------------------------------------
    def reload_problems(self) -> None:
        """重建题目树, 并保持当前选中项(如果有的话)。"""
        self.problems = oop_bank.all_problems()
        keep = self.problem["id"] if self.problem else ""
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
                self.tree.insert(node, "end", iid=problem["id"], text="%s %s  %s" % (
                    glyph, problem["id"], problem["title"]), tags=(tag,))
        self.select_problem(keep or (self.problems[0]["id"] if self.problems else ""))

    def select_problem(self, pid: str, ask_save: bool = True) -> None:
        """切换当前题目: 先处理未保存的修改, 再加载讲义/题面/代码。"""
        if not pid or pid.startswith("level"):
            return
        if ask_save and self.problem is not None and self.code_editor.dirty:
            if not messagebox.askyesno("还没保存", "当前代码有未保存的修改, 要保存吗?"):
                return
            self.act_save()
        problem = oop_bank.find(pid)
        if problem is None:
            return
        self.problem = problem
        if ask_save and os.environ.get("OOP_LAB_NO_OPEN") != "1":
            oop_workspace.ensure_workspace(problem, toolchain=self.toolchain)
        self._set_readonly(self.statement_view,
                           "\n".join(oop_coach.render_problem(problem)))
        self._set_readonly(self.knowledge_view, oop_skills.teach_markdown(
            oop_workspace.problem_skills(problem)))
        exists, source = oop_workspace.read_student_code(problem)
        self.code_editor.set_text(source if exists else problem["skeleton"])
        self._set_readonly(self.result_view, "")
        self.tabs.select(0)
        status = self.store.status(problem["id"])
        if self.tree.exists(problem["id"]):
            self.tree.selection_set(problem["id"])
            self.tree.see(problem["id"])
        self.status_problem.configure(text="当前: %s %s   掌握度: %s" % (
            problem["id"].upper(),
            oc.STATUS_TEXT.get(status, ("未知", ""))[0],
            self._mastery_brief(problem)))

    def _on_tree_select(self, event=None) -> None:
        selection = self.tree.selection()
        if selection:
            self.select_problem(selection[0])

    def _mastery_brief(self, problem: Dict[str, Any]) -> str:
        """状态栏里显示这道题相关知识点的最低掌握度。"""
        profile = oop_coach.LearnerProfile()
        scores = [profile.mastery(sid)
                  for sid in oop_workspace.problem_skills(problem)]
        if not scores:
            return "—"
        return "最低 %.0f%%" % (min(scores) * 100)

    def tree_item_count(self) -> int:
        return sum(len(self.tree.get_children(node))
                   for node in self.tree.get_children(""))

    # ---- 只读文本框的读写 ---------------------------------------------
    @staticmethod
    def _set_readonly(widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
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
        """把结果写进评测结果页, 并把 [AC]/[WA] 之类染上色。"""
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
        self.tabs.select(3)

    # ---- 动作 ---------------------------------------------------------
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
        findings = oop_review.review_source(self.code_editor.get_text(), problem=problem)
        lines = oop_review.render_findings(findings, show_ok=True)
        self.show_result(lines)
        self._set_status("写法审查: %d 条提示" % len(findings))

    def act_profile(self) -> None:
        self.show_result(oop_coach.LearnerProfile().render())
        self._set_status("学习画像已刷新")

    def act_vscode(self) -> None:
        if oop_workspace.open_in_vscode(oc.WORKSPACE_DIR):
            self._set_status("已用 VSCode 打开工作区")
        else:
            messagebox.showinfo("手动打开", "没找到 VSCode, 请手动打开:\n%s" % oc.WORKSPACE_DIR)

    def _chooser(self, title: str, narrative: List[str],
                 rows: List[Tuple[str, Any]], on_pick: Callable[[Any], None]) -> None:
        """通用选择弹窗: 上面是说明文字, 下面是可双击的候选行。"""
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
            for name in result.get("order", []):          # order = 已启用的来源名
                for item in result.get(name) or []:
                    pid = item.get("pid") or item.get("title") or ""
                    rows.append(("%-10s %-10s %-34s %s" % (
                        name, pid, (item.get("title") or "")[:34],
                        item.get("difficulty") or ""), (name, pid)))
            self._chooser("搜到的题目(双击一行导入)", oop_search.render_search(result),
                          rows, lambda payload: self._import_from_search(*payload))

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
            self.store.mark(problem["id"], "passed" if report.all_passed else "doing")
            oop_coach.log_event("judge", "评测 %s" % problem["id"], lines,
                                pid=problem["id"])
            self.reload_problems()

        self._run_task(work, done, "正在编译与评测…")

    def _set_status(self, text: str) -> None:
        self.status_task.configure(text=text)

    def _set_busy_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in self.buttons:
            button.configure(state=state)

    def _on_task_error(self, exc: BaseException) -> None:
        self.show_result(["任务失败", "", "%s: %s" % (type(exc).__name__, exc)])
        messagebox.showerror("任务失败", "%s: %s" % (type(exc).__name__, exc))

    # ---- 后台任务 -----------------------------------------------------
    def _run_task(self, fn: Callable[[], Any], on_done: Callable[[Any], None],
                  label: str) -> None:
        if not self.tasks.run(fn, on_done=on_done,
                              on_error=lambda exc: self._on_task_error(exc),
                              label=label):
            self._set_status("上一个任务还没结束, 请稍等…")
            return
        self._set_busy_buttons(False)
        self._set_status(label)

    def _poll(self) -> None:
        if self.tasks.poll():
            self._set_busy_buttons(True)
            self._set_status("就绪")
        self.root.after(POLL_MS, self._poll)


def main(argv=None) -> int:
    enable_dpi_awareness()
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    LabWindow(root)
    root.mainloop()
    return 0
```

**关于 `act_judge`：** 真实实现已经完整写在上面类的 `act_judge` 里（不需要另外再写一遍）。
两点容易踩的地方先说明：

- `oop_judge.judge` 的第 2 个参数是 **源码路径**，不是题目 dict；
- 判定全过用 `report.all_passed`，**不要**写 `report.passed == report.total`
  （`total` 为 0 时两者不等价，导入题会误判）。

- [ ] **步骤 4：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestWindowSmoke -v`
预期：3 条 PASS

- [ ] **步骤 5：手工看一眼窗口**

运行：`py -c "import oop_app; oop_app.main()"`
预期：出现三栏窗口；点左边的题会切换讲义/题面；关掉窗口程序退出

- [ ] **步骤 6：Commit**

```bash
git add oop_gui_app.py tests/test_gui.py
git commit -m "feat: 三栏工作台主窗口(题目树 + 四选项卡 + 工具栏 + 状态栏)"
```

---

### 任务 7：九个动作的完整接线

**文件：**
- 修改：`oop_gui_app.py`
- 测试：`tests/test_gui.py`

- [ ] **步骤 1：核对九个动作都已按任务 6 的代码落地**

九个动作的完整代码已经在任务 6 里给出，这一步只是逐条核对，**不要重写**：

| 动作 | 是否走 TaskRunner | 关键调用 | 落点 |
| --- | --- | --- | --- |
| `act_plan` | ✅ | `oop_coach.plan(self.profile, count=3)` + `render_plan`，弹窗双击跳题 | 任务 6 |
| `act_judge` | ✅ | `oop_judge.judge(problem, source, toolchain=chain)` | 任务 6 |
| `act_search` | ✅ | `oop_search.search_all(keyword)` + `render_search` | 任务 6 |
| `act_doctor` | ✅ | `oop_judge.doctor()` + `oop_bank.validate_all()` | 任务 6 |
| `act_study` | ❌ | 弹窗列 `oop_skills.SKILLS`，选中调 `teach_lines(sid)` | 任务 6 |
| `act_review` | ❌ | `oop_review.review_source` + `render_findings` | 任务 6 |
| `act_profile` | ❌ | `self.profile.render()` | 任务 6 |
| `act_save` | ❌ | 写回 `main.cpp` | 任务 6 |
| `act_vscode` | ❌ | `oop_workspace.open_in_vscode(oc.WORKSPACE_DIR)` | 任务 6 |

核对方式：`py -c "import oop_gui_app as g; print([m for m in dir(g.LabWindow) if m.startswith('act_')])"`
预期：打印出上述 9 个方法名。

- [ ] **步骤 2：编写测试**

```python
import shutil
import tempfile


class TestActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not tk_available():
            raise unittest.SkipTest("本机没有可用的显示环境")

    def setUp(self):
        import tkinter
        import oop_workspace
        # 关键: 把练习目录改到临时目录, 绝不能让测试覆盖用户正在写的 main.cpp
        self.tmp = tempfile.mkdtemp(prefix="oop-gui-")
        self._old_workspace = oc.WORKSPACE_DIR
        oc.WORKSPACE_DIR = os.path.join(self.tmp, "workspace")
        os.environ["OOP_LAB_NO_OPEN"] = "1"
        self.workspace = oop_workspace
        self.root = tkinter.Tk()
        self.root.withdraw()
        self.window = oop_gui_app.LabWindow(self.root)

    def tearDown(self):
        oc.WORKSPACE_DIR = self._old_workspace
        self.root.destroy()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_writes_student_file(self):
        self.window.select_problem("b01")
        self.window.code_editor.set_text("// 我写的\nint main() { return 0; }\n")
        self.window.act_save()
        ok, text = self.workspace.read_student_code(self.window.problem)
        self.assertTrue(ok)
        self.assertIn("我写的", text)

    def test_review_shows_result_pane(self):
        self.window.select_problem("b01")
        self.window.code_editor.set_text("int main() { return 0; }")
        self.window.act_review()
        self.assertTrue(self.window.result_text().strip())

    def test_profile_is_text(self):
        self.window.act_profile()
        self.assertIn("%", self.window.result_text())

    def test_window_does_not_touch_real_workspace(self):
        """测试跑完后, 真的 workspace 目录不应该被动过。"""
        self.assertNotEqual(oc.WORKSPACE_DIR, self._old_workspace)
        self.assertFalse(os.path.exists(os.path.join(self._old_workspace, "b01-student-class")))
```

> `oc.WORKSPACE_DIR` 是模块级全局量，`oop_common.resolve_problem_dir` 与
> `oop_judge` / `oop_lab` 都是在**调用时**读它，所以直接改这个变量就能把整条链路
> 重定向到临时目录，不需要改任何业务代码。

- [ ] **步骤 3：运行测试验证通过**

运行：`py -m unittest tests.test_gui.TestActions -v`
预期：4 条 PASS

- [ ] **步骤 4：手工验证评测闭环**

1. 运行 `py -c "import oop_app; oop_app.main()"`
2. 选 `b01`，把 `main.cpp` 内容替换为 `oop_bank.find("b01")["solution"]`
3. 按 F5
4. 预期：结果页出现 `[AC] 通过` × 用例数；左树里 b01 变成绿色 ●

- [ ] **步骤 5：Commit**

```bash
git add oop_gui_app.py tests/test_gui.py
git commit -m "feat: 九个工具栏动作接线(排课/学/评测/审查/画像/找题/自检/VSCode/保存)"
```

---

### 任务 8：入口与启动器

**文件：**
- 修改：`oop_app.py`（`main()` 接上 GUI）
- 创建：`oop_app.bat`

- [ ] **步骤 1：补 `oop_app.main()` 的错误兜底**

```python
def main(argv=None) -> int:
    ensure_streams()
    try:
        import oop_gui_app
        return oop_gui_app.main(argv)
    except Exception:
        # 窗口都起不来时, 至少把栈写进日志并弹一个消息框, 而不是静默消失
        import logging
        import traceback
        logging.getLogger("cpp-oop-lab").exception("图形界面启动失败")
        detail = traceback.format_exc()
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, "图形界面启动失败:\n\n" + detail[-1200:], "OOP Lab", 0x10)
        except Exception:
            pass
        return 1
```

- [ ] **步骤 2：创建 `oop_app.bat`**

```bat
@echo off
rem 开发期用: 双击即用图形界面(打包后请用 dist\OOPLab.exe)
setlocal
cd /d "%~dp0"
start "" pythonw "%~dp0oop_app.py"
```

> 写完用 `oop_workspace.write_bat()` 生成，保证 ASCII + CRLF（项目约定）。

- [ ] **步骤 3：验证**

运行：双击 `oop_app.bat`
预期：出现窗口，且**没有**黑框控制台窗口

- [ ] **步骤 4：Commit**

```bash
git add oop_app.py oop_app.bat
git commit -m "feat: GUI 入口与开发期启动器(启动失败时弹框而非静默退出)"
```

---

### 任务 9：打包成单文件 exe

**文件：**
- 创建：`build_exe.py`
- 创建：`build_exe.bat`
- 修改：`.gitignore`（忽略 `build/`、`dist/`、`*.spec`）

- [ ] **步骤 1：实现 `build_exe.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_exe.py - 用 PyInstaller 把 GUI 打包成单文件 exe"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

APP_NAME = "OOPLab"
HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    onedir = "--onedir" in argv
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--log-level", "WARN",
        "--onedir" if onedir else "--onefile",
        "--windowed",
        "--name", APP_NAME,
        os.path.join(HERE, "oop_app.py"),
    ]
    print("正在打包: %s" % " ".join(args[2:]))
    code = subprocess.call(args, cwd=HERE)
    if code != 0:
        print("打包失败(退出码 %d)" % code)
        return code
    target = (os.path.join(HERE, "dist", APP_NAME)
              if onedir else os.path.join(HERE, "dist", APP_NAME + ".exe"))
    if not os.path.exists(target):
        print("打包命令成功但找不到产物: %s" % target)
        return 1
    size = os.path.getsize(target) / 1024.0 / 1024.0 if os.path.isfile(target) else 0
    print("产物: %s%s" % (target, ("  (%.1f MB)" % size) if size else ""))
    print("把 exe 拷到任意目录双击即可; data/ 与 workspace/ 会生成在 exe 旁边。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **步骤 2：创建 `build_exe.bat`（同样走 `write_bat` 生成）**

```bat
@echo off
setlocal
cd /d "%~dp0"
py build_exe.py %*
pause
```

- [ ] **步骤 3：确保打包产物不进 git**

在 `.gitignore` 追加：

```
build/
dist/
*.spec
```

- [ ] **步骤 4：打包**

运行：`py build_exe.py`
预期：结束时打印 `产物: ...\dist\OOPLab.exe  (十几 MB)`

- [ ] **步骤 5：真机验收（这一步不能省）**

1. 新建空目录 `D:\OOPLab试`, 把 `dist\OOPLab.exe` 拷进去
2. 双击
3. 预期：**不出现黑框控制台**；窗口出现后左侧有 22 道题
4. 选 `b01` → 写入参考解 → F5 → 看到 `[AC] 通过`
5. 关掉窗口 → 检查 `D:\OOPLab试\` 下出现了 `data\` 与 `workspace\`
6. 重新双击 → 预期 b01 显示为已通过（进度持久化生效）
7. 点「打开VSCode」→ 预期真的打开工作区

- [ ] **步骤 6：确认终端版仍然可用**

运行：`py oop_lab.py selftest --no-color`
预期：`全部 22 题的参考解都能通过各自的用例。题库是干净的。`

- [ ] **步骤 7：Commit**

```bash
git add build_exe.py build_exe.bat .gitignore
git commit -m "build: 一条命令打包单文件 OOPLab.exe"
```

---

### 任务 10：文档与收尾

**文件：**
- 修改：`README.md`
- 修改：`tests/test_gui.py`（补一条「打包参数正确」的测试）

- [ ] **步骤 1：补一条打包参数测试**

```python
class TestBuildScript(unittest.TestCase):
    def test_arguments_target_gui_entry(self):
        args = oop_app._build_pyinstaller_args(onedir=False)
        self.assertIn("--onefile", args)
        self.assertIn("--windowed", args)
        self.assertTrue(any(a.endswith("oop_app.py") for a in args))
        self.assertNotIn("oop_lab.py", " ".join(args))
```

> 为此把 `build_exe.py` 里拼参数的那段抽成 `_build_pyinstaller_args(onedir)`，
> 由 `main()` 调用。**不要**在测试里去真的执行 PyInstaller。

- [ ] **步骤 2：运行测试**

运行：`py -m unittest discover -s tests -t .`
预期：全绿（新增约 30 条）

- [ ] **步骤 3：README 补一节**

在「已知限制」之前插入 `## 16. 图形界面与 exe`，内容包含：

- 一句话说明：不想碰命令行就双击 `OOPLab.exe`；
- 三栏布局的截图（用文字框图，与 spec 第 5.1 节一致）；
- 与终端版的关系：`OOPLab.exe` 只做 GUI，命令行仍是 `py oop_lab.py`；
- 从源码打包：`py build_exe.py`；
- 数据落在 exe 旁边（`data\` / `workspace\`）；
- 快捷键：F5 评测、Ctrl+S 保存；
- 已知：首次启动 2~4 秒（单文件解压），杀软可能误报。

同时把目录结构那一段补上 5 个新文件。

- [ ] **步骤 4：全量验收**

```bash
py -m unittest discover -s tests -t .
py oop_lab.py selftest --no-color
py oop_lab.py doctor --no-color
```

预期：测试全绿；`全部 22 题的参考解都能通过各自的用例`；`[OK] 22 题结构自检通过`

- [ ] **步骤 5：Commit**

```bash
git add README.md build_exe.py tests/test_gui.py
git commit -m "docs: 补充图形界面与 exe 打包说明"
```

---

## 自检记录

**1. 规格覆盖度**

| 规格章节 | 对应任务 |
| --- | --- |
| §2 关键决策（tkinter/三栏/内置编辑器/串行后台/关色/onefile） | 任务 3、5、6、9 |
| §3 架构与文件职责 | 任务 0-10 的文件表 |
| §4 复用清单（唯一缺口 render_problem） | 任务 2 |
| §5 界面设计（树/四页/工具栏/状态栏） | 任务 6、7 |
| §6 线程模型 | 任务 3 |
| §7 打包 | 任务 9 |
| §8 windowed 兜底（三处） | 任务 1（`oop_app.ensure_streams` + `setup_logging` + `oop_lab`） |
| §9 测试策略（5 项） | 任务 1、2、3、4、5、6、7、10 |
| §10 验收 | 任务 9 步骤 5、任务 10 步骤 4 |
| §11 风险 | 任务 1（崩溃）、6（DPI）、9（漏收模块）、3（假死） |

**2. 占位符扫描**：无「待定 / TODO / 后续实现」，也没有 `def xxx(): ...` 这类方法桩 ——
初稿里任务 6 的构建方法、`select_problem`、以及 `act_plan/act_study/act_search/act_doctor`
一共 11 个方法曾经是 `...`，第二轮已全部替换成可直接粘贴的真实代码。

**3. 类型一致性**：全文统一使用**实际运行验证过**的签名与字段名 ——

| 用途 | 真实签名 / 字段 | 易错点 |
| --- | --- | --- |
| 评测 | `oop_judge.judge(problem, source_path, toolchain=)` | 第 2 个参数是**路径**不是 dict |
| 判定全过 | `JudgeReport.all_passed` | 不能写 `passed == total`（total=0 时不等价） |
| 诊断 | `oop_coach.diagnose(problem, source_text=, report=, findings=, profile=)` | — |
| 排课 | `oop_coach.plan(profile, count=)` → `{profile_level, target_level, assignments, notes}` | 题目在 `item.problem`，类别在 `item.kind` |
| 搜题 | `oop_search.search_all(keyword)` → `{keyword, links, errors, order, <来源名>: [...]}` | 来源名要从 `order` 里取，不能写死 `luogu` |
| 导入 | `oop_search.import_problem(target, source=)` → `(problem, error)` | 返回二元组，要判 None |
| 源码 | `oop_workspace.read_student_code(problem)` → `(ok, text)` | 也返回二元组 |
| 知识面 | `oop_workspace.problem_skills(problem)` → `List[str]` | — |

控件方法名 `set_text/get_text/show_result/knowledge_text/statement_text/result_text/
tree_item_count/status_toolchain_text` 在任务 5、6、7、10 中保持同名。

**4. 测试隔离**：任务 7 的 `TestActions` 会真的写文件，因此明确用
`oc.WORKSPACE_DIR` 重定向到 `tempfile.mkdtemp()` 并断言「真实 workspace 未被触碰」——
这是防止测试覆盖用户代码的那道闸门，不能省。
