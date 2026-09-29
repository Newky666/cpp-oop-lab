# B01 学生类：封装与 const 成员函数

> **先学后练**：本页只讲题目。动手之前请先读 [knowledge.md](knowledge.md) —— 里面是本题涉及的 K01、K02、K05 共 3 个知识点的完整讲解、示例与常见坑。

| 项目 | 内容 |
| --- | --- |
| 难度 | ★☆☆ 基础 |
| 知识点 | 类的定义 / 访问控制 / 构造函数 / const成员函数 |
| 自动用例 | 3 组 |

## 题目描述

面向对象的第一步: 把“学生”这个抽象概念变成一段代码。校园里每个学生都有学号、姓名、成绩, 也有“展示自己信息”的动作 —— 这就是属性(数据成员)与方法(成员函数)。关键约束是访问控制: 数据必须 private, 只能通过 public 接口访问, 这就是封装。

## 具体要求

1. 用 class 定义 Student, 数据成员 id(int)/name(std::string)/score(int) 全部放在 private 区。
2. 提供一个带默认参数的构造函数 Student(int id = 0, const std::string& name = "", int score = 0), 并尽量使用成员初始化列表。
3. 提供三个 const 成员函数: int getId() const、const std::string& getName() const、int getScore() const。
4. 提供 void show() const, 输出一行: 学号 姓名 成绩（三者之间用一个空格分隔）。

## 输入输出

第一行一个整数 n(1 ≤ n ≤ 1000)。接下来 n 行, 每行是 学号 姓名 成绩。输出 n 行, 每行输出对应的 学号 姓名 成绩。

## 样例

### 样例 1

输入
```text
2
1001 Tom 88
1002 Jerry 95
```
输出
```text
1001 Tom 88
1002 Jerry 95
```

## 提示

- getter 必须加 const, 否则 const Student 对象(以及 const 引用)调不动它们。
- show() 里不要用 std::endl 也行, 用 '\n' 更快; 两者评测都接受。
- 成绩用 int 就够了, 本题不需要浮点。

## 完成前自查(面向对象要点)

- [ ] 数据成员是否全在 private 区?
- [ ] 构造函数是否用了初始化列表而不是在函数体里赋值?
- [ ] 读取数据的成员函数是否都加了 const?

## 怎么练

1. 先读 [knowledge.md](knowledge.md) 里的知识点讲解。
2. 编辑 `main.cpp`, 把 `TODO` 那一段补完(题目给的 `main` 不要改)。
3. VSCode: `Ctrl+Shift+B` 构建 → `F5` 调试; 想跑某一组用例: `终端 → 运行任务 → 运行当前题 · 用例 N`。
4. Visual Studio: 打开工作区里的 `oop_lab.sln`, 把本工程设为启动项目后 `F5`。
5. 命令行一步到位:

```bat
py oop_lab.py judge b01        :: 评测 + 老师式诊断
py oop_lab.py review b01       :: 写法审查
py oop_lab.py study b01        :: 再看一遍知识点讲义
```
