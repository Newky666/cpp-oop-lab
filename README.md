# C++ 面向对象训练营 · OOP Lab

> **一条命令进菜单，一个工作区练全部题，每道题先学知识点再动手。**
>
> 40 道阶梯式内建题（含教材《Visual C++面向对象与可视化程序设计(第 5 版)》对齐的 MFC 题）+
> 洛谷/dotcpp/Codeforces/GitHub/任意网站联网找题 →
> 自适应排课 → **先读知识点讲义** → 在 **VSCode 或 Visual Studio** 里写代码 →
> 一键评测(逐行比对) → **老师式诊断(错在哪、哪个知识点没掌握、怎么补)** →
> 学习画像 + 学习日志。
>
> 纯 Python 标准库实现，零第三方依赖。

![依赖](https://img.shields.io/badge/dependencies-纯标准库-brightgreen) ![平台](https://img.shields.io/badge/platform-Windows%2010%2F11-informational) ![题库](https://img.shields.io/badge/题库-40%20题-blue) ![知识点](https://img.shields.io/badge/知识点-33%20个-orange) ![教材](https://img.shields.io/badge/教材-Visual%20C%2B%2B%20第5版%20(黄维通)-yellowgreen) ![编辑器](https://img.shields.io/badge/编辑器-VSCode%20%7C%20Visual%20Studio-success)

---

## 目录

- [1. 它解决什么问题](#1-它解决什么问题)
- [2. 快速开始](#2-快速开始)
- [3. 集中操作：一个菜单搞定](#3-集中操作一个菜单搞定)
- [4. 先学后练：每道题前面的知识点讲义](#4-先学后练每道题前面的知识点讲义)
- [5. 一个统一工作区（VSCode + Visual Studio 通用）](#5-一个统一工作区vscode--visual-studio-通用)
- [6. 老师模式：排课 → 判对错 → 讲解 → 记录](#6-老师模式排课--判对错--讲解--记录)
- [7. 题目总览（40 题 · 含教材第 5 版对齐）](#7-题目总览40-题--含教材第-5-版对齐)
- [8. 命令一览](#8-命令一览)
- [9. 自动「指正」：评测 + 写法审查 + 诊断](#9-自动指正评测--写法审查--诊断)
- [10. 学习画像与学习日志](#10-学习画像与学习日志)
- [11. 多源找题：不绑定任何网站](#11-多源找题不绑定任何网站)
- [12. 环境自检](#12-环境自检)
- [13. 文件结构](#13-文件结构)
- [14. 实现设计](#14-实现设计)
- [15. 怎么加自己的题](#15-怎么加自己的题)
- [16. 图形界面与 exe](#16-图形界面与-exe)
- [17. 已知限制](#17-已知限制)

---

## 1. 它解决什么问题

学完「类与对象」这一章，课本上的例子都看得懂，但自己一写就乱：

- 抽象不出类，一个 `main` 从头写到尾；
- 数据成员全写成 `public`，封装形同虚设；
- 写了析构函数却忘了拷贝构造，程序偶尔崩溃；
- 该用虚函数的地方用 `if-else` 判类型；
- 写完不知道对不对，也没有人能立刻指出问题；
- 换个编辑器就得重新配一遍构建和调试。

这个项目的对策：

| 痛点 | 对应机制 |
| --- | --- |
| 不知道该干嘛 | **一个菜单**：排课 / 学知识点 / 开练 / 评测 / 画像 / 找题 / 自检全在里面 |
| 不懂知识点就做题 | **先学后练**：每题自带 `knowledge.md` 讲义，题面顶部也会先指向它 |
| 环境配不起来 | **一个统一工作区**：一套配置 + `oop_lab.sln`，VSCode 与 VS 都能直接 F5 |
| 不知道练什么 | **自适应排课**：按薄弱知识点 + 难度梯度选 3 道，并给出选它的理由 |
| 题目太简单/太难 | 连赢两把加半档，连输两把退半档；相关知识点全熟练的题直接排除 |
| 不知道对不对 | `judge` 自动编译 + 跑全部用例，**逐行给出差异** |
| 不知道错在哪 | `diagnose` 把编译错误/崩溃码/用例差异翻译成**知识点 + 讲解** |
| 没人点评 | `submit` 生成一份**自带全部上下文的点评申请** |

---

## 2. 快速开始

> **不想碰命令行？** 直接跳到 [16. 图形界面与 exe](#16-图形界面与-exe)：
> 双击 `OOPLab.exe`，出来一个窗口，选题、看讲义、写代码、点评测全在里面。

**前置条件**

- Windows 10/11
- Python 3.8+（本机若 `python` 指向 Microsoft Store 占位符，请统一用 **`py`**）
- 一个 C++ 编译器（`doctor` 会告诉你现在有什么）：
  - **MSVC**：安装 Visual Studio，勾选「使用 C++ 的桌面开发」
  - **MinGW-w64**：装好并把 `g++` 加进 `PATH`
- 编辑器：VSCode（装 C/C++ 扩展）或 Visual Studio，任选

**就两条命令**

```bat
cd d:\code\cpp-oop-lab
py oop_lab.py doctor     :: 一次性检查编译器 / 编辑器 / 题库
py oop_lab.py            :: 进入交互式主菜单(所有功能都在里面)
```

不想敲命令：**双击 `oop_lab.bat`** —— 同样进菜单，退出时自动暂停。

**只想按顺序走一遍的话**

```bat
py oop_lab.py plan              :: 教练排课: 练哪几道、为什么
py oop_lab.py study b04         :: 先学: 这道题的知识点讲义
py oop_lab.py new b04           :: 生成题目目录并打开统一工作区
:: ... 在 VSCode / VS 里写 main.cpp ...
py oop_lab.py judge b04         :: 评测 + 老师式诊断 + 更新画像
py oop_lab.py submit b04        :: 生成提交包, 贴给 AI/老师点评
```

---

## 3. 集中操作：一个菜单搞定

```
========================================================================
  C++ 面向对象训练营 · OOP Lab    从类与对象到 MFC 可视化, 28 题阶梯式过关
========================================================================
  进度 3/22   [######..........]  14.3%   档位 第 1 档 · 基础   MSVC (cl.exe + vcvars64)
  练习工作区: D:\code\cpp-oop-lab\workspace
------------------------------------------------------------------------
  1)  教练安排今天的题
  2)  学知识点(先学后练)
  3)  题目列表
  4)  看某道题(题面)
  5)  开练某道题(生成工程并打开编辑器)
  6)  评测当前题(编译 + 用例 + 老师式诊断)
  7)  写法审查(12 条 OOP 规则)
  8)  我的学习画像(33 个知识点掌握度)
  9)  学习日志
  10) 联网找题 / 导入题目
  11) 只看某道题的参考解
  12) 打开 VSCode 工作区
  13) 打开 Visual Studio
  14) 环境自检
  15) 题库自检(40 题参考解真编译, MFC 题未装组件时跳过)
  0)  退出

请选择 [0-15]:
```

要点：

- 需要题目编号的菜单项**会问你要编号**，直接回车就用教练推荐的那一题；
- 每做完一步自动回到菜单，不用重新敲命令；
- 输出被重定向时（写脚本、CI）不会卡在菜单里，会自动退回总览面板 ——
  所以 `py oop_lab.py > out.txt` 依然安全。

---

## 4. 先学后练：每道题前面的知识点讲义

每道题的目录里，**排在最前面的不是代码，而是 `knowledge.md`**：

```
b01-student-class/
├── knowledge.md     ← 先读这个: 知识点的要点 / 常见坑 / 正确写法示例 / 动手前自问
├── problem.md       ← 再读这个: 题面(顶部会提醒你先看讲义)
├── main.cpp         ← 最后写这个
├── tests/01.in 01.out ...
└── b01-student-class.vcxproj
```

讲义内容来自统一的 33 个知识点图谱（17 个 C++ 面向对象 + 16 个教材第 2~8 章的 MFC/Windows 知识点），例如 `b01` 会带上：

```
## K01 类与封装    <sub>第 1 档</sub>

把“数据”和“操作数据的函数”捆成一个类型, 并把数据藏起来, 只留出必要的接口。

### 要点
1. class 默认访问级别是 private, struct 默认是 public —— 练习里优先用 class + 显式 public:。
2. 数据成员一律 private; 需要给外部看的用取值函数(getter)暴露, 而不是把成员开成 public。
...
### 常见坑
- 把数据成员写成 public, 封装直接失效;
- 给每个成员都配 getter/setter, 等于把 private 当装饰 —— 应该暴露“有意义的操作”而不是裸数据;
...
### 正确写法示例
    class Account {
    private:
        double balance_;              // 数据藏起来
    public:
        explicit Account(double init) : balance_(init) {}
        void deposit(double amount);   // 暴露“有意义的操作”
        double balance() const;        // 只读的取值函数
    };

### 动手前自问
> 这个类的数据, 外部能随便改吗? 能改的路径是不是都经过了校验?
```

不想离开终端也行：

```bat
py oop_lab.py study b04        :: 打印 b04 涉及的全部知识点讲义
py oop_lab.py study K12        :: 只看某个知识点
py oop_lab.py skills           :: 列出全部 33 个知识点
```

---

## 5. 一个统一工作区（VSCode + Visual Studio 通用）

题库只有一个工作区，所有配置都在**最外层**，每道题只是它的一个子文件夹：

```
workspace/
├── oop_lab.code-workspace        ← 想让 VSCode 双击打开就用它
├── oop_lab.sln                   ← Visual Studio 打开这个
├── build.bat / run_case.bat      ← 全题库共用(接收参数, 不写死题目)
├── .vscode/
│   ├── tasks.json               构建/运行「当前打开的文件」
│   ├── launch.json              调试「当前打开的文件」
│   ├── c_cpp_properties.json / settings.json / extensions.json
├── b01-student-class/
│   ├── knowledge.md  problem.md  main.cpp
│   ├── tests/01.in 01.out ...
│   └── b01-student-class.vcxproj
├── b04-deep-copy-array/ ...
└── i01-mystring-rule-of-three/ ...
```

### VSCode（推荐）

1. `文件 → 打开文件夹` → 选 `workspace`（**只需打开一次**，不用每题开一次）
2. 在左侧点开任意题目，编辑它的 `main.cpp`
3. `Ctrl+Shift+B` 构建 —— 编译的是**你当前打开的那个文件**，产物固定是
   `<题目目录>/build/main.exe`
4. `F5` 调试（会自动先构建，程序跑在独立控制台里，可以直接敲输入）
5. 想跑某一组用例：`终端 → 运行任务 → 运行当前题 · 用例 N`（1~4）

关键就是那句「当前打开的文件」：切题目只要切文件，构建/调试配置一个字都不用改。

### Visual Studio

1. 打开 `workspace\oop_lab.sln`
2. 在解决方案资源管理器里，把要练的那个工程右键 → **设为启动项目**
3. `F5` 调试 / `Ctrl+F5` 直接运行

生成的 `.vcxproj` 有几个刻意的设置：

| 设置 | 为什么 |
| --- | --- |
| `PlatformToolset` 按本机 MSVC 版本自动推断 | 不写会被 MSBuild 当成 VS2010 报 `MSB8020`；可用 `OOP_PLATFORM_TOOLSET` 覆盖 |
| `TargetName = main` | 产物同样是 `build\main.exe`，与 `judge`、与 VSCode 完全一致 |
| `/utf-8` | 源码里有中文注释/字符串时不会乱码 |
| `stdcpp17` + `Console` 子系统 | 与题库的编译参数对齐 |
| `Debug|x64` 与 `Release|x64` | 练题用 Debug，想跑快点切 Release |

> 每道题在 VS 里是一个独立工程，`oop_lab.sln` 每次都按工作区实际内容重新生成
> （GUID 由目录名确定性推导，不会每次都变）。

### 两边的产物与命令行完全一致

| 入口 | 产物 |
| --- | --- |
| VSCode `Ctrl+Shift+B` | `<题目目录>/build/main.exe` |
| Visual Studio `F5` | `<题目目录>/build/main.exe` |
| `build.bat <cpp>` | `<题目目录>/build/main.exe` |
| `py oop_lab.py judge b04` | `<题目目录>/build/main.exe` |

---

## 6. 老师模式：排课 → 判对错 → 讲解 → 记录

### 6.1 知识点图谱（33 个）

| 档位 | 知识点 |
| --- | --- |
| 基础 | `K01` 类与封装 · `K02` 构造函数与初始化列表 · `K03` 析构与对象生命周期 · `K04` 拷贝构造与深拷贝 · `K05` const 正确性与 this · `K06` static 成员与静态工厂 · `K07` 运算符重载 |
| 进阶 | `K08` 继承与派生 · `K09` 虚函数与运行时多态 · `K10` 抽象类与虚析构 · `K11` 友元 · `K12` 拷贝控制与 Rule of Three · `K17` 组合与聚合(has-a) |
| 高级 | `K13` 类模板与特化 · `K14` RAII 与智能指针 · `K15` 设计模式 · `K16` 多重继承与虚继承 |
| 可视化 · MFC | `K18` Windows 编程基础与消息机制 · `K19` 设备环境与 GDI 绘图 · `K20` 映像模式与坐标变换 · `K21` 字体与文本输出 · `K22` 键盘消息 · `K23` 鼠标消息 · `K24` 菜单与加速键 · `K25` 对话框与 DDX · `K26` 位图与图标 · `K27` 基础控件 · `K28` 列表框与组合框 · `K29` 滚动条与通用控件 · `K30` 文档视图与串行化 · `K31` 命令路由与快捷菜单/工具条 · `K32` 多媒体程序设计 · `K33` 消息映射与 MFC 程序骨架 |

题目的中文标签按「最长关键词命中」自动映射到知识点；从洛谷/dotcpp/CF 导入的题会从
题面和标题里猜知识点，同样能参与画像与排课。

### 6.2 自适应排课

```bat
py oop_lab.py plan
```

```
今天练这几道
------------------------------------------------------------------------------
当前档位: 第 1 档 · 基础    本次目标难度: 第 1 档

1. b04  深拷贝：带指针的数组类
   [过关题] ★☆☆ 析构与对象生命周期, 拷贝构造与深拷贝
   · 覆盖你目前的薄弱点: 析构与对象生命周期 / 拷贝构造与深拷贝
   开局: py oop_lab.py new b04

3. lg:P1109  学生分组
   [拓展题] ★☆☆ 类与封装
   · 来自 洛谷 的拓展题(没有自动评测, 需要你自己对拍验证)
```

打分：`0.45×知识点收益 + 0.25×难度贴合 + 0.20×新鲜度 + 0.10×来源可信度`。
硬规则：已通过的不再派；**相关知识点掌握度全 ≥0.8 的题直接排除**（这就是
「不出过于简单的题」的落地）；难度最多跨一档；同一知识点不连出三题；
连赢两把 +半档、连输两把 −半档。

### 6.3 判断对错

```
[RE] 运行时错误   用例 1/4  退出码 3221226356 (0xC0000374) | 堆损坏: 几乎一定是重复释放或越界写(深拷贝没写?)

老师点评 · RE
------------------------------------------------------------------------------
程序崩了 —— 这类问题几乎都和内存或边界有关。

【运行错误诊断】
按可能性从高到低排查:
  · 数组越界 / 访问空指针 —— 最容易出现在下标循环和指针成员上。
  · 对象被重复释放(double free) —— 通常是深拷贝没写, 两个对象共享一块内存。
  · 除零、模零。
  · 递归太深导致栈溢出。
```

三种输入都会被翻译成「知识点 + 为什么 + 怎么改」：

| 输入 | 怎么用 |
| --- | --- |
| 编译器报错 | 正则匹配到知识点（覆盖 GCC / clang / MSVC 的中英文报错），逐条解释 |
| 运行期失败 | 把 Windows 崩溃码翻译成人话（`0xC0000374` 堆损坏 / `0xC0000005` 访问冲突 / `0xC00000FD` 栈溢出 …）并给出排查顺序 |
| 用例差异 | 逐行贴出「期望 vs 实际」，并按「一组都没过 / 部分没过 / 全过」给不同的清单 |

### 6.4 记录

详见 [第 10 节](#10-学习画像与学习日志)。

---

## 7. 题目总览（40 题 · 含教材第 5 版对齐）

> **教材对齐**: 第 4 档 `v01~v18` 对齐黄维通、童军博
> 《Visual C++面向对象与可视化程序设计（第 5 版）》（高教社）**第 1~8 章全覆盖**：
> `v01~v03` 第 1 章 C++ 细节（控制台题，可自动评测）；
> `v04~v14` 第 2~6 章（GDI 绘图 / 画笔画刷 / 映像模式 / 字体文本 / 鼠标键盘 /
> 菜单 / 对话框 / 位图 / 按钮编辑框 / 列表框 / 进度条）；
> `v15~v18` 第 7~8 章（文档视图串行化 / 快捷菜单 / 工具条状态栏 / 多媒体）。
> MFC 题需要 VS 的 MFC 组件（见 [12. 环境自检](#12-环境自检)），未安装时评测自动降级为
> 「要点检查」（检查是否用对了 CDC / CPen / 消息映射等关键写法），装好后即可真编译。

### 第 1 档 · 基础 ★☆☆ —— 一个类从无到有

| 编号 | 题目 | 考察点 |
| --- | --- | --- |
| `b01` | 学生类：封装与 const 成员函数 | 类的定义 / 访问控制 / 构造函数 / `const` 成员函数 |
| `b02` | 日期类：构造函数初始化列表与闰年判定 | 初始化列表 / 成员函数封装 / 逻辑封装 |
| `b03` | 生命周期三部曲：构造 / 拷贝构造 / 析构 | 对象生命周期（类定义填空题） |
| `b04` | 深拷贝：带指针的数组类 | 拷贝构造 / 深拷贝 / `new[]` 与 `delete[]` |
| `b05` | const 成员函数与值语义：Point | `const` 正确性 / `this` / 值返回 |
| `b06` | static 成员：发票流水号工厂 | `static` 数据成员 / 静态工厂 / 拷贝陷阱 |
| `b07` | 运算符重载入门：复数类 Complex | `operator+ - == << >>` / 友元 |

### 第 2 档 · 进阶 ★★☆ —— 继承与多态

| 编号 | 题目 | 考察点 |
| --- | --- | --- |
| `i01` | Rule of Three：自己实现一个字符串类 | 拷贝赋值 / 自赋值 / Rule of Three |
| `i02` | 继承与派生：员工与经理 | 派生类构造 / `protected` / 成员函数覆盖 |
| `i03` | 构造与析构的调用顺序 | 继承链的构造析构顺序 |
| `i04` | 虚函数与运行时多态：用基类指针画图形 | 虚函数 / 基类指针容器 / 模板方法 |
| `i05` | 抽象类与虚析构 | 纯虚函数 / 抽象类 / **虚析构的必要性** |
| `i06` | 友元：`operator*` 与工具类 | 友元函数 / 友元类 / 封装边界 |
| `i07` | 运算符重载进阶：有理数类 Fraction | 运算符重载 / 不变式维护 / 辗转相除 |
| `i08` | 组合（has-a）：订单与折扣，别什么关系都说成继承 | 组合 vs 继承 / 成员对象生命周期 / 引用返回 / const 正确性 |

### 第 3 档 · 高级 ★★★ —— 设计写进代码

| 编号 | 题目 | 考察点 |
| --- | --- | --- |
| `a01` | 类模板：自己写一个 `MyVector<T>` | 类模板 / 动态扩容 / `operator[]` / 深拷贝 |
| `a02` | 模板特化：为 `bool` 和 `double` 定制输出 | 类模板全特化 |
| `a03` | RAII：自己实现一个独占智能指针 | RAII / `= delete` / 资源管理 |
| `a04` | 设计模式：单例 Logger | 单例 / 静态局部变量 / 禁止拷贝 |
| `a05` | 设计模式：工厂方法 + `unique_ptr` | 工厂模式 / 智能指针 / 错误处理 |
| `a06` | 设计模式：观察者（发布-订阅） | 观察者模式 / 接口 + 多态 |
| `a07` | 多重继承与虚继承：菱形继承 | 多重继承 / `virtual` 基类 / 构造顺序 |

### 第 4 档 · 可视化 · MFC ◆◆◆◆ —— 对齐教材第 5 版

| 编号 | 题目 | 考察点 | 教材 |
| --- | --- | --- | --- |
| `v01` | 嵌套类：学生成绩单 | 类的嵌套定义 / 成员对象 | 1.2.2 |
| `v02` | 内联方法：两种写法 | 类内定义(隐式) / `inline` 类外定义(显式) | 1.2.3 |
| `v03` | 类指针与 this：链式调用 | `new`/`delete` / `p->` / 返回 `*this` | 1.6 |
| `v04` | CDC 绘图：直线 / 矩形 / 椭圆 | `CPaintDC` / `MoveTo`+`LineTo` / `Rectangle` / `Ellipse` | 2.5~2.6 |
| `v05` | 画笔、画刷与颜色 | `CPen` / `CBrush` / `RGB` / `SelectObject` 后恢复旧对象 | 2.4 |
| `v06` | 鼠标与键盘响应 | `ON_WM_LBUTTONDOWN` / `OnKeyDown` / `CPoint` / `VK_ESCAPE` | 第 4 章 |
| `v07` | 字体与文本输出 | `CFont` / `CreatePointFont` / `SetTextColor` / `SetBkMode` / `DrawText` 居中 | 第 3 章 |
| `v08` | 映像模式：按毫米画图 | `SetMapMode(MM_LOMETRIC)` / 逻辑单位 0.1mm / y 轴向上 | 2.3 |
| `v09` | 菜单与命令响应 | `CMenu` 动态菜单 / `ON_COMMAND` / 命令 ID | 5.1 |
| `v10` | 模态对话框与 DDX | `DoModal` / `DDX_Text` / `UpdateData` / `OnInitDialog`（需 .rc 资源） | 5.3 |
| `v11` | 位图与 BitBlt | `CBitmap` / `CreateCompatibleDC` / `SelectObject` / `BitBlt` | 5.2 |
| `v12` | 按钮与编辑框 | `CButton` 程序化创建 / `ON_BN_CLICKED` / `Get/SetDlgItemText` | 6.2 · 6.5 |
| `v13` | 列表框与选择变化 | `CListBox` / `AddString` / `GetCurSel` 判 `LB_ERR` / `ON_LBN_SELCHANGE` | 6.6 |
| `v14` | 进度条与定时器 | `CProgressCtrl` / `SetRange32` / `SetPos` / `SetTimer` + `OnTimer` | 6.8 |
| `v15` | 文档视图与串行化 | `CDocument` / `CView` / `Serialize` / `CArchive` / `CSingleDocTemplate`（需 .rc） | 7.1~7.2 |
| `v16` | 快捷菜单与命令响应 | `ON_WM_CONTEXTMENU` / `CreatePopupMenu` / `TrackPopupMenu` | 7.3~7.4 |
| `v17` | 多媒体：播放声音 | `PlaySound` / `SND_ASYNC` / `SND_PURGE` / `winmm.lib` / MCI | 第 8 章 |
| `v18` | 工具条与状态栏 | `CToolBar` / `LoadToolBar` / `CStatusBar` / `SetIndicators`（需 .rc） | 7.5 |

每题都带：`knowledge.md` 讲义 + 题面 + 逐条要求 + 样例 + 提示 + **完成前自查清单** +
带 `TODO` 的骨架（**头文件不写全，改成提示让你自己补 `#include`**，`using namespace std;` 已给好）+ 自动评测用例
（MFC 题为要点检查）+ 参考解（通过后解锁）。

---

## 8. 命令一览

```bat
:: ——— 日常(其实只需要记住第一条) ———
py oop_lab.py                    交互式主菜单(双击 oop_lab.bat 同效)
py oop_lab.py menu               显式进入菜单
py oop_lab.py open               用 VSCode 打开统一工作区
py oop_lab.py open-vs            用 Visual Studio 打开 oop_lab.sln

:: ——— 老师模式 ———
py oop_lab.py plan               按你的水平安排今天练哪几道(含理由)
py oop_lab.py plan -n 5          多安排几道; --local-only 只用本地题库
py oop_lab.py study b04          先学后练: 本题的知识点讲义
py oop_lab.py study K12          只看某个知识点
py oop_lab.py diagnose b04       老师式诊断: 错在哪 / 哪个知识点 / 怎么补
py oop_lab.py profile            学习画像: 33 个知识点掌握度 + 综合档位
py oop_lab.py log -n 10          学习日志

:: ——— 找题 / 练题 ———
py oop_lab.py list               题目列表(-l 2 只看进阶, -t 虚函数 按知识点)
py oop_lab.py show b01           看题面
py oop_lab.py new b01            生成/补齐这一题并打开统一工作区
py oop_lab.py new b01 --force    连 main.cpp 一起覆盖(默认不覆盖你的代码!)

:: ——— 验证 ———
py oop_lab.py judge b01          编译 + 跑用例 + 诊断 + 更新画像与日志
py oop_lab.py run b01 --case 2   编译并跑第 2 组用例
py oop_lab.py review b01         OOP 写法审查(12 条规则)并给规范分

:: ——— 收尾 ———
py oop_lab.py submit b01         生成提交包, 贴给 AI/老师点评
py oop_lab.py submit b01 -m "我不确定要不要写虚析构"
py oop_lab.py solution b01       看参考解(通过后解锁, --force 强看)

:: ——— 题库 / 联网 ———
py oop_lab.py progress           进度与统计(经验值 / 用时 / 提交次数)
py oop_lab.py search 线段树       多源找题(来源清单可自由增删)
py oop_lab.py pull P1001         导入洛谷题目(1049=dotcpp, CF4A=Codeforces)
py oop_lab.py pull <任意网址>     从任意网站的题面页导入
py oop_lab.py sources            管理题目来源(增删启停)

:: ——— 自检 ———
py oop_lab.py doctor             环境自检(编译器 / 编辑器 / 题库健康度)
py oop_lab.py selftest           用每题参考解真编译一遍
py -m unittest discover -s tests -t .    回归测试(165 条: 101 命令行/题库 + 64 GUI)
```

全局开关：`--no-color`（关闭彩色）、`-v`（调试日志 + 显示用例实际输出）。

---

## 9. 自动「指正」：评测 + 写法审查 + 诊断

### `judge`

```
[WA] 答案错误   用例 1/3  输出不一致

用例 1 的差异(第 1 行):
  期望: '1001 Tom 88'
  实际: '1001 88 Tom'
```

比对规则：**统一换行符 → 逐行去掉行尾空白 → 去掉首尾空行**，然后严格逐行比较
（行首空白保留，因为它是有意义的内容）。编译错误会原样贴出前 40 行。

### `review`：12 条面向对象的启发式规则

| 规则 | 级别 | 检查内容 |
| --- | --- | --- |
| `R00` | 错误 | 题目要求用类，但代码里没有 `class` / `struct` |
| `R01` | 警告 | 有析构却缺拷贝构造 / 拷贝赋值（Rule of Three 破防） |
| `R02` | 警告 | 有虚函数但析构不是 `virtual` |
| `R03` | 警告 | `operator=` 没有处理自赋值 |
| `R04` | 警告 | `new` 与 `delete` 数量不匹配、`new[]` 配 `delete` |
| `R05` | 警告 | 接收 `const X&` 形参的成员函数却自己没加 `const` |
| `R06` | 警告 | `class A : B` 这种默认 **private 继承** |
| `R07` | 警告 | 还留着 `TODO` 没处理 |
| `R08` | 提示 | `using namespace std;` |
| `R09` | 提示 | `printf` / `scanf` / `strcpy` 等 C 风格或危险函数 |
| `R10` | 提示 | 重写虚函数没写 `override` |
| `R11` | 提示 | `<bits/stdc++.h>` 不可移植 |
| `R12` | 提示 | 大量 `std::endl` |

每条规则都绑定到一个知识点，所以审查结果会直接变成学习画像里该知识点的惩罚分。
审查是**宁可漏报不误报**的启发式，规范分仅供参考。

---

## 10. 学习画像与学习日志

```bat
py oop_lab.py profile
```

```
综合档位: 第 1 档 · 基础   (连续通过 1 次 / 连续未过 0 次)
练习次数: 评测 3 次 · 审查 1 次 · 生成提交包 0 次 · 学习 1 天
累计评测耗时: 12.4 秒

第 1 档 · 基础
  K01 类与封装             █████······· 熟练
  K02 构造函数与初始化列表 █████······· 熟练
  K03 析构与对象生命周期   ············ 未练过
  K04 拷贝构造与深拷贝     ██████······ 基本掌握  2 次(过 1)
```

**掌握度怎么算**：

```
good       = 满分次数 + 0.55 × 部分通过次数
raw        = good / 尝试次数
confidence = min(1, 尝试次数 / 3)          ← 只做过一次不会给满分
score      = raw × (0.55 + 0.45 × confidence) − 审查惩罚(最多扣 0.30)
再叠加遗忘衰减: 超过 7 天没碰, 每多一天乘 0.95(下限 0.6)
```

综合档位由三个档位的「知识点覆盖率」（掌握度 ≥ 0.7 的比例）决定，不会因为一道题
碰巧通过就跳档。

**学习日志**（两份，都在 `data/`）：

| 文件 | 用途 |
| --- | --- |
| `learning_log.md` | 人类可读的 markdown，每次新题/评测/审查/提交/排课都追加一段（已去掉颜色转义，可直接当学习笔记） |
| `learning_log.jsonl` | 结构化事件流，`py oop_lab.py log` 读它做展示 |

---

## 11. 多源找题：不绑定任何网站

```bat
py oop_lab.py search 线段树
py oop_lab.py search 成绩 --source dotcpp
py oop_lab.py sources             :: 看/改来源清单
```

来源清单在 `data/sources.json`，**随时可以增删**：

| kind | 说明 |
| --- | --- |
| `luogu` | 洛谷：有难度与标签，题面可完整抓取 |
| `dotcpp` | C 语言网：题名自带 `[编程入门]` 之类分类前缀 |
| `codeforces` | Codeforces：免鉴权 API 拿 tag + rating，可按水平精准挑题 |
| `github` | 推荐成体系的练习仓库（公开搜索 API，失败回退精选清单） |
| `bing` | 网页兜底 |
| `generic` | **任意网站**：给一个带 `{q}` 的搜索地址 + 一条条目正则即可 |

加一个自定义站点（以牛客为例，内置但默认关闭）：

```bat
py oop_lab.py sources --add nowcoder --kind generic --label 牛客 ^
   --hosts nowcoder.com ^
   --search-url "https://ac.nowcoder.com/acm/problem/list?keyword={q}" ^
   --item-regex "href=\"(https://ac\.nowcoder\.com/acm/problem/\d+)\"[^>]*>\s*([^<]{4,90}?)\s*<"
py oop_lab.py sources --enable nowcoder
```

### 导入任意一道题

```bat
py oop_lab.py pull P3373          :: 洛谷
py oop_lab.py pull 1049           :: dotcpp
py oop_lab.py pull CF4A           :: Codeforces
py oop_lab.py pull https://noi.openjudge.cn/ch0101/01/     :: 任意站点
```

认得出域名的站点走**专用解析**（更准）；认不出来的链接走**通用抽取**：

1. 先用「文本多、链接少」的打分圈出正文容器（导航/侧边栏自动被排除）；
2. 再把 HTML 转成文本，按「题目描述 / 输入格式 / 输出格式 / 样例输入 / 提示」这类
   中英文小标题切段落；
3. 样例优先取「样例输入/输出」标记，没有标记就从 `<pre>` 块配对；
4. 容器版与整页版**都跑一遍，取更像题面的那个**，容器识别失误也不会一无所获。

实测可用的站点：洛谷、dotcpp、Codeforces、OpenJudge、牛客。
导入时会自动猜难度档位（难度标签优先，否则用标题关键词 —— dotcpp 的
`[编程入门]` 前缀能正确判成第 1 档）并从题面猜知识点。

> 导入的题**没有内建评测用例**，所以 `judge` 会提示「无自动用例」，排课时也会被
> 标成**拓展题**，与有评测的过关题分开。请自己往 `tests/` 里补数据，或去原站提交验证。
>
> JS 渲染的站点（例如 51Nod）抓不到内容，这时命令会给出链接让你自己看 ——
> 网络失败永远不会影响本地题库和评测。

---

## 12. 环境自检

```bat
py oop_lab.py doctor
```

```
== C++ 工具链自检 ==
[OK] 编译器      MSVC (cl.exe + vcvars64)  [C:\Program Files\...\vcvars64.bat]
     · MSVC 只能通过 vcvars64.bat 环境使用, 评测脚本已自动处理
== 目录 ==
题库目录: D:\code\cpp-oop-lab
练习工作区: D:\code\cpp-oop-lab\workspace
== 编辑器 ==
[OK] VSCode code 命令可用: C:\Users\...\bin\code.CMD
[OK] Visual Studio 可用(oop_lab.sln 可直接 F5)
     将生成的 VS 工程平台工具集: v145
== MFC 可视化支持(教材第 2~8 章) ==
[OK] MFC 可用: ...\atlmfc\include\afxwin.h          ← 装了就是这行
[!] 未安装 MFC 组件 —— MFC 题目只做要点检查, 不能真编译   ← 没装是这行
     · 安装方法: VS Installer → 修改 → 单个组件 →
       勾选「适用于最新 v143 生成工具的 C++ MFC(x86 和 x64)」后重新打开终端
== 题库健康度 ==
  [OK] 40 题结构自检通过
  在线导入题目: 0 题
```

> **MFC 组件是可选的、但强烈建议装**：教材第 2~8 章的题目用 Visual Studio 刷题时
> 需要它（VS 工程已经写好 `UseOfMfc`）；不装也能读讲义、写代码、跑要点检查，
> 只是 `judge` 不会真编译，判断依据变成「要点检查」。

---

## 13. 文件结构

```
cpp-oop-lab/
├── oop_lab.py            统一命令行入口 + 交互式主菜单
├── oop_lab.bat           双击进菜单
├── oop_app.py            图形界面入口(打包成 OOPLab.exe 的就是它)
├── oop_app.bat           双击直接开图形界面(开发期用)
├── oop_gui_app.py        图形界面主窗口: 三栏布局 / 工具栏 / 状态栏 / 业务接线
├── oop_gui_editor.py     代码编辑器控件(行号 + C++ 高亮 + 自动缩进 + Ctrl+S)
├── oop_gui_tasks.py      后台任务执行器(编译/联网不卡界面)
├── build_exe.py          一条命令打包单文件 exe
├── build_exe.bat         双击打包
├── oop_common.py         公共设施(终端宽度与颜色 / JSON 原子写 / 输出归一化 / 进度存储)
├── oop_html.py           底层网页工具(HTTP / 编码 / HTML 转文本 / 空白规范化)
├── oop_web.py            通用题面抽取 + 可配置的来源注册表
├── oop_bank_visual.py    第 4 档题库(18 题, 对齐教材第 5 版: 3 控制台 + 15 MFC)
├── oop_lab_icon.py       图标数据(64×64 PNG base64, 由 tools/make_ico.py 生成)
├── tools/make_ico.py     图标生成器(纯标准库手绘 → 多尺寸 oop_lab.ico)
├── oop_lab.ico           exe 文件图标(PyInstaller --icon 用)
├── oop_skills.py         知识点图谱: 33 个知识点 + 讲义 + 报错/审查规则映射表
├── oop_coach.py          教练引擎: 学习画像 / 自适应排课 / 诊断讲解 / 学习日志
├── oop_bank.py           题库聚合层(内建 + 在线导入, 查找/过滤/结构自检)
├── oop_bank_basic.py     第 1 档题库(7 题, 含参考解与用例)
├── oop_bank_adv.py       第 2 档题库(8 题)
├── oop_bank_pro.py       第 3 档题库(7 题)
├── oop_judge.py          编译与评测引擎(MSVC / MinGW 双后端)
├── oop_review.py         OOP 静态审查(12 条规则)
├── oop_search.py         多源找题(洛谷 / dotcpp / Codeforces / GitHub / 必应 / 任意站点)
├── oop_workspace.py      统一工作区(VSCode 配置 + VS 解决方案 + 讲义 + 提交包)
├── tests/test_oop_lab.py 命令行 / 题库回归测试(97 条, 纯标准库 unittest)
├── tests/test_gui.py     图形界面测试(54 条: 高亮/缩进/任务队列/窗口/真跑 mainloop 的冒烟)
├── data/                 运行期生成: progress.json / profile.json / sources.json /
│                         user_problems.json / learning_log.md / learning_log.jsonl
└── workspace/            运行期生成: 统一练习工作区(见第 5 节)
```

运行期文件都在 `.gitignore` 里（编译产物、日志、画像），你的 `main.cpp` 会被正常跟踪。

---

## 14. 实现设计

### 双编译器后端

| 后端 | 怎么调 |
| --- | --- |
| `g++` / `clang++` | 直接在 `PATH` 里找，`-std=c++17 -O0 -g -Wall -Wextra` |
| MSVC `cl.exe` | `vswhere` 定位安装（失败则扫常见目录）→ 生成临时 `.bat` 调 `vcvars64.bat` 后编译 |

两个后端都会带上 `set VSLANG=1033`，让 MSVC 说英文 —— 中文报错每台机器措辞不同，
没法做稳定诊断（诊断表里仍保留了中文兜底规则）。

评测前会调 `SetErrorMode(SEM_NOGPFAULTERRORBOX)` 关掉 Windows 的「程序已停止工作」
弹窗：不关的话，学生写出野指针时每个崩溃用例都要等弹窗超时，4 个用例能拖到 21 秒
（实测降到 3.4 秒）。

### 批处理文件的三个坑（都踩过）

1. **编码**：`.bat` 里写中文，cmd 会按控制台代码页（中文系统是 GBK）逐行解析 UTF-8
   字节，注释被解码成乱码后甚至会把一行拆成几条命令去执行，脚本直接报废。
   → 生成的批处理**一律纯 ASCII**（英文提示），中文说明放在 markdown 里；
   写入时强制 `encoding="ascii"`。
2. **换行**：必须 CRLF，LF-only 在标签、括号块等场景会出错。
   → 统一的 `write_bat()` / `write_text_crlf()` 负责转换。
3. **`/I"路径\"` 的尾部反斜杠**：`%~dpI` 天然以 `\` 结尾，写进 `/I"...\"` 会**把引号
   转义掉**，MSVC 于是认为没有源文件（`error D8003: 缺少源文件名`）。
   → 取到目录后先剥掉末尾反斜杠再使用。

另外 `rem` 行里不能出现 `<` `>` —— cmd 会把它当重定向处理。

### VS 工程与解决方案

- `PlatformToolset` 必须显式写：不写会被当成 VS2010，报 `MSB8020 找不到 v100 工具集`。
  按 `VC\Tools\MSVC\<版本>` 推断：`14.5x → v145`(VS18) / `14.3~14.4x → v143`(VS2022) /
  `14.2x → v142`(VS2019) / `14.1x → v141`(VS2017)；可用 `OOP_PLATFORM_TOOLSET` 覆盖。
- 工程 GUID 用 `uuid5(题目目录名)` 确定性生成，反复生成 `.sln` 不会全变。
- `TargetName=main` 让 VS 的产物与 `judge`、VSCode 的产物路径完全一致。
- `.sln` / `.vcxproj` 用 CRLF 写，Visual Studio 才不会有奇怪的提示。

### 通用题面抽取

`oop_web.extract_problem()` 会**试好几个范围再取最好的**：指定的容器（如 Codeforces 的
`div.ttypography`）→ 自动识别的正文容器 → 整页兜底。每个结果用
「描述长度是否合理 + 有没有输入/输出/提示 + 有没有样例 − UI 噪声」打分，取最高分。

容器识别是 readability 的精简版：给每个块算
`文本长度 − 3 × 链接文字长度`，在接近最高分的候选里取嵌套最深的那个。
页面顶栏和侧边栏链接密度高，自然被排除。

### 输出比对的取舍

`normalize_output()` 只做三件事：统一换行、去掉**行尾**空白、去掉**首尾**空行。
刻意不做的事：忽略大小写、压缩中间空格、忽略行首空白 —— 这些「宽容」会让本该报错的
格式错误悄悄蒙混过关。

### 存储

进度、画像、来源配置、导入的题目都用「同目录临时文件 + `os.replace`」原子写；
文件损坏时自动回退为空，不让一个坏 JSON 把整个程序带崩。

---

## 15. 怎么加自己的题

在任意一个 `oop_bank_*.py` 里往 `PROBLEMS` 追加一个字典：

```python
_p(
    id="b08",
    slug="my-problem",               # 英文短名, 生成目录 workspace/b08-my-problem
    title="我的题目",
    topics=["继承与派生"],            # 会自动映射到知识点, 讲义也按它生成
    desc="题面背景……",
    require=["要求一", "要求二"],
    io="输入……输出……",
    samples=[{"in": "1\n", "out": "1\n"}],
    hints=["提示"],
    checklist=["自查点"],
    skeleton="// TODO: 补全头文件(<iostream> 等)\nusing namespace std;\n// TODO: ...\nint main() { return 0; }\n",
    solution="……完整可编译的参考解……",
    tests=[{"in": "1\n", "out": "1\n"}],
)
```

然后：

```bat
py oop_lab.py doctor --no-color     :: 结构自检, 会指出缺了哪个字段
py oop_lab.py selftest --id b08     :: 真编译一遍参考解, 验证用例答案没写错
py oop_lab.py study b08             :: 检查 topics 有没有落到知识点上
py oop_lab.py new b08               :: 生成题目目录 + 讲义 + VS 工程
```

想调整教学策略：

| 想改什么 | 改哪里 |
| --- | --- |
| 知识点、讲义内容、编译器报错/审查规则映射 | `oop_skills.py` |
| 掌握度公式、排课权重、诊断话术 | `oop_coach.py` |
| 难度档位、关键词→难度、导入流程 | `oop_search.py` |
| 工作区文件内容（tasks/launch/vcxproj/sln/讲义模板） | `oop_workspace.py` |
| 通用题面抽取规则、来源注册表 | `oop_web.py` |

---

## 16. 图形界面与 exe

不想碰命令行就**双击 `OOPLab.exe`**。它和命令行版共用同一套题库、同一个工作区、
同一份进度与画像 —— 只是把「敲命令」换成「点按钮」。

```
┌────────────────────────────────────────────────────────────────────────────┐
│ OOP Lab — C++ 面向对象训练营                                                │
│ [教练排课][学知识点][保存][评测 F5][写法审查][学习画像][找题][打开VSCode][打开VS][自检]│
├──────────────┬─────────────────────────────────────────────────────────────┤
│ ★☆☆ 基础 (0/7)│ ┌ 讲义 ── 题面 ── [我的代码] ── 评测结果 ──────────────────┐│
│  ● b01 学生类 │ │   1 │ // TODO: 补全头文件                                ││
│  ○ b02 日期类 │ │   2 │ using namespace std;                               ││
│ ★★☆ 进阶(0/8)│ │   4 │ class Student {                                    ││
│  ○ i01 Rule… │ │   5 │     // TODO                                        ││
├──────────────┴─────────────────────────────────────────────────────────────┤
│ 编译器: MSVC (cl.exe) │ 当前 b01 未开始 │ 掌握度: 最低 0%      │ 就绪        │
└────────────────────────────────────────────────────────────────────────────┘
```

- **左边**题目树按档位分组，`0/7` 是这一档的通过进度；● 已通过 / ◐ 进行中 / ○ 未开始。
  点一下就切题，会自动生成或读回这一题的工程与你的代码。
- **中间四个选项卡**按使用顺序排：先看「讲义」→ 再看「题面」→ 在「我的代码」里写 →
  点评测自动跳到「评测结果」。
- 快捷键：**F5** 评测、**Ctrl+S** 保存；标题栏的 `*` 表示还没保存。
- 「教练排课」「找题」的弹窗里可以**双击一行**直接跳到那一题。

### 图标

图标是**用代码画出来的**（`tools/make_ico.py`，纯标准库：手绘渲染 → 超采样抗锯齿 →
PNG-in-ICO 打包成 256/128/64/48/32/16 六个尺寸）：

```bat
py tools\make_ico.py         :: 重新生成 oop_lab.ico 与 oop_lab_icon.py
```

图案是「类继承关系图」：上方一个父类方块、下方两个子类方块用连线相连（深蓝→紫渐变底）。
`build_exe.py` 会把 `oop_lab.ico` 传给 PyInstaller（文件图标）；窗口左上角用的是
内嵌的 64×64 PNG（`oop_lab_icon.py`），不依赖外部文件 —— 单文件 exe 里也能显示。

### 从源码打包

```bat
py build_exe.py              :: -> dist\OOPLab.exe   单文件, 约 9.7 MB(带图标)
py build_exe.py --onedir     :: -> dist\OOPLab\      文件夹版, 启动更快
```

PyInstaller 是**打包期工具**，运行期依然零第三方依赖（构建好的 exe 里已经带上了
Python 解释器和 tkinter）。

### exe 放哪儿、数据在哪儿

exe 可以放在**任意目录**，首次运行会在**它旁边**创建：

```
D:\OOPLab\
├── OOPLab.exe
├── data\          ← 进度 / 画像 / 学习日志 / 导入的题目
├── workspace\     ← 练习工作区(和你用命令行时是同一套结构)
└── oop_lab.log    ← 启动与出错记录
```

所以推荐做法是：建一个空目录 → 把 exe 丢进去 → 双击。换机器时把整个目录拷走，
进度也跟着走。

### 启动失败怎么办

exe 没有控制台，看不到报错。所有启动信息和异常都会写进 **exe 旁边的 `oop_lab.log`**，
启动失败时还会弹一个消息框把调用栈贴出来。

### GUI 与命令行的关系

| | 图形界面 | 命令行 |
| --- | --- | --- |
| 入口 | `OOPLab.exe` / `oop_app.bat` | `py oop_lab.py` / `oop_lab.bat` |
| 能做的事 | 排课 / 学 / 写 / 评测 / 审查 / 画像 / 找题 / 自检 | **全部**（含 `submit` 提交包、`pull` 导入、`sources` 管理） |

命令行版一行都没删，两者可以混用（比如在 GUI 里练、用 `py oop_lab.py submit` 生成提交包
发给老师）。

### 界面是怎么保证不卡的

编译一次 2~5 秒、联网找题可达 10 秒、题库自检几十秒 —— 这些如果跑在界面线程上，
窗口会变成「未响应」。所以它们全部交给 `oop_gui_tasks.TaskRunner`：后台线程执行、
结果投进队列、主线程用 `root.after()` 每 50ms 取一次。任务运行期间那四个按钮会置灰，
不会出现连点导致的状态错乱。

---

## 17. 已知限制

- 只支持 Windows 10/11（批处理、`vcvars` 探测、崩溃码解释、VS 工程都是 Windows 专用的）。
- 只支持**单文件题目**（`main.cpp`）。要练多文件编译请直接改生成的工程文件。
- `review` 与诊断都是文本启发式，不是编译器级别的语义分析：复杂模板代码、宏、多继承的
  边角情况可能漏报。它的定位是「写完后的自查与引导」，不是评分工具。
- 掌握度是**启发式的相对值**，不是绝对水平度量；它的价值在于“和自己比、决定下一题练什么”。
- 联网搜题解析的是各站公开页面/接口，对方改版后可能需要同步调整 `oop_search.py` 与
  `oop_web.py`；解析都拆成了纯函数，测试里有固定的样例串，改完跑一遍测试就知道有没有改坏。
- 在线导入的题没有内建评测用例，无法自动判定对错，只能作为**拓展题**。
- JS 渲染（纯前端）的题库站点抓不到内容，导入时会提示改用链接自己看。
- **图形界面的已知情况**：
  - 单文件 exe 首次启动要解压，约 **2~4 秒**白屏，之后每次打开都正常（想更快就用 `--onedir`）。
  - PyInstaller 打出来的 exe 体积约 10 MB，个别杀毒软件可能误报，加白名单即可。
  - 界面**故意不内置多文件工程**：只认每道题的 `main.cpp`，和命令行版保持一致。
  - 内置编辑器定位是「随手改两行」，没有自动补全、重构、跳转定义 ——
    重度编辑请点工具栏的「打开VSCode」。

---

## 许可证

MIT
