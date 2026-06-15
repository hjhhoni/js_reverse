/* 通过字面量的方式创建对象 */
/* var stu_info = {
    'name': 'admin',
    'age': 18,
    print_info: function () {
        console.log('this ->', this);
        // this: 类似python中的self, 指向当前对象实例
        console.log(`姓名: ${this.name}, 年龄: ${this.age}`)
    }
}

console.log(stu_info);
console.log(stu_info.name);
console.log(stu_info.age);
stu_info.print_info(); */


/* 通过函数的方式创建对象 */
/* function create_student(name, age) {
    this.name = name;
    this.age = age;
    this.print_info = function () {
        console.log(`姓名: ${this.name}, 年龄: ${this.age}岁`)
    }
}

var stu_info_1 = new create_student('柏汌', 18);
var stu_info_2 = new create_student('安娜', 20);
console.log(stu_info_1.name);
stu_info_1.print_info();
stu_info_2.print_info(); */


/* 通过Object创建对象 */
/* var stu_info_3 = new Object();
stu_info_3.name = '南枫';
stu_info_3.age = 22;
stu_info_3.print_info = function () {
    console.log(`姓名: ${this.name}, 年龄: ${this.age}岁`)
}
console.log(stu_info_3.name);
stu_info_3.print_info(); */


/* 使用类创建对象 */
class Student {
    // 使用构造方法创建属性, 类似python中的__init__方法
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    print_info() {
        console.log(`姓名: ${this.name}, 年龄: ${this.age}岁`)
    }
}

var stu_info_4 = new Student('夏洛', 22);
stu_info_4.print_info();
