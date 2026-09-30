// ================== TODO: 补全头文件 ==================
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
