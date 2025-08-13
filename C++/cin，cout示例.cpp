#include <iostream>
#include <cstdlib>

int main() {
    // 设置命令提示符的代码页为 UTF-8
    system("chcp 65001");

    // 输出中文提示信息
    std::cout << "请输入你的名字：";

    // 用于存储用户输入的名字
    std::string name;

    // 从标准输入读取一行文本
    std::getline(std::cin, name);

    // 输出问候语
    std::cout << "你好，" << name << "！" << std::endl;

    return 0;
}