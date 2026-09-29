# 实现计划：对齐教材第 5 版（批次 1）

**规格：** `docs/superpowers/specs/2026-09-29-textbook-v5-alignment-design.md`
**约定：** 命令都在 `D:\code\cpp-oop-lab` 下、Python 一律 `py`；
测试固定 `py -m unittest discover -s tests -t .`；改完必须跑测试 + `selftest`。

---

## T1 图标（PNG → 多尺寸 ICO → exe/窗口接入）

- [ ] 生成 1024×1024 图标 PNG：深色圆角底 + 「C++」主视觉（`docs/icon/oop_lab_icon.png` 存档）
- [ ] 新增 `tools/make_ico.py`（放仓库内 `tools/`）：tkinter PhotoImage 读 PNG →
      `subsample` 得 256/128/64/32/16 → 各尺寸 PNG → 拼 PNG-in-ICO 写到 `oop_lab.ico`
      （纯 stdlib：struct + 手写 ICONDIR/ICONDIRENTRY）
- [ ] `build_exe.py`：`_build_pyinstaller_args` 加 `--icon <abs>/oop_lab.ico`；
      找不到 ico 时静默跳过（不阻塞打包）
- [ ] `oop_gui_app.main()`：`root.iconphoto(True, tk.PhotoImage(data=BASE64_PNG_64))`
      并把 base64 常量放 `oop_gui_app.py` 顶部（新增 `ICON_PNG_B64`）
- [ ] 验证：`py tools/make_ico.py` 产物存在且 >5KB；`py build_exe.py` 成功；
      exe 运行后窗口左上角有图标

## T2 题库 schema 扩展（framework/subsystem/defines/libs/checks）

- [ ] `oop_bank.py::_normalize`：补默认 `framework="console"`、`subsystem=""`、
      `defines=[]`、`libs=[]`、`checks=[]`
- [ ] `oop_bank.validate`：非法 framework / checks 结构错误 报出来
- [ ] 测试：3 条（默认值、非法 framework、checks 结构）

## T3 judge 三路径（console / mfc 真编译 / mfc 静态降级）

- [ ] `oop_judge`：
  - 编译命令按题目拼参数：`framework=="mfc"` → `/D_AFXDLL /MD /D_WINDOWS` + defines +
    `/link /SUBSYSTEM:WINDOWS|CONSOLE` + libs
  - `detect_mfc()`：找 `afxwin.h`/`mfc*.lib`（vswhere 定位 + 常见目录扫）
  - `run_checks(source, checks)`：(通过数, [未通过条目]) —— 纯函数，可单测
  - `judge()`：`framework=="mfc"` 时——有 MFC → 真编译（tests 为空也判「编译通过」）；
    无 MFC → 不编译，跑 checks，报告标注「静态检查（未真编译，需安装 MFC）」
- [ ] 测试：`run_checks` 4 条（命中/缺失/正则非法容错/空规则）；编译参数拼装 2 条

## T4 doctor + 档位 4

- [ ] `oop_judge.doctor()`：MFC 段 —— `[OK] MFC 可编译教材第 2~8 章` 或
      `[!] 未安装 MFC 组件 → VS Installer → 单个组件 → 适用于最新 v143 生成工具的 C++ MFC`
- [ ] `oop_common`：`LEVEL_NAMES[4]="可视化 · MFC"`、`LEVEL_STARS[4]="◈◈◈◈"`（风格与现有一致）
- [ ] 遍历 level 的硬编码 `(1, 2, 3)` 全部改为 `sorted(LEVEL_NAMES)`：
      `oop_gui_app.reload_problems`、`oop_lab` 总览/进度条、`oop_coach` 档位相关
- [ ] 测试：level 4 出现在树/总览；doctor 不炸

## T5 知识点 K18/K19/K33 + 第 2 章题目 v04~v06

- [ ] `oop_skills.py`：新增 K18（Windows 编程基础与句柄）、K19（设备环境与 GDI 绘图）、
      K33（消息映射与 MFC 程序骨架）；讲义含要点/坑/示例/自查，示例**头文件完整**
- [ ] `oop_bank_pro.py`（或新增 `oop_bank_visual.py`）：`v04` 用 CDC 画直线/矩形/椭圆；
      `v05` 画笔/画刷/颜色（CPen/CBrush/RGB）；`v06` 消息映射骨架（OnPaint + BEGIN_MESSAGE_MAP）
      —— 每题：完整骨架、参考解、checks（关键 API 正则）、无 tests
- [ ] `oop_bank.py` 聚合新模块
- [ ] 验证：`doctor` 结构自检通过；`study v04` 有讲义；`new v04` 生成工程

## T6 第 1 章细节题 v01~v03（console，可自动评测）

- [ ] `v01` 嵌套类（教材 1.2.2）、`v02` 内联方法（1.2.3）、`v03` 类指针与 this（1.6）
- [ ] 每题完整 skeleton（全部 include）+ 参考解 + 3 组 tests
- [ ] `selftest --id v01..v03` 真编译通过

## T7 测试与文档收尾

- [ ] `tests/test_gui.py` / `test_oop_lab.py`：图标常量存在、头文件完整性守卫
      （遍历全部题：skeleton/solution 必须含 `#include` 且不裸 std::）
- [ ] README：新增「对齐教材第 5 版」一节（章节表 + MFC 安装指引 + `v` 题说明 + 图标）
- [ ] 全量验收：unittest 全绿、selftest 全过、doctor OK、exe 重打包 + 真机启动、
      `git commit`（中文规范，分主题提交）

## 验收命令汇总

```bat
py -m unittest discover -s tests -t .
py oop_lab.py doctor --no-color
py oop_lab.py selftest --no-color
py oop_lab.py study v04 --no-color
py oop_lab.py new v04
py build_exe.py
```
