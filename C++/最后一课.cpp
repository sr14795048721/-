#include <iostream>
#include <string>
using namespace std;

void print(string str)//无返回值 函数名
{
	cout << str;
}
int main()//主函数只能有一个
{
	print("Hello");//调用自定义函数
	return 0;
}