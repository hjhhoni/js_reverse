package 基础语法;
public class TryDemo{
    public static void main(String[] args) {
        // // 一般定义变量不用修饰符，直接赋值即可
        // int a = 10;  // 整数 4字节
        // float h = 3.14f;  // 浮点数 4字节
        // double b = 3.14;  // 浮点数 8字节
        // char d = 'a';  // 字符 2字节
        // String c = "hello world";  // 字符串 16字节
        // long e = 1000000000L;  // 长整数 8字节
        // short f = 100;  // 短整数 2字节
        // final int g = 1000;  // 常量 4字节 相当于js的const
        // System.out.println(a);
        // System.out.println(b);   
        // System.out.println(c);
        // System.out.println(d);
        // System.out.println(e);
        // System.out.println(f);
        // System.out.println(g);
        // System.out.println(h);
        // System.out.println("hello world");

        // 选择语句
        // int a = 10;
        // if (a>5){
        //     System.out.println("a大于5");
        // } else if (a<5) {
        //     System.out.println("a不大于5");
        // } else {
        //     System.out.println("a等于5");
        // }
        // switch(a){
        //     case 10:
        //         System.out.println("a等于10");
        //         break;
        //     case 5:
        //         System.out.println("a等于5");
        //         break;
        //     default:
        //         System.out.println("a不等于10也不等于5");
        //         break;
        // }
        // 三元运算符
        // int b = a>5?a:5;  // 如果a大于5，b等于a，否则b等于5
        // System.out.println(b);

        // 循环语句
        // for (int i=1;i<10;i++){
        //     System.out.println(i);
        // }
        // int a = 0;
        // // while (a<5){
        // //     System.out.println(a);
        // //     a++;
        // // }
        // do {
        //     System.out.println(a);  // 先无条件执行一次，再判断是否继续执行
        //     a++;
        // } while (a<5);
        // 方法
        // System.out.println(add(1,2));
        // 数组
        int[] arr = {1,2,3,4,5};
        // int[] arr2;
        // arr2 = new int[5];
        // int[] arr3 = new int[5];
        // System.out.println(arr[0]);
        // System.out.println(arr2[0]);
        // System.out.println(arr3[0]);
        // 数组的遍历
        // for (int i=0;i<arr.length;i++){
        //     System.out.println(arr[i]);
        // }
        // 二位数组
        // int[][] arr2 = {{1,2,3},{4,5,6}};
        // int[][] arr3 = new int[2][3];
        // for (int i=0;i<arr2.length;i++){
        //     for (int j=0;j<arr2[i].length;j++){
        //         System.out.println(arr2[i][j]);
        //     }
        // }
    } 
    public static int add(int a,int b){  //不可以在方法内部定义方法
        int c = a+b;
        return c;
    }
}