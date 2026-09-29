# 先学后练 · B01 学生类：封装与 const 成员函数

> 建议先花 5~10 分钟把这一页读完, 再打开 `main.cpp` 动手。
> 卡住的时候回到这里对照「要点」和「常见坑」。

| 项目 | 内容 |
| --- | --- |
| 本题知识点 | K01 类与封装、K02 构造函数与初始化列表、K05 const 正确性与 this |
| 难度 | ★☆☆ 基础 |

---

## K01 类与封装    <sub>第 1 档</sub>

把“数据”和“操作数据的函数”捆成一个类型, 并把数据藏起来, 只留出必要的接口。

### 要点

1. class 默认访问级别是 private, struct 默认是 public —— 练习里优先用 class + 显式 public:。
2. 数据成员一律 private; 需要给外部看的用取值函数(getter)暴露, 而不是把成员开成 public。
3. 接口(public)要少而稳定, 实现细节(private)可以随便改 —— 这就是封装带来的抗变化能力。
4. this 指针在成员函数里指向“当前对象”, 返回 *this 才能支持链式调用。

### 常见坑

- 把数据成员写成 public, 封装直接失效;
- 给每个成员都配 getter/setter, 等于把 private 当装饰 —— 应该暴露“有意义的操作”而不是裸数据;
- 在类定义里写实现(内联)没问题, 但别把整个程序逻辑都堆进去。

### 正确写法示例

```cpp
class Account {
private:
    double balance_;              // 数据藏起来
public:
    explicit Account(double init) : balance_(init) {}
    void deposit(double amount);   // 暴露“有意义的操作”
    double balance() const;        // 只读的取值函数
};
```

### 动手前自问

> 问自己: 这个类的数据, 外部能随便改吗? 能改的路径是不是都经过了校验?

---

## K02 构造函数与初始化列表    <sub>第 1 档</sub>

对象一出生就必须是合法的。构造函数负责给每个成员一个确定的初值。

### 要点

1. 成员初始化列表的执行顺序只取决于成员的声明顺序, 与你在列表里的书写顺序无关。
2. const 成员、引用成员、没有默认构造的成员对象, 只能在初始化列表里赋值, 函数体里赋值不合法。
3. explicit 修饰单参数构造函数, 防止编译器偷偷做隐式类型转换。
4. 构造函数可以重载; 用默认参数可以少写好几个重载版本。

### 常见坑

- 在函数体里写 `x = v;` 而不是 `: x(v)` —— 对类类型成员这是“先默认构造再赋值”, 多一次开销;
- 初始化列表顺序写错, 依赖了还没初始化的成员;
- 忘了给指针成员初始化, 留下野指针。

### 正确写法示例

```cpp
class Date {
    int year_, month_, day_;
public:
    Date(int y, int m, int d) : year_(y), month_(m), day_(d) {}  // 初始化列表
};
```

### 动手前自问

> 每个数据成员都在初始化列表里出现了吗? 顺序和声明顺序一致吗?

---

## K05 const 正确性与 this    <sub>第 1 档</sub>

const 不是装饰品 —— 它让编译器帮你证明“这个函数不会改对象”。

### 要点

1. 不修改对象状态的成员函数都应该加 const, 否则 const 对象调用不了它;
2. const 成员函数里 this 的类型是 `const T*`, 不能改成员(除非成员声明为 mutable);
3. 参数能传 const 引用就传 const 引用: 避免拷贝, 又能接受临时对象;
4. 返回“内部数据的引用”时, 如果对象是 const 的, 返回的也必须是 const 引用。

### 常见坑

- 一半函数有 const 一半没有, 用的时候到处报错;
- 为了让 const 对象能编译, 直接把成员声明成 mutable —— 这是在骗编译器;
- getter 返回 `const std::string&`, 但函数自己没加 const。

### 正确写法示例

```cpp
class Point {
    int x_, y_;
public:
    int x() const { return x_; }                       // 只读 -> const
    Point moveBy(int dx, int dy) const {               // 不改自身 -> const
        return Point(x_ + dx, y_ + dy);
    }
};
```

### 动手前自问

> 把所有不改对象的成员函数都加上 const, 代码还能编译通过吗?

---


## 学完了?

回到 [problem.md](problem.md) 看题目要求, 然后编辑 `main.cpp`。

- VSCode: `Ctrl+Shift+B` 构建, `F5` 调试(会自动先构建)
- Visual Studio: 把本工程设为启动项目, `F5` 调试
- 命令行评测: `py oop_lab.py judge b01`
