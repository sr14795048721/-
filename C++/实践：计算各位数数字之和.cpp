#include <iostream>

int main() {
    int number, sum = 0, remainder;

    // ��ȡ�û����������
    std::cout << "������һ������: ";
    std::cin >> number;

    // ȷ�����Ǵ����������
    if (number < 0) {
        number = -number;
    }

    // �����λ��֮��
    while (number > 0) {
        remainder = number % 10; // ��ȡ��λ��
        sum += remainder;        // �ۼӵ��ܺ���
        number /= 10;            // �Ƴ���λ��
    }

    // ������
    std::cout << "�������ĸ�λ��֮����: " << sum << std::endl;

    return 0;
}
