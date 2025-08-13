#include <iostream>

int main() {
    int number, sum = 0, remainder;

    // 获取用户输入的整数
    std::cout << "请输入一个整数: ";
    std::cin >> number;

    // 确保我们处理的是正数
    if (number < 0) {
        number = -number;
    }

    // 计算个位数之和
    while (number > 0) {
        remainder = number % 10; // 获取个位数
        sum += remainder;        // 累加到总和中
        number /= 10;            // 移除个位数
    }

    // 输出结果
    std::cout << "该整数的个位数之和是: " << sum << std::endl;

    return 0;
}
