#include <iostream>

// 计算梯形面积的函数
double calculateTrapezoidArea(double topBase, double bottomBase, double height) {
    return (topBase + bottomBase) * height / 2.0;
}

int main() {
    double topBase, bottomBase, height;

    // 从用户那里获取梯形的上底、下底和高
    std::cout << "请输入梯形的上底长度: ";
    std::cin >> topBase;
    std::cout << "请输入梯形的下底长度: ";
    std::cin >> bottomBase;
    std::cout << "请输入梯形的高: ";
    std::cin >> height;

    // 计算面积
    double area = calculateTrapezoidArea(topBase, bottomBase, height);

    // 输出结果
    std::cout << "梯形的面积是: " << area << std::endl;

    return 0;
}
