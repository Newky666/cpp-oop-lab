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
            "// ================== TODO: 补全头文件 ==================\n"
            "// 本题需要用到的头文件(请自己补全 #include):\n"
            "//   <iostream>\n"
            "//   <iomanip>\n"
            "// 下面这行 using namespace std; 已帮你写好\n"
            "\n"
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
            "// ================== TODO: 补全头文件 ==================\n"
            "// 本题需要用到的头文件(请自己补全 #include):\n"
            "//   <iostream>\n"
            "// 下面这行 using namespace std; 已帮你写好\n"
            "\n"
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
            "// ================== TODO: 补全头文件 ==================\n"
            "// 本题需要用到的头文件(请自己补全 #include):\n"
            "//   <iostream>\n"
            "//   <string>\n"
            "// 下面这行 using namespace std; 已帮你写好\n"
            "\n"
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
    # ---------------------------------------------------------------- v09
    _p(
        id="v09",
        slug="menu-command",
        title="菜单与命令响应（教材 5.1）",
        topics=["菜单资源", "菜单消息"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 5.1: 菜单项点击发出的是命令消息(WM_COMMAND), 用 ON_COMMAND 把命令 ID "
            "挂到处理函数上。本题不用 .rc 资源文件, 而是用 CMenu 在程序里动态建菜单 —— "
            "教材 7.4 的快捷菜单也是同一套 API。"
        ),
        require=[
            "为菜单命令定义一个命令 ID(如 #define IDM_ABOUT 1001)。",
            "在 OnCreate 里用 CMenu 动态创建菜单: CreateMenu + AppendMenu(MF_STRING, IDM_ABOUT, \"关于\")。",
            "用 SetMenu 把菜单挂到窗口上。",
            "消息映射表里写 ON_COMMAND(IDM_ABOUT, &CMainWnd::OnAbout)。",
            "处理函数 OnAbout 里弹一个 MessageBox 响应点击。",
        ],
        io="图形界面程序: 窗口带一个「关于」菜单, 点击后弹出消息框。",
        hints=[
            "CMenu 建议作为窗口类的成员变量(生命周期跟着窗口走), 局部变量出函数就没了。",
            "MF_STRING 表示这是一个文本菜单项; 想加分隔线用 AppendMenu(MF_SEPARATOR, 0, NULL)。",
            "菜单命令 ID 是普通整数, 只要不与其它 ID 冲突即可。",
        ],
        checklist=[
            "#define 的命令 ID 与 ON_COMMAND 里写的一致吗?",
            "CMenu 对象活到窗口销毁了吗?",
            "SetMenu 挂上窗口了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// TODO: 定义菜单命令 ID(例如 #define IDM_ABOUT 1001)\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"菜单练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    // TODO: 声明 OnAbout(afx_msg void)\n"
            "    CMenu m_menu;                       // 成员: 生命周期随窗口\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    // TODO: 挂上 ON_COMMAND(IDM_ABOUT, &CMainWnd::OnAbout)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 5.1 完成 ==================\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "    // TODO: 1) m_menu.CreateMenu()\n"
            "    // TODO: 2) m_menu.AppendMenu(MF_STRING, IDM_ABOUT, \"关于\")\n"
            "    // TODO: 3) SetMenu(&m_menu)\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "// TODO: 实现 OnAbout: 弹一个 MessageBox\n"
            "// ==========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "#define IDM_ABOUT 1001                  // 菜单命令 ID\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"菜单练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    afx_msg void OnAbout();\n"
            "    CMenu m_menu;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    ON_COMMAND(IDM_ABOUT, &CMainWnd::OnAbout)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "\n"
            "    m_menu.CreateMenu();                             // 动态建菜单\n"
            "    m_menu.AppendMenu(MF_STRING, IDM_ABOUT, \"关于\");\n"
            "    SetMenu(&m_menu);                                // 挂到窗口\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "void CMainWnd::OnAbout()\n"
            "{\n"
            "    MessageBox(\"这是动态创建的菜单项\", \"菜单练习\", MB_OK);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"#define\s+IDM_\w+", "hint": "用 #define 定义菜单命令 ID"},
            {"pattern": r"\bCreateMenu\s*\(|\bCreatePopupMenu\s*\(", "hint": "用 CMenu 动态创建菜单"},
            {"pattern": r"\bAppendMenu\s*\(", "hint": "用 AppendMenu 添加菜单项"},
            {"pattern": r"\bON_COMMAND\s*\(", "hint": "消息映射表里要有 ON_COMMAND(ID, handler)"},
            {"pattern": r"\bSetMenu\s*\(", "hint": "用 SetMenu 把菜单挂到窗口"},
        ],
    ),
    # ---------------------------------------------------------------- v10
    _p(
        id="v10",
        slug="modal-dialog",
        title="模态对话框与 DDX（教材 5.3）",
        topics=["对话框资源", "模态对话框"],
        framework="mfc",
        subsystem="windows",
        needs_resource=True,    # 需要 .rc 资源(IDD/IDC), 纯 main.cpp 只做要点检查
        desc=(
            "教材 5.3: 模态对话框用 DoModal 阻塞运行, 返回 IDOK/IDCANCEL; "
            "控件与成员变量的同步靠 DDX —— UpdateData(TRUE) 把控件值收进变量, "
            "UpdateData(FALSE) 把变量值刷到控件。"
            "本题按教材写法补全一个登录对话框类(资源 ID 来自 resource.h, "
            "真实编译需要在 VS 里用资源编辑器建 .rc, 所以本题按要点检查评分)。"
        ),
        require=[
            "CLoginDlg 派生自 CDialogEx, 构造函数传对话框资源 ID: CDialogEx(IDD_LOGIN)。",
            "成员变量 CString m_user; 在 DoDataExchange 里用 DDX_Text(pDX, IDC_EDIT_USER, m_user) 绑定。",
            "OnInitDialog 先调用 CDialogEx::OnInitDialog(), 再用 SetDlgItemText 预填 \"admin\"。",
            "OnOK 里先 UpdateData(TRUE) 收输入, 再调基类 CDialogEx::OnOK()。",
            "给出使用代码: CLoginDlg dlg; if (dlg.DoModal() == IDOK) { /* 用 dlg.m_user */ }",
        ],
        io="图形界面程序: 弹出模态登录对话框, 点确定后返回输入的用户名。",
        hints=[
            "IDD_LOGIN / IDC_EDIT_USER 由资源编辑器生成在 resource.h 里, 这里按教材习惯 #include \"resource.h\"。",
            "DoModal 的返回值就是 IDOK / IDCANCEL —— 先判断再读成员变量。",
            "非模态对话框不用 DoModal, 而是 Create(IDD, this) + ShowWindow(SW_SHOW); 且对象必须活到关闭。",
        ],
        checklist=[
            "构造函数把资源 ID 传给基类了吗?",
            "DoDataExchange 里调用基类版本了吗?",
            "UpdateData 的方向(TRUE 收 / FALSE 刷)用对了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "#include \"resource.h\"        // IDD_LOGIN / IDC_EDIT_USER 由资源编辑器生成\n"
            "\n"
            "// ================== TODO: 按教材 5.3 补全登录对话框 ==================\n"
            "class CLoginDlg : public CDialogEx {\n"
            "public:\n"
            "    CString m_user;                 // 与编辑框绑定\n"
            "    // TODO: 构造函数: 把 IDD_LOGIN 传给基类\n"
            "    // TODO: OnInitDialog: 调基类 -> 预填 \"admin\"\n"
            "    // TODO: OnOK: UpdateData(TRUE) -> 调基类\n"
            "protected:\n"
            "    // TODO: DoDataExchange: 调基类 -> DDX_Text 绑定 IDC_EDIT_USER\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CLoginDlg, CDialogEx)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// TODO: 写使用代码: CLoginDlg dlg; if (dlg.DoModal() == IDOK) { ... }\n"
            "// ====================================================================\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"对话框练习\"); }\n"
            "    afx_msg void OnOpenDlg();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnOpenDlg()\n"
            "{\n"
            "    CLoginDlg dlg;                                  // 模态: 栈对象正好\n"
            "    if (dlg.DoModal() == IDOK)\n"
            "        SetWindowText(\"欢迎, \" + dlg.m_user);\n"
            "}\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "#include \"resource.h\"\n"
            "\n"
            "class CLoginDlg : public CDialogEx {\n"
            "public:\n"
            "    CString m_user;\n"
            "    CLoginDlg() : CDialogEx(IDD_LOGIN) {}          // 资源 ID 交给基类\n"
            "\n"
            "    virtual BOOL OnInitDialog()\n"
            "    {\n"
            "        CDialogEx::OnInitDialog();                  // 先让基类初始化\n"
            "        SetDlgItemText(IDC_EDIT_USER, \"admin\");     // 预填\n"
            "        return TRUE;\n"
            "    }\n"
            "\n"
            "    virtual void OnOK()\n"
            "    {\n"
            "        UpdateData(TRUE);                           // 控件 -> 成员变量\n"
            "        CDialogEx::OnOK();\n"
            "    }\n"
            "\n"
            "protected:\n"
            "    virtual void DoDataExchange(CDataExchange* pDX)\n"
            "    {\n"
            "        CDialogEx::DoDataExchange(pDX);\n"
            "        DDX_Text(pDX, IDC_EDIT_USER, m_user);       // 绑定编辑框与成员\n"
            "    }\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "\n"
            "BEGIN_MESSAGE_MAP(CLoginDlg, CDialogEx)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"对话框练习\"); }\n"
            "    afx_msg void OnOpenDlg();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnOpenDlg()\n"
            "{\n"
            "    CLoginDlg dlg;                                  // 模态对话框: 栈对象合适\n"
            "    if (dlg.DoModal() == IDOK)                      // 阻塞直到关闭\n"
            "        SetWindowText(\"欢迎, \" + dlg.m_user);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCDialogEx\b|\bCDialog\b", "hint": "对话框类要派生自 CDialogEx/CDialog"},
            {"pattern": r"\bDoModal\b", "hint": "模态对话框用 DoModal 打开"},
            {"pattern": r"\bDoDataExchange\b", "hint": "要实现 DoDataExchange 做 DDX 绑定"},
            {"pattern": r"\bDDX_Text\s*\(", "hint": "用 DDX_Text 绑定控件与成员变量"},
            {"pattern": r"\bUpdateData\s*\(\s*TRUE\s*\)", "hint": "OnOK 里要 UpdateData(TRUE) 收集输入"},
            {"pattern": r"\bOnInitDialog\b", "hint": "要实现 OnInitDialog 做初始化"},
        ],
    ),
    # ---------------------------------------------------------------- v11
    _p(
        id="v11",
        slug="bitmap-bitblt",
        title="位图与 BitBlt（教材 5.2）",
        topics=["位图资源", "BitBlt"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 5.2: 位图不能直接画到窗口 —— 要先进「兼容 DC」中转, 再用 BitBlt 贴到目标 DC。"
            "本题不用资源文件, 用 CreateCompatibleBitmap 在内存里建一块位图, "
            "在它上面画点东西, 再 BitBlt 到窗口上。"
        ),
        require=[
            "创建 CBitmap 并用 CreateCompatibleBitmap(&dc, 200, 100) 建立位图。",
            "用 CDC 的 CreateCompatibleDC(&dc) 建立兼容 DC。",
            "把位图 SelectObject 进兼容 DC(保存旧位图指针)。",
            "在兼容 DC 上画一个矩形(证明内存绘制)。",
            "用 dc.BitBlt(10, 10, 200, 100, &memDC, 0, 0, SRCCOPY) 把位图贴到窗口。",
            "绘制结束后把旧位图 SelectObject 回兼容 DC。",
        ],
        io="图形界面程序: 窗口左上角出现一块从内存位图贴过来的矩形图案。",
        hints=[
            "兼容 DC 是「离屏画布」: 在位图上画完再整块贴到屏幕, 这就是双缓冲的基础。",
            "BitBlt 的参数顺序: 目标 x,y, 宽, 高, 源 DC 指针, 源 x,y, 光栅操作 SRCCOPY。",
            "位图和兼容 DC 都是 GDI 对象, 用完恢复旧对象, 否则句柄泄漏。",
        ],
        checklist=[
            "CBitmap / CreateCompatibleDC / SelectObject / BitBlt 四件套齐了吗?",
            "BitBlt 的宽高与位图尺寸一致吗?",
            "旧位图恢复了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"位图与 BitBlt\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 5.2 完成 ==================\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    // TODO: 1) CBitmap bmp; bmp.CreateCompatibleBitmap(&dc, 200, 100);\n"
            "    // TODO: 2) CDC memDC; memDC.CreateCompatibleDC(&dc);\n"
            "    // TODO: 3) 位图 SelectObject 进 memDC(记住旧位图)\n"
            "    // TODO: 4) 在 memDC 上画一个矩形\n"
            "    // TODO: 5) dc.BitBlt(10, 10, 200, 100, &memDC, 0, 0, SRCCOPY);\n"
            "    // TODO: 6) 恢复旧位图\n"
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
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"位图与 BitBlt\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "\n"
            "    CBitmap bmp;\n"
            "    bmp.CreateCompatibleBitmap(&dc, 200, 100);      // 内存位图\n"
            "    CDC memDC;\n"
            "    memDC.CreateCompatibleDC(&dc);                  // 兼容 DC\n"
            "    CBitmap* oldBmp = memDC.SelectObject(&bmp);     // 位图进兼容 DC\n"
            "\n"
            "    CBrush brush(RGB(0, 128, 255));\n"
            "    CBrush* oldBrush = memDC.SelectObject(&brush);\n"
            "    memDC.Rectangle(0, 0, 199, 99);                 // 在内存里画\n"
            "    memDC.SelectObject(oldBrush);\n"
            "\n"
            "    dc.BitBlt(10, 10, 200, 100, &memDC, 0, 0, SRCCOPY);   // 贴到窗口\n"
            "    memDC.SelectObject(oldBmp);                     // 恢复旧位图\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCBitmap\b", "hint": "要创建 CBitmap 位图对象"},
            {"pattern": r"\bCreateCompatibleDC\s*\(", "hint": "要建立兼容 DC(CreateCompatibleDC)"},
            {"pattern": r"\bCreateCompatibleBitmap\s*\(|\bLoadBitmap\s*\(", "hint": "用 CreateCompatibleBitmap/LoadBitmap 准备位图"},
            {"pattern": r"\bSelectObject\s*\(", "hint": "位图要 SelectObject 进兼容 DC"},
            {"pattern": r"\bBitBlt\s*\(", "hint": "用 BitBlt 把位图贴到窗口 DC"},
            {"pattern": r"SelectObject\s*\(\s*old", "hint": "用完把旧位图恢复回去"},
        ],
    ),
    # ---------------------------------------------------------------- v12
    _p(
        id="v12",
        slug="button-edit",
        title="按钮与编辑框（教材 6.2 / 6.5）",
        topics=["按钮控件", "编辑框"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 6.2/6.5: 控件也是窗口 —— 程序化创建按钮/编辑框, 按钮点击用 ON_BN_CLICKED "
            "映射处理函数, 编辑框内容用 GetDlgItemText/SetDlgItemText 读写。"
            "本题不使用资源编辑器, 全部用代码创建, 所以在自己程序里 #define 控件 ID 即可。"
        ),
        require=[
            "用 #define 定义两个控件 ID(如 IDC_EDIT_NAME / IDC_BTN_HELLO / IDC_STATIC_SHOW)。",
            "在 OnCreate 里创建编辑框(CEdit 或直接用 CreateWindow)与按钮(CButton::Create)。",
            "按钮创建样式包含 WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON。",
            "消息映射表里用 ON_BN_CLICKED(IDC_BTN_HELLO, &CMainWnd::OnHello) 挂按钮点击。",
            "OnHello 里用 GetDlgItemText 取编辑框内容, 拼上问候语后用 SetDlgItemText 显示。",
        ],
        io="图形界面程序: 输入名字点按钮, 结果文本出现在窗口里。",
        hints=[
            "按钮点击通知是 BN_CLICKED, 对应映射宏 ON_BN_CLICKED。",
            "GetDlgItemText(IDC, str) / SetDlgItemText(IDC, str) 是 CWnd 的便捷函数, 不用自己找句柄。",
            "创建控件一定要带 WS_VISIBLE, 否则控件存在但看不见。",
        ],
        checklist=[
            "按钮样式里有 WS_VISIBLE 吗?",
            "ON_BN_CLICKED 的 ID 与创建时传的 ID 一致吗?",
            "取到的文本有没有拼对?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// TODO: #define 控件 ID(IDC_EDIT_NAME / IDC_BTN_HELLO / IDC_STATIC_SHOW)\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"按钮与编辑框\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    // TODO: 声明 OnHello(afx_msg void)\n"
            "    CEdit m_edit;\n"
            "    CButton m_btn;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    // TODO: 挂上 ON_BN_CLICKED(IDC_BTN_HELLO, &CMainWnd::OnHello)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 6.2 / 6.5 完成 ==================\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "    // TODO: 创建编辑框(CRect(20,20,220,50))与按钮(CRect(20,60,120,95))\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "// TODO: 实现 OnHello: GetDlgItemText 取名字 -> 拼接 -> SetDlgItemText\n"
            "// =================================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "#define IDC_EDIT_NAME   2001\n"
            "#define IDC_BTN_HELLO   2002\n"
            "#define IDC_STATIC_SHOW 2003\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"按钮与编辑框\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    afx_msg void OnHello();\n"
            "    CEdit m_edit;\n"
            "    CButton m_btn;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    ON_BN_CLICKED(IDC_BTN_HELLO, &CMainWnd::OnHello)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "\n"
            "    m_edit.Create(WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,\n"
            "                  CRect(20, 20, 220, 50), this, IDC_EDIT_NAME);\n"
            "    m_btn.Create(\"打招呼\", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,\n"
            "                 CRect(20, 60, 120, 95), this, IDC_BTN_HELLO);\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "void CMainWnd::OnHello()\n"
            "{\n"
            "    CString name;\n"
            "    GetDlgItemText(IDC_EDIT_NAME, name);            // 读编辑框\n"
            "    if (name.IsEmpty()) name = \"同学\";\n"
            "    SetDlgItemText(IDC_STATIC_SHOW, \"你好, \" + name + \"!\");   // 显示\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"#define\s+IDC_\w+", "hint": "用 #define 定义控件 ID"},
            {"pattern": r"\bCButton\b|\bCreateWindow\w*\s*\(", "hint": "要创建按钮控件(CButton)"},
            {"pattern": r"\bWS_VISIBLE\b", "hint": "控件样式要包含 WS_VISIBLE"},
            {"pattern": r"\bON_BN_CLICKED\s*\(", "hint": "用 ON_BN_CLICKED 挂按钮点击"},
            {"pattern": r"\bGetDlgItemText\s*\(", "hint": "用 GetDlgItemText 读编辑框内容"},
        ],
    ),
    # ---------------------------------------------------------------- v13
    _p(
        id="v13",
        slug="listbox-sel",
        title="列表框与选择变化（教材 6.6）",
        topics=["列表框控件", "组合框控件"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 6.6: 列表框用 AddString 装数据, GetCurSel 取当前选中(没选中返回 LB_ERR), "
            "GetLBText 把文本取出来; 选中变化会发 LBN_SELCHANGE 通知。"
            "本题做一个「选语言」列表框: 选中后把结果展示出来。"
        ),
        require=[
            "用 #define 定义列表框与显示控件的 ID。",
            "在 OnCreate 里创建列表框(CListBox::Create, 样式含 WS_VISIBLE | LBS_NOTIFY)。",
            "用 AddString 至少装入三项(如 C++ / C# / Python)。",
            "消息映射表里挂 ON_LBN_SELCHANGE(IDC_LIST_LANG, &CMainWnd::OnSelChange)。",
            "OnSelChange 里 GetCurSel 先判 LB_ERR, 再 GetLBText 取文本并显示。",
        ],
        io="图形界面程序: 列表里选择一项, 窗口里显示选中项。",
        hints=[
            "创建列表框的样式: WS_CHILD | WS_VISIBLE | WS_BORDER | LBS_NOTIFY —— 没有 LBS_NOTIFY 收不到选中通知。",
            "GetCurSel() == LB_ERR 表示当前没有选中项, 必须先判断。",
            "SetCurSel(0) 可以预先选中第一项。",
        ],
        checklist=[
            "列表框创建样式里有 LBS_NOTIFY 吗?",
            "取选中前判 LB_ERR 了吗?",
            "ON_LBN_SELCHANGE 的 ID 与创建一致吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// TODO: #define IDC_LIST_LANG / IDC_STATIC_SHOW\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"列表框练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    // TODO: 声明 OnSelChange(afx_msg void)\n"
            "    CListBox m_list;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    // TODO: 挂上 ON_LBN_SELCHANGE(IDC_LIST_LANG, &CMainWnd::OnSelChange)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 6.6 完成 ==================\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "    // TODO: 创建列表框并 AddString 三项(C++ / C# / Python)\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "// TODO: 实现 OnSelChange: GetCurSel 判 LB_ERR -> GetLBText -> 显示\n"
            "// ===========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "#define IDC_LIST_LANG   3001\n"
            "#define IDC_STATIC_SHOW 3002\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"列表框练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    afx_msg void OnSelChange();\n"
            "    CListBox m_list;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    ON_LBN_SELCHANGE(IDC_LIST_LANG, &CMainWnd::OnSelChange)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "\n"
            "    m_list.Create(WS_CHILD | WS_VISIBLE | WS_BORDER | LBS_NOTIFY,\n"
            "                  CRect(20, 20, 220, 200), this, IDC_LIST_LANG);\n"
            "    m_list.AddString(\"C++\");\n"
            "    m_list.AddString(\"C#\");\n"
            "    m_list.AddString(\"Python\");\n"
            "    m_list.SetCurSel(0);                            // 预选第一项\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "void CMainWnd::OnSelChange()\n"
            "{\n"
            "    int index = m_list.GetCurSel();\n"
            "    if (index == LB_ERR)                            // 先判 -1\n"
            "        return;\n"
            "    CString text;\n"
            "    m_list.GetLBText(index, text);\n"
            "    SetDlgItemText(IDC_STATIC_SHOW, \"你选了: \" + text);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCListBox\b", "hint": "要创建 CListBox 列表框"},
            {"pattern": r"\bAddString\s*\(", "hint": "用 AddString 装入列表项"},
            {"pattern": r"\bGetCurSel\s*\(", "hint": "用 GetCurSel 取当前选中"},
            {"pattern": r"\bLB_ERR\b", "hint": "取选中项前要判 LB_ERR(-1)"},
            {"pattern": r"\bON_LBN_SELCHANGE\s*\(", "hint": "用 ON_LBN_SELCHANGE 挂选中变化"},
            {"pattern": r"\bLBS_NOTIFY\b|\bLBS_SORT\b", "hint": "列表框样式要通知位(LBS_NOTIFY)"},
        ],
    ),
    # ---------------------------------------------------------------- v14
    _p(
        id="v14",
        slug="progress-timer",
        title="进度条与定时器（教材 6.8）",
        topics=["进度条", "滚动条控件"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 6.3/6.8: 进度条围绕「范围 + 位置」工作(SetRange32 / SetPos); "
            "让它动起来最常见的办法是 SetTimer + OnTimer 定时推进。"
            "本题做一个循环推进的进度条。"
        ),
        require=[
            "用 #define 定义进度条的 ID。",
            "在 OnCreate 里创建进度条(CProgressCtrl::Create)。",
            "用 SetRange32(0, 100) 设置范围。",
            "用 SetTimer(1, 100, NULL) 启动 100ms 的定时器。",
            "消息映射表里挂 ON_WM_TIMER(); 在 OnTimer 里用 GetPos/SetPos 推进进度(取模循环)。",
        ],
        io="图形界面程序: 窗口里的进度条每 100ms 前进一格, 满了从头再来。",
        hints=[
            "SetTimer(1, 100, NULL) 的第一个参数是定时器 ID, OnTimer 的 nIDEvent 就是它。",
            "推进用 m_progress.SetPos((m_progress.GetPos() + 5) % 105) 之类的取模, 避免超出范围。",
            "OnTimer 处理完记得调用基类的 CFrameWnd::OnTimer(nIDEvent)。",
        ],
        checklist=[
            "SetRange32 与 SetPos 都写了吗?",
            "ON_WM_TIMER 挂了吗? OnTimer 里判了定时器 ID 吗?",
            "SetPos 的值会超出上限吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// TODO: #define IDC_PROGRESS 4001\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"进度条练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    afx_msg void OnTimer(UINT_PTR nIDEvent);\n"
            "    CProgressCtrl m_progress;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    ON_WM_TIMER()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 6.8 完成 ==================\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "    // TODO: 创建进度条 + SetRange32(0, 100) + SetTimer(1, 100, NULL)\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "// TODO: 实现 OnTimer: 推进 m_progress 的位置(取模循环), 并调用基类\n"
            "// ==========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "#define IDC_PROGRESS 4001\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"进度条练习\"); }\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    afx_msg void OnTimer(UINT_PTR nIDEvent);\n"
            "    CProgressCtrl m_progress;\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "    ON_WM_TIMER()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "int CMainWnd::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "\n"
            "    m_progress.Create(WS_CHILD | WS_VISIBLE,\n"
            "                      CRect(20, 20, 320, 45), this, IDC_PROGRESS);\n"
            "    m_progress.SetRange32(0, 100);                  // 范围 0~100\n"
            "    SetTimer(1, 100, NULL);                         // 100ms 定时器\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "void CMainWnd::OnTimer(UINT_PTR nIDEvent)\n"
            "{\n"
            "    if (nIDEvent == 1) {\n"
            "        int pos = m_progress.GetPos() + 5;\n"
            "        if (pos > 100) pos = 0;                     // 取模循环\n"
            "        m_progress.SetPos(pos);\n"
            "    }\n"
            "    CFrameWnd::OnTimer(nIDEvent);                   // 交回基类\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bCProgressCtrl\b", "hint": "要用 CProgressCtrl 进度条控件"},
            {"pattern": r"\bSetRange32\s*\(|\bSetRange\s*\(", "hint": "用 SetRange32/SetRange 设置进度范围"},
            {"pattern": r"\bSetPos\s*\(", "hint": "用 SetPos 推进进度位置"},
            {"pattern": r"\bSetTimer\s*\(", "hint": "用 SetTimer 启动定时器"},
            {"pattern": r"\bON_WM_TIMER\b", "hint": "消息映射表里要有 ON_WM_TIMER()"},
            {"pattern": r"\bOnTimer\b", "hint": "要实现 OnTimer 响应定时器"},
        ],
    ),
    # ---------------------------------------------------------------- v15
    _p(
        id="v15",
        slug="doc-view-serialize",
        title="文档视图与串行化（教材 7.1~7.2）",
        topics=["文档视图", "串行化"],
        framework="mfc",
        subsystem="windows",
        needs_resource=True,    # 文档模板要用 IDR_MAINFRAME 资源
        desc=(
            "教材 7.1: SDI 程序把数据放文档(CDocument)、显示放视图(CView), "
            "存盘/读盘统一走 Serialize(CArchive)。本题按教材结构补全一个便签程序: "
            "文档负责数据与串行化, 视图负责显示与取文档。"
            "(完整 SDI 工程的文档模板要用到 IDR_MAINFRAME 资源, 所以本题按要点检查评分。)"
        ),
        require=[
            "文档类 CNoteDoc 派生自 CDocument, 含数据成员 CString m_text 与 int m_count。",
            "重写 Serialize(CArchive& ar): 用 ar.IsStoring() 判断方向, 存为 `ar << m_text << m_count`。",
            "读盘用同样的顺序 `ar >> m_text >> m_count`(顺序必须与存盘一致)。",
            "视图类 CNoteView 派生自 CView, 提供 CNoteDoc* GetDocument() 返回 (CNoteDoc*)m_pDocument。",
            "在视图的 OnDraw 里通过 GetDocument() 取数据并显示(比如 TextOut)。",
        ],
        io="图形界面程序: SDI 便签; 新建/打开/保存走 MFC 框架, 数据格式由 Serialize 决定。",
        hints=[
            "文档类里别忘了 DECLARE_DYNCREATE / IMPLEMENT_DYNCREATE(框架要靠它动态创建文档);",
            "Serialize 是个虚函数, 重写时签名必须一模一样: virtual void Serialize(CArchive& ar)。",
            "GetDocument() 是 MFC 向导在视图里生成的模式, 内部就是强转 m_pDocument。",
        ],
        checklist=[
            "数据成员放在文档类里了吗?",
            "Serialize 的读写顺序对称吗? IsStoring 判断了吗?",
            "视图通过 GetDocument() 取文档而不是自己存数据吧?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// ================== TODO: 按教材 7.1 补全文档类与视图类 ==================\n"
            "class CNoteDoc : public CDocument {\n"
            "public:\n"
            "    CString m_text;                 // 数据: 便签内容\n"
            "    int m_count;                    // 数据: 字数\n"
            "    // TODO: 重写 Serialize(CArchive& ar): IsStoring 分支, 读写顺序一致\n"
            "    DECLARE_DYNCREATE(CNoteDoc)\n"
            "};\n"
            "\n"
            "class CNoteView : public CView {\n"
            "public:\n"
            "    // TODO: GetDocument(): 返回 (CNoteDoc*)m_pDocument\n"
            "    // TODO: OnDraw(CDC* pDC): 取文档数据, 用 pDC->TextOut 显示\n"
            "};\n"
            "// ==========================================================================\n"
            "\n"
            "#include \"resource.h\"      // IDR_MAINFRAME(文档模板要用的菜单/图标资源)\n"
            "class CNoteApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "BOOL CNoteApp::InitInstance()\n"
            "{\n"
            "    CSingleDocTemplate* tmpl = new CSingleDocTemplate(\n"
            "        IDR_MAINFRAME, RUNTIME_CLASS(CNoteDoc),\n"
            "        RUNTIME_CLASS(CFrameWnd), RUNTIME_CLASS(CNoteView));\n"
            "    AddDocTemplate(tmpl);               // 不注册文档模板, 程序起不来\n"
            "    return CWinApp::InitInstance();\n"
            "}\n"
            "CNoteApp theApp;\n"
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "class CNoteDoc : public CDocument {\n"
            "public:\n"
            "    CString m_text;\n"
            "    int m_count = 0;\n"
            "\n"
            "    virtual void Serialize(CArchive& ar)\n"
            "    {\n"
            "        if (ar.IsStoring())\n"
            "            ar << m_text << m_count;        // 存盘\n"
            "        else\n"
            "            ar >> m_text >> m_count;        // 读盘: 同样的顺序\n"
            "    }\n"
            "    DECLARE_DYNCREATE(CNoteDoc)\n"
            "};\n"
            "IMPLEMENT_DYNCREATE(CNoteDoc, CDocument)\n"
            "\n"
            "class CNoteView : public CView {\n"
            "public:\n"
            "    CNoteDoc* GetDocument() { return (CNoteDoc*)m_pDocument; }\n"
            "    virtual void OnDraw(CDC* pDC)\n"
            "    {\n"
            "        CNoteDoc* doc = GetDocument();\n"
            "        pDC->TextOut(20, 20, doc->m_text);  // 显示文档里的数据\n"
            "    }\n"
            "    DECLARE_DYNCREATE(CNoteView)\n"
            "};\n"
            "IMPLEMENT_DYNCREATE(CNoteView, CView)\n"
            "\n"
            "#include \"resource.h\"\n"
            "class CNoteApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "BOOL CNoteApp::InitInstance()\n"
            "{\n"
            "    CSingleDocTemplate* tmpl = new CSingleDocTemplate(\n"
            "        IDR_MAINFRAME, RUNTIME_CLASS(CNoteDoc),\n"
            "        RUNTIME_CLASS(CFrameWnd), RUNTIME_CLASS(CNoteView));\n"
            "    AddDocTemplate(tmpl);\n"
            "    return CWinApp::InitInstance();\n"
            "}\n"
            "CNoteApp theApp;\n"
        ),
        checks=[
            {"pattern": r"\bCDocument\b", "hint": "文档类要派生自 CDocument"},
            {"pattern": r"\bCView\b", "hint": "视图类要派生自 CView"},
            {"pattern": r"\bSerialize\s*\(\s*CArchive\s*&", "hint": "要重写 Serialize(CArchive& ar)"},
            {"pattern": r"\bIsStoring\b", "hint": "用 ar.IsStoring() 区分存盘/读盘"},
            {"pattern": r"\bGetDocument\s*\(", "hint": "视图里要提供 GetDocument()"},
            {"pattern": r"\bCSingleDocTemplate\b|\bCMultiDocTemplate\b", "hint": "SDI 用 CSingleDocTemplate 注册文档模板"},
        ],
    ),
    # ---------------------------------------------------------------- v16
    _p(
        id="v16",
        slug="context-menu",
        title="快捷菜单与命令响应（教材 7.3~7.4）",
        topics=["快捷菜单", "命令路由"],
        framework="mfc",
        subsystem="windows",
        desc=(
            "教材 7.4: 右键快捷菜单的核心是 TrackPopupMenu —— 用 CMenu 动态建(或 LoadMenu 加载)"
            "一个弹出菜单, 在鼠标位置弹出来, 菜单项照旧用 ON_COMMAND 响应。"
            "本题不用资源文件, 全部动态创建。"
        ),
        require=[
            "处理 WM_CONTEXTMENU 消息: afx_msg void OnContextMenu(CWnd* pWnd, CPoint point);",
            "消息映射表里加 ON_WM_CONTEXTMENU()。",
            "在 OnContextMenu 里用 CMenu::CreatePopupMenu 创建菜单, AppendMenu 添加两项(关于/退出)。",
            "用 menu.TrackPopupMenu(TPM_RIGHTBUTTON, point.x, point.y, this) 在鼠标处弹出。",
            "两个菜单项分别用 ON_COMMAND(IDM_ABOUT, ...) / ON_COMMAND(IDM_QUIT, ...) 响应。",
        ],
        io="图形界面程序: 窗口里点右键弹出快捷菜单, 选「关于」弹消息框、选「退出」关窗口。",
        hints=[
            "OnContextMenu 的 point 参数**已经是屏幕坐标**, 直接传给 TrackPopupMenu 即可(不用再转换)。",
            "CMenu 局部对象在 TrackPopupMenu 返回后再析构是安全的(弹出期间函数阻塞)。",
            "MF_SEPARATOR 加分隔线: AppendMenu(MF_SEPARATOR, 0, NULL)。",
        ],
        checklist=[
            "ON_WM_CONTEXTMENU 与 ON_COMMAND 都挂了吗?",
            "TrackPopupMenu 的坐标用的是 point(屏幕坐标)吗?",
            "TPM_RIGHTBUTTON 标志加了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "\n"
            "// TODO: #define IDM_ABOUT 6001 / IDM_QUIT 6002\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"快捷菜单练习\"); }\n"
            "    // TODO: 声明 OnContextMenu(CWnd*, CPoint) / OnAbout() / OnQuit()\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    // TODO: ON_WM_CONTEXTMENU() 与两个 ON_COMMAND\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材 7.4 完成 ==================\n"
            "// void CMainWnd::OnContextMenu(CWnd* pWnd, CPoint point)\n"
            "//   CMenu menu; menu.CreatePopupMenu();\n"
            "//   menu.AppendMenu(MF_STRING, IDM_ABOUT, \"关于\");\n"
            "//   menu.AppendMenu(MF_SEPARATOR, 0, NULL);\n"
            "//   menu.AppendMenu(MF_STRING, IDM_QUIT, \"退出\");\n"
            "//   menu.TrackPopupMenu(TPM_RIGHTBUTTON, point.x, point.y, this);\n"
            "// void CMainWnd::OnAbout()  -> MessageBox\n"
            "// void CMainWnd::OnQuit()   -> PostMessage(WM_CLOSE)\n"
            "// ===========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "\n"
            "#define IDM_ABOUT 6001\n"
            "#define IDM_QUIT  6002\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"快捷菜单练习\"); }\n"
            "    afx_msg void OnContextMenu(CWnd* pWnd, CPoint point);\n"
            "    afx_msg void OnAbout();\n"
            "    afx_msg void OnQuit();\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_CONTEXTMENU()\n"
            "    ON_COMMAND(IDM_ABOUT, &CMainWnd::OnAbout)\n"
            "    ON_COMMAND(IDM_QUIT, &CMainWnd::OnQuit)\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnContextMenu(CWnd* /*pWnd*/, CPoint point)\n"
            "{\n"
            "    CMenu menu;\n"
            "    menu.CreatePopupMenu();                 // 动态建弹出菜单\n"
            "    menu.AppendMenu(MF_STRING, IDM_ABOUT, \"关于\");\n"
            "    menu.AppendMenu(MF_SEPARATOR, 0, NULL);\n"
            "    menu.AppendMenu(MF_STRING, IDM_QUIT, \"退出\");\n"
            "    menu.TrackPopupMenu(TPM_RIGHTBUTTON, point.x, point.y, this);\n"
            "    // point 本身就是屏幕坐标, 直接使用\n"
            "}\n"
            "\n"
            "void CMainWnd::OnAbout()\n"
            "{\n"
            "    MessageBox(\"这是右键菜单里的‘关于’\", \"提示\", MB_OK);\n"
            "}\n"
            "\n"
            "void CMainWnd::OnQuit()\n"
            "{\n"
            "    PostMessage(WM_CLOSE);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bON_WM_CONTEXTMENU\b", "hint": "消息映射表里要有 ON_WM_CONTEXTMENU()"},
            {"pattern": r"\bOnContextMenu\b", "hint": "要实现 OnContextMenu 处理函数"},
            {"pattern": r"\bCreatePopupMenu\s*\(|\bLoadMenu\s*\(", "hint": "要创建弹出菜单(CreatePopupMenu/LoadMenu)"},
            {"pattern": r"\bTrackPopupMenu\s*\(", "hint": "用 TrackPopupMenu 弹出菜单"},
            {"pattern": r"\bTPM_RIGHTBUTTON\b", "hint": "TrackPopupMenu 用 TPM_RIGHTBUTTON 标志"},
            {"pattern": r"\bON_COMMAND\s*\(", "hint": "菜单项用 ON_COMMAND 响应"},
        ],
    ),
    # ---------------------------------------------------------------- v17
    _p(
        id="v17",
        slug="multimedia-sound",
        title="多媒体：播放声音（教材第 8 章）",
        topics=["多媒体", "音频"],
        framework="mfc",
        subsystem="windows",
        libs=["winmm.lib"],
        desc=(
            "教材第 8 章: 最简单的音频播放是 PlaySound —— 一行代码异步播放 wav; "
            "播放、停止都用它; 更复杂的控制(定位/循环/更多格式)用 MCI 的 mciSendString。"
            "本题用左右键/按键演示播放与停止(播放系统声音别名, 不需要音频文件)。"
        ),
        require=[
            "在文件顶部用 #pragma comment(lib, \"winmm.lib\") 链接多媒体库(或工程里加 winmm.lib)。",
            "鼠标左键按下(OnLButtonDown)时用 PlaySound 播放: PlaySound(\"SystemStart\", NULL, SND_ALIAS | SND_ASYNC)。",
            "按 Esc(OnKeyDown 里判断 VK_ESCAPE)时用 PlaySound(NULL, NULL, SND_PURGE) 停止播放。",
            "在注释里写出播放真实音频文件的写法: PlaySound(路径, NULL, SND_FILENAME | SND_ASYNC)。",
            "两个处理函数都要在消息映射表里挂上(ON_WM_LBUTTONDOWN / ON_WM_KEYDOWN)。",
        ],
        io="图形界面程序: 左键点击播放系统声音, 按 Esc 停止。",
        hints=[
            "SND_ASYNC 是异步播放(不卡住界面); SND_SYNC 会阻塞, 长音频千万别用。",
            "SND_ALIAS 表示「第一个参数是系统声音别名」(如 SystemStart/SystemAsterisk), 不需要文件。",
            "忘了链接 winmm.lib 会报 LNK2019: unresolved external symbol PlaySound。",
        ],
        checklist=[
            "#pragma comment(lib, \"winmm.lib\") 写了吗?",
            "用的是 SND_ASYNC 吗?",
            "停止用 SND_PURGE 了吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "// TODO: #pragma comment(lib, \"winmm.lib\")\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"多媒体练习\"); }\n"
            "    // TODO: 声明 OnLButtonDown(UINT, CPoint) 与 OnKeyDown(UINT, UINT, UINT)\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    // TODO: ON_WM_LBUTTONDOWN() 与 ON_WM_KEYDOWN()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "// ================== TODO: 按教材第 8 章完成 ==================\n"
            "// OnLButtonDown: PlaySound(\"SystemStart\", NULL, SND_ALIAS | SND_ASYNC);\n"
            "// OnKeyDown:     if (nChar == VK_ESCAPE) PlaySound(NULL, NULL, SND_PURGE);\n"
            "//                (记得 CFrameWnd::OnKeyDown(...) 交回基类)\n"
            "// =========================================================\n"
            + _APP_TAIL
        ),
        solution=(
            "#include <afxwin.h>\n"
            "#pragma comment(lib, \"winmm.lib\")      // 多媒体函数(PlaySound/mciSendString)所在库\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"多媒体练习\"); }\n"
            "    afx_msg void OnLButtonDown(UINT nFlags, CPoint point);\n"
            "    afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)\n"
            "    ON_WM_LBUTTONDOWN()\n"
            "    ON_WM_KEYDOWN()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "void CMainWnd::OnLButtonDown(UINT nFlags, CPoint point)\n"
            "{\n"
            "    // 播放系统声音(不需要音频文件):\n"
            "    PlaySound(\"SystemStart\", NULL, SND_ALIAS | SND_ASYNC);\n"
            "    // 播放真实文件时这样写:\n"
            "    // PlaySound(\"C:\\\\music\\\\bgm.wav\", NULL, SND_FILENAME | SND_ASYNC);\n"
            "    CFrameWnd::OnLButtonDown(nFlags, point);\n"
            "}\n"
            "\n"
            "void CMainWnd::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)\n"
            "{\n"
            "    if (nChar == VK_ESCAPE)\n"
            "        PlaySound(NULL, NULL, SND_PURGE);   // 停止当前播放\n"
            "    CFrameWnd::OnKeyDown(nChar, nRepCnt, nFlags);\n"
            "}\n"
            + _APP_TAIL
        ),
        checks=[
            {"pattern": r"\bPlaySound\s*\(", "hint": "用 PlaySound 播放声音"},
            {"pattern": r"\bSND_ASYNC\b", "hint": "用 SND_ASYNC 异步播放(不卡界面)"},
            {"pattern": r"\bSND_PURGE\b", "hint": "用 SND_PURGE 停止播放"},
            {"pattern": r"winmm\.lib", "hint": "要链接 winmm.lib(否则 LNK2019)"},
            {"pattern": r"\bSND_FILENAME\b", "hint": "注释里给出播放文件的写法(SND_FILENAME)", "required": False},
            {"pattern": r"\bmciSendString\b", "hint": "进阶: 也可用 MCI 的 mciSendString", "required": False},
        ],
    ),
    # ---------------------------------------------------------------- v18
    _p(
        id="v18",
        slug="toolbar-statusbar",
        title="工具条与状态栏（教材 7.5）",
        topics=["工具条", "状态栏"],
        framework="mfc",
        subsystem="windows",
        needs_resource=True,    # 工具条的按钮位图来自资源(IDR_MAINFRAME)
        desc=(
            "教材 7.5: 工具条(CToolBar)的按钮位图与状态栏(CStatusBar)的窗格都由资源定义 —— "
            "CreateEx 创建、LoadToolBar 加载、SetIndicators 设置窗格。"
            "工具条按钮和菜单共用命令 ID, 点击走的还是 ON_COMMAND。"
            "(工具条需要位图资源, 纯 main.cpp 按要点检查评分。)"
        ),
        require=[
            "主框架类里声明两个成员: CToolBar m_toolbar; 与 CStatusBar m_status;。",
            "在 OnCreate 里用 m_toolbar.CreateEx(this, TBSTYLE_FLAT, WS_CHILD | WS_VISIBLE | CBRS_TOP) 创建工具条。",
            "用 m_toolbar.LoadToolBar(IDR_MAINFRAME) 加载工具条资源(位图在 .rc 里)。",
            "用 m_status.Create(this) 创建状态栏, 再用 SetIndicators(indicators, 3) 设置窗格。",
            "指示器数组里至少包含 ID_SEPARATOR 与两个状态窗格(如 ID_INDICATOR_CAPS / ID_INDICATOR_NUM)。",
        ],
        io="图形界面程序: 窗口顶部有工具条、底部有状态栏(窗格显示 Caps/Num 状态)。",
        hints=[
            "CBRS_TOP 让工具条停靠在窗口顶部; 其它常用值还有 CBRS_BOTTOM/CBRS_FLYBY。",
            "工具条按钮的 ID 由 IDR_MAINFRAME 位图资源顺序决定, 与命令 ID 一一对应。",
            "indicator 数组必须是 static 的(CStatusBar 内部会长期引用它)。",
        ],
        checklist=[
            "CreateEx 的样式含 CBRS_TOP 与 WS_VISIBLE 吗?",
            "LoadToolBar / SetIndicators 都调用了吗?",
            "indicators 数组是 static 吗?",
        ],
        skeleton=(
            "#include <afxwin.h>\n"
            "#include \"resource.h\"      // IDR_MAINFRAME / ID_INDICATOR_* 在资源头文件里\n"
            "\n"
            "// ================== TODO: 按教材 7.5 补全主框架类 ==================\n"
            "class CMainFrame : public CFrameWnd {\n"
            "public:\n"
            "    CMainFrame() { Create(NULL, \"工具条与状态栏\"); }\n"
            "    // TODO: 声明成员 CToolBar m_toolbar; CStatusBar m_status;\n"
            "    // TODO: 声明并实现 afx_msg int OnCreate(LPCREATESTRUCT);\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "// BEGIN_MESSAGE_MAP 里记得 ON_WM_CREATE()\n"
            "\n"
            "// int CMainFrame::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "// {\n"
            "//     if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "//     TODO: 1) CreateEx 创建工具条\n"
            "//     TODO: 2) LoadToolBar(IDR_MAINFRAME)\n"
            "//     TODO: 3) m_status.Create(this) + SetIndicators(indicators, 3)\n"
            "//     return 0;\n"
            "// }\n"
            "// ==================================================================\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "BOOL CMyApp::InitInstance()\n"
            "{\n"
            "    m_pMainWnd = new CMainFrame();\n"
            "    m_pMainWnd->ShowWindow(SW_SHOW);\n"
            "    m_pMainWnd->UpdateWindow();\n"
            "    return TRUE;\n"
            "}\n"
            "CMyApp theApp;\n"
        ),
        solution=(
            "#include <afxwin.h>\n"
            "#include \"resource.h\"\n"
            "\n"
            "class CMainFrame : public CFrameWnd {\n"
            "public:\n"
            "    CMainFrame() { Create(NULL, \"工具条与状态栏\"); }\n"
            "    CToolBar m_toolbar;                 // 工具条\n"
            "    CStatusBar m_status;                // 状态栏\n"
            "    afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainFrame, CFrameWnd)\n"
            "    ON_WM_CREATE()\n"
            "END_MESSAGE_MAP()\n"
            "\n"
            "int CMainFrame::OnCreate(LPCREATESTRUCT lpCreateStruct)\n"
            "{\n"
            "    if (CFrameWnd::OnCreate(lpCreateStruct) == -1) return -1;\n"
            "\n"
            "    m_toolbar.CreateEx(this, TBSTYLE_FLAT,\n"
            "                       WS_CHILD | WS_VISIBLE | CBRS_TOP);\n"
            "    m_toolbar.LoadToolBar(IDR_MAINFRAME);       // 按钮位图来自资源\n"
            "\n"
            "    m_status.Create(this);\n"
            "    static UINT indicators[] = {\n"
            "        ID_SEPARATOR, ID_INDICATOR_CAPS, ID_INDICATOR_NUM\n"
            "    };\n"
            "    m_status.SetIndicators(indicators, 3);\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "class CMyApp : public CWinApp {\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "BOOL CMyApp::InitInstance()\n"
            "{\n"
            "    m_pMainWnd = new CMainFrame();\n"
            "    m_pMainWnd->ShowWindow(SW_SHOW);\n"
            "    m_pMainWnd->UpdateWindow();\n"
            "    return TRUE;\n"
            "}\n"
            "CMyApp theApp;\n"
        ),
        checks=[
            {"pattern": r"\bCToolBar\b", "hint": "要用 CToolBar 工具条类"},
            {"pattern": r"\bLoadToolBar\s*\(|\bLoadBitmap\s*\(", "hint": "用 LoadToolBar 加载工具条资源"},
            {"pattern": r"\bCreateEx\s*\(", "hint": "用 CreateEx 创建工具条并指定停靠样式"},
            {"pattern": r"\bCBRS_TOP\b", "hint": "工具条停靠样式用 CBRS_TOP"},
            {"pattern": r"\bCStatusBar\b", "hint": "要用 CStatusBar 状态栏类"},
            {"pattern": r"\bSetIndicators\s*\(", "hint": "用 SetIndicators 设置状态栏窗格"},
        ],
    ),
]
