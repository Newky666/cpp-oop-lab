# 设计说明：OOP Lab 图形界面 + 单文件 exe

- 日期：2026-09-29
- 版本：1.0
- 前置：本设计给已有的 `cpp-oop-lab`（终端版）加一个图形界面，并打包成单文件 exe。
  **不重写任何业务逻辑**，终端版继续可用。

## 1. 目标与约束

**目标**：让完全不懂命令行的人也能练 OOP —— 双击 `OOPLab.exe`，出来一个窗口，
在里面选题、看讲义、写代码、点一下评测、看老师诊断。

**约束**：

- 继续遵守项目约定：**纯 Python 标准库，不引入任何第三方运行时依赖**；
  PyInstaller 只作为**打包期**工具（已装 6.22.3），不进运行期依赖。
- 本机环境已确认：Python 3.10.5 + tkinter 8.6（含 ttk / ScrolledText）+ PyInstaller 6.22.3。
- GUI 必须在**没有控制台**的模式下能跑（`--windowed`），且不能因此崩溃。
- 现有 97 条单元测试与 `selftest` 必须继续全绿。

**成功标准**：打包后把 `OOPLab.exe` 拷到任意空目录，双击 → 选题 → 写完代码 → F5 →
看到逐用例结果与诊断 → 关掉重开，进度还在。

**非目标（YAGNI）**：语法自动补全、多文件工程、主题换肤、内置题库编辑器、exe 自动更新。
这些都不服务于「练 OOP」这个目标。

## 2. 关键决策

| 决策点 | 选择 | 理由 |
| --- | --- | --- |
| 界面技术 | `tkinter` + `ttk` | 标准库自带，能直接打进 exe；零依赖 |
| 界面形态 | 三栏工作台 | 选题 / 看讲义 / 写代码 / 看结果 同屏，信息密度最高 |
| 代码编辑 | 内置编辑器 + 一键 VSCode | 不依赖 VSCode 也能练；但重度用户仍可切过去 |
| 后台任务 | 单线程串行 + `queue` + `after()` | 编译 2~5 秒、联网可达 10 秒，主线程做必然假死 |
| 颜色处理 | 启动时 `oc.set_color_enabled(False)` | 复用现有 `render_*` 的纯文本输出，零改动 |
| 打包形态 | `--onefile --windowed` | 拷贝方便；首次启动慢 2~4 秒可接受 |
| 数据目录 | 复用 `oc._detect_base_dir()` | frozen 时返回 exe 所在目录，已实现且有注释 |
| 与终端版关系 | 并存 | `py oop_lab.py` 一行不删；exe 只做 GUI |

## 3. 架构

```
OOPLab.exe (oop_app.py)
   └── oop_gui_app.py        主窗口：三栏布局 / 工具栏 / 状态栏 / 业务接线
         ├── oop_gui_editor.py   CodeEditor 控件：行号 / C++ 高亮 / 缩进 / Ctrl+S
         └── oop_gui_tasks.py    TaskRunner：后台线程 + queue + after() 轮询

         ↓ 全部通过现有模块（不重写）
   oop_bank / oop_skills / oop_coach / oop_judge / oop_review /
   oop_search / oop_workspace / oop_common
```

### 文件职责

| 文件 | 状态 | 职责 | 依赖 |
| --- | --- | --- | --- |
| `oop_gui_tasks.py` | 新增 | 后台任务：提交、串行执行、成功/异常回调 | 仅标准库（**与 UI 无关，可单测**） |
| `oop_gui_editor.py` | 新增 | `CodeEditor`：行号栏、高亮、自动缩进、保存 | 仅标准库 tkinter（**不依赖题库**） |
| `oop_gui_app.py` | 新增 | 组装窗口与业务；把点击翻译成模块调用 | 以上两个 + 全部业务模块 |
| `oop_app.py` | 新增 | 入口：windowed 兜底 + 启动 GUI | `oop_gui_app` |
| `build_exe.py` | 新增 | 组装 PyInstaller 参数并调用 | `oop_judge`（探测路径） |
| `build_exe.bat` | 新增 | 双击打包 | `build_exe.py` |
| `tests/test_gui.py` | 新增 | 高亮/缩进/任务队列/窗口冒烟 | `unittest` |
| `oop_coach.py` | **改** | 新增 `render_problem(problem) -> List[str]` | — |
| `oop_common.py` | **改** | `setup_logging` 在 `sys.stderr is None` 时跳过 StreamHandler | — |
| `oop_lab.py` | **改** | `stdout.reconfigure` 加 None 判断；`cmd_show` 改为调用 `oop_coach.render_problem` | `oop_coach` |

## 4. 复用清单（已核实，均有现成函数）

| 界面区域 | 复用的函数 | 返回 |
| --- | --- | --- |
| 题目树 | `oop_bank.all_problems()` / `level_counts()` / `id_order()` + `oc.ProgressStore.status()` | 数据 |
| 讲义页 | `oop_skills.teach_markdown(oop_workspace.problem_skills(p))` | markdown |
| 题面页 | **`oop_coach.render_problem(p)`（本次新增）** | `List[str]` |
| 代码页 | `oop_workspace.ensure_workspace(p)` / `student_source_path(p)` / `read_student_code(p)` | 路径/文本 |
| 评测 | `oop_judge.judge(...)` → `oop_judge.render_report(report)` | `List[str]` |
| 诊断 | `oop_coach.diagnose(...)` → `oop_coach.render_diagnosis(...)` | `List[str]` |
| 排课 | `oop_coach.plan(profile, count)` → `render_plan(result)` | `List[str]` |
| 画像 | `oop_coach.LearnerProfile().render()` | `List[str]` |
| 日志 | `oop_coach.render_log(n)` | `List[str]` |
| 写法审查 | `oop_review.review_source(code)` → `render_findings(...)` | `List[str]` |
| 找题 | `oop_search.search_all(kw)` → `render_search(result)`；`oop_search.import_problem(...)` | `List[str]` |
| 自检 | `oop_judge.doctor()` | `(ok, List[str])` |

**结论：现有模块只有「题面渲染」一处缺口**，其余零改动复用。

## 5. 界面设计

### 5.1 布局

```
┌────────────────────────────────────────────────────────────────────────────┐
│ OOP Lab — C++ 面向对象训练营                                                │
│ [教练排课][学知识点][保存][评测 F5][写法审查][学习画像][找题][打开VSCode][自检]│
├──────────────┬─────────────────────────────────────────────────────────────┤
│ ★☆☆ 基础 (0/7)│ ┌ 讲义 ── 题面 ── [我的代码] ── 评测结果 ──────────────────┐│
│  ● b01 学生类 │ │   1 │ #include <iostream>                                ││
│  ○ b02 日期类 │ │   2 │ using namespace std;                               ││
│ ★★☆ 进阶(0/8)│ │   4 │ class Student {                                    ││
│  ○ i01 Rule… │ │   5 │     // TODO                                        ││
├──────────────┴─────────────────────────────────────────────────────────────┤
│ MSVC (cl.exe) │ 当前 b01 未开始 │ 掌握度 K01 60% K05 40% │ [就绪] 0.3s      │
└────────────────────────────────────────────────────────────────────────────┘
```

- 窗口默认 1280×800，最小 960×640；左侧面板默认宽 260px（`ttk.PanedWindow`，可拖动）。
- 启动时 `ctypes.windll.shcore.SetProcessDpiAwareness(1)`，避免高 DPI 下字体发虚。
- 字体：界面 `Microsoft YaHei UI` 10，代码 `Consolas` 11。

### 5.2 题目树

- `ttk.Treeview`，两级：档位分组节点（`★☆☆ 基础 (0/7)`）+ 题目节点。
- 题目节点文本 `b01  学生类：封装与 const 成员函数`；颜色表示状态：
  ● 已通过（绿）/ ◐ 进行中（黄）/ ○ 未开始（灰）。
- 单击题目 → 加载讲义、题面、代码；首次打开自动 `ensure_workspace()` 生成工程。

### 5.3 四个选项卡

| 选项卡 | 内容 | 说明 |
| --- | --- | --- |
| 讲义 | `teach_markdown` 渲染结果 | 默认选中页（先学后练） |
| 题面 | `render_problem` 结果 | 只读 |
| 我的代码 | `CodeEditor` | 可编辑；切换题目时若有未保存修改要询问 |
| 评测结果 | `render_report` + `render_diagnosis` | 上色：行首 `[AC]` 绿、`[WA]/[CE]/[RE]` 红 |

### 5.4 工具栏行为

| 按钮 | 行为 | 线程 |
| --- | --- | --- |
| 教练排课 | `plan` → 弹窗列出 3 题，双击题目跳到该题 | 后台（可能联网） |
| 学知识点 | 弹窗列出 17 个知识点，选中看 `teach_lines` | 主线程 |
| 保存 | 写回 `main.cpp` | 主线程 |
| 评测 F5 | 保存 → `judge` → 结果页 | **后台** |
| 写法审查 | `review_source` → 结果页 | 主线程 |
| 学习画像 | `LearnerProfile().render()` | 主线程 |
| 找题 | 弹窗输入关键词 → `search_all` → 列表 + 导入按钮 | **后台** |
| 打开VSCode | `oop_workspace.open_in_vscode(workspace)` | 主线程 |
| 自检 | `oop_judge.doctor()` + 题库结构自检 | **后台** |

### 5.5 状态栏

三段：编译器标签（`Toolchain.describe()`）│ 当前题目与状态 │ 任务状态（`就绪` / `正在编译…` / 耗时）。
任务运行期间，所有**走 `TaskRunner` 的**按钮（教练排课 / 评测 / 找题 / 自检）置灰，
其余按钮（学知识点 / 保存 / 审查 / 画像 / VSCode）保持可用 —— 它们是毫秒级操作，不需要排队。

## 6. 线程模型

```python
class TaskRunner:
    def run(self, fn, on_done=None, on_error=None) -> bool   # 已有任务在跑则返回 False
```

- 内部单线程串行执行（`threading.Thread` + `queue.Queue`），刻意不做并发：
  避免同时编译两份、也避免用户连点造成状态错乱。
- 主线程用 `root.after(50, self._poll)` 轮询队列，**所有控件操作只发生在主线程**。
- 回调在 `fn` 里抛异常时走 `on_error`；界面显示错误文本而不是崩溃。
- `TaskRunner` 不引用任何控件，因此可以脱离 Tk 单测。

## 7. 打包

```
py build_exe.py            →  dist\OOPLab.exe（约 12~15 MB）
py build_exe.py --onedir   →  dist\OOPLab\（启动更快，备用）
```

PyInstaller 参数：`--onefile --windowed --name OOPLab --noconfirm --clean --log-level WARN`。
体积不是本项目的优化目标，因此**不做 `--exclude-module` 之类的裁剪**（少一层踩坑风险）。

- **不需要 `--add-data`**：题库是 `.py` 模块，PyInstaller 自动收集；
  源码里没有需要随包分发的数据文件（`data/sources.json` 首次运行自动生成）。
- exe 可放任意目录；首次运行在**exe 同级**创建 `data\` 与 `workspace\`
  （依赖已有的 `oc._detect_base_dir()` 的 `sys.frozen` 分支）。
- exe 只做 GUI。命令行用户继续 `py oop_lab.py`。

## 8. windowed 模式兜底（必须做）

`--windowed` 打包后 `sys.stdout` / `sys.stderr` 是 `None`，而现有代码里有：

- `oop_common.setup_logging()` 里 `logging.StreamHandler(sys.stderr)`；
- `oop_lab.py` 里的 `sys.stdout.reconfigure(errors="replace")`。

两者都会在启动瞬间抛异常。处理方式：

1. `oop_common.setup_logging()`：`sys.stderr is None` 时只写文件，不加 StreamHandler。
2. `oop_lab.py`：reconfigure 前判空。
3. `oop_app.py` 启动第一件事：`sys.stdout` / `sys.stderr` 为 `None` 时替换成 `io.StringIO()`，
   这样任何残留的 `print()` 都不会炸。

三处都做，任何一处单独失效都不会导致崩溃。

## 9. 测试策略

`tests/test_gui.py`（stdlib unittest）：

1. **高亮纯函数**：`highlight_spans(text)` 返回 `[(start, end, tag)]`，
   断言关键字/字符串/注释/预处理各自命中且不越界；
2. **自动缩进**：`indent_after(text, index)` 对 `{` 增 4 格、`}` 退 4 格、普通行继承缩进；
3. **TaskRunner**：成功回调、异常进 `on_error`、运行中 `run()` 返回 `False`、串行不重叠；
4. **窗口冒烟**：真建一次 `Tk`（`TclError` 时 `skipTest`），加载题库、切题、销毁；
5. **`render_problem`**：用 `oop_bank.find("b01")` 断言输出里包含题号 `b01`、标题、
   `require` 的每一条、`samples` 里的输入输出，以及 `io` 说明。

不改动、也不放宽现有 97 条测试。

## 10. 验收

1. `py -m unittest discover -s tests -t .` → 全绿（97 + 新增）。
2. `py oop_lab.py selftest` → 22 题参考解全通过。
3. `py oop_lab.py doctor` → 题库结构自检通过。
4. `py build_exe.py` 成功产出 `dist\OOPLab.exe`。
5. 手工验收：把 exe 拷到空目录 → 双击 → 选题 → 写代码 → F5 看到 AC →
   画像与进度更新 → 关闭重开进度还在 → 无控制台黑框闪现。

## 11. 风险

| 风险 | 影响 | 对策 |
| --- | --- | --- |
| windowed 下 stdout 为 None | 启动即崩 | 第 8 节三处兜底 |
| 单文件 exe 首次启动 2~4 秒 | 像卡死 | 启动即显示窗口 + 状态栏「正在准备…」 |
| tkinter 在高 DPI 下发虚 | 字糊 | `SetProcessDpiAwareness(1)` |
| PyInstaller 漏收模块 | 运行期 ImportError | 打包后**必须**手工跑一遍完整闭环（第 10 节第 5 条），不能只看「打包成功」 |
| 编译/联网阻塞界面 | 假死 | 全部走 `TaskRunner` |
