#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_bank_pro.py - 第 3 档(高级)题目

这一档是“把设计写进代码”的阶段:
    类模板与模板特化 → RAII 与智能指针 → 单例 / 工厂 / 观察者三种经典模式
    → 多重继承与虚继承

题目依然全部可自动评测, 但验收点从“能不能跑”升级为“接口设计对不对”。
"""

from __future__ import annotations

from typing import Any, Dict, List


def _p(**kwargs: Any) -> Dict[str, Any]:
    problem = {
        "level": 3,
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
    # ------------------------------------------------------------------ a01
    _p(
        id="a01",
        slug="myvector-template",
        title="类模板：自己写一个 MyVector<T>",
        topics=["类模板", "模板成员函数", "深拷贝", "运算符重载"],
        desc=(
            "模板的意义在于“写一次, 用无数次”: 同一份代码既能装 int 又能装 std::string, "
            "编译期为每种类型各生成一份。"
            "本题要求你实现一个精简版 vector —— 它同时考模板语法、动态扩容、operator[] 和深拷贝。"
        ),
        require=[
            "定义类模板 template <class T> class MyVector, 不要改 main。",
            "内部用 T* data_ 与 int size_ 保存数据, 容量不足时按倍数扩容(每次翻倍即可)。",
            "提供默认构造、析构(delete[])、深拷贝构造函数。",
            "void push_back(const T& v): 添加元素, 必要时扩容。",
            "int size() const: 返回元素个数。",
            "同时提供 T& operator[](int) 与 const T& operator[](int) const 两个版本。",
        ],
        io="第一行整数 n。第二行 n 个整数, 第三行 n 个字符串。输出三行: n 与整数和、字符串序列、以及深拷贝验证结果。",
        samples=[{
            "in": "3\n10 20 30\naa bb cc\n",
            "out": "n=3 sum=60\naa bb cc\n10 -1\n",
        }],
        hints=[
            "模板的成员函数如果写在类外, 每个函数前面都要重复写 template <class T>。本题建议直接写在类内。",
            "扩容时先 new 新数组、逐个复制、再 delete[] 旧数组, 顺序不能反。",
            "深拷贝是必须的: 模板用 raw 指针存数据, 默认拷贝构造会造成 double free。",
            "operator[] 的 const 版本让 const 对象也能用下标读取。",
        ],
        checklist=[
            "类内是否同时提供了 operator[] 的 const 与非 const 版本?",
            "析构里是 delete[] 吗?",
            "push_back 在 size_ == cap_ 时有没有扩容?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义类模板 MyVector<T> ==================
//
// 要求:
//   * 成员: T* data_; int size_; int cap_;
//   * MyVector() / ~MyVector() / MyVector(const MyVector&)   深拷贝
//   * void push_back(const T& v)      容量不足时翻倍扩容
//   * int size() const
//   * T& operator[](int i) 与 const T& operator[](int i) const


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;

    MyVector<int> vi;
    for (int i = 0; i < n; ++i) {
        int x;
        cin >> x;
        vi.push_back(x);
    }

    MyVector<string> vs;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        vs.push_back(s);
    }

    long long sum = 0;
    for (int i = 0; i < vi.size(); ++i) sum += vi[i];
    cout << "n=" << vi.size() << " sum=" << sum << endl;

    for (int i = 0; i < vs.size(); ++i) {
        cout << vs[i] << (i + 1 == vs.size() ? '\\n' : ' ');
    }

    MyVector<int> cp = vi;      // 模板的深拷贝
    cp[0] = -1;
    cout << vi[0] << " " << cp[0] << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

template <class T>
class MyVector {
private:
    T* data_;
    int size_;
    int cap_;

    void grow() {
        int newCap = (cap_ == 0) ? 4 : cap_ * 2;
        T* fresh = new T[newCap];
        for (int i = 0; i < size_; ++i) fresh[i] = data_[i];
        delete[] data_;
        data_ = fresh;
        cap_ = newCap;
    }

public:
    MyVector() : data_(nullptr), size_(0), cap_(0) {}

    MyVector(const MyVector& other) : data_(nullptr), size_(0), cap_(0) {
        if (other.size_ > 0) {
            data_ = new T[other.size_];
            for (int i = 0; i < other.size_; ++i) data_[i] = other.data_[i];
            size_ = other.size_;
            cap_ = other.size_;
        }
    }

    ~MyVector() {
        delete[] data_;
    }

    void push_back(const T& v) {
        if (size_ == cap_) grow();
        data_[size_++] = v;
    }

    int size() const { return size_; }

    T& operator[](int i) { return data_[i]; }
    const T& operator[](int i) const { return data_[i]; }
};

int main() {
    int n;
    if (!(cin >> n)) return 0;

    MyVector<int> vi;
    for (int i = 0; i < n; ++i) {
        int x;
        cin >> x;
        vi.push_back(x);
    }

    MyVector<string> vs;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        vs.push_back(s);
    }

    long long sum = 0;
    for (int i = 0; i < vi.size(); ++i) sum += vi[i];
    cout << "n=" << vi.size() << " sum=" << sum << endl;

    for (int i = 0; i < vs.size(); ++i) {
        cout << vs[i] << (i + 1 == vs.size() ? '\\n' : ' ');
    }

    MyVector<int> cp = vi;      // 模板的深拷贝
    cp[0] = -1;
    cout << vi[0] << " " << cp[0] << endl;
    return 0;
}
""",
        tests=[
            {"in": "3\n10 20 30\naa bb cc\n", "out": "n=3 sum=60\naa bb cc\n10 -1\n"},
            {"in": "1\n5\nz\n", "out": "n=1 sum=5\nz\n5 -1\n"},
            {"in": "4\n1 2 3 4\nw x y z\n", "out": "n=4 sum=10\nw x y z\n1 -1\n"},
        ],
    ),
    # ------------------------------------------------------------------ a02
    _p(
        id="a02",
        slug="formatter-specialization",
        title="模板特化：为 bool 和 double 定制输出",
        topics=["类模板", "模板全特化", "std::ostringstream"],
        desc=(
            "模板给的是“通用答案”, 但通用答案并不总是好答案: "
            "std::cout << true 只会输出 1, 而业务上通常想要 true。"
            "这时候就用全特化(template <> ...)为特定类型换上专门实现。"
        ),
        require=[
            "定义类模板 template <class T> struct Formatter, 含 static std::string format(const T& value), 用输出流默认格式转字符串。",
            "全特化 Formatter<bool>: 真返回 true, 假返回 false。",
            "全特化 Formatter<double>: 固定 2 位小数(例如 3.14159 得到 3.14)。",
            "不要改 main。",
        ],
        io="本题没有输入。按顺序输出 5 行结果。",
        samples=[{"in": "", "out": "42\n3.14\ntrue\nfalse\nhi\n"}],
        hints=[
            "全特化的写法是 template <> struct Formatter<bool> { ... };, 尖括号里不能有类型参数。",
            "转字符串可以用 std::ostringstream: os << value; return os.str();",
            "double 的特化里先 os << std::fixed << std::setprecision(2) 再输出。",
        ],
        checklist=[
            "全特化前面是不是写了 template <> ?",
            "format 是不是 static 的(题目是按 Formatter<T>::format(...) 调用的)?",
            "主模板能不能通用于 std::string ?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <sstream>
//   <iomanip>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 定义类模板 Formatter<T> 及两个全特化 ==================
//
//   主模板          : 用输出流默认格式
//   Formatter<bool>   -> "true" / "false"
//   Formatter<double> -> 固定 2 位小数
//
// 注意: format 必须是 static 成员函数


// ================== 以下 main 不要修改 ==================
int main() {
    cout << Formatter<int>::format(42) << endl;
    cout << Formatter<double>::format(3.14159) << endl;
    cout << Formatter<bool>::format(true) << endl;
    cout << Formatter<bool>::format(false) << endl;
    cout << Formatter<string>::format("hi") << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
using namespace std;

template <class T>
struct Formatter {
    static string format(const T& value) {
        ostringstream os;
        os << value;
        return os.str();
    }
};

template <>
struct Formatter<bool> {
    static string format(const bool& value) {
        return value ? "true" : "false";
    }
};

template <>
struct Formatter<double> {
    static string format(const double& value) {
        ostringstream os;
        os << fixed << setprecision(2) << value;
        return os.str();
    }
};

int main() {
    cout << Formatter<int>::format(42) << endl;
    cout << Formatter<double>::format(3.14159) << endl;
    cout << Formatter<bool>::format(true) << endl;
    cout << Formatter<bool>::format(false) << endl;
    cout << Formatter<string>::format("hi") << endl;
    return 0;
}
""",
        tests=[
            {"in": "", "out": "42\n3.14\ntrue\nfalse\nhi\n"},
        ],
    ),
    # ------------------------------------------------------------------ a03
    _p(
        id="a03",
        slug="scoped-ptr-raii",
        title="RAII：自己实现一个独占智能指针",
        topics=["RAII", "智能指针语义", "delete 拷贝构造", "资源管理"],
        desc=(
            "RAII 是 C++ 管理资源的核心思想: 把资源的生命周期绑在对象的生命周期上 —— "
            "栈对象析构时自动释放, 无论中间有没有提前 return、有没有抛异常。"
            "本题写一个 ScopedPtr, 它证明了一件事: 智能指针没那么神秘, 就是把 new/delete 关进类里。"
        ),
        require=[
            "定义类模板 template <class T> class ScopedPtr, 不要改 main。",
            "explicit ScopedPtr(T* p = nullptr): 接管裸指针。",
            "~ScopedPtr(): delete 持有的指针。",
            "禁止拷贝: ScopedPtr(const ScopedPtr&) = delete; 且 operator= 同样 = delete。",
            "T& operator*() const、T* operator->() const、T* get() const。",
            "void reset(T* p): 先释放旧指针, 再接管新指针(自己传自己时要处理好)。",
        ],
        io="本题没有输入。输出资源的获取、使用、释放轨迹。",
        samples=[{
            "in": "",
            "out": "acquire A\nuse A\nuse A\nacquire B\nacquire C\nrelease B\nvalid=1\nrelease C\nrelease A\ndone\n",
        }],
        hints=[
            "operator-> 返回 T*, 编译器会自动帮你再做一次 ->, 所以 p->use() 能跑通。",
            "禁止拷贝用 C++11 的 = delete 最清晰(老式写法是把它们声明为 private 且不实现)。",
            "reset 里注意顺序: 先 new 成功再 delete 旧的, 或者先存旧指针等接管后再释放。",
            "先构造的先析构: q 在 p 之后构造, 所以先打印 release C 再 release A。",
        ],
        checklist=[
            "拷贝构造和拷贝赋值是不是都禁用了?",
            "析构函数有没有漏掉 nullptr 判断?（delete nullptr 其实是安全的）",
            "reset 之后旧资源确实被释放了吗?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;
struct Resource {
    string name;
    explicit Resource(const string& n) : name(n) {
        cout << "acquire " << name << endl;
    }
    ~Resource() {
        cout << "release " << name << endl;
    }
    void use() const {
        cout << "use " << name << endl;
    }
};

// ================== TODO: 在这里定义类模板 ScopedPtr<T> ==================
//
//   * explicit ScopedPtr(T* p = nullptr)
//   * ~ScopedPtr()                       delete 裸指针
//   * ScopedPtr(const ScopedPtr&) = delete;            禁止拷贝
//   * ScopedPtr& operator=(const ScopedPtr&) = delete;
//   * T& operator*() const
//   * T* operator->() const
//   * T* get() const
//   * void reset(T* p)                   先释放旧的, 再接管新的


// ================== 以下 main 不要修改 ==================
int main() {
    {
        ScopedPtr<Resource> p(new Resource("A"));
        p->use();
        (*p).use();

        ScopedPtr<Resource> q(new Resource("B"));
        q.reset(new Resource("C"));
        cout << "valid=" << (q.get() != nullptr) << endl;
    }
    cout << "done" << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

struct Resource {
    string name;
    explicit Resource(const string& n) : name(n) {
        cout << "acquire " << name << endl;
    }
    ~Resource() {
        cout << "release " << name << endl;
    }
    void use() const {
        cout << "use " << name << endl;
    }
};

template <class T>
class ScopedPtr {
private:
    T* ptr_;

public:
    explicit ScopedPtr(T* p = nullptr) : ptr_(p) {}

    ~ScopedPtr() {
        delete ptr_;
    }

    ScopedPtr(const ScopedPtr&) = delete;
    ScopedPtr& operator=(const ScopedPtr&) = delete;

    T& operator*() const { return *ptr_; }
    T* operator->() const { return ptr_; }
    T* get() const { return ptr_; }

    void reset(T* p = nullptr) {
        if (p == ptr_) return;
        delete ptr_;
        ptr_ = p;
    }
};

int main() {
    {
        ScopedPtr<Resource> p(new Resource("A"));
        p->use();
        (*p).use();

        ScopedPtr<Resource> q(new Resource("B"));
        q.reset(new Resource("C"));
        cout << "valid=" << (q.get() != nullptr) << endl;
    }
    cout << "done" << endl;
    return 0;
}
""",
        tests=[
            {"in": "",
             "out": "acquire A\nuse A\nuse A\nacquire B\nacquire C\nrelease B\nvalid=1\nrelease C\nrelease A\ndone\n"},
        ],
    ),
    # ------------------------------------------------------------------ a04
    _p(
        id="a04",
        slug="singleton-logger",
        title="设计模式：单例 Logger",
        topics=["单例模式", "静态局部变量", "禁止拷贝", "引用返回"],
        desc=(
            "单例要保证“整个程序里只存在一个实例”。"
            "现代 C++ 的实现只有三行: 构造函数私有、拷贝禁用、函数内 static 局部变量。"
            "别小看那个 static —— C++11 起它自带线程安全的初始化保证。"
        ),
        require=[
            "只定义 Logger 类, 不要改 main。",
            "static Logger& instance(): 返回全局唯一实例(推荐用函数内 static 局部变量实现)。",
            "构造函数必须是 private; 拷贝构造与拷贝赋值必须 = delete。",
            "void log(const std::string& msg): 输出 [序号] 消息, 序号从 1 开始递增, 每行一条。",
            "int count() const: 返回已经记录了多少条日志。",
        ],
        io="第一行整数 n, 第二行 n 个不含空白的字符串。依次输出 n 行日志, 然后输出 count=<条数>, 最后输出两次取到的实例是否同一个对象(0 或 1)。",
        samples=[{"in": "2\nstart tick\n", "out": "[1] start\n[2] tick\ncount=2\n1\n"}],
        hints=[
            "函数内 static 局部变量只在第一次执行到这行时构造, 天然满足“只有一个”。",
            "instance() 返回引用而不是指针或对象, 这样调用方写 Logger::instance().log(...) 最自然。",
            "把构造函数设为 private 之后, 外部就再也没法 Logger x; 了。",
        ],
        checklist=[
            "构造函数是 private 吗?",
            "拷贝构造/拷贝赋值都禁用了没有?",
            "instance() 返回的是 Logger& 吗?",
            "序号是在 log() 里自增, 而不是在构造函数里?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 在这里定义单例类 Logger ==================
//
//   * static Logger& instance();            返回唯一实例
//   * void log(const string& msg);     输出 "[序号] 消息", 序号从 1 递增
//   * int count() const;                    已记录条数
//   * 构造函数 private, 拷贝构造与拷贝赋值 = delete


// ================== 以下 main 不要修改 ==================
int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        Logger::instance().log(s);
    }
    cout << "count=" << Logger::instance().count() << endl;
    Logger& a = Logger::instance();
    Logger& b = Logger::instance();
    cout << (&a == &b) << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

class Logger {
private:
    int seq_;

    Logger() : seq_(0) {}
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

public:
    static Logger& instance() {
        static Logger only;      // C++11 起, 静态局部变量的初始化是线程安全的
        return only;
    }

    void log(const string& msg) {
        ++seq_;
        cout << '[' << seq_ << "] " << msg << endl;
    }

    int count() const { return seq_; }
};

int main() {
    int n;
    if (!(cin >> n)) return 0;
    for (int i = 0; i < n; ++i) {
        string s;
        cin >> s;
        Logger::instance().log(s);
    }
    cout << "count=" << Logger::instance().count() << endl;
    Logger& a = Logger::instance();
    Logger& b = Logger::instance();
    cout << (&a == &b) << endl;
    return 0;
}
""",
        tests=[
            {"in": "2\nstart tick\n", "out": "[1] start\n[2] tick\ncount=2\n1\n"},
            {"in": "1\nhello\n", "out": "[1] hello\ncount=1\n1\n"},
            {"in": "3\na b c\n", "out": "[1] a\n[2] b\n[3] c\ncount=3\n1\n"},
        ],
    ),
    # ------------------------------------------------------------------ a05
    _p(
        id="a05",
        slug="factory-unique-ptr",
        title="设计模式：工厂方法 + unique_ptr",
        topics=["工厂模式", "unique_ptr", "多态", "错误处理"],
        desc=(
            "工厂模式把“选择创建哪个派生类”这件事从调用方手里拿走, 集中到一处。"
            "调用方只递进去一个类型标记, 拿回来一个基类指针, 完全不需要知道背后有哪些具体类型 —— "
            "以后新增一种图形, 只要改工厂, 调用方一行都不用动。"
        ),
        require=[
            "定义抽象基类 Shape(name/area 为纯虚函数, 虚析构) 与 Circle / Rectangle, 不要改 main。",
            "ShapeFactory::create(char kind, double a, double b) 返回 std::unique_ptr<Shape>。",
            "kind 为 C 时创建 Circle(a); kind 为 R 时创建 Rectangle(a, b)。",
            "其他字符返回空的 unique_ptr(不要返回 nullptr 裸指针, 不要抛异常)。",
            "圆周率使用 3.141592653589793。",
        ],
        io="第一行整数 t。接下来 t 行: 每行 字符 a b。图形输出 name 与面积（保留 1 位小数, 由 main 控制）, 非法类型输出 unknown, 最后输出 total=<总面积>。",
        samples=[{
            "in": "4\nC 1 0\nR 2 3\nC 2 0\nX 1 1\n",
            "out": "Circle 3.1\nRectangle 6.0\nCircle 12.6\nunknown\ntotal=21.7\n",
        }],
        hints=[
            "std::unique_ptr<Shape> 在离开作用域时自动 delete, 所以 main 里完全没有 delete 语句。",
            "返回空智能指针写 return std::unique_ptr<Shape>(); 或 return {}; 都行。",
            "工厂里记得让 Shape 的析构是 virtual, 否则 unique_ptr<Shape> 删除派生对象时行为不正确。",
        ],
        checklist=[
            "基类的两个纯虚函数 + 虚析构都写了吗?",
            "非法类型是不是返回了空指针而不是崩溃?",
            "工厂是不是 static 成员函数?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <iomanip>
//   <memory>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 定义 Shape / Circle / Rectangle / ShapeFactory ==================
//
// Shape:   virtual string name() const = 0;
//          virtual double area() const = 0;
//          virtual ~Shape() {}
// Circle(double r)           area = 3.141592653589793 * r * r
// Rectangle(double w, double h)   area = w * h
//
// ShapeFactory::create(char kind, double a, double b) -> unique_ptr<Shape>
//          'C' -> Circle(a)      'R' -> Rectangle(a, b)     其他 -> 空指针


// ================== 以下 main 不要修改 ==================
int main() {
    cout << fixed << setprecision(1);
    int t;
    if (!(cin >> t)) return 0;
    double total = 0.0;
    while (t--) {
        char kind;
        double a, b;
        cin >> kind >> a >> b;
        unique_ptr<Shape> s = ShapeFactory::create(kind, a, b);
        if (!s) {
            cout << "unknown" << endl;
            continue;
        }
        cout << s->name() << " " << s->area() << endl;
        total += s->area();
    }
    cout << "total=" << total << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <iomanip>
#include <memory>
#include <string>
using namespace std;

class Shape {
public:
    virtual string name() const = 0;
    virtual double area() const = 0;
    virtual ~Shape() {}
};

class Circle : public Shape {
private:
    double r_;

public:
    explicit Circle(double r) : r_(r) {}
    string name() const { return "Circle"; }
    double area() const { return 3.141592653589793 * r_ * r_; }
};

class Rectangle : public Shape {
private:
    double w_;
    double h_;

public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    string name() const { return "Rectangle"; }
    double area() const { return w_ * h_; }
};

class ShapeFactory {
public:
    static unique_ptr<Shape> create(char kind, double a, double b) {
        if (kind == 'C') return unique_ptr<Shape>(new Circle(a));
        if (kind == 'R') return unique_ptr<Shape>(new Rectangle(a, b));
        return unique_ptr<Shape>();
    }
};

int main() {
    cout << fixed << setprecision(1);
    int t;
    if (!(cin >> t)) return 0;
    double total = 0.0;
    while (t--) {
        char kind;
        double a, b;
        cin >> kind >> a >> b;
        unique_ptr<Shape> s = ShapeFactory::create(kind, a, b);
        if (!s) {
            cout << "unknown" << endl;
            continue;
        }
        cout << s->name() << " " << s->area() << endl;
        total += s->area();
    }
    cout << "total=" << total << endl;
    return 0;
}
""",
        tests=[
            {"in": "4\nC 1 0\nR 2 3\nC 2 0\nX 1 1\n",
             "out": "Circle 3.1\nRectangle 6.0\nCircle 12.6\nunknown\ntotal=21.7\n"},
            {"in": "1\nR 1.5 2\n", "out": "Rectangle 3.0\ntotal=3.0\n"},
            {"in": "2\nX 0 0\nC 0 0\n", "out": "unknown\nCircle 0.0\ntotal=0.0\n"},
        ],
    ),
    # ------------------------------------------------------------------ a06
    _p(
        id="a06",
        slug="observer-pattern",
        title="设计模式：观察者(发布-订阅)",
        topics=["观察者模式", "抽象基类", "指针容器", "运行时多态"],
        desc=(
            "观察者模式解决“一变多知”的问题: 主题状态一变, 所有订阅者都被通知, "
            "而主题完全不需要知道订阅者的具体类型, 只看 Observer 这个接口。"
            "这是事件系统、GUI、消息总线的共同骨架。"
        ),
        require=[
            "定义接口 Observer(纯虚 update(int), 虚析构)、主题 Subject、观察者 Screen, 不要改 main。",
            "Subject::attach(Observer*) 按加入顺序保存订阅者; detach(Observer*) 移除(不存在时不做任何事)。",
            "Subject::notify(int value) 按加入顺序依次调用每个订阅者的 update(value)。",
            "Screen : public Observer, 构造 Screen(const std::string& id)。",
            "Screen::update(int v) 输出: <id> got <v>（每行一条）。",
        ],
        io="本题没有输入。按通知顺序输出每个观察者收到的消息。",
        samples=[{"in": "", "out": "A got 1\nB got 1\nC got 1\nA got 2\nC got 2\n"}],
        hints=[
            "Subject 内部可以用 std::vector<Observer*> 保存订阅者。",
            "detach 里用 std::find 找到位置再 erase。",
            "Subject 里不 delete 任何 Observer —— 所有权归 main 里的栈对象, 这叫“只管引用不管生死”。",
        ],
        checklist=[
            "Observer 的析构是 virtual 吗?",
            "detach 一个不存在的观察者会崩溃吗?",
            "notify 遍历时有没有可能因为 detach 而迭代器失效?（本题顺序执行, 不会）",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
//   <vector>
//   <algorithm>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 定义 Observer / Subject / Screen ==================
//
// Observer:   virtual void update(int value) = 0;   virtual ~Observer() {}
// Subject:
//     void attach(Observer* o);       void detach(Observer* o);
//     void notify(int value);         按加入顺序通知
//     virtual ~Subject() {}
// Screen : public Observer
//     Screen(const string& id);  update 输出 "<id> got <value>"


// ================== 以下 main 不要修改 ==================
int main() {
    Subject subject;
    Screen a("A"), b("B"), c("C");
    subject.attach(&a);
    subject.attach(&b);
    subject.attach(&c);
    subject.notify(1);
    subject.detach(&b);
    subject.notify(2);
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

class Observer {
public:
    virtual void update(int value) = 0;
    virtual ~Observer() {}
};

class Subject {
private:
    vector<Observer*> observers_;

public:
    void attach(Observer* o) {
        observers_.push_back(o);
    }

    void detach(Observer* o) {
        vector<Observer*>::iterator it =
            std::find(observers_.begin(), observers_.end(), o);
        if (it != observers_.end()) observers_.erase(it);
    }

    void notify(int value) {
        for (size_t i = 0; i < observers_.size(); ++i) {
            observers_[i]->update(value);
        }
    }

    virtual ~Subject() {}
};

class Screen : public Observer {
private:
    string id_;

public:
    explicit Screen(const string& id) : id_(id) {}

    void update(int value) {
        cout << id_ << " got " << value << endl;
    }
};

int main() {
    Subject subject;
    Screen a("A"), b("B"), c("C");
    subject.attach(&a);
    subject.attach(&b);
    subject.attach(&c);
    subject.notify(1);
    subject.detach(&b);
    subject.notify(2);
    return 0;
}
""",
        tests=[
            {"in": "", "out": "A got 1\nB got 1\nC got 1\nA got 2\nC got 2\n"},
        ],
    ),
    # ------------------------------------------------------------------ a07
    _p(
        id="a07",
        slug="diamond-virtual-inherit",
        title="多重继承与虚继承：菱形继承",
        topics=["多重继承", "虚继承", "菱形继承", "构造顺序"],
        desc=(
            "手机既是相机又是屏幕, 于是 SmartPhone 同时继承 Camera 和 ScreenModule; "
            "而两者又都继承自 Device —— 这就形成了菱形继承。"
            "不写 virtual 继承的话, SmartPhone 里会有两份 Device, sp.deviceId() 直接编译报错。"
            "本题就是要你亲手把这个菱形“缝”回去。"
        ),
        require=[
            "定义 Device / Camera / ScreenModule / SmartPhone 四个类, 不要改 main。",
            "Device: protected int id, 构造函数 Device(int i) 输出 Device <i>, 提供 int deviceId() const。",
            "Camera : virtual public Device, 构造函数 Camera(int i, int mp) 输出 Camera <mp>, 提供 int cameraMp() const。",
            "ScreenModule : virtual public Device, 构造函数 ScreenModule(int i, int inch) 输出 Screen <inch>, 提供 int screenInch() const。",
            "SmartPhone : public Camera, public ScreenModule, 构造函数 SmartPhone(int i, int mp, int inch) 输出 SmartPhone。",
            "由于 Device 是虚基类, 必须在 SmartPhone 的初始化列表里直接初始化 Device(i)。",
        ],
        io="输入三个整数 id mp inch。输出构造轨迹四行, 然后一行汇总信息。",
        samples=[{"in": "7 108 6\n", "out": "Device 7\nCamera 108\nScreen 6\nSmartPhone\nid=7 mp=108 inch=6\n"}],
        hints=[
            "虚继承里, 最派生类负责初始化虚基类, 中间类的 Device(...) 初始化会被忽略。",
            "构造顺序: 虚基类 → 非虚基类(按声明顺序) → 自身。所以 Device 排在最前面。",
            "少了 virtual 的话, sp.deviceId() 会出现二义性编译错误 —— 这就是菱形继承的经典症状。",
        ],
        checklist=[
            "Camera 与 ScreenModule 是不是都用了 virtual public Device ?",
            "SmartPhone 的初始化列表里有没有直接写 Device(i) ?",
            "deviceId() / cameraMp() / screenInch() 都是 const 成员函数吗?",
        ],
        skeleton="""// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <string>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 定义 Device / Camera / ScreenModule / SmartPhone ==================
//
// Device:       protected int id;
//               Device(int i)            输出 "Device <i>"
//               int deviceId() const
// Camera      : virtual public Device
//               Camera(int i, int mp)    输出 "Camera <mp>"
//               int cameraMp() const
// ScreenModule: virtual public Device
//               ScreenModule(int i, int inch)   输出 "Screen <inch>"
//               int screenInch() const
// SmartPhone  : public Camera, public ScreenModule
//               SmartPhone(int i, int mp, int inch)   输出 "SmartPhone"
//               并且自己在初始化列表里初始化虚基类 Device(i)


// ================== 以下 main 不要修改 ==================
int main() {
    int id, mp, inch;
    if (!(cin >> id >> mp >> inch)) return 0;
    SmartPhone sp(id, mp, inch);
    cout << "id=" << sp.deviceId() << " mp=" << sp.cameraMp()
              << " inch=" << sp.screenInch() << endl;
    return 0;
}
""",
        solution="""#include <iostream>
#include <string>
using namespace std;

class Device {
protected:
    int id;

public:
    explicit Device(int i) : id(i) {
        cout << "Device " << i << endl;
    }

    int deviceId() const { return id; }
};

class Camera : virtual public Device {
protected:
    int mp_;

public:
    Camera(int i, int mp) : Device(i), mp_(mp) {
        cout << "Camera " << mp << endl;
    }

    int cameraMp() const { return mp_; }
};

class ScreenModule : virtual public Device {
protected:
    int inch_;

public:
    ScreenModule(int i, int inch) : Device(i), inch_(inch) {
        cout << "Screen " << inch << endl;
    }

    int screenInch() const { return inch_; }
};

class SmartPhone : public Camera, public ScreenModule {
public:
    SmartPhone(int i, int mp, int inch)
        : Device(i), Camera(i, mp), ScreenModule(i, inch) {
        cout << "SmartPhone" << endl;
    }
};

int main() {
    int id, mp, inch;
    if (!(cin >> id >> mp >> inch)) return 0;
    SmartPhone sp(id, mp, inch);
    cout << "id=" << sp.deviceId() << " mp=" << sp.cameraMp()
              << " inch=" << sp.screenInch() << endl;
    return 0;
}
""",
        tests=[
            {"in": "7 108 6\n", "out": "Device 7\nCamera 108\nScreen 6\nSmartPhone\nid=7 mp=108 inch=6\n"},
            {"in": "1 12 5\n", "out": "Device 1\nCamera 12\nScreen 5\nSmartPhone\nid=1 mp=12 inch=5\n"},
        ],
    ),
]
