// package 面向对象;
public class Learn {
    public static void main(String[] args) {
        Person p1 = new Person("张三",18,"男");
        p1.say();
        // p1.name = "李四";  private只能访问不可修改
        // p1.age = 20;
        // p1.sex = "女";
        p1.say();
    }
}
class Person{
    private String name;
    private int age;
    private String sex;
    // 构造方法
    public Person(String name,int age,String sex){
        this.name = name;
        this.age = age;
        this.sex = sex;
    }
    // 方法
    public void say(){
        System.out.println("我是"+name+"，我今年"+age+"岁，我是"+sex);
    }
}
// 对象：具体的人
