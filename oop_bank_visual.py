#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_bank_visual.py - 第 4 档(可视化 · MFC)题目

对齐教材: 黄维通、童军博《Visual C++面向对象与可视化程序设计(第 5 版)》
(高等教育出版社, ISBN 9787040646832)。

- v01~v03 对应第 1 章的 C++ 细节(MFC 环境下也要用到的语言基础):
  嵌套类 / 内联方法 / 类指针与 this —— 控制台题, 全自动评测;
- v04~v06 对应第 2、4 章的 MFC 编程:
  GDI 绘图 / 画笔与画刷 / 键盘鼠标响应 —— 窗口程序, framework="mfc",
  评测方式为「编译验证 + 要点检查(checks)」(装了 MFC 组件才能真编译)。

编排约定与其它题库模块一致(见 oop_bank_basic.py 顶部说明)。
"""

from __future__ import annotations

from typing import Any, Dict, List


def _p(**kwargs: Any) -> Dict[str, Any]:
    problem = {
        "level": 4,
        "hints": [],
        "checklist": [],
        "samples": [],
        "tests": [],
        "topics": [],
        "require": [],
        "subtasks": [],
    }
    problem.update(kwargs)
    return problem


#: MFC 题公共的骨架尾巴(应用程序对象 + 入口), 避免每题重复抄
_APP_TAIL = (
    "\n"
    "BOOL CMyApp::InitInstance()\n"
    "{\n"
    "    CMainWnd* wnd = new CMainWnd();\n"
    "    m_pMainWnd = wnd;\n"
    "    wnd->ShowWindow(SW_SHOW);\n"
    "    wnd->UpdateWindow();\n"
    "    return TRUE;\n"
    "}\n"
    "\n"
    "CMyApp theApp;                      // 全局唯一的应用程序对象\n"
)


PROBLEMS: List[Dict[str, Any]] = [
    # ---------------------------------------------------------------- v01
    _p(
        id="v01",
        slug="nested-class",
        title="嵌套类：学生成绩单（教材 1.2.2）",
        topics=["嵌套类", "类与封装"],
        desc=(
            "教材第 1 章 1.2.2 介绍了类的嵌套定义: 一个只在内部使用的小类型, "
            "可以直接定义在另一个类的里面, 不污染外部命名空间。"
            "本题让你把「三门课成绩」封装成一个嵌套类 Score, 由 Student 持有。"
        ),
        require=[
            "在 class Student 内部定义嵌套类 Score, 数据成员(三门课成绩)private。",
            "Score 提供构造函数 Score(int a, int b, int c) 与 double average() const。",
            "Student 持有一个 Score 成员对象, 在初始化列表里构造它。",
            "Student 提供 double average() const, 直接转调嵌套类的 average()。",
            "输出平均分, 保留 1 位小数(fixed + setprecision(1))。",
        ],
        io=("第一行一个整数 n(1 ≤ n ≤ 100)。接下来 n 行, 每行三个整数(三门课成绩)。"
            "每行输出该学生的平均分, 保留 1 位小数。"),
        samples=[{"in": "2\n90 80 70\n100 100 100\n", "out": "80.0\n100.0\n"}],
        hints=[
            "嵌套类默认只能被外部类访问, 外部想直接用 Student::Score 也可以, 但要写全 Student::Score。",
            "嵌套类不会自动访问外部类的 this —— 它只是“定义在里面的独立类”。",
            "平均分用 (a + b + c) / 3.0, 别写整数除法。",
        ],
        checklist=[
            "嵌套类定义在 private 区了吗?(它不是给外部用的)",
            "成员对象 Score 在初始化列表里构造了吗?",
            "average() 加了 const 吗?",
        ],
        skeleton=(
            "#include <iostream>\n"
            "#include <iomanip>\n"
            "using namespace std;\n"
            "\n"
            "// ================== TODO: 按教材 1.2.2 补全 Student 类 ==================\n"
            "// 要求:\n"
            "//   * 在 Student 内部定义嵌套类 Score(三个 private 成绩成员)\n"
            "//   * Score 提供 Score(int a, int b, int c) 与 double average() const\n"
            "//   * Student 持有一个 Score 成员(初始化列表里构造)并转调 average()\n"
            "class Student {\n"
            "\n"
            "};\n"
            "// ========================================================================\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    cout << fixed << setprecision(1);\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        int a, b, c;\n"
            "        cin >> a >> b >> c;\n"
            "        const Student s(a, b, c);\n"
            "        cout << s.average() << '\\n';\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        solution=(
            "#include <iostream>\n"
            "#include <iomanip>\n"
            "using namespace std;\n"
            "\n"
            "class Student {\n"
            "private:\n"
            "    class Score {                     // 嵌套类: 只在 Student 内部使用\n"
            "    private:\n"
            "        int chinese_, math_, english_;\n"
            "    public:\n"
            "        Score(int a, int b, int c)\n"
            "            : chinese_(a), math_(b), english_(c) {}\n"
            "        double average() const { return (chinese_ + math_ + english_) / 3.0; }\n"
            "    };\n"
            "\n"
            "    Score score_;                     // 成员对象: 组合关系\n"
            "\n"
            "public:\n"
            "    Student(int a, int b, int c) : score_(a, b, c) {}\n"
            "    double average() const { return score_.average(); }\n"
            "};\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    cout << fixed << setprecision(1);\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        int a, b, c;\n"
            "        cin >> a >> b >> c;\n"
            "        const Student s(a, b, c);\n"
            "        cout << s.average() << '\\n';\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        tests=[
            {"in": "1\n90 80 70\n", "out": "80.0\n"},
            {"in": "2\n100 100 100\n60 70 80\n", "out": "100.0\n70.0\n"},
            {"in": "1\n0 0 1\n", "out": "0.3\n"},
        ],
    ),
    # ---------------------------------------------------------------- v02
    _p(
        id="v02",
        slug="inline-methods",
        title="内联方法：两种写法（教材 1.2.3）",
        topics=["内联方法", "成员函数"],
        desc=(
            "教材 1.2.3 讲了内联方法: 函数体写在类定义里面是「隐式内联」; "
            "写在类外面、函数前加 inline 关键字是「显式内联」。"
            "两种写法都要会用 —— 本题各写一个。"
        ),
        require=[
            "定义 class Counter: 两个 private 成员 sum_(总和) 与 count_(个数)。",
            "count(int v) 用类内定义(隐式内联): 把 v 累加进 sum_ 并把 count_ 加 1。",
            "value() const 与 size() const 用类外定义 + inline 关键字(显式内联)。",
            "main 里读入 n 个整数, 每个都调用 count(); 输出总和 与 个数(空格分隔)。",
        ],
        io=("第一行一个整数 n(1 ≤ n ≤ 1000)。第二行 n 个整数(可为负数)。"
            "输出一行: 总和 个数。"),
        samples=[{"in": "5\n10 20 30 40 50\n", "out": "150 5\n"}],
        hints=[
            "类外写内联: 返回类型前面写 inline, 且必须写在头文件里(或者同一个 .cpp)。",
            "类内定义的成员函数天生就是内联的, 不需要再写 inline。",
            "size() 返回个数, value() 返回总和, 都是只读的 —— 记得 const。",
        ],
        checklist=[
            "count() 是不是写在类里面? value()/size() 是不是写在类外面并带 inline?",
            "两个类外函数都加了 const 吗?",
            "输出格式是「总和 个数」, 中间一个空格。",
        ],
        skeleton=(
            "#include <iostream>\n"
            "using namespace std;\n"
            "\n"
            "// ================== TODO: 按教材 1.2.3 实现 Counter ==================\n"
            "// 要求:\n"
            "//   * count(int v) 写在类里面(隐式内联)\n"
            "//   * value() / size() 在类里只写声明, 定义写在类外、函数前加 inline\n"
            "class Counter {\n"
            "private:\n"
            "    int sum_;\n"
            "    int count_;\n"
            "public:\n"
            "    Counter() : sum_(0), count_(0) {}\n"
            "    // TODO: 1) 类内定义 count(int v)\n"
            "    // TODO: 2) 在这里声明 value() 与 size()(只写声明, 别写函数体)\n"
            "};\n"
            "\n"
            "// TODO: 3) 在这里用 inline 写 value() 与 size() 的类外定义\n"
            "// =====================================================================\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    Counter counter;\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        int v;\n"
            "        cin >> v;\n"
            "        counter.count(v);\n"
            "    }\n"
            "    cout << counter.value() << ' ' << counter.size() << '\\n';\n"
            "    return 0;\n"
            "}\n"
        ),
        solution=(
            "#include <iostream>\n"
            "using namespace std;\n"
            "\n"
            "class Counter {\n"
            "private:\n"
            "    int sum_;\n"
            "    int count_;\n"
            "public:\n"
            "    Counter() : sum_(0), count_(0) {}\n"
            "\n"
            "    void count(int v) {           // 类内定义 = 隐式内联\n"
            "        sum_ += v;\n"
            "        ++count_;\n"
            "    }\n"
            "    int value() const;            // 类里只声明...\n"
            "    int size() const;\n"
            "};\n"
            "\n"
            "inline int Counter::value() const { return sum_; }     // ...类外用 inline 定义\n"
            "inline int Counter::size() const { return count_; }\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    Counter counter;\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        int v;\n"
            "        cin >> v;\n"
            "        counter.count(v);\n"
            "    }\n"
            "    cout << counter.value() << ' ' << counter.size() << '\\n';\n"
            "    return 0;\n"
            "}\n"
        ),
        tests=[
            {"in": "5\n10 20 30 40 50\n", "out": "150 5\n"},
            {"in": "1\n-7\n", "out": "-7 1\n"},
            {"in": "3\n0 0 0\n", "out": "0 3\n"},
        ],
    ),
    # ---------------------------------------------------------------- v03
    _p(
        id="v03",
        slug="object-pointer-this",
        title="类指针与 this：链式调用（教材 1.6）",
        topics=["类指针", "this指针", "成员函数"],
        desc=(
            "教材 1.6 讲了类的指针: 用 new 在堆上创建对象, 通过 -> 访问成员, "
            "用完必须 delete。同时演示 this 指针的经典用法 —— "
            "让 set 函数返回 *this, 从而支持 p->setName(...).setAge(...) 这样的链式调用。"
        ),
        require=[
            "定义 class Person: private 成员 name_(string) 与 age_(int)。",
            "setName(const string&) 返回 Person&, 返回 *this(链式调用的关键)。",
            "setAge(int) 同样返回 Person&。",
            "show() const 输出一行: 姓名 年龄。",
            "main 里必须用 Person* p = new Person(); 通过 p-> 调用(链式), 最后 delete p。",
        ],
        io=("第一行一个整数 n(1 ≤ n ≤ 100)。接下来 n 行, 每行 姓名 年龄。"
            "每行输出 姓名 年龄。"),
        samples=[{"in": "2\nTom 18\nJerry 20\n", "out": "Tom 18\nJerry 20\n"}],
        hints=[
            "返回 *this 的类型是 Person&(引用), 不能返回 Person(会拷贝)。",
            "p->setName(\"Tom\").setAge(18) 相当于 (p->setName(\"Tom\")).setAge(18)。",
            "new 出来的对象必须 delete —— 这正是 K03/K04 讲的资源管理起手式。",
        ],
        checklist=[
            "setName/setAge 的返回类型是引用 Person& 吗?",
            "链式调用的点号顺序对吗? (先 setName 再 setAge)",
            "delete p 写了吗?",
            "show() 是 const 吗?",
        ],
        skeleton=(
            "#include <iostream>\n"
            "#include <string>\n"
            "using namespace std;\n"
            "\n"
            "// ================== TODO: 按教材 1.6 补全 Person ==================\n"
            "// 要求:\n"
            "//   * 数据成员 name_ / age_ 全 private\n"
            "//   * setName(const string&) 返回 Person& 并 return *this\n"
            "//   * setAge(int) 同样返回 Person&\n"
            "//   * show() const 输出: 姓名 年龄\n"
            "class Person {\n"
            "\n"
            "};\n"
            "// ==================================================================\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        string name;\n"
            "        int age;\n"
            "        cin >> name >> age;\n"
            "        // TODO: 用 new 创建对象, 通过指针链式设置, show 之后 delete\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        solution=(
            "#include <iostream>\n"
            "#include <string>\n"
            "using namespace std;\n"
            "\n"
            "class Person {\n"
            "private:\n"
            "    string name_;\n"
            "    int age_;\n"
            "public:\n"
            "    Person() : name_(\"\"), age_(0) {}\n"
            "\n"
            "    Person& setName(const string& name) {   // 返回 *this 支持链式调用\n"
            "        name_ = name;\n"
            "        return *this;\n"
            "    }\n"
            "    Person& setAge(int age) {\n"
            "        age_ = age;\n"
            "        return *this;\n"
            "    }\n"
            "    void show() const { cout << name_ << ' ' << age_ << '\\n'; }\n"
            "};\n"
            "\n"
            "int main() {\n"
            "    int n;\n"
            "    if (!(cin >> n)) return 0;\n"
            "    for (int i = 0; i < n; ++i) {\n"
            "        string name;\n"
            "        int age;\n"
            "        cin >> name >> age;\n"
            "        Person* p = new Person();               // 堆上创建\n"
            "        p->setName(name).setAge(age);           // 指针 + 链式调用\n"
            "        p->show();\n"
            "        delete p;                               // 谁 new 谁 delete\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        tests=[
            {"in": "2\nTom 18\nJerry 20\n", "out": "Tom 18\nJerry 20\n"},
            {"in": "1\nA 0\n", "out": "A 0\n"},
        ],
    ),
    # ---------------------------------------------------------------- v04
    _p(
        id="v04",
        slug="gdi-drawing",
        title="CDC 绘图：直线 / 矩形 / 椭圆（教材 2.5~2.6）",
        topics=["设备环境", "CDC", "绘图"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材第 2 章的核心: 所有绘图都通过设备环境(DC)完成。"
            "在 MFC 里, WM_PAINT 消息的处理函数里创建 CPaintDC 对象, "
            "它自动完成 BeginPaint/EndPaint, 然后就可以用 dc 的成员函数画图了。"
        ),
        require=[
            "在 OnPaint() 里用 CPaintDC 获取设备环境(不要用 CClientDC)。",
            "用 MoveTo + LineTo 画一条直线。",
            "用 Rectangle 画一个矩形。",
            "用 Ellipse 画一个椭圆。",
            "消息映射表里保留 ON_WM_PAINT()(骨架里已写好, 别删)。",
        ],
        io="图形界面程序: 没有控制台输入输出, 运行后窗口里应出现一条直线、一个矩形、一个椭圆。",
        hints=[
            "CPaintDC dc(this); —— this 是窗口对象, DC 就绑定在它上面。",
            "Rectangle(左, 上, 右, 下) 与 Ellipse(左, 上, 右, 下) 的参数都是外接矩形。",
            "想验证效果: 编译运行后拖动窗口, 图形应该自动重画(因为重绘逻辑就在 OnPaint 里)。",
        ],
        checklist=[
            "用的是 CPaintDC 而不是 CClientDC 吗?",
            "三种图形都画了吗?",
            "ON_WM_PAINT() 还在消息映射表里吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"GDI 绘图\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 2.5~2.6 完成绘图 ==================\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);      // 绑定 WM_PAINT 的设备环境\n"
            "\n"
            "    // TODO: 用 dc 画一条直线(MoveTo + LineTo)\n"
            "    // TODO: 画一个矩形(dc.Rectangle)\n"
            "    // TODO: 画一个椭圆(dc.Ellipse)\n"
            "}\n"
            "// ==================================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"GDI 绘图\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);                 // 自动 BeginPaint / EndPaint\n"
            "\n"
            "    dc.MoveTo(20, 20);                 // 直线\n"
            "    dc.LineTo(340, 200);\n"
            "\n"
            "    dc.Rectangle(40, 60, 200, 180);    // 矩形(左 上 右 下)\n"
            "    dc.Ellipse(160, 90, 320, 210);     // 椭圆\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCPaintDC\b", "hint": "OnPaint 里要用 CPaintDC 获取设备环境"},
            {"pattern": r"\bMoveTo\b[\s\S]*\bLineTo\b", "hint": "用 MoveTo + LineTo 画直线"},
            {"pattern": r"\bRectangle\s*\(", "hint": "用 Rectangle 画矩形"},
            {"pattern": r"\bEllipse\s*\(", "hint": "用 Ellipse 画椭圆"},
            {"pattern": r"\bON_WM_PAINT\b", "hint": "消息映射表里要有 ON_WM_PAINT()"},
            {"pattern": r"\bBEGIN_MESSAGE_MAP\b", "hint": "必须有 BEGIN_MESSAGE_MAP/END_MESSAGE_MAP"},
        ],
    ),
    # ---------------------------------------------------------------- v05
    _p(
        id="v05",
        slug="pen-brush-color",
        title="画笔、画刷与颜色（教材 2.4）",
        topics=["画笔", "画刷", "颜色"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 2.4: 画笔(CPen)控制线条的样式/宽度/颜色, 画刷(CBrush)控制填充。"
            "创建出来的 GDI 对象必须 SelectObject 选进 DC 才起作用, 用完还要把旧对象恢复 —— "
            "这是教材反复强调的完整套路。"
        ),
        require=[
            "创建一支红色、3 像素宽的实线画笔(CPen + PS_SOLID + RGB(255, 0, 0))。",
            "创建一把黄色画刷(CBrush + RGB(255, 255, 0))。",
            "把画笔和画刷都用 SelectObject 选进 DC, 并保存旧对象。",
            "画一个椭圆(边框用红笔、内部填黄刷)。",
            "绘制结束后把旧对象依次恢复(SelectObject 回旧画笔/旧画刷)。",
        ],
        io="图形界面程序: 运行后窗口里出现一个红边黄底的椭圆。",
        hints=[
            "创建: CPen pen(PS_SOLID, 3, RGB(255, 0, 0)); CBrush brush(RGB(255, 255, 0));",
            "选进 DC 并保存: CPen* oldPen = dc.SelectObject(&pen);",
            "恢复顺序没有严格要求, 但两步都要做 —— 少一步就是 GDI 对象泄漏(见 K19 的坑)。",
        ],
        checklist=[
            "CPen / CBrush / RGB / SelectObject 都出现了吗?",
            "恢复旧对象的代码写了吗?(dc.SelectObject(oldPen) 之类)",
            "椭圆的外接矩形坐标合理吗?(左上角要小于右下角)",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"画笔与画刷\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 2.4 完成 ==================\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    // TODO: 创建红色 3 像素画笔与黄色画刷\n"
            "    // TODO: 用 SelectObject 选进 DC 并保存旧对象\n"
            "    // TODO: 画椭圆(红边黄底)\n"
            "    // TODO: 把旧对象恢复回去\n"
            "}\n"
            "// ==========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"画笔与画刷\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    CPen pen(PS_SOLID, 3, RGB(255, 0, 0));      // 红色 3 像素实线笔\n"
            "    CBrush brush(RGB(255, 255, 0));             // 黄色画刷\n"
            "    CPen* oldPen = dc.SelectObject(&pen);       // 选进 DC 并保存旧笔\n"
            "    CBrush* oldBrush = dc.SelectObject(&brush); // 选进 DC 并保存旧刷\n"
            "\n"
            "    dc.Ellipse(60, 60, 320, 240);               // 红边黄底椭圆\n"
            "\n"
            "    dc.SelectObject(oldPen);                    // 恢复旧笔, 防 GDI 泄漏\n"
            "    dc.SelectObject(oldBrush);                  // 恢复旧刷\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCPen\s+\w+\s*\(", "hint": "要创建 CPen 对象(画笔)"},
            {"pattern": r"\bCBrush\s+\w+\s*\(", "hint": "要创建 CBrush 对象(画刷)"},
            {"pattern": r"RGB\s*\(", "hint": "颜色用 RGB(...) 宏指定"},
            {"pattern": r"\bSelectObject\b", "hint": "画笔/画刷要 SelectObject 选进 DC"},
            {"pattern": r"\bEllipse\s*\(", "hint": "要画一个椭圆(Ellipse)"},
            {"pattern": r"SelectObject\s*\(\s*old", "hint": "用完要把旧 GDI 对象恢复回去"},
        ],
    ),
    # ---------------------------------------------------------------- v06
    _p(
        id="v06",
        slug="mouse-keyboard",
        title="鼠标与键盘响应（教材第 4 章）",
        topics=["鼠标消息", "键盘消息"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材第 4 章: 窗口程序要响应用户操作, 就是给鼠标/键盘消息写处理函数, "
            "并在消息映射表里把消息和处理函数挂上钩。"
            "本题同时处理左键按下(在点击位置画一个标记)与按键(Esc 退出)。"
        ),
        require=[
            "添加鼠标左键按下处理函数: afx_msg void OnLButtonDown(UINT nFlags, CPoint point);",
            "鼠标处理函数里用 CClientDC 在点击位置画一个小椭圆作为标记。",
            "添加按键处理函数: afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);",
            "按键处理函数里判断 nChar == VK_ESCAPE 时调用 PostMessage(WM_CLOSE) 退出。",
            "消息映射表里加入 ON_WM_LBUTTONDOWN() 与 ON_WM_KEYDOWN()。",
        ],
        io="图形界面程序: 鼠标左键点击窗口会在点击处留下一个标记; 按 Esc 关闭窗口。",
        hints=[
            "CPoint point 是客户区坐标, 直接用 point.x / point.y。",
            "画标记: dc.Ellipse(point.x - 4, point.y - 4, point.x + 4, point.y + 4);",
            "处理完记得调用基类版本(CFrameWnd::OnLButtonDown(...)), 保持默认行为。",
        ],
        checklist=[
            "两个处理函数都加了 afx_msg 前缀并在类里声明了吗?",
            "消息映射表里两个 ON_WM_ 条目都加了吗?",
            "OnKeyDown 用的是 VK_ESCAPE(虚拟键码) 而不是 'Esc' 字符串吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"鼠标与键盘\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    // TODO: 声明 OnLButtonDown 与 OnKeyDown(都要 afx_msg 前缀)\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "    // TODO: 在这里挂上 ON_WM_LBUTTONDOWN() 与 ON_WM_KEYDOWN()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "    dc.TextOut(10, 10, \"左键点击看看; 按 Esc 退出\");\n"
            "}\n"
            "\n"
            "// ================== TODO: 按教材第 4 章补全两个处理函数 ==================\n"
            "// void CMainWnd::OnLButtonDown(UINT nFlags, CPoint point) { ... }\n"
            "// void CMainWnd::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags) { ... }\n"
            "// ========================================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"鼠标与键盘\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    afx_msg void OnLButtonDown(UINT nFlags, CPoint point);\n"
            "    afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "    ON_WM_LBUTTONDOWN()\n"
            "    ON_WM_KEYDOWN()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "    dc.TextOut(10, 10, \"左键点击看看; 按 Esc 退出\");\n"
            "}\n"
            "\n"
            "void CMainWnd::OnLButtonDown(UINT nFlags, CPoint point)\n"
            "{\n"
            "    CClientDC dc(this);                        // 非 WM_PAINT 期间随时可画\n"
            "    dc.Ellipse(point.x - 4, point.y - 4, point.x + 4, point.y + 4);\n"
            "    CFrameWnd::OnLButtonDown(nFlags, point);   // 不处理的部分交回基类\n"
            "}\n"
            "\n"
            "void CMainWnd::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)\n"
            "{\n"
            "    if (nChar == VK_ESCAPE)                    // 虚拟键码: Esc\n"
            "        PostMessage(WM_CLOSE);\n"
            "    CFrameWnd::OnKeyDown(nChar, nRepCnt, nFlags);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bON_WM_LBUTTONDOWN\b", "hint": "消息映射表里要挂 ON_WM_LBUTTONDOWN()"},
            {"pattern": r"\bON_WM_KEYDOWN\b", "hint": "消息映射表里要挂 ON_WM_KEYDOWN()"},
            {"pattern": r"\bOnLButtonDown\s*\(\s*UINT\b", "hint": "OnLButtonDown 签名要写 (UINT nFlags, CPoint point)"},
            {"pattern": r"\bOnKeyDown\s*\(\s*UINT\b", "hint": "OnKeyDown 签名要写 (UINT nChar, UINT nRepCnt, UINT nFlags)"},
            {"pattern": r"\bCPoint\b", "hint": "鼠标坐标用 CPoint 接收"},
            {"pattern": r"\bVK_ESCAPE\b", "hint": "按键判断用虚拟键码 VK_ESCAPE"},
        ],
    ),
    # ---------------------------------------------------------------- v07
    _p(
        id="v07",
        slug="font-text",
        title="字体与文本输出（教材第 3 章）",
        topics=["字体", "文本输出"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材第 3 章: 文本输出 = 选字体 + 设颜色 + 输出。"
            "本题要求在窗口正中输出一行红色标题, 背景透明(不盖住底下的内容), "
            "并演示 GDI 对象的完整使用套路(创建 → 选入 → 用 → 恢复)。"
        ),
        require=[
            "创建 20 磅的字体: CFont + CreatePointFont(200, \"宋体\")。",
            "用 SelectObject 把字体选进 DC 并保存旧字体指针。",
            "用 SetTextColor 把文字设为红色(RGB(255, 0, 0))。",
            "用 SetBkMode(TRANSPARENT) 让文字背景透明。",
            "用 DrawText 把 \"Hello, MFC\" 在客户区居中输出(DT_CENTER | DT_VCENTER | DT_SINGLELINE)。",
            "输出完成后把旧字体恢复回去(SelectObject)。",
        ],
        io="图形界面程序: 窗口正中出现一行居中的红色文字。",
        hints=[
            "CreatePointFont(200, ...) 的参数单位是 0.1 磅 —— 200 就是 20 磅。",
            "居中用: CRect rect; GetClientRect(&rect); dc.DrawText(text, &rect, DT_CENTER | ...)。",
            "DT_VCENTER 必须和 DT_SINGLELINE 一起用才有效。",
        ],
        checklist=[
            "CFont 创建后 SetFont/SelectObject 了吗?",
            "SetBkMode(TRANSPARENT) 设了吗?",
            "旧字体恢复了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"字体与文本\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材第 3 章完成 ==================\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    // TODO: 1) 创建 20 磅字体(CFont + CreatePointFont(200, \"宋体\"))\n"
            "    // TODO: 2) SelectObject 选进 DC, 记下旧字体\n"
            "    // TODO: 3) SetTextColor 红色 + SetBkMode(TRANSPARENT)\n"
            "    // TODO: 4) DrawText 把 \"Hello, MFC\" 在客户区居中\n"
            "    // TODO: 5) 恢复旧字体\n"
            "}\n"
            "// ============================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"字体与文本\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    CFont font;\n"
            "    font.CreatePointFont(200, \"宋体\");        // 20 磅(单位是 0.1 磅)\n"
            "    CFont* oldFont = dc.SelectObject(&font);   // 选进 DC 并保存旧字体\n"
            "\n"
            "    dc.SetTextColor(RGB(255, 0, 0));           // 红色文字\n"
            "    dc.SetBkMode(TRANSPARENT);                 // 文字背景透明\n"
            "\n"
            "    CRect rect;\n"
            "    GetClientRect(&rect);                      // 整块客户区\n"
            "    dc.DrawText(\"Hello, MFC\", &rect,\n"
            "                DT_CENTER | DT_VCENTER | DT_SINGLELINE);   // 居中输出\n"
            "\n"
            "    dc.SelectObject(oldFont);                  // 恢复旧字体, 防 GDI 泄漏\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCFont\b", "hint": "要创建 CFont 字体对象"},
            {"pattern": r"\bCreatePointFont\s*\(|\bCreateFont\s*\(", "hint": "用 CreatePointFont/CreateFont 创建字体"},
            {"pattern": r"\bSetTextColor\s*\(", "hint": "用 SetTextColor 设置文字颜色"},
            {"pattern": r"\bSetBkMode\s*\(", "hint": "用 SetBkMode(TRANSPARENT) 让文字背景透明"},
            {"pattern": r"\bDrawText\s*\(", "hint": "用 DrawText 输出文本(支持居中)"},
            {"pattern": r"\bSelectObject\s*\(|\bSetFont\s*\(", "hint": "字体要选进 DC(SelectObject/SetFont)"},
            {"pattern": r"SelectObject\s*\(\s*old", "hint": "用完要把旧字体恢复回去(SelectObject(oldFont))"},
        ],
    ),
    # ---------------------------------------------------------------- v08
    _p(
        id="v08",
        slug="map-mode",
        title="映像模式：按毫米画图（教材 2.3）",
        topics=["映像模式", "绘图"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 2.3: 默认 MM_TEXT 的坐标单位是像素, 换台显示器图的大小就变了。"
            "把映像模式切成 MM_LOMETRIC 后, 1 个逻辑单位 = 0.1 毫米, 图形就有了"
            "真实的物理尺寸。本题要求画一个 40mm×30mm 的矩形和它的对角线。"
        ),
        require=[
            "在 OnPaint 里用 CPaintDC 取设备环境后, 调用 SetMapMode(MM_LOMETRIC)。",
            "画一个 400×300 逻辑单位的矩形(= 40mm × 30mm), 即 Rectangle(100, 100, 500, 400)。",
            "画一条从 (100, 400) 到 (500, 100) 的对角线(MoveTo + LineTo)。",
            "在代码注释里注明「1 逻辑单位 = 0.1 毫米、y 轴向上」, 提醒自己坐标方向变了。",
        ],
        io="图形界面程序: 窗口里出现一个 40mm×30mm 的矩形与它的对角线。",
        hints=[
            "MM_LOMETRIC(公制) 下 100 个单位 = 10 毫米; 40 毫米 = 400 个单位。",
            "注意 y 轴向上: 数值更大的 y 在上方 —— Rectangle 的 top 参数反而更小。",
            "想让图形在任何分辨率下都保持物理尺寸, 这就是正确做法; 只想按像素画就用默认 MM_TEXT。",
        ],
        checklist=[
            "SetMapMode(MM_LOMETRIC) 在画图之前调用了吗?",
            "坐标数值是按 0.1 毫米给的(不是像素)吗?",
            "y 轴方向的口诀记住了吗?(MM_TEXT 向下 / MM_LOMETRIC 向上)",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"映像模式\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 2.3 完成 ==================\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    // TODO: 1) SetMapMode(MM_LOMETRIC)  —— 1 逻辑单位 = 0.1 毫米, y 轴向上\n"
            "    // TODO: 2) 画 40mm x 30mm 的矩形(即 400 x 300 逻辑单位)\n"
            "    // TODO: 3) 画从 (100, 400) 到 (500, 100) 的对角线(MoveTo + LineTo)\n"
            "}\n"
            "// ==========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"映像模式\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    dc.SetMapMode(MM_LOMETRIC);\n"
            "    // 1 逻辑单位 = 0.1 毫米, y 轴向上(与 MM_TEXT 相反)\n"
            "\n"
            "    dc.Rectangle(100, 100, 500, 400);   // 400x300 单位 = 40mm x 30mm\n"
            "\n"
            "    dc.MoveTo(100, 400);                // 对角线: 从左下(y=400 在下) \n"
            "    dc.LineTo(500, 100);                //         到右上(y=100 在上)\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bSetMapMode\s*\(", "hint": "要调用 SetMapMode 切换映像模式"},
            {"pattern": r"\bMM_LOMETRIC\b", "hint": "用公制模式 MM_LOMETRIC(0.1 毫米)"},
            {"pattern": r"\bRectangle\s*\(", "hint": "要画一个矩形"},
            {"pattern": r"\bMoveTo\b[\s\S]*\bLineTo\b", "hint": "用 MoveTo + LineTo 画对角线"},
        ],
    ),
]
