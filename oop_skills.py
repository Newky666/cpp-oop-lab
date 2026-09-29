#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_skills.py - 面向对象知识点图谱 + 讲解素材

这个模块是“老师视角”的地基: 把面向对象拆成 17 个可考核的知识点(K01~K17),
每个知识点带着

    summary      一句话说清它解决什么问题
    points       要点(讲课提纲)
    pitfalls     初学者最常踩的坑
    example      一小段“正确写法”的代码
    check        写完后用来自查的一句话

另外提供两张诊断表:

    COMPILER_ERRORS  编译器报错 -> 知识点 + 为什么会这样 + 怎么改
    REVIEW_HINTS     静态审查规则(R01~R12) -> 知识点 + 讲法

题库题目里写的中文 topics 通过 ``classify()`` 用关键词映射到知识点,
所以在线导入的题目(带洛谷/dotcpp 标签)也能自动归类。
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# 知识点定义
# ---------------------------------------------------------------------------
SKILLS: List[Dict[str, Any]] = [
    {
        "id": "K01", "level": 1, "name": "类与封装",
        "keywords": ["类的定义", "访问控制", "封装", "private", "public",
                     "成员函数", "this指针", "逻辑封装", "封装边界"],
        "summary": "把“数据”和“操作数据的函数”捆成一个类型, 并把数据藏起来, 只留出必要的接口。",
        "points": [
            "class 默认访问级别是 private, struct 默认是 public —— 练习里优先用 class + 显式 public:。",
            "数据成员一律 private; 需要给外部看的用取值函数(getter)暴露, 而不是把成员开成 public。",
            "接口(public)要少而稳定, 实现细节(private)可以随便改 —— 这就是封装带来的抗变化能力。",
            "this 指针在成员函数里指向“当前对象”, 返回 *this 才能支持链式调用。",
        ],
        "pitfalls": [
            "把数据成员写成 public, 封装直接失效;",
            "给每个成员都配 getter/setter, 等于把 private 当装饰 —— 应该暴露“有意义的操作”而不是裸数据;",
            "在类定义里写实现(内联)没问题, 但别把整个程序逻辑都堆进去。",
        ],
        "example": (
            "class Account {\n"
            "private:\n"
            "    double balance_;              // 数据藏起来\n"
            "public:\n"
            "    explicit Account(double init) : balance_(init) {}\n"
            "    void deposit(double amount);   // 暴露“有意义的操作”\n"
            "    double balance() const;        // 只读的取值函数\n"
            "};"
        ),
        "check": "问自己: 这个类的数据, 外部能随便改吗? 能改的路径是不是都经过了校验?",
    },
    {
        "id": "K02", "level": 1, "name": "构造函数与初始化列表",
        "keywords": ["构造函数", "初始化列表"],
        "summary": "对象一出生就必须是合法的。构造函数负责给每个成员一个确定的初值。",
        "points": [
            "成员初始化列表的执行顺序只取决于成员的声明顺序, 与你在列表里的书写顺序无关。",
            "const 成员、引用成员、没有默认构造的成员对象, 只能在初始化列表里赋值, 函数体里赋值不合法。",
            "explicit 修饰单参数构造函数, 防止编译器偷偷做隐式类型转换。",
            "构造函数可以重载; 用默认参数可以少写好几个重载版本。",
        ],
        "pitfalls": [
            "在函数体里写 `x = v;` 而不是 `: x(v)` —— 对类类型成员这是“先默认构造再赋值”, 多一次开销;",
            "初始化列表顺序写错, 依赖了还没初始化的成员;",
            "忘了给指针成员初始化, 留下野指针。",
        ],
        "example": (
            "class Date {\n"
            "    int year_, month_, day_;\n"
            "public:\n"
            "    Date(int y, int m, int d) : year_(y), month_(m), day_(d) {}  // 初始化列表\n"
            "};"
        ),
        "check": "每个数据成员都在初始化列表里出现了吗? 顺序和声明顺序一致吗?",
    },
    {
        "id": "K03", "level": 1, "name": "析构与对象生命周期",
        "keywords": ["析构函数", "对象生命周期", "构造函数调用顺序", "析构函数调用顺序",
                     "继承链", "生命周期"],
        "summary": "析构函数负责把对象占用的资源还回去。构造顺序与析构顺序正好相反。",
        "points": [
            "局部对象出作用域自动析构, 顺序与构造顺序相反;",
            "有继承时: 构造 = 基类 → 派生类, 析构 = 派生类 → 基类;",
            "成员对象的构造先于本类构造函数体(按声明顺序), 析构后于本类析构函数体;",
            "只要一个类自己管理了资源, 就必须同时考虑析构 + 拷贝构造 + 拷贝赋值。",
        ],
        "pitfalls": [
            "以为析构函数会“自动帮你释放 new 出来的内存” —— 只有写了 delete 才会;",
            "把析构写成会抛异常的操作(析构里抛异常很危险);",
            "在析构里访问已经析构的成员对象。",
        ],
        "example": (
            "class Buf {\n"
            "    int* data_;\n"
            "public:\n"
            "    explicit Buf(int n) : data_(new int[n]()) {}\n"
            "    ~Buf() { delete[] data_; }        // 谁申请谁释放\n"
            "};"
        ),
        "check": "这个类里所有 new 出来的东西, 在析构里都有对应的释放吗?",
    },
    {
        "id": "K04", "level": 1, "name": "拷贝构造与深拷贝",
        "keywords": ["拷贝构造函数", "深拷贝", "动态内存", "浅拷贝"],
        "summary": "拷贝一个对象时, 是“共享同一块内存”还是“各自拥有一份”, 必须由你明确决定。",
        "points": [
            "编译器默认生成的拷贝构造是逐成员拷贝: 指针成员只会被拷贝地址(浅拷贝);",
            "浅拷贝 + 析构里 delete = 两个对象释放同一块内存 = double free 崩溃;",
            "深拷贝就是在拷贝构造里自己 new 一块内存, 再把内容复制过来;",
            "拷贝构造的形参必须是引用(通常是 const T&), 传值会导致无限递归。",
        ],
        "pitfalls": [
            "写了析构函数却忘了拷贝构造(典型崩溃组合);",
            "拷贝构造里只 new 了内存, 忘了复制元素内容;",
            "拷贝构造写成 `T(T other)` —— 编译不过或死循环。",
        ],
        "example": (
            "IntArray(const IntArray& other) : data_(nullptr), size_(other.size_) {\n"
            "    if (size_ > 0) {\n"
            "        data_ = new int[size_];\n"
            "        for (int i = 0; i < size_; ++i) data_[i] = other.data_[i];\n"
            "    }\n"
            "}"
        ),
        "check": "把对象拷一份, 改其中一个, 另一个会跟着变吗? 如果不该变, 你写深拷贝了吗?",
    },
    {
        "id": "K05", "level": 1, "name": "const 正确性与 this",
        "keywords": ["const成员函数", "值返回", "const", "const正确性"],
        "summary": "const 不是装饰品 —— 它让编译器帮你证明“这个函数不会改对象”。",
        "points": [
            "不修改对象状态的成员函数都应该加 const, 否则 const 对象调用不了它;",
            "const 成员函数里 this 的类型是 `const T*`, 不能改成员(除非成员声明为 mutable);",
            "参数能传 const 引用就传 const 引用: 避免拷贝, 又能接受临时对象;",
            "返回“内部数据的引用”时, 如果对象是 const 的, 返回的也必须是 const 引用。",
        ],
        "pitfalls": [
            "一半函数有 const 一半没有, 用的时候到处报错;",
            "为了让 const 对象能编译, 直接把成员声明成 mutable —— 这是在骗编译器;",
            "getter 返回 `const std::string&`, 但函数自己没加 const。",
        ],
        "example": (
            "class Point {\n"
            "    int x_, y_;\n"
            "public:\n"
            "    int x() const { return x_; }                       // 只读 -> const\n"
            "    Point moveBy(int dx, int dy) const {               // 不改自身 -> const\n"
            "        return Point(x_ + dx, y_ + dy);\n"
            "    }\n"
            "};"
        ),
        "check": "把所有不改对象的成员函数都加上 const, 代码还能编译通过吗?",
    },
    {
        "id": "K06", "level": 1, "name": "static 成员与静态工厂",
        "keywords": ["static数据成员", "static成员函数", "静态工厂", "对象计数"],
        "summary": "static 成员属于“类”而不是“对象”, 用来表达所有对象共享的状态。",
        "points": [
            "static 数据成员必须在类外再定义一次(或在 C++17 里写 inline static);",
            "static 成员函数没有 this, 所以不能访问非静态成员;",
            "静态工厂函数可以只暴露“造对象”的接口, 把构造函数藏起来;",
            "函数内的 static 局部变量只构造一次, C++11 起初始化是线程安全的。",
        ],
        "pitfalls": [
            "忘了类外定义 -> 链接错误 undefined reference;",
            "把“对象个数”的计数写在拷贝构造函数里, 结果容器扩容时数字乱涨;",
            "在 static 成员函数里直接访问成员变量(编译不过)。",
        ],
        "example": (
            "class Ticket {\n"
            "    static int issued_;\n"
            "public:\n"
            "    static Ticket issue() { return Ticket(++issued_); }\n"
            "    static int total() { return issued_; }\n"
            "};\n"
            "int Ticket::issued_ = 0;   // 类外定义, 别忘了"
        ),
        "check": "这个共享状态真的属于“类”吗? 它会在什么时候被改写?",
    },
    {
        "id": "K07", "level": 1, "name": "运算符重载",
        "keywords": ["运算符重载", "operator<<", "operator>>", "比较运算符",
                     "有理性化简", "欧几里得算法"],
        "summary": "让自定义类型用起来像内置类型, 但必须遵守运算符原本的语义。",
        "points": [
            "算术运算符返回新对象且是 const 成员函数, 绝不能改自身;",
            "operator= 必须返回 `T&` 才能支持 `a = b = c`;",
            "operator<< / >> 要返回流引用 `std::ostream&` / `std::istream&`, 才能链式输出;",
            "运算符重载不能改变优先级, 也不能发明新运算符;",
            "定义域有“不变式”时(比如有理数分母恒正且最简), 每次运算都要维护它。",
        ],
        "pitfalls": [
            "把 operator+ 写成修改自身(那么 `a + b` 会顺手改掉 a);",
            "operator< 和 operator== 语义不一致, 导致排序/去重行为诡异;",
            "== 忘了处理浮点误差或约分, 明明相等的分数比较不等。",
        ],
        "example": (
            "Complex operator+(const Complex& o) const {     // const + 返回值\n"
            "    return Complex(re_ + o.re_, im_ + o.im_);\n"
            "}\n"
            "friend std::ostream& operator<<(std::ostream& os, const Complex& c) {\n"
            "    return os << c.re_ << '+' << c.im_ << 'i';   // 返回流引用\n"
            "}"
        ),
        "check": "每个运算符的语义都和内置类型一致吗? 有没有哪个运算顺手改了自己?",
    },
    {
        "id": "K08", "level": 2, "name": "继承与派生",
        "keywords": ["继承与派生", "派生类构造函数", "protected", "成员函数覆盖"],
        "summary": "继承表达“is-a”关系: 派生类自动拥有基类的数据和行为。",
        "points": [
            "派生类只能在初始化列表里调用基类构造函数;",
            "protected 让派生类能访问, 但外部仍然看不到 —— 是“给子类的接口”;",
            "构造顺序: 基类 → 成员对象 → 自身; 析构正好反过来;",
            "派生类写同名函数会“隐藏”基类版本, 需要时用 `using Base::func;` 拉回来。",
        ],
        "pitfalls": [
            "忘了在初始化列表里调用带参的基类构造(编译不过);",
            "用 private 继承(不加 public)导致多态失效;",
            "把基类数据成员写成 private, 派生类访问不到就只能到处加 getter。",
        ],
        "example": (
            "class Manager : public Employee {           // 注意 public\n"
            "    int bonus_;\n"
            "public:\n"
            "    Manager(const std::string& n, int s, int b)\n"
            "        : Employee(n, s), bonus_(b) {}      // 显式调用基类构造\n"
            "};"
        ),
        "check": "这是“is-a”还是“has-a”? 如果是 has-a, 应该用成员对象而不是继承。",
    },
    {
        "id": "K09", "level": 2, "name": "虚函数与运行时多态",
        "keywords": ["虚函数", "运行时多态", "基类指针", "vector容器", "指针容器"],
        "summary": "手里拿着基类指针, 却能调到派生类真正的实现 —— 这是多态。",
        "points": [
            "只有 virtual 函数才会“看对象真实类型”; 非虚函数看的是指针类型;",
            "基类里被派生类改写的函数, 在派生类里加 override 让编译器帮你检查签名;",
            "多态必须通过指针或引用: `Base b = derived;` 会发生对象切片;",
            "基类里的“接口函数”可以调用虚函数(模板方法模式), 调用时会自动分派。",
        ],
        "pitfalls": [
            "忘了写 virtual, 结果算出来全是基类的结果;",
            "签名差一点点(少了 const)导致没构成重写, 只是新写了一个函数;",
            "把派生对象按值塞进 vector<Base>, 切片后多态失效。",
        ],
        "example": (
            "class Shape {\n"
            "public:\n"
            "    virtual double area() const { return 0.0; }\n"
            "    void print() const { std::cout << area(); }   // 调用虚函数 -> 自动分派\n"
            "};\n"
            "class Circle : public Shape {\n"
            "public:\n"
            "    double area() const override { return 3.14159 * r_ * r_; }\n"
            "};"
        ),
        "check": "我用的是基类指针/引用吗? 被调用的那个函数是 virtual 吗?",
    },
    {
        "id": "K10", "level": 2, "name": "抽象类与虚析构",
        "keywords": ["纯虚函数", "抽象类", "虚析构函数", "多态删除", "虚析构"],
        "summary": "抽象类只描述接口, 不能实例化; 通过基类指针删对象时, 基类析构必须是 virtual。",
        "points": [
            "`virtual double area() const = 0;` 是纯虚函数, 含纯虚函数的类就是抽象类;",
            "抽象类不能创建对象, 但可以有指针和引用 —— 这正是多态的入口;",
            "基类析构不是 virtual 时, `delete base_ptr` 只会调用基类析构, 派生类资源泄漏;",
            "有虚函数的类, 析构函数就应该声明为 virtual。",
        ],
        "pitfalls": [
            "忘了 = 0, 结果基类还得给个没意义的实现;",
            "基类析构漏写 virtual, 程序能跑但资源静默泄漏;",
            "想在抽象类里创建对象(编译不过), 应该用工厂函数返回指针。",
        ],
        "example": (
            "class Shape {\n"
            "public:\n"
            "    virtual double area() const = 0;      // 纯虚 -> 抽象类\n"
            "    virtual ~Shape() {}                    // 必须!\n"
            "};"
        ),
        "check": "有没有基类指针 delete 的场景? 基类析构是 virtual 吗?",
    },
    {
        "id": "K11", "level": 2, "name": "友元",
        "keywords": ["友元函数", "友元类"],
        "summary": "友元是封装边界上“特意开的一扇门”, 要开得少、开得有理有据。",
        "points": [
            "友元不是成员函数, 定义时不要写 `类名::` 前缀;",
            "friend 声明写在类里, 但它本质上是“给外部函数/类访问私有成员的授权”;",
            "运算符重载需要访问两侧对象私有数据时, 友元比加一堆 getter 更干净;",
            "友元关系不能传递, 也不能继承。",
        ],
        "pitfalls": [
            "为了图省事把所有东西都声明 friend —— 等于放弃封装;",
            "明明是成员函数却写了 friend(重复授权);",
            "友元函数里误用 this(它没有 this)。",
        ],
        "example": (
            "class Matrix {\n"
            "    int m[2][2];\n"
            "public:\n"
            "    friend Matrix operator*(const Matrix& a, const Matrix& b);\n"
            "    friend class Calculator;          // 友元类\n"
            "};"
        ),
        "check": "不加 friend 真的做不到吗? 如果只是想读数据, 加个 getter 是不是更好?",
    },
    {
        "id": "K12", "level": 2, "name": "拷贝控制与 Rule of Three",
        "keywords": ["拷贝赋值运算符", "自赋值", "Rule of Three"],
        "summary": "析构函数、拷贝构造、拷贝赋值这三件事, 只要写了一件, 另外两件就必须一起考虑。",
        "points": [
            "operator= 要返回 `T&`; 开头先处理自赋值 `if (this == &other) return *this;`;",
            "更稳的写法: 先构造出新的资源, 成功后再释放旧的(异常安全);",
            "现代 C++ 也可以用“拷贝并交换”惯用法一行搞定;",
            "不想支持拷贝就明确禁用: `T(const T&) = delete;` —— 让错误在编译期暴露。",
        ],
        "pitfalls": [
            "operator= 里先 delete 自己的资源, 再去读 other —— 如果是自赋值就读到已释放内存;",
            "operator= 返回 void 或 T(而不是 T&), 导致 `a = b = c` 编译不过或多做一次拷贝;",
            "忘了处理“容量不足需要扩容”或“新旧大小不同”的情况。",
        ],
        "example": (
            "MyString& operator=(const MyString& other) {\n"
            "    if (this == &other) return *this;             // 1. 自赋值\n"
            "    char* fresh = new char[other.size_ + 1];      // 2. 先申请\n"
            "    std::memcpy(fresh, other.data_, other.size_ + 1);\n"
            "    delete[] data_;                               // 3. 再释放旧的\n"
            "    data_ = fresh; size_ = other.size_;\n"
            "    return *this;                                 // 4. 返回 *this\n"
            "}"
        ),
        "check": "写个 `a = a;` 试试, 会不会把对象弄坏?",
    },
    {
        "id": "K13", "level": 3, "name": "类模板与特化",
        "keywords": ["类模板", "模板成员函数", "模板全特化", "std::ostringstream", "模板"],
        "summary": "写一次, 用无数次: 编译器为每种类型各生成一份代码。",
        "points": [
            "类模板的成员函数如果写在类外, 每个都要重复写 `template <class T>`;",
            "模板定义通常要放在头文件里(实例化时要看得到完整定义);",
            "全特化 `template <> struct X<int> {...};` 用来给某个类型换实现;",
            "模板代码里的错误往往在实例化时才报, 报错信息很长 —— 先看第一行“实例化自哪里”。",
        ],
        "pitfalls": [
            "把模板实现单独放 .cpp, 结果链接时找不到符号;",
            "用 `str.format` 之外的占位符风格写模板参数, 记混了;",
            "模板里用 `>>` 忘记加空格(C++11 前的问题, 现在一般没事)。",
        ],
        "example": (
            "template <class T>\n"
            "class MyVector {\n"
            "    T* data_; int size_, cap_;\n"
            "public:\n"
            "    void push_back(const T& v) { if (size_ == cap_) grow(); data_[size_++] = v; }\n"
            "};\n"
            "template <> struct Formatter<bool> {          // 全特化\n"
            "    static std::string format(const bool& v) { return v ? \"true\" : \"false\"; }\n"
            "};"
        ),
        "check": "这个模板对 int / std::string / 自定义类型都能编译过吗?",
    },
    {
        "id": "K14", "level": 3, "name": "RAII 与智能指针",
        "keywords": ["RAII", "智能指针语义", "delete 拷贝构造", "资源管理", "unique_ptr"],
        "summary": "把资源的生命周期绑在对象的生命周期上: 栈对象析构, 资源自动释放。",
        "points": [
            "RAII = 构造时获取资源, 析构时释放资源; 提前 return、抛异常都不会漏;",
            "独占所有权用 std::unique_ptr(不可拷贝, 但可移动);",
            "共享所有权用 std::shared_ptr, 但不要滥用, 循环引用要用 weak_ptr;",
            "自己写智能指针时, 拷贝构造/拷贝赋值必须 `= delete`, 否则会出现两个指针管一块内存。",
        ],
        "pitfalls": [
            "`unique_ptr<T> a = b;` —— 编译不过, 因为独占所有权不能拷贝;",
            "用同一个裸指针构造两个 shared_ptr -> 双重释放;",
            "只写了 reset 没写析构, 或者 reset 时忘了释放旧指针。",
        ],
        "example": (
            "template <class T>\n"
            "class ScopedPtr {\n"
            "    T* p_;\n"
            "public:\n"
            "    explicit ScopedPtr(T* p = nullptr) : p_(p) {}\n"
            "    ~ScopedPtr() { delete p_; }\n"
            "    ScopedPtr(const ScopedPtr&) = delete;             // 禁止拷贝\n"
            "    ScopedPtr& operator=(const ScopedPtr&) = delete;\n"
            "    T* operator->() const { return p_; }\n"
            "};"
        ),
        "check": "中途 return 或者抛异常时, 这份资源会被释放吗?",
    },
    {
        "id": "K15", "level": 3, "name": "设计模式",
        "keywords": ["单例模式", "工厂模式", "观察者模式", "错误处理", "多态",
                     "引用返回", "接口指针数组", "抽象基类"],
        "summary": "模式是“被反复验证过的类与类之间的关系”, 用来解决变化点。",
        "points": [
            "单例: 构造函数私有 + 拷贝禁用 + 函数内 static 局部变量(现代写法);",
            "工厂: 把“选哪个派生类”这件事集中到一个函数里, 调用方只看基类接口;",
            "观察者: 主题只依赖 Observer 抽象接口, 变更时广播给所有订阅者;",
            "模式的目标永远是“把变化隔离到一处”, 不是为了显得高级。",
        ],
        "pitfalls": [
            "单例返回指针且不析构, 或者允许外部 new 出第二个实例;",
            "工厂返回裸指针却没有明确所有权, 导致泄漏或双重释放;",
            "观察者列表里保存了已销毁对象的指针(悬垂)。",
        ],
        "example": (
            "class Logger {\n"
            "    Logger() {}\n"
            "    Logger(const Logger&) = delete;\n"
            "public:\n"
            "    static Logger& instance() { static Logger only; return only; }  // 单例\n"
            "};\n"
            "static std::unique_ptr<Shape> create(char k, double a, double b);   // 工厂"
        ),
        "check": "如果明天要多加一种类型/多一个订阅者, 我需要改几处代码?",
    },
    {
        "id": "K16", "level": 3, "name": "多重继承与虚继承",
        "keywords": ["多重继承", "虚继承", "菱形继承"],
        "summary": "一个类可以同时是两种东西; 共同的祖先要用 virtual 继承, 否则会出现两份。",
        "points": [
            "菱形继承不加 virtual, 共同基类会出现两份 -> 访问成员时二义性编译错误;",
            "虚继承下, 由“最派生类”负责初始化虚基类, 中间类的初始化会被忽略;",
            "构造顺序: 虚基类 → 非虚基类(按声明顺序) → 自身;",
            "多重继承更适合“继承接口”, 而不是继承多份实现。",
        ],
        "pitfalls": [
            "忘了 virtual, 结果 `obj.baseMethod()` 编译报二义性;",
            "以为中间类的基类构造还在生效(虚继承下被忽略);",
            "拿多重继承去拼功能, 最后职责混乱。",
        ],
        "example": (
            "class Device { protected: int id_; };\n"
            "class Camera : virtual public Device { ... };      // 虚继承\n"
            "class Screen : virtual public Device { ... };\n"
            "class Phone : public Camera, public Screen {\n"
            "public:\n"
            "    Phone(int i, ...) : Device(i), Camera(...), Screen(...) {}   // 最派生类负责初始化\n"
            "};"
        ),
        "check": "这个共同基类只需要一份吗? 需要的话, 继承时写 virtual 了吗?",
    },
    {
        "id": "K17", "level": 2, "name": "组合与聚合(has-a)",
        "keywords": ["组合关系", "对象组合", "成员对象生命周期", "has-a", "is-a", "聚合"],
        "summary": "“有一个”用成员对象表达, “是一个”才用继承 —— 组合耦合更松, 应该优先考虑。",
        "points": [
            "判据: 只有在句子里说通“A 是一个 B”时才用继承; “A 有一个 B”一律用成员对象。",
            "组合成员是整体的一部分: 构造顺序 = 成员对象(按声明顺序) → 整体自身, 析构正好相反;",
            "成员对象要在初始化列表里构造; 如果它没有默认构造函数, 不在列表里初始化就是编译错误;",
            "组合把“变化”关进一个小盒子里: 换成员类型只改一处, 而继承会牵动整个派生体系;",
            "整体只暴露“整体能做什么”, 内部的零件(容器、成员对象)不该被外部绕过整体直接改动。",
        ],
        "pitfalls": [
            "为了复用几个函数就继承 —— 造出一堆“并不是 is-a”的继承, 后面改一处崩一片;",
            "成员对象没有默认构造函数, 却忘了在初始化列表里构造它(报 no matching function for call);",
            "以为初始化列表的书写顺序决定构造顺序 —— 实际只按成员在类里的声明顺序;",
            "把内部容器的引用交出去, 外部就能绕过整体直接改零件, 封装等于没做。",
        ],
        "example": (
            "class Engine {                          // 零件\n"
            "public:\n"
            "    explicit Engine(int power) : power_(power) {}\n"
            "private:\n"
            "    int power_;\n"
            "};\n"
            "class Car {                             // 整体: 组合(has-a), 不是继承\n"
            "    Engine engine_;                     // 成员对象: 先于 Car 构造, 晚于 Car 析构\n"
            "public:\n"
            "    explicit Car(int power) : engine_(power) {}   // 只能在初始化列表里构造它\n"
            "};"
        ),
        "check": "这个关系是“是”还是“有”? 如果是“有”, 我为什么还要把它写成继承?",
    },
    # ------------------------------------------------------------- 第 4 档
    # 教材(黄维通《Visual C++面向对象与可视化程序设计》第 5 版)第 2~8 章的
    # 可视化程序设计知识点。全部基于 MFC(第 2~8 章) —— 讲义里的示例都带完整头文件。
    {
        "id": "K18", "level": 4, "name": "Windows 编程基础与消息机制",
        "keywords": ["Windows编程", "窗口句柄", "HWND", "消息循环", "消息机制",
                     "WM_PAINT", "窗口类", "句柄", "消息驱动"],
        "summary": "Windows 程序是“消息驱动”的: 系统把用户操作变成消息投递给窗口, 你写处理函数响应它。",
        "points": [
            "几乎所有 Windows 对象在 API 层都是句柄: 窗口 HWND、设备环境 HDC、画笔 HPEN、画刷 HBRUSH —— 句柄是不透明整数, 用完要还。",
            "经典消息循环三件套: GetMessage 取消息 → TranslateMessage 处理键盘 → DispatchMessage 派发给窗口过程。",
            "一条消息有三个要素: hwnd(发给哪个窗口)、message(WM_ 开头的编号)、wParam/lParam(附加参数)。",
            "MFC 把“消息 → 处理函数”的对应关系写进消息映射表(见 K33), 你不再手写 window procedure 的 switch。",
            "重绘消息 WM_PAINT 是“必须处理”的消息: 窗口被遮挡/最小化恢复后, 系统靠它让你重画内容。",
        ],
        "pitfalls": [
            "没处理的消息忘了交给默认窗口过程(API 里是 DefWindowProc) —— 窗口会拖不动、关不掉;",
            "把绘制逻辑写在别处、WM_PAINT 里什么都不做 —— 窗口被遮挡再露出来就一片空白;",
            "记混参数位置: 鼠标坐标在 lParam(低 16 位 x、高 16 位 y), 键码在 wParam。",
        ],
        "example": (
            "// MFC 里“消息 → 处理函数”靠消息映射表(完整可编译的骨架见 K33)\n"
            "BEGIN_MESSAGE_MAP(CMainFrame, CFrameWnd)\n"
            "    ON_WM_PAINT()                       // WM_PAINT -> OnPaint\n"
            "    ON_WM_LBUTTONDOWN()                 // 左键按下 -> OnLButtonDown\n"
            "END_MESSAGE_MAP()"
        ),
        "check": "窗口被别的窗口挡住、再露出来时, 你的内容还能自动重画吗?(重绘逻辑在 OnPaint 里吗)",
    },
    {
        "id": "K19", "level": 4, "name": "设备环境与 GDI 绘图",
        "keywords": ["设备环境", "CDC", "CPaintDC", "CClientDC", "GDI", "绘图",
                     "画笔", "画刷", "CPen", "CBrush", "SelectObject", "映像模式", "RGB"],
        "summary": "所有绘图都必须通过“设备环境”(DC)进行; 画笔管线条, 画刷管填充。",
        "points": [
            "取 DC 的几种方式: OnPaint 里用 CPaintDC(构造自动 BeginPaint、析构自动 EndPaint); 想在别处随时画用 CClientDC; OnDraw 里直接用参数里的 CDC*。",
            "画笔 CPen 负责画线/画边框, 画刷 CBrush 负责填充; 创建后必须 SelectObject 选进 DC 才生效。",
            "颜色用宏 RGB(红, 绿, 蓝), 每个分量 0~255; 红色是 RGB(255, 0, 0)。",
            "使用自定义 GDI 对象的完整套路: 创建 → 选进 DC 并保存旧对象 → 绘制 → 把旧对象选回去 → 让新对象析构。",
            "默认映像模式 MM_TEXT: 坐标单位是像素, 原点在客户区左上角, x 向右、y 向下。",
        ],
        "pitfalls": [
            "只创建了 CPen 却没 SelectObject —— 画的还是默认黑笔, 看起来“没生效”;",
            "用完不把旧 GDI 对象选回去 —— 画笔析构时还选在 DC 里会造成 GDI 资源泄漏(画几百次就卡);",
            "在 OnPaint 之外用 CPaintDC —— 会触发断言/死锁, 那个 DC 只能在 WM_PAINT 期间存在。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 在 OnPaint 里画一条红色粗线\n"
            "void CMyView::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);                    // 绑定 WM_PAINT 的设备环境\n"
            "    CPen pen(PS_SOLID, 3, RGB(255, 0, 0));   // 3 像素宽的红色实线画笔\n"
            "    CPen* oldPen = dc.SelectObject(&pen);    // 选进 DC, 保存旧笔\n"
            "    dc.MoveTo(10, 10);\n"
            "    dc.LineTo(300, 200);\n"
            "    dc.SelectObject(oldPen);                 // 用完恢复, 防 GDI 泄漏\n"
            "}"
        ),
        "check": "我创建的画笔/画刷选进 DC 了吗? 用完把旧对象恢复回去了吗?",
    },
    {
        "id": "K33", "level": 4, "name": "消息映射与 MFC 程序骨架",
        "keywords": ["消息映射", "MFC程序结构", "CWinApp", "InitInstance",
                     "BEGIN_MESSAGE_MAP", "DECLARE_MESSAGE_MAP", "afxwin", "MFC"],
        "summary": "一个 MFC 程序 = 应用程序对象 + 主窗口 + 消息映射表; main 函数由 MFC 库替你写好了。",
        "points": [
            "全局唯一的 CWinApp 派生类对象就是“应用程序对象”: MFC 提供的入口会调用它的 InitInstance, 你在那里创建并显示主窗口。",
            "消息映射三件套: 类声明里 DECLARE_MESSAGE_MAP()、实现文件里 BEGIN_MESSAGE_MAP/END_MESSAGE_MAP 包围的条目表、以及 afx_msg 前缀的处理函数。",
            "处理函数的名字和签名是固定的: OnPaint、OnLButtonDown、OnKeyDown…… 写错签名能编译过但消息不会被派发到。",
            "MFC 头文件是 <afxwin.h>(包含它就有了 CWinApp/CWnd/CDC 等); 类名习惯上以 C 开头。",
            "InitInstance 返回 FALSE 表示“初始化失败, 直接退出程序”, 不是“跳过某个步骤”。",
        ],
        "pitfalls": [
            "类声明里忘了 DECLARE_MESSAGE_MAP() —— 消息映射表接不上, 处理函数永远不被调用;",
            "处理函数签名与教材不一致(比如 OnLButtonDown 少写了 UINT nFlags) —— 编译能过但收不到消息;",
            "在 InitInstance 里忘记 m_pMainWnd = &wnd 或忘记 wnd.ShowWindow/SW_SHOW —— 窗口建了但不显示。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "class CMyApp : public CWinApp {          // 应用程序对象\n"
            "public:\n"
            "    virtual BOOL InitInstance();\n"
            "};\n"
            "class CMainWnd : public CFrameWnd {      // 主窗口\n"
            "public:\n"
            "    CMainWnd() { Create(NULL, \"My First MFC\"); }\n"
            "    afx_msg void OnPaint();\n"
            "    DECLARE_MESSAGE_MAP()                // 消息映射声明(三件套之一)\n"
            "};\n"
            "BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)   // 消息映射表(三件套之二)\n"
            "    ON_WM_PAINT()\n"
            "END_MESSAGE_MAP()\n"
            "void CMainWnd::OnPaint() { CPaintDC dc(this); }\n"
            "BOOL CMyApp::InitInstance() {\n"
            "    CMainWnd* wnd = new CMainWnd();\n"
            "    m_pMainWnd = wnd;\n"
            "    wnd->ShowWindow(SW_SHOW);            // 不显示就什么都看不到\n"
            "    wnd->UpdateWindow();\n"
            "    return TRUE;\n"
            "}\n"
            "CMyApp theApp;                           // 全局唯一的应用程序对象"
        ),
        "check": "消息映射三件套(声明宏 / 映射表 / afx_msg 处理函数)都齐了吗? 处理函数签名和教材一致吗?",
    },
    {
        "id": "K22", "level": 4, "name": "键盘消息",
        "keywords": ["键盘消息", "OnKeyDown", "OnKeyUp", "WM_KEYDOWN", "虚拟键码", "VK_"],
        "summary": "键盘事件以 WM_KEYDOWN/WM_KEYUP/WM_CHAR 三类消息送达, MFC 把它们分发到 OnKeyDown 等处理函数。",
        "points": [
            "MFC 处理函数原型固定: afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)。",
            "nChar 是虚拟键码: 字母/数字键 VK_ 后缀与其 ASCII 一致(如 VK_ESCAPE=27、VK_RETURN=13), 方向键用 VK_LEFT 等。",
            "WM_KEYDOWN 是“物理按键”, WM_CHAR 才是“输入的字符” —— 想接收字符(含中文)要处理 OnChar。",
            "拿按键的可读名字: GetKeyNameText; 判断按下时是否带 Shift/Ctrl 用 GetKeyState。",
        ],
        "pitfalls": [
            "窗口没有输入焦点时收不到键盘消息 —— 用 SetFocus 或先点击窗口;",
            "把 nChar 当字符直接用 —— 它是虚拟键码, 想直接输出字符应该用 OnChar 的参数;",
            "按住不放会连发 WM_KEYDOWN(自动重复), 计数类逻辑要自己滤掉重复。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 在窗口类里声明:\n"
            "//   afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);\n"
            "// 消息映射表里加:\n"
            "//   ON_WM_KEYDOWN()\n"
            "void CMainWnd::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)\n"
            "{\n"
            "    if (nChar == VK_ESCAPE)               // 按 Esc 退出\n"
            "        PostMessage(WM_CLOSE);\n"
            "    CFrameWnd::OnKeyDown(nChar, nRepCnt, nFlags);   // 不处理的情况交回基类\n"
            "}"
        ),
        "check": "处理的是按键(OnKeyDown)还是字符(OnChar)? 消息映射表里挂上 ON_WM_KEYDOWN 了吗?",
    },
    {
        "id": "K23", "level": 4, "name": "鼠标消息",
        "keywords": ["鼠标消息", "OnLButtonDown", "OnLButtonUp", "OnMouseMove",
                     "WM_LBUTTONDOWN", "CPoint"],
        "summary": "鼠标按键与移动以 WM_xBUTTONDOWN/UP/MOVE 消息送达, MFC 分发到 OnLButtonDown 等函数, 坐标在 CPoint 里。",
        "points": [
            "MFC 处理函数原型固定: afx_msg void OnLButtonDown(UINT nFlags, CPoint point);",
            "point 是客户区坐标(相对窗口左上角); 需要屏幕坐标时用 ClientToScreen 转换。",
            "nFlags 里带着修饰键状态: MK_CONTROL、MK_SHIFT、MK_LBUTTON 等, 用按位与判断。",
            "典型套路: 在 OnLButtonDown 里记住起点, 在 OnMouseMove 里画橡皮筋, 在 OnLButtonUp 里定稿。",
        ],
        "pitfalls": [
            "把 CPoint 当成屏幕绝对坐标用 —— 多显示器/窗口移动后全错, 要转换走 ClientToScreen;",
            "只在 OnLButtonDown 画图却没有重绘准备 —— 窗口一旦被遮挡, 用 WM_PAINT 重画时没有持久数据可恢复;",
            "忘了在消息映射表里挂 ON_WM_LBUTTONDOWN, 函数写了也不被调用。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 声明: afx_msg void OnLButtonDown(UINT nFlags, CPoint point);\n"
            "// 映射表: ON_WM_LBUTTONDOWN()\n"
            "void CMainWnd::OnLButtonDown(UINT nFlags, CPoint point)\n"
            "{\n"
            "    CString text;\n"
            "    text.Format(\"你点在了 (%d, %d)\", point.x, point.y);   // point 是客户区坐标\n"
            "    CClientDC dc(this);\n"
            "    dc.TextOut(10, 10, text);\n"
            "    CFrameWnd::OnLButtonDown(nFlags, point);\n"
            "}"
        ),
        "check": "处理函数参数顺序对不对(UINT nFlags, CPoint point)? 坐标要客户区还是屏幕坐标?",
    },
    {
        "id": "K20", "level": 4, "name": "映像模式与坐标变换",
        "keywords": ["映像模式", "坐标变换", "MM_TEXT", "MM_LOMETRIC", "SetMapMode",
                     "逻辑坐标"],
        "summary": "逻辑坐标到设备坐标的换算规则由「映像模式」决定 —— 默认 MM_TEXT 是像素, 换成 MM_LOMETRIC 就是 0.1 毫米。",
        "points": [
            "默认映像模式 MM_TEXT: 1 逻辑单位 = 1 像素, 原点在客户区左上角, y 轴向下。",
            "SetMapMode(MM_LOMETRIC): 1 逻辑单位 = 0.1 毫米, **y 轴向上**; MM_HIMETRIC 则 0.01 毫米。",
            "按物理尺寸绘图的场合(打印、图纸)要用公制模式, 否则换台显示器/改分辨率图就变形。",
            "逻辑坐标 = 你传给画图函数的数值; 设备坐标 = 屏幕像素。两者之间由映像模式 + 窗口原点共同换算。",
        ],
        "pitfalls": [
            "切换映像模式后, 原来的坐标数值含义全变了(像素 → 0.1mm), 忘了同步改数值画面就“缩没了”;",
            "按 MM_TEXT 的习惯在 MM_LOMETRIC 下画 —— y 轴方向是反的, 图形上下颠倒;",
            "设置映像模式要在 OnPaint 里对当前 DC 做(CPaintDC dc(this); dc.SetMapMode(...)), 换一个 DC 就要重设。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "void CMyView::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "    dc.SetMapMode(MM_LOMETRIC);        // 之后坐标单位 = 0.1 毫米, y 向上\n"
            "    dc.Rectangle(100, 50, 500, 350);   // 40mm x 30mm 的矩形\n"
            "}"
        ),
        "check": "我的坐标是像素还是物理尺寸? 对应的映像模式设对了吗?",
    },
    {
        "id": "K21", "level": 4, "name": "字体与文本输出",
        "keywords": ["字体", "文本输出", "CFont", "CreateFont", "CreatePointFont",
                     "LOGFONT", "TextOut", "DrawText", "SetTextColor", "SetBkColor",
                     "SetBkMode", "SetFont"],
        "summary": "文本输出三件套: 选字体(SetFont) + 设颜色(SetTextColor/SetBkColor) + 输出(TextOut/DrawText)。",
        "points": [
            "创建字体: CFont + CreateFont(高度, 粗细, ...) 或更省事的 CreatePointFont(点大小, 字体名)。",
            "像其它 GDI 对象一样: SetFont 选进 DC 要保存旧字体指针, 用完恢复(否则 GDI 泄漏)。",
            "颜色: SetTextColor 设文字颜色, SetBkColor 设背景色; SetBkMode(TRANSPARENT) 让文字背景透明。",
            "TextOut(x, y, text) 输出单行; DrawText(text, &rect, DT_CENTER | DT_WORDBREAK) 支持居中与自动换行。",
            "居中排版要先量文本尺寸: dc.GetTextExtent(text) 得到宽高, 再反推左上角。",
        ],
        "pitfalls": [
            "创建了 CFont 却忘了 SetFont —— 输出还是默认系统字体;",
            "SetBkMode 不设 TRANSPARENT 时, 文字会带着黑/白底色把下面的图形盖住;",
            "DrawText 默认会擦掉矩形区域背景(要 dt 的参数控制), 在已有图形上叠字要注意。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "void CMyWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "    CFont font;\n"
            "    font.CreatePointFont(200, \"宋体\");        // 20 磅(单位为 0.1 磅)\n"
            "    CFont* oldFont = dc.SelectObject(&font);\n"
            "    dc.SetTextColor(RGB(255, 0, 0));          // 红色文字\n"
            "    dc.SetBkMode(TRANSPARENT);                // 透明背景\n"
            "    dc.TextOut(20, 20, \"Hello, MFC\");\n"
            "    dc.SelectObject(oldFont);                 // 恢复旧字体\n"
            "}"
        ),
        "check": "字体选进 DC 了吗? 旧字体恢复了吗? 背景模式设成透明了吗?",
    },
    {
        "id": "K24", "level": 4, "name": "菜单与加速键",
        "keywords": ["菜单资源", "菜单消息", "加速键", "命令消息", "ON_COMMAND",
                     "UPDATE_COMMAND_UI", "CMenu", "快捷菜单"],
        "summary": "点击菜单项发出的是「命令消息」(WM_COMMAND), 用 ON_COMMAND 把命令 ID 挂到处理函数; 加速键与菜单共用同一个 ID。",
        "points": [
            "每个菜单项有一个命令 ID(资源里 IDM_/ID_ 开头); 点击 → WM_COMMAND → 映射宏 ON_COMMAND(ID, 处理函数)。",
            "菜单项状态(变灰/打勾)用 ON_UPDATE_COMMAND_UI 在菜单弹出前同步, 不在 ON_COMMAND 里改。",
            "加速键表把 Ctrl+S 这类组合映射到同一个命令 ID —— 加一组快捷键不用改任何代码。",
            "程序里动态建菜单用 CMenu: CreateMenu/AppendMenu + SetMenu; 右键快捷菜单用 TrackPopupMenu。",
        ],
        "pitfalls": [
            "资源里改了菜单 ID 却忘了改代码里的 ID → 点了没反应;",
            "ON_COMMAND 写错消息映射表(应该写在拥有该处理函数的类里);",
            "把动态菜单的 CMenu 对象建成局部变量 → 函数退出菜单就没了(要让它活到用完之后)。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 消息映射表里: ON_COMMAND(IDM_ABOUT, &CMainWnd::OnAbout)\n"
            "// 类声明里:    afx_msg void OnAbout();\n"
            "void CMainWnd::OnAbout()\n"
            "{\n"
            "    MessageBox(\"这是关于对话框\", \"关于\", MB_OK);\n"
            "}\n"
            "// 动态建菜单(不用资源):\n"
            "//   CMenu menu; menu.CreateMenu();\n"
            "//   menu.AppendMenu(MF_STRING, IDM_ABOUT, \"关于\");\n"
            "//   SetMenu(&menu);"
        ),
        "check": "菜单项的命令 ID 与 ON_COMMAND 里写的一致吗? 状态更新用的是更新命令 UI 吗?",
    },
    {
        "id": "K25", "level": 4, "name": "对话框与 DDX 数据交换",
        "keywords": ["对话框资源", "模态对话框", "非模态对话框", "DoModal",
                     "CDialogEx", "OnInitDialog", "UpdateData", "DDX"],
        "summary": "对话框分模态(DoModal 阻塞)与非模态(Create 后并存); 控件与成员变量之间的同步靠 DDX, UpdateData 是那道闸门。",
        "points": [
            "模态对话框: 构造函数传资源 ID, DoModal() 阻塞运行, 返回 IDOK / IDCANCEL。",
            "非模态对话框: Create(IDD, this) + ShowWindow(SW_SHOW); 对象必须活到对话框关闭(常 new, 自删用 PostNcDestroy)。",
            "DDX 在 DoDataExchange 里写: DDX_Text(pDX, IDC_EDIT_NAME, m_name) 把控件和成员变量绑定。",
            "UpdateData(TRUE): 控件 → 变量(取输入); UpdateData(FALSE): 变量 → 控件(显示); 不调用就读到旧值。",
            "OnInitDialog 里做初始化(默认值/焦点), 必须调用基类的 CDialogEx::OnInitDialog()。",
        ],
        "pitfalls": [
            "非模态对话框用栈对象 → 函数一返回对象就析构, 对话框瞬间消失;",
            "读成员变量前忘了 UpdateData(TRUE) → 拿到的还是上次的值;",
            "OnInitDialog 忘了调基类版本 → 控件不初始化、焦点不对。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "#include \"resource.h\"          // 对话框控件 ID 在资源头文件里\n"
            "class CLoginDlg : public CDialogEx {\n"
            "public:\n"
            "    CString m_user;                 // 与编辑框绑定\n"
            "    CLoginDlg() : CDialogEx(IDD_LOGIN) {}\n"
            "    virtual BOOL OnInitDialog() {\n"
            "        CDialogEx::OnInitDialog();  // 先让基类做初始化\n"
            "        SetDlgItemText(IDC_EDIT_USER, \"admin\");\n"
            "        return TRUE;\n"
            "    }\n"
            "    void OnOK() {\n"
            "        UpdateData(TRUE);           // 控件 -> 成员变量\n"
            "        CDialogEx::OnOK();\n"
            "    }\n"
            "protected:\n"
            "    virtual void DoDataExchange(CDataExchange* pDX) {\n"
            "        CDialogEx::DoDataExchange(pDX);\n"
            "        DDX_Text(pDX, IDC_EDIT_USER, m_user);\n"
            "    }\n"
            "    DECLARE_MESSAGE_MAP()\n"
            "};\n"
            "// 使用: CLoginDlg dlg; if (dlg.DoModal() == IDOK) { /* dlg.m_user 已是最新值 */ }"
        ),
        "check": "是模态还是非模态? 对象生命周期对不对? UpdateData 的方向(TRUE/FALSE)用对了吗?",
    },
    {
        "id": "K26", "level": 4, "name": "位图与图标资源",
        "keywords": ["位图资源", "图标资源", "CBitmap", "CreateCompatibleDC", "BitBlt",
                     "LoadBitmap", "LoadIcon", "SetIcon", "兼容DC"],
        "summary": "位图不能直接画到窗口, 要先进「兼容 DC」中转, 再用 BitBlt 贴到目标 DC 上。",
        "points": [
            "位图显示四步: CBitmap 创建/加载 → CreateCompatibleDC 建兼容 DC → SelectObject 把位图选进兼容 DC → BitBlt 贴到窗口 DC。",
            "BitBlt(x, y, w, h, &srcDC, srcX, srcY, SRCCOPY): SRCCOPY 是直接复制, 最常用。",
            "加载位图资源用 LoadBitmap(IDB_XXX); 也可以用 CreateCompatibleBitmap 建一块空白位图自己画。",
            "应用程序图标是资源 IDR_MAINFRAME; 窗口换图标用 SetIcon(LoadIcon(...)); 任务栏图标同样来自这里。",
            "兼容 DC 与位图都是 GDI 对象: 用完 SelectObject 恢复旧对象, 再让它们析构, 否则 GDI 泄漏。",
        ],
        "pitfalls": [
            "把位图直接 SelectObject 进窗口 DC 就以为能显示 —— 必须先经兼容 DC;",
            "兼容 DC 用完不 DeleteDC / 不恢复旧位图 → GDI 资源泄漏;",
            "BitBlt 的宽高和位图实际尺寸不一致 → 图像被拉伸或只贴出一部分。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "void CMainWnd::OnPaint()\n"
            "{\n"
            "    CPaintDC dc(this);\n"
            "    CBitmap bmp;\n"
            "    bmp.CreateCompatibleBitmap(&dc, 200, 100);   // 建一块 200x100 的位图\n"
            "    CDC memDC;\n"
            "    memDC.CreateCompatibleDC(&dc);               // 兼容 DC\n"
            "    CBitmap* old = memDC.SelectObject(&bmp);     // 位图选进兼容 DC\n"
            "    memDC.Rectangle(0, 0, 199, 99);              // 在内存里画\n"
            "    dc.BitBlt(10, 10, 200, 100, &memDC, 0, 0, SRCCOPY);   // 贴到窗口\n"
            "    memDC.SelectObject(old);                     // 恢复\n"
            "}"
        ),
        "check": "位图走兼容 DC 了吗? BitBlt 的尺寸参数对吗? GDI 对象都恢复了吗?",
    },
    {
        "id": "K27", "level": 4, "name": "基础控件：按钮 / 静态 / 编辑框",
        "keywords": ["按钮控件", "CButton", "静态控件", "CStatic", "编辑框", "CEdit",
                     "BN_CLICKED", "ON_BN_CLICKED", "SetDlgItemText", "GetDlgItemText",
                     "控件通知"],
        "summary": "控件也是窗口; 操作控件是给它发消息(或调用它的类方法), 控件的事件以「通知消息」回到父窗口。",
        "points": [
            "程序化创建: CButton* p = new CButton; p->Create(\"确定\", WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON, rect, this, IDC_OK);",
            "按钮点击的通知是 BN_CLICKED → 用 ON_BN_CLICKED(IDC_OK, &CMyWnd::OnOk) 映射到处理函数。",
            "编辑框读写: SetDlgItemText/GetDlgItemText(父窗口便捷函数) 或 CEdit 的 SetWindowText/GetWindowText。",
            "静态控件 CStatic 用来显示文本/图标, 一般不给输入; 编辑框 CEdit 负责输入。",
            "通知消息按控件前缀区分: BN_(按钮)/EN_(编辑框)/LBN_(列表框)/CBN_(组合框), 映射宏同名加 ON_。",
        ],
        "pitfalls": [
            "创建控件时忘写 WS_VISIBLE → 控件存在但看不见;",
            "控件 ID 重复 → GetDlgItem 拿到的是另一个控件;",
            "在对话框程序里该用资源编辑器 + DDX 放控件, 却在 OnInitDialog 里手写 Create —— 两种方式别混(手写 Create 适合动态控件)。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 类里: CButton m_btn;  afx_msg void OnClicked();  ON_BN_CLICKED(IDC_BTN, &CMyWnd::OnClicked)\n"
            "void CMainWnd::OnCreate(LPCREATESTRUCT lpcs)   // 窗口创建时建控件\n"
            "{\n"
            "    CFrameWnd::OnCreate(lpcs);\n"
            "    m_btn.Create(\"点我\", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,\n"
            "                 CRect(20, 20, 120, 50), this, IDC_BTN);\n"
            "}\n"
            "void CMainWnd::OnClicked()\n"
            "{\n"
            "    CString name;\n"
            "    GetDlgItemText(IDC_EDIT_NAME, name);        // 取编辑框内容\n"
            "    SetDlgItemText(IDC_STATIC_RESULT, \"你好, \" + name);   // 显示到静态控件\n"
            "}"
        ),
        "check": "控件创建时给了 WS_VISIBLE 吗? 通知映射(ON_BN_)挂对了吗? 控件 ID 唯一吗?",
    },
    {
        "id": "K28", "level": 4, "name": "列表框与组合框",
        "keywords": ["列表框控件", "CListBox", "组合框控件", "CComboBox", "AddString",
                     "GetCurSel", "SetCurSel", "LBN_SELCHANGE", "CBN_SELCHANGE"],
        "summary": "列表框是纯列表, 组合框是「编辑框 + 列表」; 常用三件套: AddString 增项 / GetCurSel 取选中 / GetLBText 取文本。",
        "points": [
            "AddString 追加并返回索引; InsertString 插到指定位置; ResetContent 清空; GetCount 数项。",
            "GetCurSel 返回当前选中索引(没有选中返回 LB_ERR = -1); GetLBText(index, str) 取该项文本。",
            "选中变化通知: 列表框 LBN_SELCHANGE、组合框 CBN_SELCHANGE → ON_LBN_SELCHANGE / ON_CBN_SELCHANGE。",
            "组合框样式: CBS_DROPDOWN(可编辑)、CBS_DROPDOWNLIST(只选不可编辑)、CBS_SIMPLE(一直展开)。",
        ],
        "pitfalls": [
            "不判断 GetCurSel 的 -1 就直接 GetLBText → 取到空串或断言失败;",
            "组合框写 LBN_ 通知、列表框写 CBN_ → 消息映射对不上, 毫无反应;",
            "列表项很多时忘了排序(需要时手动 SortString 或加 LBS_SORT 样式)。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 类里: CListBox m_list;  afx_msg void OnSelChanged();\n"
            "//        ON_LBN_SELCHANGE(IDC_LIST, &CMyWnd::OnSelChanged)\n"
            "void CMainWnd::OnCreate(LPCREATESTRUCT lpcs)\n"
            "{\n"
            "    CFrameWnd::OnCreate(lpcs);\n"
            "    m_list.Create(WS_CHILD | WS_VISIBLE | WS_BORDER | LBS_NOTIFY,\n"
            "                  CRect(10, 10, 200, 200), this, IDC_LIST);\n"
            "    m_list.AddString(\"C++\");\n"
            "    m_list.AddString(\"MFC\");\n"
            "    m_list.SetCurSel(0);\n"
            "}\n"
            "void CMainWnd::OnSelChanged()\n"
            "{\n"
            "    int index = m_list.GetCurSel();\n"
            "    if (index != LB_ERR) {                     // 先判 -1!\n"
            "        CString text;\n"
            "        m_list.GetLBText(index, text);\n"
            "        SetDlgItemText(IDC_STATIC_SHOW, text);\n"
            "    }\n"
            "}"
        ),
        "check": "取选中项前判了 LB_ERR 吗? 通知宏(LBN_/CBN_)与控件类型匹配吗?",
    },
    {
        "id": "K29", "level": 4, "name": "滚动条与通用控件",
        "keywords": ["滚动条控件", "CScrollBar", "SetScrollRange", "SetScrollPos",
                     "进度条", "CProgressCtrl", "滑块控件", "CSliderCtrl", "ON_NOTIFY",
                     "通用控件"],
        "summary": "滚动条/进度条/滑块都围绕「范围 + 位置」工作; 交互要么走滚动通知, 要么走 WM_NOTIFY。",
        "points": [
            "滚动条: SetScrollRange(最小, 最大) + SetScrollPos(位置, TRUE 重绘); 拖动通知 WM_HSCROLL/WM_VSCROLL(→ OnHScroll/OnVScroll)。",
            "进度条 CProgressCtrl: SetRange32 + SetPos; 常用 SetTimer/OnTimer 定时推进。",
            "滑块 CSliderCtrl: SetRange + SetPos + SetPageSize; 变化通知走 WM_NOTIFY。",
            "通用控件(进度条/滑块/日期选择等)的通知消息是 WM_NOTIFY → 用 ON_NOTIFY(通知码, ID, 处理函数) 映射。",
        ],
        "pitfalls": [
            "SetScrollPos 的第二个参数忘了 TRUE → 代码里的位置对了, 屏幕上不动;",
            "SetPos 超过 SetRange 的上限 → 进度条停在满格(不会再涨);",
            "把 WM_NOTIFY 当成 WM_COMMAND 处理 → 通用控件的通知收不到。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 类里: CProgressCtrl m_progress; ON_WM_TIMER()\n"
            "void CMainWnd::OnCreate(LPCREATESTRUCT lpcs)\n"
            "{\n"
            "    CFrameWnd::OnCreate(lpcs);\n"
            "    m_progress.Create(WS_CHILD | WS_VISIBLE, CRect(20, 20, 320, 45),\n"
            "                      this, IDC_PROGRESS);\n"
            "    m_progress.SetRange32(0, 100);\n"
            "    SetTimer(1, 100, NULL);                    // 每 100ms 推进一格\n"
            "}\n"
            "void CMainWnd::OnTimer(UINT_PTR nIDEvent)\n"
            "{\n"
            "    if (nIDEvent == 1) {\n"
            "        int pos = m_progress.GetPos() + 5;\n"
            "        m_progress.SetPos(pos % 105);          // 循环推进\n"
            "    }\n"
            "    CFrameWnd::OnTimer(nIDEvent);\n"
            "}"
        ),
        "check": "范围与位置都设置了吗? 通知走的是滚动消息还是 WM_NOTIFY?",
    },
    {
        "id": "K30", "level": 4, "name": "文档视图与串行化",
        "keywords": ["文档视图", "CDocument", "CView", "Serialize", "串行化",
                     "CArchive", "SDI", "MDI", "文档模板"],
        "summary": "SDI/MDI 程序把「数据」放文档(CDocument)、「显示」放视图(CView); 存盘/读盘统一走 Serialize(CArchive)。",
        "points": [
            "一个文档可以有多个视图: 视图里 GetDocument() 拿文档指针, 文档用 UpdateAllViews() 通知所有视图刷新。",
            "文档模板(CSingleDocTemplate / CMultiDocTemplate)把 文档类/框架类/视图类 绑在一起, 在 InitInstance 里 AddDocTemplate 注册。",
            "串行化: 文档重写 Serialize(CArchive& ar), 用 ar.IsStoring() 判断方向, ar << / ar >> 像流一样读写数据。",
            "框架会在 新建/打开/存盘 时自动调用 OnNewDocument / OnOpenDocument / OnSaveDocument, 你只管在 Serialize 里写数据格式。",
        ],
        "pitfalls": [
            "把数据存在视图里 —— 换一个视图/窗口数据就丢了, 数据应该在文档里;",
            "Serialize 里读和写的顺序不一致 → 读出的数据全部错位;",
            "InitInstance 里忘了 AddDocTemplate → 程序启动即报错或直接退出。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 文档类: 数据 + 串行化\n"
            "class CNoteDoc : public CDocument {\n"
            "public:\n"
            "    CString m_text;\n"
            "    int m_count = 0;\n"
            "    virtual void Serialize(CArchive& ar) {\n"
            "        if (ar.IsStoring())\n"
            "            ar << m_text << m_count;       // 存盘: 写的顺序\n"
            "        else\n"
            "            ar >> m_text >> m_count;       // 读盘: 必须同样的顺序\n"
            "    }\n"
            "};\n"
            "// 视图类: 显示 + 取文档\n"
            "class CNoteView : public CView {\n"
            "public:\n"
            "    CNoteDoc* GetDocument() { return (CNoteDoc*)m_pDocument; }\n"
            "};"
        ),
        "check": "数据在文档里还是视图里? Serialize 的读写顺序对称吗?",
    },
    {
        "id": "K31", "level": 4, "name": "命令路由与快捷菜单/工具条",
        "keywords": ["命令路由", "快捷菜单", "TrackPopupMenu", "工具条", "CToolBar",
                     "状态栏", "CStatusBar", "右键菜单"],
        "summary": "菜单命令没人处理时会沿「视图 → 文档 → 框架 → 应用」自动传递(命令路由); 快捷菜单用 TrackPopupMenu 弹出。",
        "points": [
            "命令路由: ON_COMMAND 写在视图/文档/框架/应用任意一层都能收到消息, 框架自动把命令传给“最内层”的处理者。",
            "快捷菜单: OnContextMenu(或 OnRButtonDown)里: CMenu::LoadMenu + GetSubMenu → TrackPopupMenu(TPM_RIGHTBUTTON, 屏幕x, 屏幕y, this)。",
            "TrackPopupMenu 的坐标是**屏幕坐标** —— 鼠标消息给的是客户区坐标, 先 ClientToScreen 转换。",
            "工具条 CToolBar / 状态栏 CStatusBar 的按钮与窗格由资源定义(需要 .rc); 菜单项与按钮的可用状态统一用 ON_UPDATE_COMMAND_UI 更新。",
        ],
        "pitfalls": [
            "快捷菜单坐标忘了 ClientToScreen → 菜单弹在屏幕左上角而不是鼠标处;",
            "弹菜单前忘了 SetForegroundWindow / 弹完忘了 PostMessage(WM_NULL) → 菜单点不掉(不释放捕获);",
            "工具条按钮 ID 与命令处理函数的 ID 不一致 → 按钮点了没反应。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "// 声明: afx_msg void OnContextMenu(CWnd* pWnd, CPoint point);\n"
            "//       消息映射: ON_WM_CONTEXTMENU()\n"
            "void CMainWnd::OnContextMenu(CWnd* /*pWnd*/, CPoint point)\n"
            "{\n"
            "    CMenu menu;\n"
            "    menu.LoadMenu(IDR_POPUP);               // 资源里的菜单(也可 CreatePopupMenu 动态建)\n"
            "    CMenu* popup = menu.GetSubMenu(0);\n"
            "    popup->TrackPopupMenu(TPM_RIGHTBUTTON, point.x, point.y, this);\n"
            "    // OnContextMenu 传进来的 point 已经是屏幕坐标, 不用再转换\n"
            "}"
        ),
        "check": "快捷菜单的坐标是屏幕坐标吗? 命令映射挂在哪一层(视图/文档/框架)?",
    },
    {
        "id": "K32", "level": 4, "name": "多媒体程序设计",
        "keywords": ["多媒体", "PlaySound", "mciSendString", "音频", "winmm",
                     "MCI", "Media Player"],
        "summary": "最简单的音频播放是 PlaySound; 更复杂的控制(wav/mp3/暂停/定位)用 MCI(mciSendString)。",
        "points": [
            "PlaySound(文件名, NULL, SND_FILENAME | SND_ASYNC) 异步播放 wav; 需要链接 winmm.lib。",
            "PlaySound(NULL, NULL, SND_PURGE) 停止当前播放; SND_LOOP 循环。",
            "MCI 一行一命令: mciSendString(\"open a.mp3 alias m\", ...) → \"play m\" → \"close m\", 支持更多格式与控制。",
            "教材还介绍 Windows Media Player 控件(ActiveX, 在 .rc 对话框里插入), 功能最全但要资源。",
        ],
        "pitfalls": [
            "忘了链接 winmm.lib → LNK2019 unresolved external symbol PlaySound;",
            "用 SND_SYNC 播放长音频 → 整个界面卡住(应该用 SND_ASYNC);",
            "音频文件用相对路径, 工作目录不对就找不到 → 用绝对路径或确认工作目录。",
        ],
        "example": (
            "#include <afxwin.h>\n"
            "#pragma comment(lib, \"winmm.lib\")          // 或工程属性里加 winmm.lib\n"
            "void CMainWnd::OnPlayMusic()\n"
            "{\n"
            "    // 异步播放(不卡界面):\n"
            "    PlaySound(\"C:\\\\music\\\\bgm.wav\", NULL, SND_FILENAME | SND_ASYNC);\n"
            "    // 停止:\n"
            "    // PlaySound(NULL, NULL, SND_PURGE);\n"
            "}"
        ),
        "check": "链接了 winmm.lib 吗? 用的是异步播放吗? 文件路径能找到吗?",
    },
]

SKILL_BY_ID: Dict[str, Dict[str, Any]] = {s["id"]: s for s in SKILLS}


def skill(skill_id: str) -> Optional[Dict[str, Any]]:
    return SKILL_BY_ID.get(skill_id)


def skill_name(skill_id: str) -> str:
    item = SKILL_BY_ID.get(skill_id)
    return item["name"] if item else skill_id


def all_skill_ids() -> List[str]:
    return [s["id"] for s in SKILLS]


def path_order() -> List[str]:
    """按 难度档位 → 定义顺序 排出的学习路径。"""
    ordered = sorted(SKILLS, key=lambda s: (int(s["level"]), SKILLS.index(s)))
    return [s["id"] for s in ordered]


def skills_by_level(level: int) -> List[Dict[str, Any]]:
    return [s for s in SKILLS if int(s["level"]) == int(level)]


def classify(topics: Sequence[str], limit: int = 4) -> List[str]:
    """把题目里的中文 topics 映射到知识点 id。

    匹配规则是“关键词必须是被包含在 topic 里的子串”(不是反过来),
    并且**同一个 topic 只认最长命中的那个关键词**, 否则
    “拷贝构造函数”会同时命中 K02(构造函数) 和 K04(拷贝构造函数)。
    """
    if not topics:
        return []
    picked: Dict[str, int] = {}
    for raw in topics:
        topic = str(raw).strip().lower()
        if not topic:
            continue
        best_skill: Optional[str] = None
        best_len = 0
        for item in SKILLS:
            for keyword in item["keywords"]:
                word = str(keyword).lower()
                if word and word in topic and len(word) > best_len:
                    best_skill, best_len = item["id"], len(word)
        if best_skill:
            picked[best_skill] = max(picked.get(best_skill, 0), best_len)
    order = path_order()
    return sorted(picked, key=lambda sid: order.index(sid))[:limit]


def classify_text(text: str, limit: int = 3) -> List[str]:
    """从一段自由文本(题目标题 + 题目描述)里猜知识点。

    在线导入的题(洛谷/dotcpp)没有我们统一的知识点标签, 靠这个函数补上,
    这样它们也能参与学习画像与自适应选题。
    """
    blob = (text or "").lower()
    if not blob.strip():
        return []
    hits: Dict[str, int] = {}
    for item in SKILLS:
        for keyword in item["keywords"]:
            word = str(keyword).lower()
            if word and word in blob:
                hits[item["id"]] = max(hits.get(item["id"], 0), len(word))
    order = path_order()
    # 命中越长越具体, 优先返回; 同样长度时按学习路径排
    return sorted(hits, key=lambda sid: (-hits[sid], order.index(sid)))[:limit]


def teach_markdown(skill_ids: Sequence[str], width: int = 76) -> str:
    """把若干知识点写成一份 markdown 讲义(用于每题目录下的 knowledge.md)。"""
    lines: List[str] = []
    for sid in skill_ids:
        item = skill(sid)
        if item is None:
            continue
        lines.append("## %s %s    <sub>第 %d 档</sub>" % (
            sid, item["name"], int(item["level"])))
        lines.append("")
        lines.append(item["summary"])
        lines.append("")
        lines.append("### 要点")
        lines.append("")
        for index, point in enumerate(item["points"], start=1):
            lines.append("%d. %s" % (index, point))
        lines.append("")
        lines.append("### 常见坑")
        lines.append("")
        for pitfall in item["pitfalls"]:
            lines.append("- %s" % pitfall)
        lines.append("")
        lines.append("### 正确写法示例")
        lines.append("")
        lines.append("```cpp")
        lines.append(item["example"].rstrip())
        lines.append("```")
        lines.append("")
        lines.append("### 动手前自问")
        lines.append("")
        lines.append("> %s" % item["check"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def teach_lines(skill_id: str, width: int = 76) -> List[str]:
    """生成一个知识点的完整讲解(纯文本行, 交给命令行/提交包直接用)。"""
    import oop_common as oc

    item = skill(skill_id)
    if item is None:
        return ["(没有这个知识点的讲解: %s)" % skill_id]
    lines: List[str] = []
    title = "%s %s   [第 %d 档]" % (item["id"], item["name"], item["level"])
    lines.append(oc.color(title, "bold"))
    lines.extend(oc.wrap_text(item["summary"], width, indent="  "))
    lines.append("")
    lines.append(oc.color("  要点", "cyan"))
    for index, point in enumerate(item["points"], start=1):
        lines.extend(oc.wrap_text("%d) %s" % (index, point), width, indent="     "))
    lines.append("")
    lines.append(oc.color("  常见坑", "yellow"))
    for point in item["pitfalls"]:
        lines.extend(oc.wrap_text("· " + point, width, indent="     "))
    lines.append("")
    lines.append(oc.color("  正确写法示例", "cyan"))
    for row in item["example"].split("\n"):
        lines.append("     " + row)
    lines.append("")
    lines.extend(oc.wrap_text("  自查: " + item["check"], width))
    return lines


# ---------------------------------------------------------------------------
# 诊断表 1: 编译器报错 -> 知识点
# ---------------------------------------------------------------------------
# (正则, 知识点, 这是怎么回事, 怎么改)
COMPILER_ERRORS: List[Tuple[str, str, str, str]] = [
    (r"unresolved external|undefined reference|LNK2019|LNK2001",
     "K06",
     "链接期找不到某个函数的定义 —— 常见于“只声明没实现”, 或者 static 成员忘了在类外定义。",
     "检查是不是漏了函数体; static 数据成员要在类外写一行 `int 类名::成员 = 0;`。"),
    (r"no matching function for call to|no instance of constructor",
     "K02",
     "构造函数的参数对不上 —— 要么参数个数/类型不符, 要么你传了参数但类里只有默认构造。",
     "对照 main 里怎么创建对象的, 把构造函数签名写成完全一致。"),
    (r"discards qualifiers|passing .* as .this. argument|argument has type .const|"
     r"not marked const|cannot convert .*const",
     "K05",
     "const 正确性问题: const 对象(或 const 引用)调用了没有 const 的成员函数。",
     "给不修改对象状态的成员函数加上 const。"),
    (r"is private within this context|is protected within this context",
     "K01",
     "访问了 private / protected 成员 —— 外部代码只能走 public 接口。",
     "要么给类加一个 public 的成员函数, 要么确认这行代码是不是该写在类里(或者用 friend)。"),
    (r"cannot instantiate abstract|is abstract|pure virtual",
     "K10",
     "想创建抽象类的对象, 或者某个纯虚函数在派生类里没有实现。",
     "抽象类只能通过指针/引用使用; 派生类必须把所有纯虚函数都实现掉。"),
    (r"use of deleted function|call to deleted constructor",
     "K14",
     "调用了被 `= delete` 禁用的函数(常见于禁止拷贝的智能指针类)。",
     "独占所有权的类型不能拷贝, 改成传引用或移动。"),
    (r"invalid new-expression of abstract|object of abstract",
     "K10",
     "派生类没有实现基类全部的纯虚函数, 所以它自己也是抽象类。",
     "检查派生类的函数签名(参数、const)是否和基类完全一致。"),
    (r"too few arguments|too many arguments",
     "K02",
     "调用时给的参数个数和函数声明不一致。",
     "数一数参数; 别把逗号写成中文逗号。"),
    (r"expected .*;|expected .*\)",
     "K02",
     "语法层面缺了一个符号, 最常见的是漏分号或者括号不配对。",
     "看报错行的**上一行**末尾有没有 `;`, 括号是否成对。"),
    (r"was not declared in this scope|undeclared identifier|is not a member",
     "K01",
     "用了一个没声明过的名字 —— 拼写错误、没包含头文件、或者函数不是这个类的成员。",
     "核对拼写; 需要 `#include <string>` / `<vector>` / `<memory>` 等; 检查函数是不是写在了类外却忘了加 `类名::`。"),
    (r"return type|no return statement|not all control paths return",
     "K02",
     "函数声明了返回类型, 但某条路径没有 return。",
     "给非 void 函数的所有分支补上返回值。"),
    (r"cannot convert .* to .* in initialization|invalid conversion",
     "K02",
     "类型不匹配, 而且没有可用的隐式转换。",
     "显式构造或者改参数类型; 也可能是忘了加 explicit 之外的类型转换。"),
    (r"redefinition|multiple definition",
     "K01",
     "同一个东西被定义了两次 —— 常见于把函数实现写进了头文件、或者重复 include。",
     "实现放 .cpp; 头文件加 include guard。"),
    (r"override.*does not override|marked .override. but does not override",
     "K09",
     "你以为在重写基类虚函数, 但签名不完全一致(常见是少了 const)。",
     "对照基类把那行抄下来, 只改函数体。"),
    (r"ambiguous",
     "K16",
     "名字有二义性 —— 菱形继承不加 virtual 时, 成员会有两份。",
     "把共同基类改成虚继承 `virtual public Base`, 或者用明确的 `A::member` 限定。"),
    # ---- 兜底: 万一编译器仍然吐中文(没带上 VSLANG=1033 的时候) --------------
    (r"不能将.*this.*指针从.*const|转换丢失限定符|丢弃限定符",
     "K05",
     "const 正确性问题: 拿一个 const 对象去调用没有 const 的成员函数。",
     "给不修改对象状态的成员函数加上 const。"),
    (r"是 private|无法访问.*private|不可访问",
     "K01",
     "访问了 private / protected 成员。",
     "走 public 接口, 或者在类内部访问。"),
    (r"未声明的标识符|未定义标识符|找不到标识符",
     "K01",
     "用了一个没声明过的名字。",
     "核对拼写、补 #include、确认函数是不是少了 `类名::` 前缀。"),
    (r"没有与参数列表匹配的构造函数|无法将.*转换为|不存在从.*到.*的转换",
     "K02",
     "构造函数的参数对不上。",
     "对照 main 里创建对象的方式, 把构造函数签名写成一致。"),
    (r"抽象类|纯虚函数.*没有|没有实现.*纯虚",
     "K10",
     "派生类没有实现基类全部的纯虚函数, 它自己仍然是抽象类。",
     "把所有纯虚函数都实现掉, 并检查签名(参数、const)是否一致。"),
    (r"应输入|缺少.*分号|syntax error|语法错误",
     "K02",
     "语法层面缺了符号, 最常见是漏分号或括号不配对。",
     "看报错行的上一行末尾有没有 `;`。"),
    (r"无法解析的外部符号|无法解析的外部命令|LNK2019",
     "K06",
     "链接期找不到某个函数或静态成员的定义。",
     "检查是不是只声明没实现; static 数据成员要在类外写一行定义。"),
    (r"没有合适的默认构造函数|没有与参数列表匹配的构造函数|无法实例化抽象类|no default constructor",
     "K02",
     "创建对象时构造函数对不上; 也可能是成员对象 / 基类没有默认构造函数, 而你没在初始化列表里把它构造出来。",
     "对照 main 里的创建方式写构造函数; 成员对象和基类都只能在初始化列表里构造, "
     "例如 `Order(...) : owner_(o), discount_(t, a) {}`。"),
]

# ---------------------------------------------------------------------------
# 诊断表 2: 静态审查规则 -> 知识点
# ---------------------------------------------------------------------------
REVIEW_HINTS: Dict[str, Tuple[str, List[str]]] = {
    "R00": ("K01", ["题目要求用类解决, 但代码里没有类 —— 先把“要抽象什么”想清楚再动手。"]),
    "R01": ("K12", [
        "Rule of Three 破防了。只要写了析构函数, 拷贝构造和拷贝赋值就得一起考虑。",
        "最保险的做法: 先用 `= delete` 明确禁用拷贝, 等真的需要拷贝时再写深拷贝。",
    ]),
    "R02": ("K10", [
        "有虚函数就说明这个类可能被当基类用, 那么通过基类指针 delete 时, 基类析构必须是 virtual,",
        "否则派生类的析构函数根本不会被调用。",
    ]),
    "R03": ("K12", [
        "`a = a` 时, 如果先释放了自己的资源再去读 other, 读到的就是已经释放的内存。",
        "开头加一行 `if (this == &other) return *this;` 就解决了。",
    ]),
    "R04": ("K14", [
        "new 和 delete 必须一一对应, new[] 必须配 delete[]。",
        "更省心的做法是交给 std::unique_ptr / std::vector 管, 让析构自动发生。",
    ]),
    "R05": ("K05", [
        "不修改对象状态的成员函数都应该加 const。",
        "加了 const 之后 const 对象也能调用它, 这也是编译器帮你做检查的机会。",
    ]),
    "R06": ("K08", [
        "`class A : B` 是 private 继承, 外部无法把 A 当 B 用, 多态也就没了。",
        "继承体系基本都用 `public` 继承。",
    ]),
    "R07": ("K01", ["TODO 还留着, 说明有功能没写完, 先补完再评测。"]),
    "R08": ("K01", ["`using namespace std;` 在头文件里会污染所有包含它的文件, .cpp 里也建议显式写 std::。"]),
    "R09": ("K14", ["C 风格的字符串函数不检查长度, 用 std::string 更安全。"]),
    "R10": ("K09", ["重写虚函数时加 override, 签名写错会立刻编译报错, 而不是悄悄变成新函数。"]),
    "R11": ("K13", ["<bits/stdc++.h> 只有 GCC 有, MSVC 编译不过, 要显式包含用到的头文件。"]),
    "R12": ("K03", ["std::endl 每次都刷缓冲区, 循环里用 '\\n' 更快。"]),
}


def map_compiler_error(log: str) -> List[Dict[str, str]]:
    """从编译器输出里找出可解释的错误, 返回诊断条目。"""
    import re

    text = log or ""
    found: List[Dict[str, str]] = []
    seen: List[str] = []
    for pattern, skill_id, why, how in COMPILER_ERRORS:
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        if skill_id in seen:
            continue                                # 同一知识点只讲一次
        seen.append(skill_id)
        line = text.count("\n", 0, match.start()) + 1
        found.append({
            "skill": skill_id,
            "line": str(line),
            "why": why,
            "how": how,
        })
        if len(found) >= 3:
            break
    return found


def map_review_rule(rule: str) -> Optional[str]:
    item = REVIEW_HINTS.get(rule)
    return item[0] if item else None
