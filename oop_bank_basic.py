#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_bank_basic.py - 第 1 档(基础)题目

这一档只考察“一个类从无到有”的完整过程:
    类定义 → 访问控制 → 构造函数/初始化列表 → 析构函数 → const 成员函数
    → static 成员 → 运算符重载入门

编排约定(所有题库模块共用):
    level      1/2/3
    id         题目编号, 全局唯一
    slug       英文短名, 用于生成工程目录 workspace/<id>-<slug>
    title      中文标题
    topics     知识点标签(用于 list --tag 过滤)
    desc       题目背景
    require    对类/程序的具体要求(逐条)
    io         输入输出规格
    samples    题面样例 [{"in": ..., "out": ...}]
    hints      提示(可空)
    checklist  OOP 自查清单(做题后逐条核对)
    skeleton   给学生填空的 main.cpp 内容
    solution   参考解(完整可编译, 由 `selftest` 命令自动验证)
    tests      自动评测用例 [{"in": ..., "out": ...}]
"""

from __future__ import annotations

from typing import Any, Dict, List

PI = "3.141592653589793"


def _p(**kwargs: Any) -> Dict[str, Any]:
    problem = {
        "level": 1,
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


PROBLEMS: List[Dict[str, Any]] = [
    # ------------------------------------------------------------------ b01
    _p(
        id="b01",
        slug="student-class",
        title="学生类：封装与 const 成员函数",
        topics=["类的定义", "访问控制", "构造函数", "const成员函数"],
        desc=(
            "面向对象的第一步: 把“学生”这个抽象概念变成一段代码。"
            "校园里每个学生都有学号、姓名、成绩, 也有“展示自己信息”的动作 —— "
            "这就是属性(数据成员)与方法(成员函数)。"
            "关键约束是访问控制: 数据必须 private, 只能通过 public 接口访问, "
            "这就是封装。"
        ),
        require=[
            "用 class 定义 Student, 数据成员 id(int)/name(std::string)/score(int) 全部放在 private 区。",
            "提供一个带默认参数的构造函数 Student(int id = 0, const std::string& name = \"\", int score = 0), 并尽量使用成员初始化列表。",
            "提供三个 const 成员函数: int getId() const、const std::string& getName() const、int getScore() const。",
            "提供 void show() const, 输出一行: 学号 姓名 成绩（三者之间用一个空格分隔）。",
        ],
        io="第一行一个整数 n(1 ≤ n ≤ 1000)。接下来 n 行, 每行是 学号 姓名 成绩。输出 n 行, 每行输出对应的 学号 姓名 成绩。",
        samples=[{"in": "2\n1001 Tom 88\n1002 Jerry 95\n", "out": "1001 Tom 88\n1002 Jerry 95\n"}],
        hints=[
            "getter 必须加 const, 否则 const Student 对象(以及 const 引用)调不动它们。",
            "show() 里不要用 std::endl 也行, 用 '\\n' 更快; 两者评测都接受。",
            "成绩用 int 就够了, 本题不需要浮点。",
        ],
        checklist=[
            "数据成员是否全在 private 区?",
            "构造函数是否用了初始化列表而不是在函数体里赋值?",
            "读取数据的成员函数是否都加了 const?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Student 类 ==================
//
// 要求:
//   * 数据成员 id / name / score 全部 private
//   * 构造函数带默认参数, 使用成员初始化列表
//   * getId() / getName() / getScore() 都是 const 成员函数
//   * show() const 输出: 学号 姓名 成绩


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        int id, score;
        string name;
        cin >> id >> name >> score;
        const Student s(id, name, score);
        s.show();
    }
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

class Student {
private:
    int id;
    string name;
    int score;

public:
    Student(int id_ = 0, const string& name_ = "", int score_ = 0)
        : id(id_), name(name_), score(score_) {}

    int getId() const { return id; }
    const string& getName() const { return name; }
    int getScore() const { return score; }

    void show() const {
        cout << id << ' ' << name << ' ' << score << '\\n';
    }
};

int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        int id, score;
        string name;
        cin >> id >> name >> score;
        const Student s(id, name, score);
        s.show();
    }
    return 0;
}
""",
        tests=[
            {"in": "2\n1001 Tom 88\n1002 Jerry 95\n", "out": "1001 Tom 88\n1002 Jerry 95\n"},
            {"in": "1\n7 A 0\n", "out": "7 A 0\n"},
            {"in": "3\n1 aa 100\n2 bb 59\n3 cc 60\n", "out": "1 aa 100\n2 bb 59\n3 cc 60\n"},
        ],
    ),
    # ------------------------------------------------------------------ b02
    _p(
        id="b02",
        slug="date-init-list",
        title="日期类：构造函数初始化列表与闰年判定",
        topics=["构造函数", "初始化列表", "成员函数", "逻辑封装"],
        desc=(
            "为什么必须有构造函数? 因为对象一旦出生就应该处于“合法状态”。"
            "本题把“日期是否合法”和“求下一天”这两件事完整地封装进 Date 类, "
            "外界不需要知道闰年规则, 只需要问对象。"
        ),
        require=[
            "定义 Date 类, 数据成员 year/month/day 为 private int。",
            "构造函数 Date(int y, int m, int d) 必须使用成员初始化列表。",
            "bool valid() const 判断日期是否合法(月份 1-12, 天数符合当月上限, 闰年 2 月 29 天)。",
            "void nextDay() 把日期推进到后一天(非法日期不做任何事)。",
            "std::string toString() const 返回 yyyy-mm-dd（月和日不足两位补 0，年份至少 4 位）。",
        ],
        io="第一行整数 n(1 ≤ n ≤ 2000)。接下来 n 行, 每行 y m d。对每个日期: 合法则输出它的下一天(格式 yyyy-mm-dd), 否则输出 invalid。",
        samples=[{
            "in": "4\n2000 2 28\n2023 2 28\n2024 12 31\n2023 2 29\n",
            "out": "2000-02-29\n2023-03-01\n2025-01-01\ninvalid\n",
        }],
        hints=[
            "闰年规则: 能被 4 整除, 且(不能被 100 整除 或 能被 400 整除)。",
            "用一个 static const int 数组存每月天数, 2 月单独判断最省事。",
            "std::setw(4) / std::setfill('0') 在 <iomanip> 里。注意 setfill 设一次就一直生效。",
        ],
        checklist=[
            "构造函数是否用了初始化列表(而不是函数体内赋值)?",
            "valid() 和 toString() 是否都加了 const?",
            "nextDay() 修改了对象状态, 所以不能加 const —— 你分清楚了吗?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <iomanip>
//   <sstream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Date 类 ==================
//
// 要求:
//   * year / month / day 全部 private
//   * 构造函数 Date(int y, int m, int d) 使用成员初始化列表
//   * bool valid() const
//   * void nextDay()
//   * string toString() const  -> "yyyy-mm-dd"


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        int y, m, d;
        cin >> y >> m >> d;
        Date dt(y, m, d);
        if (!dt.valid()) {
            cout << "invalid" << endl;
        } else {
            dt.nextDay();
            cout << dt.toString() << endl;
        }
    }
    return 0;
}
""",
        solution="""#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
using namespace std;

class Date {
private:
    int year;
    int month;
    int day;

    static bool isLeap(int y) {
        return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
    }

    int daysInMonth() const {
        static const int table[13] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
        if (month == 2 && isLeap(year)) return 29;
        return table[month];
    }

public:
    Date(int y, int m, int d) : year(y), month(m), day(d) {}

    bool valid() const {
        if (year < 1 || month < 1 || month > 12 || day < 1) return false;
        return day <= daysInMonth();
    }

    void nextDay() {
        if (!valid()) return;
        if (++day > daysInMonth()) {
            day = 1;
            if (++month > 12) {
                month = 1;
                ++year;
            }
        }
    }

    string toString() const {
        ostringstream os;
        os << setfill('0') << setw(4) << year << '-'
           << setw(2) << month << '-' << setw(2) << day;
        return os.str();
    }
};

int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        int y, m, d;
        cin >> y >> m >> d;
        Date dt(y, m, d);
        if (!dt.valid()) {
            cout << "invalid" << endl;
        } else {
            dt.nextDay();
            cout << dt.toString() << endl;
        }
    }
    return 0;
}
""",
        tests=[
            {"in": "4\n2000 2 28\n2023 2 28\n2024 12 31\n2023 2 29\n",
             "out": "2000-02-29\n2023-03-01\n2025-01-01\ninvalid\n"},
            {"in": "3\n1900 2 28\n2100 3 1\n2024 2 29\n",
             "out": "1900-03-01\n2100-03-02\n2024-03-01\n"},
            {"in": "3\n2023 13 1\n2023 0 5\n2023 4 31\n", "out": "invalid\ninvalid\ninvalid\n"},
        ],
    ),
    # ------------------------------------------------------------------ b03
    _p(
        id="b03",
        slug="thing-lifecycle",
        title="生命周期三部曲：构造 / 拷贝构造 / 析构",
        topics=["构造函数", "拷贝构造函数", "析构函数", "对象生命周期"],
        desc=(
            "本题是经典的“类定义填空题”: main 已经写好, 你只需要写出 Thing 类。"
            "它要让你亲眼看到 —— 一个对象从出生、被复制、到死亡, 到底调用了什么。"
            "特别注意 `Thing c = b;` 这一行: 它不是赋值, 而是拷贝构造。"
        ),
        require=[
            "只定义 Thing 类, 不要改 main, 也不要自己写 main。",
            "构造函数 Thing(const std::string& name) 输出: create <name>",
            "拷贝构造函数输出: copy <name>",
            "析构函数输出: destroy <name>",
            "每条输出单独占一行。",
        ],
        io="输入一行, 一个不含空白的字符串(对象的名字)。按顺序输出整个生命周期中发生的事件。",
        samples=[{
            "in": "Sam\n",
            "out": "create Sam\ncopy Sam\ncopy Sam\ndestroy Sam\ndestroy Sam\ndestroy Sam\ndone\n",
        }],
        hints=[
            "拷贝构造函数的参数必须是 const Thing&（传值会无限递归）。",
            "同一作用域里, 三个对象的析构顺序与构造顺序相反: c → b → a。",
            "题目要求“每条输出一行”, 用 std::endl 或 '\\n' 都行。",
        ],
        checklist=[
            "拷贝构造函数的形参是不是 const Thing& 引用?",
            "构造函数是不是也用初始化列表保存了 name?",
            "是否理解了 `Thing c = b;` 走的是拷贝构造而不是 operator= ?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Thing 类 ==================
//
// 输出约定(每条各占一行):
//   构造函数      ->  create <name>
//   拷贝构造函数  ->  copy <name>
//   析构函数      ->  destroy <name>


// ================== 以下 main 不要修改 ==================
int main() {
    string name;
    if (!(cin >> name)) return 0;
    {
        Thing a(name);
        Thing b(a);
        Thing c = b;
    }
    cout << "done" << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

class Thing {
private:
    string name_;

public:
    explicit Thing(const string& name) : name_(name) {
        cout << "create " << name_ << endl;
    }

    Thing(const Thing& other) : name_(other.name_) {
        cout << "copy " << name_ << endl;
    }

    ~Thing() {
        cout << "destroy " << name_ << endl;
    }
};

int main() {
    string name;
    if (!(cin >> name)) return 0;
    {
        Thing a(name);
        Thing b(a);
        Thing c = b;
    }
    cout << "done" << endl;
    return 0;
}
""",
        tests=[
            {"in": "Sam\n",
             "out": "create Sam\ncopy Sam\ncopy Sam\ndestroy Sam\ndestroy Sam\ndestroy Sam\ndone\n"},
            {"in": "box\n",
             "out": "create box\ncopy box\ncopy box\ndestroy box\ndestroy box\ndestroy box\ndone\n"},
        ],
    ),
    # ------------------------------------------------------------------ b04
    _p(
        id="b04",
        slug="deep-copy-array",
        title="深拷贝：带指针的数组类",
        topics=["拷贝构造函数", "深拷贝", "动态内存", "析构函数"],
        desc=(
            "编译器默认生成的拷贝构造函数是“逐成员拷贝”, 对指针来说只拷贝了地址 —— "
            "于是两个对象共用同一块内存, 析构时 double free 直接崩。"
            "本题要求你手写拷贝构造, 让 b 拥有自己的独立数组(深拷贝)。"
        ),
        require=[
            "只定义 IntArray 类, 不要改 main。",
            "IntArray(int n): 用 new int[n] 分配 n 个元素并全部初始化为 0（n ≤ 0 时按空数组处理, 不要 new int[0] 之外的花活）。",
            "~IntArray(): 用 delete[] 释放内存。",
            "IntArray(const IntArray& other): 深拷贝(自己 new 一块内存并逐个复制)。",
            "int& operator[](int i): 返回下标引用, 支持 a[i] = x 与 std::cin >> a[i]。",
            "long long sum() const: 返回所有元素之和。",
        ],
        io="第一行整数 n(1 ≤ n ≤ 1000), 第二行 n 个整数。输出两行, 见样例。",
        samples=[{"in": "4\n1 2 3 4\n", "out": "1 0\n10 9\n"}],
        hints=[
            "忘记写拷贝构造 + 有析构函数 = 典型崩溃组合, 这在 C++ 里叫“Rule of Three”。",
            "默认拷贝构造会把 b.data 指到和 a.data 同一块内存, b[0] = 0 会连带改掉 a[0] —— 输出第一行就会变成 `0 0`。",
            "operator[] 不要加 const; 需要 const 版本可以再加一个 `const int& operator[](int) const`。",
        ],
        checklist=[
            "拷贝构造函数里是不是重新 new 了一块内存?",
            "析构函数里是不是 delete[]（而不是 delete）?",
            "如果 a 的 n 是 0, 你的代码会不会崩?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 IntArray 类 ==================
//
// 要求:
//   * IntArray(int n)            分配 n 个 int, 全部置 0
//   * ~IntArray()                delete[] 释放
//   * IntArray(const IntArray&)  深拷贝(自己要 new)
//   * int& operator[](int)       支持 a[i] 读写
//   * long long sum() const      求和


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;
    IntArray a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];
    IntArray b = a;          // 深拷贝: b 必须拥有自己的内存
    b[0] = 0;
    cout << a[0] << " " << b[0] << endl;
    cout << a.sum() << " " << b.sum() << endl;
    return 0;
}
""",
        solution="""#include <iostream>
using namespace std;

class IntArray {
private:
    int* data_;
    int size_;

public:
    explicit IntArray(int n) : data_(nullptr), size_(n > 0 ? n : 0) {
        if (size_ > 0) {
            data_ = new int[size_];
            for (int i = 0; i < size_; ++i) data_[i] = 0;
        }
    }

    IntArray(const IntArray& other) : data_(nullptr), size_(other.size_) {
        if (size_ > 0) {
            data_ = new int[size_];
            for (int i = 0; i < size_; ++i) data_[i] = other.data_[i];
        }
    }

    ~IntArray() {
        delete[] data_;
    }

    int& operator[](int i) { return data_[i]; }
    const int& operator[](int i) const { return data_[i]; }

    int size() const { return size_; }

    long long sum() const {
        long long total = 0;
        for (int i = 0; i < size_; ++i) total += data_[i];
        return total;
    }
};

int main() {
    int n;
    if (!(cin >> n)) return 0;
    IntArray a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];
    IntArray b = a;          // 深拷贝: b 必须拥有自己的内存
    b[0] = 0;
    cout << a[0] << " " << b[0] << endl;
    cout << a.sum() << " " << b.sum() << endl;
    return 0;
}
""",
        tests=[
            {"in": "4\n1 2 3 4\n", "out": "1 0\n10 9\n"},
            {"in": "1\n5\n", "out": "5 0\n5 0\n"},
            {"in": "3\n-1 -2 -3\n", "out": "-1 0\n-6 -5\n"},
            {"in": "5\n100 200 300 400 500\n", "out": "100 0\n1500 1400\n"},
        ],
    ),
    # ------------------------------------------------------------------ b05
    _p(
        id="b05",
        slug="point-const-this",
        title="const 成员函数与值语义：Point",
        topics=["const成员函数", "this指针", "值返回"],
        desc=(
            "main 里写的是 `const Point p(x, y);` —— 一个 const 对象。"
            "只要你的成员函数忘了写 const, 这行就编译不过。"
            "这类“编译期报错”正是 const 的价值: 让编译器帮你证明“这个函数不会改对象”。"
        ),
        require=[
            "只定义 Point 类, 不要改 main。",
            "Point(int x, int y) 使用成员初始化列表。",
            "int x() const 与 int y() const 返回坐标。",
            "Point moveBy(int dx, int dy) const: 返回平移后的**新对象**, 自身坐标保持不变。",
            "double distTo(const Point& other) const: 返回与 other 的欧氏距离。",
        ],
        io="输入一行四个整数 x y dx dy。输出三行: 原点坐标、平移后坐标、两点距离(保留 2 位小数)。",
        samples=[{"in": "0 0 3 4\n", "out": "0 0\n3 4\n5.00\n"}],
        hints=[
            "distTo 里用 std::sqrt, 需要 #include <cmath>。",
            "moveBy 不能改自身, 所以要 return Point(x_ + dx, y_ + dy); —— 这叫值语义。",
            "为什么 moveBy 也要 const? 因为它不修改对象状态, 加上 const 后 const 对象才能调用它。",
        ],
        checklist=[
            "x() / y() / moveBy() / distTo() 四个人是不是都加了 const?",
            "moveBy 有没有误写成修改自身坐标?",
            "构造函数是否用了初始化列表?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <iomanip>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Point 类 ==================
//
// 要求:
//   * Point(int x, int y)              成员初始化列表
//   * int x() const / int y() const
//   * Point moveBy(int dx, int dy) const   返回新点, 自身不变
//   * double distTo(const Point& o) const  欧氏距离


// ================== 以下 main 不要修改 ==================
int main() {
    int x, y, dx, dy;
    if (!(cin >> x >> y >> dx >> dy)) return 0;
    const Point p(x, y);
    Point q = p.moveBy(dx, dy);
    cout << p.x() << " " << p.y() << endl;
    cout << q.x() << " " << q.y() << endl;
    cout << fixed << setprecision(2) << p.distTo(q) << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <iomanip>
#include <cmath>
using namespace std;

class Point {
private:
    int x_;
    int y_;

public:
    Point(int x, int y) : x_(x), y_(y) {}

    int x() const { return x_; }
    int y() const { return y_; }

    Point moveBy(int dx, int dy) const {
        return Point(x_ + dx, y_ + dy);
    }

    double distTo(const Point& other) const {
        double dx = x_ - other.x_;
        double dy = y_ - other.y_;
        return sqrt(dx * dx + dy * dy);
    }
};

int main() {
    int x, y, dx, dy;
    if (!(cin >> x >> y >> dx >> dy)) return 0;
    const Point p(x, y);
    Point q = p.moveBy(dx, dy);
    cout << p.x() << " " << p.y() << endl;
    cout << q.x() << " " << q.y() << endl;
    cout << fixed << setprecision(2) << p.distTo(q) << endl;
    return 0;
}
""",
        tests=[
            {"in": "0 0 3 4\n", "out": "0 0\n3 4\n5.00\n"},
            {"in": "1 1 -1 -1\n", "out": "1 1\n0 0\n1.41\n"},
            {"in": "2 3 0 0\n", "out": "2 3\n2 3\n0.00\n"},
            {"in": "-5 0 5 0\n", "out": "-5 0\n0 0\n5.00\n"},
        ],
    ),
    # ------------------------------------------------------------------ b06
    _p(
        id="b06",
        slug="static-factory",
        title="static 成员：发票流水号工厂",
        topics=["static数据成员", "static成员函数", "静态工厂"],
        desc=(
            "每个对象都要共享同一个“已发号数量”, 这就是 static 数据成员的用途 —— "
            "它属于类, 不属于任何对象。本题还藏着一个陷阱: "
            "std::vector 的 push_back 会拷贝对象, 如果你把计数写在构造函数里, "
            "号会多出来。计数只能在 issue() 这一个入口里发生。"
        ),
        require=[
            "只定义 Ticket 类, 不要改 main。",
            "用 static 数据成员记录已发号总数, 并在类外完成定义(否则链接会报 undefined symbol)。",
            "static Ticket issue(const std::string& name): 静态工厂, 每次调用分配一个从 1 开始递增的流水号。",
            "int serial() const 返回流水号; const std::string& name() const 返回名字。",
            "static int totalIssued() 返回总共发号的数量。",
            "构造函数/拷贝构造函数里**不要**自增计数, 否则 push_back 的拷贝会让 issued 变成 5。",
        ],
        io="第一行整数 n(1 ≤ n ≤ 1000), 第二行 n 个不含空白的字符串。输出 n+1 行, 第一行 issued=<总数>, 之后每行 流水号 名字。",
        samples=[{"in": "3\nalice bob carol\n", "out": "issued=3\n1 alice\n2 bob\n3 carol\n"}],
        hints=[
            "static 数据成员必须在类外再写一行定义: int Ticket::issued_ = 0;（C++17 也可以写 inline static 直接初始化）。",
            "static 成员函数里没有 this, 所以不能访问非静态成员 —— 它只能造对象再返回。",
            "发号顺序 = 调用 issue() 的顺序。",
        ],
        checklist=[
            "类外有没有补上 static 数据成员的定义?",
            "计数是不是只在 issue() 里自增?（拷贝构造里千万别加）",
            "serial() / name() 加了 const 吗?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
//   <vector>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Ticket 类 ==================
//
// 要求:
//   * static Ticket issue(const string& name)   静态工厂, 流水号从 1 递增
//   * int serial() const
//   * const string& name() const
//   * static int totalIssued()
//
// 注意: push_back 会拷贝对象, 所以计数只能发生在 issue() 里!


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<Ticket> v;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        v.push_back(Ticket::issue(s));
    }
    cout << "issued=" << Ticket::totalIssued() << endl;
    for (size_t i = 0; i < v.size(); ++i) {
        cout << v[i].serial() << " " << v[i].name() << endl;
    }
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
#include <vector>
using namespace std;

class Ticket {
private:
    int serial_;
    string name_;

    static int issued_;   // 已发号总数, 属于类而不属于对象

    Ticket(int serial, const string& name) : serial_(serial), name_(name) {}

public:
    static Ticket issue(const string& name) {
        ++issued_;
        return Ticket(issued_, name);
    }

    int serial() const { return serial_; }
    const string& name() const { return name_; }
    static int totalIssued() { return issued_; }
};

int Ticket::issued_ = 0;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<Ticket> v;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        v.push_back(Ticket::issue(s));
    }
    cout << "issued=" << Ticket::totalIssued() << endl;
    for (size_t i = 0; i < v.size(); ++i) {
        cout << v[i].serial() << " " << v[i].name() << endl;
    }
    return 0;
}
""",
        tests=[
            {"in": "3\nalice bob carol\n", "out": "issued=3\n1 alice\n2 bob\n3 carol\n"},
            {"in": "1\nsolo\n", "out": "issued=1\n1 solo\n"},
            {"in": "5\na b c d e\n", "out": "issued=5\n1 a\n2 b\n3 c\n4 d\n5 e\n"},
        ],
    ),
    # ------------------------------------------------------------------ b07
    _p(
        id="b07",
        slug="complex-operator",
        title="运算符重载入门：复数类 Complex",
        topics=["运算符重载", "operator<<", "operator>>", "友元"],
        desc=(
            "运算符重载不是“炫技”, 而是让自定义类型像内置类型一样自然。"
            "有了 + 和 << 之后, `std::cout << (a + b)` 这种写法才成立。"
            "本题要你实现四个运算符: +、-、==、<<（外加读入用的 >>）。"
        ),
        require=[
            "只定义 Complex 类, 不要改 main。",
            "构造函数 Complex(double re = 0, double im = 0)，成员初始化列表。",
            "重载二元 operator+ 与 operator-（都是 const 成员函数, 返回新对象）。",
            "重载 operator== 比较实部与虚部。",
            "重载 operator<<, 输出格式 3+4i / 3-4i（虚部为负时用减号, 不输出 +-）; 虚部为 0 时输出 3+0i 也可以接受, 请按 3+0i 输出。",
            "重载 operator>>, 依次读入两个 double(实部、虚部)。",
        ],
        io="输入一行四个数: a的实部 a的虚部 b的实部 b的虚部。输出三行: a+b、a-b、a==b(0 或 1)。",
        samples=[{"in": "3 4 1 -2\n", "out": "4+2i\n2+6i\n0\n"}],
        hints=[
            "operator<< 想访问 private 的 re/im, 要么写成友元函数, 要么提供 real()/imag() 取值函数。",
            "operator<< 的第一个参数是 std::ostream&, 必须返回这个流对象本身才能链式输出。",
            "判断虚部正负时注意 -0.0 的情况, 不过本题用例不会出现。",
        ],
        checklist=[
            "operator+ / operator- / operator== 是不是都加了 const?",
            "operator<< 返回的是 std::ostream& 而不是 std::ostream 吗?",
            "有没有把 operator+ 写成修改自身(那 a+b 就会改变 a)?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义 Complex 类 ==================
//
// 要求:
//   * Complex(double re = 0, double im = 0)
//   * 重载 + - ==    (const 成员函数)
//   * 重载 operator<<  ->  3+4i / 3-4i / 3+0i
//   * 重载 operator>>  ->  依次读入实部、虚部
//   提示: 输出函数需要访问 private 成员, 可以用 friend。


// ================== 以下 main 不要修改 ==================
int main() {
    Complex a, b;
    if (!(cin >> a >> b)) return 0;
    cout << (a + b) << endl;
    cout << (a - b) << endl;
    cout << (a == b) << endl;
    return 0;
}
""",
        solution="""#include <iostream>
using namespace std;

class Complex {
private:
    double re_;
    double im_;

public:
    Complex(double re = 0, double im = 0) : re_(re), im_(im) {}

    double real() const { return re_; }
    double imag() const { return im_; }

    Complex operator+(const Complex& other) const {
        return Complex(re_ + other.re_, im_ + other.im_);
    }

    Complex operator-(const Complex& other) const {
        return Complex(re_ - other.re_, im_ - other.im_);
    }

    bool operator==(const Complex& other) const {
        return re_ == other.re_ && im_ == other.im_;
    }

    friend ostream& operator<<(ostream& os, const Complex& c) {
        os << c.re_;
        if (c.im_ < 0) os << '-' << -c.im_;
        else os << '+' << c.im_;
        os << 'i';
        return os;
    }

    friend istream& operator>>(istream& is, Complex& c) {
        return is >> c.re_ >> c.im_;
    }
};

int main() {
    Complex a, b;
    if (!(cin >> a >> b)) return 0;
    cout << (a + b) << endl;
    cout << (a - b) << endl;
    cout << (a == b) << endl;
    return 0;
}
""",
        tests=[
            {"in": "3 4 1 -2\n", "out": "4+2i\n2+6i\n0\n"},
            {"in": "1 0 1 0\n", "out": "2+0i\n0+0i\n1\n"},
            {"in": "0 -5 0 5\n", "out": "0+0i\n0-10i\n0\n"},
        ],
    ),
]
