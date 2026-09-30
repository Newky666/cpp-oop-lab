// ================== TODO: 补全头文件 ==================
// 本题需要用到的头文件(请自己补全 #include):
//   <iostream>
//   <iomanip>
// 下面这行 using namespace std; 已帮你写好

using namespace std;

// ================== TODO: 按教材 1.2.2 补全 Student 类 ==================
// 要求:
//   * 在 Student 内部定义嵌套类 Score(三个 private 成绩成员)
//   * Score 提供 Score(int a, int b, int c) 与 double average() const
//   * Student 持有一个 Score 成员(初始化列表里构造)并转调 average()
class Student {

};
// ========================================================================

int main() {
    int n;
    if (!(cin >> n)) return 0;
    cout << fixed << setprecision(1);
    for (int i = 0; i < n; ++i) {
        int a, b, c;
        cin >> a >> b >> c;
        const Student s(a, b, c);
        cout << s.average() << '\n';
    }
    return 0;
}
