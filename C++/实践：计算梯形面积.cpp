#include <iostream>

// ������������ĺ���
double calculateTrapezoidArea(double topBase, double bottomBase, double height) {
    return (topBase + bottomBase) * height / 2.0;
}

int main() {
    double topBase, bottomBase, height;

    // ���û������ȡ���ε��ϵס��µ׺͸�
    std::cout << "���������ε��ϵ׳���: ";
    std::cin >> topBase;
    std::cout << "���������ε��µ׳���: ";
    std::cin >> bottomBase;
    std::cout << "���������εĸ�: ";
    std::cin >> height;

    // �������
    double area = calculateTrapezoidArea(topBase, bottomBase, height);

    // ������
    std::cout << "���ε������: " << area << std::endl;

    return 0;
}
