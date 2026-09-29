#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_bank_adv.py - 第 2 档(进阶)题目

这一档进入面向对象的真正核心:
    拷贝控制(拷贝构造 / 拷贝赋值 / 析构) → 继承与派生 → 构造析构顺序
    → 虚函数与运行时多态 → 抽象类与虚析构 → 友元 → 运算符重载进阶
"""

from __future__ import annotations

from typing import Any, Dict, List


def _p(**kwargs: Any) -> Dict[str, Any]:
    problem = {
        "level": 2,
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
    # ------------------------------------------------------------------ i01
    _p(
        id="i01",
        slug="mystring-rule-of-three",
        title="Rule of Three：自己实现一个字符串类",
        topics=["拷贝赋值运算符", "拷贝构造函数", "深拷贝", "自赋值", "Rule of Three"],
        desc=(
            "只要一个类自己管理了资源(这里是 new[] 出来的字符数组), "
            "那么析构函数、拷贝构造函数、拷贝赋值运算符这三件事就必须一起考虑 —— "
            "这就是 C++ 著名的“Rule of Three”。"
            "赋值运算符比拷贝构造更麻烦: 它要先释放自己原来的资源, 还要能正确处理 a = a 这种自赋值。"
        ),
        require=[
            "只定义 MyString 类, 不要改 main; 内部必须用 char* 保存内容, 不允许用 std::string 当成员。",
            "MyString(const std::string& s): 按 s 的长度分配 size+1 字节并拷贝内容(末尾补 '\\0')。",
            "深拷贝构造函数与析构函数(delete[])。",
            "MyString& operator=(const MyString& other): 必须先判断自赋值, 再释放旧内存、分配新内存。",
            "MyString operator+(const MyString& other) const: 返回拼接后的新对象, 不修改自身。",
            "bool operator==(const MyString& other) const: 内容相同即相等。",
            "int size() const: 返回字符个数(不含结尾的 '\\0')。",
            "友元 operator<< 输出内容。",
        ],
        io="输入一行两个不含空白的字符串。输出三行, 见样例。",
        samples=[{"in": "abc de\n", "out": "abc de de\nabcde len=5\n0 1\n"}],
        hints=[
            "operator= 的返回值必须是 MyString&, 最后 return *this; —— 这样才能写 a = b = c。",
            "自赋值保护: if (this == &other) return *this;",
            "更保险的写法是“先分配新内存, 再 delete 旧内存”, 这样即使 new 抛异常对象也还是完好的。",
            "operator+ 里拼字符串可以临时借一下 std::string, 真正存储还是自己的 char*。",
        ],
        checklist=[
            "operator= 里有没有判自赋值?",
            "operator= 是不是返回 MyString& 而不是 MyString?",
            "operator+ / operator== / size 是不是都加了 const?",
            "析构函数用的是 delete[] 还是 delete?",
        ],
        skeleton="""#include <iostream>
#include <string>

// ================== TODO: 在这里定义 MyString 类 ==================
//
// 要求:
//   * 成员只能用 char* 保存内容(禁止把 std::string 当成员)
//   * MyString(const std::string& s)          构造
//   * ~MyString()                             delete[]
//   * MyString(const MyString&)               深拷贝
//   * MyString& operator=(const MyString&)    要处理自赋值 a = a
//   * MyString operator+(const MyString&) const
//   * bool operator==(const MyString&) const
//   * int size() const
//   * friend std::ostream& operator<<(std::ostream&, const MyString&)


// ================== 以下 main 不要修改 ==================
int main() {
    std::string s1, s2;
    if (!(std::cin >> s1 >> s2)) return 0;
    MyString a(s1), b(s2);
    MyString c = a;      // 拷贝构造
    c = b;               // 拷贝赋值
    a = a;               // 自赋值, 不能把自己弄坏
    std::cout << a << " " << b << " " << c << std::endl;
    MyString d = a + b;
    std::cout << d << " len=" << d.size() << std::endl;
    std::cout << (a == b) << " " << (b == c) << std::endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
#include <cstring>

class MyString {
private:
    char* data_;
    int size_;

public:
    explicit MyString(const std::string& s = "") : data_(nullptr), size_(static_cast<int>(s.size())) {
        data_ = new char[size_ + 1];
        for (int i = 0; i < size_; ++i) data_[i] = s[i];
        data_[size_] = '\\0';
    }

    MyString(const MyString& other) : data_(nullptr), size_(other.size_) {
        data_ = new char[size_ + 1];
        std::memcpy(data_, other.data_, size_ + 1);
    }

    ~MyString() {
        delete[] data_;
    }

    MyString& operator=(const MyString& other) {
        if (this == &other) return *this;          // 自赋值: 直接返回
        char* fresh = new char[other.size_ + 1];   // 先申请, 成功后再释放旧的
        std::memcpy(fresh, other.data_, other.size_ + 1);
        delete[] data_;
        data_ = fresh;
        size_ = other.size_;
        return *this;
    }

    MyString operator+(const MyString& other) const {
        std::string joined(data_, size_);
        joined.append(other.data_, other.size_);
        return MyString(joined);
    }

    bool operator==(const MyString& other) const {
        return size_ == other.size_ && std::strcmp(data_, other.data_) == 0;
    }

    int size() const { return size_; }

    friend std::ostream& operator<<(std::ostream& os, const MyString& s) {
        os << s.data_;
        return os;
    }
};

int main() {
    std::string s1, s2;
    if (!(std::cin >> s1 >> s2)) return 0;
    MyString a(s1), b(s2);
    MyString c = a;      // 拷贝构造
    c = b;               // 拷贝赋值
    a = a;               // 自赋值, 不能把自己弄坏
    std::cout << a << " " << b << " " << c << std::endl;
    MyString d = a + b;
    std::cout << d << " len=" << d.size() << std::endl;
    std::cout << (a == b) << " " << (b == c) << std::endl;
    return 0;
}
""",
        tests=[
            {"in": "abc de\n", "out": "abc de de\nabcde len=5\n0 1\n"},
            {"in": "x y\n", "out": "x y y\nxy len=2\n0 1\n"},
            {"in": "same same\n", "out": "same same same\nsamesame len=8\n1 1\n"},
        ],
    ),
    # ------------------------------------------------------------------ i02
    _p(
        id="i02",
        slug="employee-inherit",
        title="继承与派生：员工与经理",
        topics=["继承与派生", "派生类构造函数", "protected", "成员函数覆盖"],
        desc=(
            "继承解决的是“is-a”关系: 经理也是员工, 所以 Manager 可以继承 Employee, "
            "白拿基类的数据成员和成员函数。"
            "但派生类怎么把参数交给基类? 只能在初始化列表里调用基类构造函数; "
            "派生类又怎么写自己的额外字段? 这就是本题的全部。"
        ),
        require=[
            "只定义 Employee 与 Manager 两个类, 不要改 main。",
            "Employee: protected 的 name(std::string) 与 salary(int), 构造函数 Employee(const std::string&, int)。",
            "Employee::print() const 输出一行: name salary（空格分隔）。",
            "Manager: public 继承 Employee, 额外 private 成员 bonus(int)。",
            "Manager 的构造函数 Manager(const std::string& n, int s, int b) 必须在初始化列表里显式调用 Employee(n, s)。",
            "Manager::print() const 输出一行: name salary bonus total，其中 total = salary + bonus。",
        ],
        io="第一行整数 t(1 ≤ t ≤ 100)。接下来 t 行: 每行先是一个字符 E 或 M。E 时后面跟 name salary; M 时后面跟 name salary bonus。每行输出对应对象的信息。",
        samples=[{
            "in": "3\nE Tom 5000\nM Jerry 8000 3000\nM Alice 6000 1000\n",
            "out": "Tom 5000\nJerry 8000 3000 11000\nAlice 6000 1000 7000\n",
        }],
        hints=[
            "基类成员写 protected, 派生类才能直接访问; 写 private 的话派生类就摸不到了。",
            "初始化顺序只取决于基类的声明顺序, 与初始化列表里写的顺序无关 —— 这也是常见坑。",
            "Manager::print() 里可以直接用 name / salary, 也可以调用 Employee::print(), 两种都对。",
        ],
        checklist=[
            "Manager 的构造函数有没有在初始化列表里调用 Employee(...) ?",
            "派生时是 public 继承还是默认的 private 继承?（本题必须是 public）",
            "两个 print() 是否都加了 const ?",
        ],
        skeleton="""#include <iostream>
#include <string>

// ================== TODO: 在这里定义 Employee 基类 与 Manager 派生类 ==================
//
// Employee:
//   protected: std::string name; int salary;
//   Employee(const std::string& n, int s)
//   void print() const                  ->  name salary
// Manager : public Employee
//   private: int bonus;
//   Manager(const std::string& n, int s, int b)   初始化列表里调用 Employee(n, s)
//   void print() const                  ->  name salary bonus (salary + bonus)


// ================== 以下 main 不要修改 ==================
int main() {
    int t;
    if (!(std::cin >> t)) return 0;
    while (t--) {
        char kind;
        std::cin >> kind;
        std::string name;
        int salary;
        std::cin >> name >> salary;
        if (kind == 'E') {
            Employee e(name, salary);
            e.print();
        } else {
            int bonus;
            std::cin >> bonus;
            Manager m(name, salary, bonus);
            m.print();
        }
    }
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>

class Employee {
protected:
    std::string name;
    int salary;

public:
    Employee(const std::string& n, int s) : name(n), salary(s) {}

    void print() const {
        std::cout << name << ' ' << salary << '\\n';
    }
};

class Manager : public Employee {
private:
    int bonus;

public:
    Manager(const std::string& n, int s, int b) : Employee(n, s), bonus(b) {}

    void print() const {
        std::cout << name << ' ' << salary << ' ' << bonus
                  << ' ' << (salary + bonus) << '\\n';
    }
};

int main() {
    int t;
    if (!(std::cin >> t)) return 0;
    while (t--) {
        char kind;
        std::cin >> kind;
        std::string name;
        int salary;
        std::cin >> name >> salary;
        if (kind == 'E') {
            Employee e(name, salary);
            e.print();
        } else {
            int bonus;
            std::cin >> bonus;
            Manager m(name, salary, bonus);
            m.print();
        }
    }
    return 0;
}
""",
        tests=[
            {"in": "3\nE Tom 5000\nM Jerry 8000 3000\nM Alice 6000 1000\n",
             "out": "Tom 5000\nJerry 8000 3000 11000\nAlice 6000 1000 7000\n"},
            {"in": "1\nE solo 1\n", "out": "solo 1\n"},
            {"in": "2\nM boss 100 200\nE staff 50\n", "out": "boss 100 200 300\nstaff 50\n"},
        ],
    ),
    # ------------------------------------------------------------------ i03
    _p(
        id="i03",
        slug="ctor-dtor-order",
        title="构造与析构的调用顺序",
        topics=["构造函数调用顺序", "析构函数调用顺序", "继承链", "虚析构函数"],
        desc=(
            "很多人对继承的困惑, 其实来自没看清“什么时候构造、什么时候析构”。"
            "规则只有两条: 构造顺序 = 基类 → 派生类(先有爸妈才有孩子); "
            "析构顺序 = 派生类 → 基类(孩子先走)。本题请把这三层继承的轨迹打印出来。"
        ),
        require=[
            "只定义 Base / Middle / Derived 三个类, 不要改 main。",
            "Base 的构造函数输出 Base ctor, 析构函数输出 Base dtor。",
            "Middle : public Base, 构造输出 Middle ctor, 析构输出 Middle dtor。",
            "Derived : public Middle, 构造输出 Derived ctor, 析构输出 Derived dtor。",
            "Base 的析构函数请写成 virtual —— 这是继承体系里的基本修养。",
            "每行一条输出。",
        ],
        io="本题没有输入。输出构造与析构的完整轨迹。",
        samples=[{
            "in": "",
            "out": "Base ctor\nMiddle ctor\nDerived ctor\n---\nDerived dtor\nMiddle dtor\nBase dtor\n",
        }],
        hints=[
            "只写 `Derived d;` 这一句, 就会自动层层往上调用基类构造。",
            "析构顺序与构造顺序严格相反。",
            "把析构写成 virtual 后, 通过基类指针 delete 也能正确析构派生类(第 2 档后面会用到)。",
        ],
        checklist=[
            "Base 的析构函数加 virtual 了吗?",
            "有没有误用 private 继承导致外部无法构造 (Middle/Derived 必须是 public 继承)?",
        ],
        skeleton="""#include <iostream>

// ================== TODO: 在这里定义 Base / Middle / Derived ==================
//
// Base:    构造输出 "Base ctor",    析构输出 "Base dtor"    (析构请写 virtual)
// Middle:  public 继承 Base,  构造输出 "Middle ctor",  析构输出 "Middle dtor"
// Derived: public 继承 Middle, 构造输出 "Derived ctor", 析构输出 "Derived dtor"


// ================== 以下 main 不要修改 ==================
int main() {
    Derived d;
    std::cout << "---" << std::endl;
    return 0;
}
""",
        solution="""#include <iostream>

class Base {
public:
    Base() { std::cout << "Base ctor" << '\\n'; }
    virtual ~Base() { std::cout << "Base dtor" << '\\n'; }
};

class Middle : public Base {
public:
    Middle() { std::cout << "Middle ctor" << '\\n'; }
    ~Middle() { std::cout << "Middle dtor" << '\\n'; }
};

class Derived : public Middle {
public:
    Derived() { std::cout << "Derived ctor" << '\\n'; }
    ~Derived() { std::cout << "Derived dtor" << '\\n'; }
};

int main() {
    Derived d;
    std::cout << "---" << std::endl;
    return 0;
}
""",
        tests=[
            {"in": "",
             "out": "Base ctor\nMiddle ctor\nDerived ctor\n---\nDerived dtor\nMiddle dtor\nBase dtor\n"},
        ],
    ),
    # ------------------------------------------------------------------ i04
    _p(
        id="i04",
        slug="virtual-polymorphism",
        title="虚函数与运行时多态：用基类指针画图形",
        topics=["虚函数", "运行时多态", "基类指针", "vector容器"],
        desc=(
            "多态要解决的是: 我手里拿着一个 Shape* 指针, 但我根本不知道它到底指向圆还是矩形。"
            "只要函数是 virtual 的, 调用时就会“看对象真正的类型”, 而不是看指针的类型。"
            "如果没有 virtual, 这里输出的一定是基类的答案 —— 这就是本题的验收点。"
        ),
        require=[
            "只定义 Shape 基类与 Circle / Rectangle 派生类, 不要改 main。",
            "Shape: virtual std::string name() const 与 virtual double area() const, 以及 void print() const（内部输出 name() 与 area(), 中间一个空格, 行尾换行）。",
            "Shape 的析构函数必须是 virtual。",
            "Circle : public Shape, 构造函数 Circle(double r), 面积为 πr²。",
            "Rectangle : public Shape, 构造函数 Rectangle(double w, double h), 面积为 w×h。",
            "圆周率请使用 3.141592653589793, 保证与测评答案一致。",
        ],
        io="第一行整数 t。接下来 t 行: C r 或 R w h。依次输出每个图形的 name 与 area（保留 2 位小数, 由 main 控制）, 最后输出 total=<面积总和>。",
        samples=[{
            "in": "3\nC 1\nR 2 3\nC 2\n",
            "out": "Circle 3.14\nRectangle 6.00\nCircle 12.57\ntotal=21.71\n",
        }],
        hints=[
            "基类里 name()/area() 必须有函数体(可以返回空/0), 因为本题还不是抽象类。",
            "print() 不要加 virtual 也能跑, 但它内部调用的 name()/area() 必须是虚的 —— 这叫“模板方法”。",
            "忘了 virtual 的话, total 会算成 0, 很容易看出来。",
        ],
        checklist=[
            "name() 和 area() 是 virtual 吗?",
            "Shape 的析构是 virtual 吗?(main 里 delete 的是 Shape*)",
            "print() 里调用的是虚函数吗?",
        ],
        skeleton="""#include <iostream>
#include <iomanip>
#include <string>
#include <vector>

// ================== TODO: 在这里定义 Shape / Circle / Rectangle ==================
//
// Shape:
//   virtual std::string name() const
//   virtual double area() const
//   void print() const      ->  name() << ' ' << area() << '\\n'
//   virtual ~Shape()
// Circle    : public Shape,  Circle(double r),        area = 3.141592653589793 * r * r
// Rectangle : public Shape,  Rectangle(double w, double h), area = w * h


// ================== 以下 main 不要修改 ==================
int main() {
    std::cout << std::fixed << std::setprecision(2);
    int t;
    if (!(std::cin >> t)) return 0;
    std::vector<Shape*> shapes;
    while (t--) {
        char kind;
        std::cin >> kind;
        if (kind == 'C') {
            double r;
            std::cin >> r;
            shapes.push_back(new Circle(r));
        } else {
            double w, h;
            std::cin >> w >> h;
            shapes.push_back(new Rectangle(w, h));
        }
    }
    double total = 0.0;
    for (std::size_t i = 0; i < shapes.size(); ++i) {
        shapes[i]->print();
        total += shapes[i]->area();
    }
    std::cout << "total=" << total << std::endl;
    for (std::size_t i = 0; i < shapes.size(); ++i) delete shapes[i];
    return 0;
}
""",
        solution="""#include <iostream>
#include <iomanip>
#include <string>
#include <vector>

class Shape {
public:
    virtual std::string name() const { return "Shape"; }
    virtual double area() const { return 0.0; }

    void print() const {
        std::cout << name() << ' ' << area() << '\\n';
    }

    virtual ~Shape() {}
};

class Circle : public Shape {
private:
    double r_;

public:
    explicit Circle(double r) : r_(r) {}

    std::string name() const { return "Circle"; }
    double area() const { return 3.141592653589793 * r_ * r_; }
};

class Rectangle : public Shape {
private:
    double w_;
    double h_;

public:
    Rectangle(double w, double h) : w_(w), h_(h) {}

    std::string name() const { return "Rectangle"; }
    double area() const { return w_ * h_; }
};

int main() {
    std::cout << std::fixed << std::setprecision(2);
    int t;
    if (!(std::cin >> t)) return 0;
    std::vector<Shape*> shapes;
    while (t--) {
        char kind;
        std::cin >> kind;
        if (kind == 'C') {
            double r;
            std::cin >> r;
            shapes.push_back(new Circle(r));
        } else {
            double w, h;
            std::cin >> w >> h;
            shapes.push_back(new Rectangle(w, h));
        }
    }
    double total = 0.0;
    for (std::size_t i = 0; i < shapes.size(); ++i) {
        shapes[i]->print();
        total += shapes[i]->area();
    }
    std::cout << "total=" << total << std::endl;
    for (std::size_t i = 0; i < shapes.size(); ++i) delete shapes[i];
    return 0;
}
""",
        tests=[
            {"in": "3\nC 1\nR 2 3\nC 2\n",
             "out": "Circle 3.14\nRectangle 6.00\nCircle 12.57\ntotal=21.71\n"},
            {"in": "2\nR 1 1\nC 0\n", "out": "Rectangle 1.00\nCircle 0.00\ntotal=1.00\n"},
            {"in": "1\nR 2.5 4\n", "out": "Rectangle 10.00\ntotal=10.00\n"},
        ],
    ),
    # ------------------------------------------------------------------ i05
    _p(
        id="i05",
        slug="abstract-virtual-dtor",
        title="抽象类与虚析构：为什么基类析构必须 virtual",
        topics=["纯虚函数", "抽象类", "虚析构函数", "多态删除"],
        desc=(
            "上一题里 Shape 必须有函数体; 这一题把 name()/area() 变成纯虚函数, "
            "Shape 就成了“抽象类”—— 它描述接口, 不能被实例化。"
            "真正致命的是另一件事: 当你 delete 一个 Shape* 时, 如果基类析构不是 virtual, "
            "派生类的析构函数根本不会被调用, 资源直接泄漏。本题用输出把这件事摊开给你看。"
        ),
        require=[
            "只定义 Shape 与 Circle / Rectangle, 不要改 main。",
            "Shape: name() 与 area() 都是纯虚函数(= 0), 因此 Shape 是抽象类。",
            "Shape 的析构函数必须是 virtual, 且输出 ~Shape。",
            "Circle: 构造函数 Circle(double r), 析构函数输出 ~Circle, name() 返回 Circle, area() 用 3.141592653589793。",
            "Rectangle: 构造函数 Rectangle(double w, double h), 析构函数输出 ~Rectangle, area() = w × h。",
            "构造时不输出任何内容, 只有析构才有输出, 每行一条。",
        ],
        io="本题没有输入。先输出两个图形的信息, 再输出 delete 时的析构轨迹。",
        samples=[{
            "in": "",
            "out": "Circle 3.14\nRectangle 6.00\n~Circle\n~Shape\n~Rectangle\n~Shape\n",
        }],
        hints=[
            "纯虚函数: virtual double area() const = 0;",
            "抽象类不能创建对象(Shape s; 会编译报错), 但可以有 Shape* 指针 —— 这正是多态的基础。",
            "把 ~Shape 前面的 virtual 去掉试试, 你会发现 ~Circle 和 ~Rectangle 全都消失了。",
        ],
        checklist=[
            "两个纯虚函数是不是都写了 = 0 ?",
            "~Shape 是不是 virtual ?",
            "派生类的 name()/area() 是否用了 override 或至少签名完全一致?",
        ],
        skeleton="""#include <iostream>
#include <iomanip>
#include <string>

// ================== TODO: 在这里定义抽象基类 Shape 与 Circle / Rectangle ==================
//
// Shape:
//   virtual std::string name() const = 0;     纯虚
//   virtual double area() const = 0;          纯虚
//   virtual ~Shape() { std::cout << "~Shape" << std::endl; }
// Circle    : public Shape   Circle(double r)     析构输出 "~Circle"
// Rectangle : public Shape   Rectangle(double w, double h)  析构输出 "~Rectangle"
// 圆周率用 3.141592653589793


// ================== 以下 main 不要修改 ==================
int main() {
    std::cout << std::fixed << std::setprecision(2);
    Shape* a = new Circle(1);
    Shape* b = new Rectangle(2, 3);
    std::cout << a->name() << " " << a->area() << std::endl;
    std::cout << b->name() << " " << b->area() << std::endl;
    delete a;
    delete b;
    return 0;
}
""",
        solution="""#include <iostream>
#include <iomanip>
#include <string>

class Shape {
public:
    virtual std::string name() const = 0;
    virtual double area() const = 0;

    virtual ~Shape() { std::cout << "~Shape" << std::endl; }
};

class Circle : public Shape {
private:
    double r_;

public:
    explicit Circle(double r) : r_(r) {}
    ~Circle() { std::cout << "~Circle" << std::endl; }

    std::string name() const { return "Circle"; }
    double area() const { return 3.141592653589793 * r_ * r_; }
};

class Rectangle : public Shape {
private:
    double w_;
    double h_;

public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    ~Rectangle() { std::cout << "~Rectangle" << std::endl; }

    std::string name() const { return "Rectangle"; }
    double area() const { return w_ * h_; }
};

int main() {
    std::cout << std::fixed << std::setprecision(2);
    Shape* a = new Circle(1);
    Shape* b = new Rectangle(2, 3);
    std::cout << a->name() << " " << a->area() << std::endl;
    std::cout << b->name() << " " << b->area() << std::endl;
    delete a;
    delete b;
    return 0;
}
""",
        tests=[
            {"in": "",
             "out": "Circle 3.14\nRectangle 6.00\n~Circle\n~Shape\n~Rectangle\n~Shape\n"},
        ],
    ),
    # ------------------------------------------------------------------ i06
    _p(
        id="i06",
        slug="matrix-friend",
        title="友元：用 operator* 与工具类突破封装",
        topics=["友元函数", "友元类", "运算符重载", "封装边界"],
        desc=(
            "封装的原则是“数据私有”, 但有时候外部函数确实需要直接摸到私有数据 —— "
            "比如矩阵乘法, 写成成员函数会很别扭（左操作数不一定是自己）。"
            "友元就是那道特意开的小门: 它明确声明“这个函数/这个类是我信得过的”。"
        ),
        require=[
            "只定义 Matrix 与 Calculator, 不要改 main。",
            "Matrix 内部保存 int m[2][2], 必须私有; 提供一个把元素全部置 0 的默认构造函数。",
            "友元 operator>> 按行优先读入 4 个整数; 友元 operator<< 按行优先输出 4 个整数(用一个空格分隔, 行尾可以有空格)。",
            "友元 operator* 实现 2×2 矩阵乘法, 返回新的 Matrix。",
            "class Calculator 里提供 static int trace(const Matrix&), 返回主对角线(第 0 行第 0 列 + 第 1 行第 1 列)之和。",
            "Calculator 必须通过 friend class Calculator 声明为 Matrix 的友元类, 不允许给 Matrix 加公开的取值函数。",
        ],
        io="输入 8 个整数: 先是矩阵 a 的 4 个元素(行优先), 再是矩阵 b 的 4 个元素。输出两行: a*b 的 4 个元素、a 的迹。",
        samples=[{"in": "1 2 3 4 5 6 7 8\n", "out": "19 22 43 50\n5\n"}],
        hints=[
            "2×2 乘法: c[i][j] = a[i][0]*b[0][j] + a[i][1]*b[1][j]。",
            "friend class Calculator; 写在 Matrix 类体里面。",
            "友元不是成员函数, 所以定义时不要再写 Matrix:: 前缀。",
        ],
        checklist=[
            "两个类里有没有意外出现 public 的取值函数?（本题要求只靠友元访问）",
            "operator<< 返回的是 std::ostream& 吗?",
            "Calculator::trace 是不是 static 的?",
        ],
        skeleton="""#include <iostream>

// ================== TODO: 在这里定义 Matrix 与 Calculator ==================
//
// Matrix:
//   int m[2][2];                     私有
//   Matrix();                        全部置 0
//   friend std::istream& operator>>(std::istream&, Matrix&);
//   friend std::ostream& operator<<(std::ostream&, const Matrix&);
//   friend Matrix operator*(const Matrix&, const Matrix&);
//   friend class Calculator;
// Calculator:
//   static int trace(const Matrix&); 主对角线之和


// ================== 以下 main 不要修改 ==================
int main() {
    Matrix a, b;
    if (!(std::cin >> a >> b)) return 0;
    Matrix c = a * b;
    std::cout << c << std::endl;
    std::cout << Calculator::trace(a) << std::endl;
    return 0;
}
""",
        solution="""#include <iostream>

class Matrix {
private:
    int m[2][2];

public:
    Matrix() {
        for (int i = 0; i < 2; ++i)
            for (int j = 0; j < 2; ++j) m[i][j] = 0;
    }

    friend std::istream& operator>>(std::istream& is, Matrix& mat) {
        for (int i = 0; i < 2; ++i)
            for (int j = 0; j < 2; ++j) is >> mat.m[i][j];
        return is;
    }

    friend std::ostream& operator<<(std::ostream& os, const Matrix& mat) {
        for (int i = 0; i < 2; ++i)
            for (int j = 0; j < 2; ++j) os << mat.m[i][j] << ' ';
        return os;
    }

    friend Matrix operator*(const Matrix& x, const Matrix& y) {
        Matrix r;
        for (int i = 0; i < 2; ++i)
            for (int j = 0; j < 2; ++j) {
                r.m[i][j] = 0;
                for (int k = 0; k < 2; ++k) r.m[i][j] += x.m[i][k] * y.m[k][j];
            }
        return r;
    }

    friend class Calculator;
};

class Calculator {
public:
    static int trace(const Matrix& mat) {
        return mat.m[0][0] + mat.m[1][1];
    }
};

int main() {
    Matrix a, b;
    if (!(std::cin >> a >> b)) return 0;
    Matrix c = a * b;
    std::cout << c << std::endl;
    std::cout << Calculator::trace(a) << std::endl;
    return 0;
}
""",
        tests=[
            {"in": "1 2 3 4 5 6 7 8\n", "out": "19 22 43 50\n5\n"},
            {"in": "1 0 0 1 1 0 0 1\n", "out": "1 0 0 1\n2\n"},
            {"in": "1 1 1 1 2 2 2 2\n", "out": "4 4 4 4\n2\n"},
        ],
    ),
    # ------------------------------------------------------------------ i07
    _p(
        id="i07",
        slug="fraction-operators",
        title="运算符重载进阶：有理数类 Fraction",
        topics=["运算符重载", "有理性化简", "比较运算符", "欧几里得算法"],
        desc=(
            "有理数是“运算符重载”最好的练习场: 它不仅要有 + − × ÷, 还要维持一个不变式 —— "
            "任何时刻分母恒为正、且分数处于最简形式。"
            "一旦某个运算忘了约分, 后面的相等比较就会莫名其妙地失败。"
        ),
        require=[
            "只定义 Fraction 类, 不要改 main。",
            "构造 Fraction(int num = 0, int den = 1): 立即把符号规整到分子上(分母恒正)并约分到最简。",
            "重载 +、-、*、/ 四个运算符, 都是 const 成员函数, 返回新的 Fraction。",
            "重载 < 与 == 两个比较运算符。",
            "友元 operator<< 输出 分子/分母, 例如 -1/4; 0 输出为 0/1。",
            "约分使用辗转相除法(欧几里得算法)。",
        ],
        io="输入一行四个整数 a b c d, 表示 x = a/b, y = c/d。依次输出: x 和 y、x+y、x−y、x×y、x÷y、x<y、x==y。",
        samples=[{"in": "1 2 3 4\n", "out": "1/2 3/4\n5/4\n-1/4\n3/8\n2/3\n1 0\n"}],
        hints=[
            "通分公式: a/b + c/d = (ad + cb) / (bd), 之后再统一约分。",
            "分母为负数时要整体取反: -1/-2 应该变成 1/2, 1/-2 应该变成 -1/2。",
            "比较大小可以交叉相乘, 但要保证分母为正, 否则不等号方向会反。",
        ],
        checklist=[
            "构造函数里有没有做规范化(符号 + 约分)?",
            "四个算术运算符里有没有复用构造函数来顺便约分?",
            "哪些运算符必须加 const ?",
        ],
        skeleton="""#include <iostream>

// ================== TODO: 在这里定义 Fraction 类 ==================
//
// 不变式: 分母永远为正, 分数永远是最简形式
//   * Fraction(int num = 0, int den = 1)
//   * operator+ - * /       const 成员函数, 返回新对象
//   * operator< operator==
//   * friend operator<<     ->  分子/分母, 如 -1/4


// ================== 以下 main 不要修改 ==================
int main() {
    int a, b, c, d;
    if (!(std::cin >> a >> b >> c >> d)) return 0;
    Fraction x(a, b), y(c, d);
    std::cout << x << " " << y << std::endl;
    std::cout << (x + y) << std::endl;
    std::cout << (x - y) << std::endl;
    std::cout << (x * y) << std::endl;
    std::cout << (x / y) << std::endl;
    std::cout << (x < y) << " " << (x == y) << std::endl;
    return 0;
}
""",
        solution="""#include <iostream>

class Fraction {
private:
    int num_;
    int den_;

    static int gcd(int a, int b) {
        if (a < 0) a = -a;
        if (b < 0) b = -b;
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }
        return a == 0 ? 1 : a;
    }

    void normalize() {
        if (den_ < 0) {
            den_ = -den_;
            num_ = -num_;
        }
        int g = gcd(num_, den_);
        num_ /= g;
        den_ /= g;
    }

public:
    Fraction(int num = 0, int den = 1) : num_(num), den_(den == 0 ? 1 : den) {
        normalize();
    }

    Fraction operator+(const Fraction& o) const {
        return Fraction(num_ * o.den_ + o.num_ * den_, den_ * o.den_);
    }

    Fraction operator-(const Fraction& o) const {
        return Fraction(num_ * o.den_ - o.num_ * den_, den_ * o.den_);
    }

    Fraction operator*(const Fraction& o) const {
        return Fraction(num_ * o.num_, den_ * o.den_);
    }

    Fraction operator/(const Fraction& o) const {
        return Fraction(num_ * o.den_, den_ * o.num_);
    }

    bool operator<(const Fraction& o) const {
        return num_ * o.den_ < o.num_ * den_;
    }

    bool operator==(const Fraction& o) const {
        return num_ == o.num_ && den_ == o.den_;
    }

    friend std::ostream& operator<<(std::ostream& os, const Fraction& f) {
        os << f.num_ << '/' << f.den_;
        return os;
    }
};

int main() {
    int a, b, c, d;
    if (!(std::cin >> a >> b >> c >> d)) return 0;
    Fraction x(a, b), y(c, d);
    std::cout << x << " " << y << std::endl;
    std::cout << (x + y) << std::endl;
    std::cout << (x - y) << std::endl;
    std::cout << (x * y) << std::endl;
    std::cout << (x / y) << std::endl;
    std::cout << (x < y) << " " << (x == y) << std::endl;
    return 0;
}
""",
        tests=[
            {"in": "1 2 3 4\n", "out": "1/2 3/4\n5/4\n-1/4\n3/8\n2/3\n1 0\n"},
            {"in": "2 4 1 2\n", "out": "1/2 1/2\n1/1\n0/1\n1/4\n1/1\n0 1\n"},
            {"in": "1 -2 1 3\n", "out": "-1/2 1/3\n-1/6\n-5/6\n-1/6\n-3/2\n1 0\n"},
        ],
    ),
    # ------------------------------------------------------------------ i08
    _p(
        id="i08",
        slug="order-composition",
        title="组合（has-a）：订单与折扣，别什么关系都说成继承",
        topics=["组合关系", "成员对象生命周期", "封装边界", "const成员函数", "has-a 与 is-a"],
        desc=(
            "上一批题目里到处是继承, 但继承只该用在“A 是一个 B”的时候。"
            "订单“有”若干商品、订单“有”一条折扣规则 —— 这些都不是“是一个”, 所以正确做法是组合: "
            "把商品和折扣作为成员对象放进订单里。"
            "组合有两个必须亲眼看到的性质: 一是成员对象的构造发生在整体构造函数体之前、析构晚于整体; "
            "二是成员对象如果没有默认构造函数, 那它只能在初始化列表里被构造 —— 漏了就是编译错误。"
            "本题还要你把“最贵的一件商品”按引用交出去, 顺便体会整体对外只暴露行为、不暴露内部容器。"
        ),
        require=[
            "只定义 Item / Discount / Order 三个类, 不要改 main。",
            "Item: private 的 name_(std::string) / unitPrice_(int) / qty_(int); "
            "构造函数 Item(const std::string& name, int unitPrice, int qty); "
            "int subtotal() const 返回 unitPrice_ × qty_; const std::string& name() const。",
            "Discount: private 的 threshold_(int) / amount_(int); 构造函数 Discount(int threshold, int amount); "
            "int apply(int total) const: total ≥ threshold_ 时返回 max(0, total - amount_), 否则原样返回。",
            "Order 必须用组合而不是继承: private 成员为 std::string owner_、std::vector<Item> items_、"
            "Discount discount_; 绝对不允许让 Order 继承 Item 或 Discount。",
            "Order 的构造函数 Order(const std::string& owner, int threshold, int amount) "
            "必须在初始化列表里构造 discount_(threshold, amount) —— Discount 没有默认构造函数, 漏了就编译不过。",
            "void add(const Item& item): 把商品加入 items_(注意形参是 const 引用, 要能接受临时对象)。",
            "int total() const: 所有商品 subtotal 之和。",
            "const Item& mostExpensive() const: 返回小计最大的那一件(用引用返回, 不允许返回副本); "
            "若有并列, 返回先加入的那一件; 调用前保证订单非空。",
            "void print() const: 按样例格式输出商品清单与汇总。",
        ],
        io=(
            "第一行: owner n threshold amount (owner 不含空白, 1 ≤ n ≤ 1000, "
            "0 ≤ threshold ≤ 10000000, 0 ≤ amount ≤ 10000000)。"
            "接下来 n 行: name price qty (0 ≤ price ≤ 10000, 1 ≤ qty ≤ 100)。"
            "输出 n+5 行: 第一行 “owner n=<件数>”, 然后每件一行 “名字 小计”, "
            "最后四行 subtotal= / discount= / saved= / top=。"
        ),
        samples=[{
            "in": "Alice 3 15000 2000\napple 1000 5\nbook 12000 1\npen 300 2\n",
            "out": ("Alice n=3\napple 5000\nbook 12000\npen 600\n"
                    "subtotal=17600\ndiscount=15600\nsaved=2000\ntop=book\n"),
        }],
        hints=[
            "组合的读法: Order “有” items_, Order “有” discount_ —— 都是成员对象, 不是基类。",
            "items_ 是 std::vector<Item>, 记得 #include <vector>; 默认构造就是空订单, 不需要在初始化列表里写。",
            "discount_ 不带默认构造函数, 所以 Order 的初始化列表必须出现 discount_(threshold, amount)。",
            "找最大值时先用 best = 0 记录位置, 从 i = 1 开始比, 条件是 `>` 而不是 `>=`, 并列时才会保留先加入的那件。",
            "mostExpensive() 返回 const Item&, 这样外部拿到的是内部对象本身而不是副本 —— "
            "这也是“整体只暴露行为”的一部分。",
            "print() 是 const 成员函数, 它只能调用其它 const 成员函数(total() / mostExpensive() / name())。",
        ],
        checklist=[
            "Order 里面是“成员对象”还是“继承”? 必须是成员对象。",
            "Order 的初始化列表里有 discount_(threshold, amount) 吗?",
            "add 的形参是 const Item& 吗? 传临时对象 Item(...) 能编译过吗?",
            "mostExpensive() 返回的是 const Item& 而不是 Item 吗?",
            "total() / print() / mostExpensive() / name() / subtotal() 都加了 const 吗?",
        ],
        skeleton="""#include <iostream>
#include <string>
#include <vector>

// ================== TODO: 在这里定义 Item / Discount / Order ==================
//
// Item       商品: private name_ / unitPrice_ / qty_
//                  Item(const std::string&, int, int)
//                  int subtotal() const            -> 单价 × 数量
//                  const std::string& name() const
//
// Discount   折扣规则: private threshold_ / amount_
//                  Discount(int threshold, int amount)          <- 没有默认构造!
//                  int apply(int total) const      -> total >= threshold ? max(0, total-amount) : total
//
// Order      订单: 组合(has-a), 不是继承!
//                  private std::string owner_;
//                  private std::vector<Item> items_;            <- 组合
//                  private Discount discount_;                  <- 组合(成员对象)
//                  Order(const std::string& owner, int threshold, int amount)
//                        初始化列表里必须构造 discount_
//                  void add(const Item& item)
//                  int total() const
//                  const Item& mostExpensive() const            <- 引用返回, 并列取先加入的
//                  void print() const                           -> 格式见 problem.md


// ================== 以下 main 不要修改 ==================
int main() {
    std::string owner;
    int n, threshold, amount;
    if (!(std::cin >> owner >> n >> threshold >> amount)) return 0;
    Order order(owner, threshold, amount);
    for (int i = 0; i < n; ++i) {
        std::string name;
        int price, qty;
        std::cin >> name >> price >> qty;
        order.add(Item(name, price, qty));
    }
    order.print();
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
#include <vector>

class Item {
private:
    std::string name_;
    int unitPrice_;
    int qty_;

public:
    Item(const std::string& name, int unitPrice, int qty)
        : name_(name), unitPrice_(unitPrice), qty_(qty) {}

    int subtotal() const { return unitPrice_ * qty_; }
    const std::string& name() const { return name_; }
};

class Discount {
private:
    int threshold_;
    int amount_;

public:
    Discount(int threshold, int amount) : threshold_(threshold), amount_(amount) {}

    int apply(int total) const {
        if (total < threshold_) return total;
        int reduced = total - amount_;
        return reduced > 0 ? reduced : 0;
    }
};

class Order {
private:
    std::string owner_;
    std::vector<Item> items_;      // 组合: 订单“有”若干商品
    Discount discount_;            // 组合: 订单“有”一条折扣规则(成员对象)

public:
    Order(const std::string& owner, int threshold, int amount)
        : owner_(owner), discount_(threshold, amount) {}   // 成员对象只能在初始化列表里构造

    void add(const Item& item) { items_.push_back(item); }

    int total() const {
        int sum = 0;
        for (std::size_t i = 0; i < items_.size(); ++i) sum += items_[i].subtotal();
        return sum;
    }

    const Item& mostExpensive() const {
        std::size_t best = 0;
        for (std::size_t i = 1; i < items_.size(); ++i) {
            if (items_[i].subtotal() > items_[best].subtotal()) best = i;
        }
        return items_[best];
    }

    void print() const {
        std::cout << owner_ << " n=" << items_.size() << '\\n';
        for (std::size_t i = 0; i < items_.size(); ++i) {
            std::cout << items_[i].name() << ' ' << items_[i].subtotal() << '\\n';
        }
        int raw = total();
        int payable = discount_.apply(raw);
        std::cout << "subtotal=" << raw << '\\n';
        std::cout << "discount=" << payable << '\\n';
        std::cout << "saved=" << (raw - payable) << '\\n';
        std::cout << "top=" << mostExpensive().name() << '\\n';
    }
};

int main() {
    std::string owner;
    int n, threshold, amount;
    if (!(std::cin >> owner >> n >> threshold >> amount)) return 0;
    Order order(owner, threshold, amount);
    for (int i = 0; i < n; ++i) {
        std::string name;
        int price, qty;
        std::cin >> name >> price >> qty;
        order.add(Item(name, price, qty));
    }
    order.print();
    return 0;
}
""",
        tests=[
            {"in": "Alice 3 15000 2000\napple 1000 5\nbook 12000 1\npen 300 2\n",
             "out": ("Alice n=3\napple 5000\nbook 12000\npen 600\n"
                     "subtotal=17600\ndiscount=15600\nsaved=2000\ntop=book\n")},
            {"in": "Bob 1 5000 1000\ntea 500 2\n",
             "out": "Bob n=1\ntea 1000\nsubtotal=1000\ndiscount=1000\nsaved=0\ntop=tea\n"},
            {"in": "Cara 2 20 5000\na 10 1\nb 20 1\n",
             "out": "Cara n=2\na 10\nb 20\nsubtotal=30\ndiscount=0\nsaved=30\ntop=b\n"},
            {"in": "Dan 3 1000 100\nx 100 1\ny 50 2\nz 30 1\n",
             "out": "Dan n=3\nx 100\ny 100\nz 30\nsubtotal=230\ndiscount=230\nsaved=0\ntop=x\n"},
        ],
    ),
]
