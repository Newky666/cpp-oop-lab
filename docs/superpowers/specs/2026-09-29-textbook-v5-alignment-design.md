# 设计说明：对齐《Visual C++面向对象与可视化程序设计（第5版）》

- 日期：2026-09-29
- 参考教材：黄维通、童军博《Visual C++面向对象与可视化程序设计（第5版）》
  （高等教育出版社，ISBN 9787040646832，324 页，环境为 Visual Studio 2022）
- 前置：在既有 `cpp-oop-lab`（22 题 + 控制台评测 + GUI/exe）之上扩展，**不推翻现有架构**。

## 1. 用户诉求 → 设计目标

| 诉求 | 落地 |
| --- | --- |
| 检查所有功能确保正常 | 全量回归（unittest/selftest/doctor/GUI/CLI 全命令 + exe 验收） |
| 给程序设计图标 | 生成图标 → 多尺寸 ICO（stdlib 打包）→ PyInstaller `--icon` + 窗口 `iconphoto` |
| 题目对齐第 5 版（考试用书） | 新增 16 个 MFC 知识点（K18~K33）+ 新档位「可视化」+ 19 道 `v` 题 |
| 在 VSCode 写码 + 程序纠错指导 | 沿用统一工作区 + `judge`/`diagnose`/`review`；新题同样生成工程 |
| 题目联网更新 | 沿用 `search`/`pull`（6 个来源）；新增「教材章节关键词包」便于按章搜题 |
| 头文件不省略 | skeleton/solution 一律完整 `#include` + `using namespace std;`（现有 22 题已达标，加测试守住） |

## 2. 教材目录 → 知识点映射

第 5 版共三部分 8 章：

| 章 | 内容 | 知识点（新增/复用） |
| --- | --- | --- |
| 1 MFC 基础知识 | MFC 概述；C++ 类/对象、嵌套类、内联、构造析构、动态内存、重载、友元、类指针、继承、多态虚函数 | 复用 K01~K12、K17（现有 22 题已覆盖）；补 3 道细节题 `v01~v03`（嵌套类/内联/类指针） |
| 2 基于对话框绘图 | Windows 编程基础、GDI、句柄、刷新、获取 DC、映像模式、画笔/画刷/颜色、CDC、CPaintDC | **K18** Windows 编程基础与句柄 · **K19** 设备环境与 GDI 绘图 · **K20** 映像模式与坐标变换 |
| 3 字体及其应用 | 字体句柄、设置字体/背景色、文本输出过程 | **K21** 字体与文本输出（CFont/TextOut/DrawText） |
| 4 键盘与鼠标响应 | 键盘消息、鼠标消息 | **K22** 键盘消息 · **K23** 鼠标消息 |
| 5 资源应用 | 菜单/加速键、位图、对话框（模态/非模态）、图标 | **K24** 菜单与加速键 · **K25** 对话框资源 · **K26** 位图与图标资源 |
| 6 控件 | 按钮、滚动条、静态、编辑框、列表框、组合框、通用控件 | **K27** 基础控件（按钮/静态/编辑框） · **K28** 列表类控件（列表框/组合框） · **K29** 滚动条与通用控件 |
| 7 文档与资源 | 文档/视图、SDI/MDI、CView、串行化、菜单消息、快捷菜单、工具条、字符串资源 | **K30** 文档视图与串行化 · **K31** 菜单消息响应与快捷菜单/工具条 |
| 8 多媒体 | 音频函数、MCI、WMP 控件 | **K32** 多媒体程序设计 |
| — | 贯穿第 2~8 章的消息映射机制 | **K33** 消息映射与 MFC 程序骨架 |

新知识点编号 K18~K33（16 个），level=4；新档位 `4 = 可视化 · MFC`（`LEVEL_NAMES/LEVEL_STARS` 扩到 4 档）。

## 3. 题目与编号

- 新前缀 `v`（visual）：`v01~v19`，全部 `level=4`。
- 覆盖：第 1 章补细节 3 题；第 2~8 章每章 2~3 题。
- 每题仍遵循现有约定：`knowledge.md` 讲义 + 题面 + 完整骨架（含全部头文件）+ 参考解 + 自查清单。
- 第 1 章的 3 题是**控制台题**（本机可全自动评测，沿用现有 `tests` 机制）；
  第 2~8 章是**窗口程序题**（MFC），评测方式见第 4 节。

## 4. 评测设计（关键决策）

### 4.1 题目 schema 扩展（`_p()` 新字段，全部可选）

```python
framework="console"        # console(默认) | mfc   —— 决定编译参数与评测方式
subsystem="windows"        # windows | console     —— MFC 窗口程序用 windows
defines=[...]              # 追加 /D 宏，如 ["_AFXDLL", "UNICODE", "_UNICODE"]
libs=[...]                 # 追加链接库，如 ["user32.lib", "gdi32.lib"]
checks=[                   # 静态检查规则（正则），GUI 题的主要评分依据
    {"pattern": r"\bBEGIN_MESSAGE_MAP\b", "hint": "必须用 BEGIN_MESSAGE_MAP/END_MESSAGE_MAP 宏对"},
    ...
]
```

- `framework="mfc"` 的题把编译参数交给 `oop_judge`：`/D_AFXDLL /MD /D_WINDOWS` +
  `/link /SUBSYSTEM:WINDOWS|CONSOLE`（MFC 头文件自带 `#pragma comment(lib, ...)`，无需手写 lib）。
- `checks` 的正则对**学生源码**逐条匹配；缺失的条目不通过。

### 4.2 三种评测路径（按环境自动选择）

| 场景 | judge 行为 | 判定依据 |
| --- | --- | --- |
| console 题 + 有编译器 | 现状 | 逐用例比对（`tests`） |
| mfc 题 + 已装 MFC | 真编译（+ 链接） | 编译链接通过 = 通过；失败 = CE + 诊断 |
| mfc 题 + 未装 MFC | 跳过编译，跑 `checks` | checks 全过 = 「静态检查通过（未真编译）」并提示安装 MFC |

`doctor` 新增 MFC 检测：找不到 `afxwin.h/mfc*.lib` 时给出 VS Installer 组件名
「适用于最新 v143 生成工具的 C++ MFC (x86 和 x64)」的安装指引。

### 4.3 MFC 题的评测呈现

- `tests` 为空 + `framework="mfc"` → 结果页显示「编译验证型题目」而非「没有自动用例」。
- 进度记 `passed` 的条件：编译通过（或静态检查全过）且 checks 全过。
- 参考解同样接受 `selftest` 真编译（装了 MFC 后即可全量验证）。

## 5. 图标设计

1. 用图像生成 1024×1024 PNG（主题：C++/训练营/图形界面，深色底 + 高对比主图形）。
2. stdlib 转 ICO：`tkinter.PhotoImage` 读 PNG → `subsample` 得 256/128/64/48(缩放近似)/32/16
   → 各尺寸导出 PNG → 按「PNG-in-ICO」格式（ICONDIR + 条目 + PNG 数据）拼成多尺寸 `.ico`。
3. 接入：
   - `oop_lab.ico`（项目根）→ `build_exe.py` 加 `--icon`（绝对路径，PyInstaller 要求）。
   - 窗口图标：把 64×64 PNG 的 base64 内嵌进 `oop_gui_app.py`，`root.iconphoto(True, PhotoImage(data=...))`
     —— 不依赖外部文件，exe 单文件也能显示。
4. 验收：exe 属性页里能看到图标；运行窗口左上角有图标。

## 6. 联网找题（沿用 + 小增强）

- 现有 `search/pull`（洛谷/dotcpp/CF/GitHub/必应/任意站点）不动。
- 新增 `oop_search.CHAPTER_KEYWORDS`：教材章节 → 搜题关键词包（如第 2 章 → 「MFC 绘图」「CDC」「画刷」），
  `py oop_lab.py search --chapter 2` 直接按章搜。讲义页提示该章建议搜索词。

## 7. 分批交付

| 批次 | 内容 |
| --- | --- |
| 1（本次） | 图标全套；schema 扩展（framework/subsystem/defines/libs/checks）；judge 三路径；doctor MFC 检测；level 4「可视化」；`v01~v03`（第 1 章细节，可自动评测）；K18/K19/K33 知识点与 `v04~v06`（第 2 章绘图） |
| 2 | 第 3~4 章（K20/K21/K22/K23 + v07~v10） |
| 3 | 第 5~6 章（K24~K29 + v11~v15） |
| 4 | 第 7~8 章（K30/K31/K32 + v16~v19）；章节关键词搜索；README/讲义收尾 |

## 8. 验收标准

1. `py -m unittest discover -s tests -t .` 全绿（现有 157 条 + 新增）。
2. `py oop_lab.py doctor` 显示 MFC 状态（含安装指引）。
3. `py oop_lab.py selftest` 对 console 题仍全过；MFC 题在未装 MFC 时明确标注「跳过（未装 MFC）」。
4. `dist\OOPLab.exe` 带图标；窗口左上角有图标。
5. 现有 22 题的 skeleton/solution 头文件完整性由测试守住。
6. 每个新知识点有讲义；每题有完整骨架（不省略任何 include）与参考解。
