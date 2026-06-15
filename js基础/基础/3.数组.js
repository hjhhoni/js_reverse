/* 
    在js中创建数组有两种方式:
        1.通过对象声明的方式创建数组
        2.通过字面量创建数组
*/

var arr = new Array(1, 2, 3);  // 通过对象声明的方式创建数组
console.log(arr);

var arr = ['1', '2', '3'];  // 通过字面量创建数组
console.log(arr);

// 元素下标取值
console.log(arr[0]);
console.log(arr[1]);
console.log(arr[2], typeof arr[2]);

// 获取数组长度
console.log('数组长度:', arr.length);

// 修改数组中的指定元素
arr[0] = 0;
console.log(arr);

// 在数组末尾添加元素
arr.push(4);
console.log(arr);

// 弹出数组末尾的元素
new_attr = arr.pop();
console.log('pop出的元素:', new_attr);
console.log(arr);

// 在数组开头添加元素
arr.unshift(-1);
console.log(arr);

// 弹出数组开头的元素
new_attr = arr.shift();
console.log('shift出的元素:', new_attr);
console.log(arr);

// 弹出指定元素
new_attr = arr.splice(1, 1);  
console.log('splice出的元素:', new_attr);
console.log(arr);


// 数组的截取与修改
// start: 操作位置、 deleteCount: 删除的个数、 items: 添加的元素(基于删除的元素的位置添加)
arr.splice(0, 1, 'a', 'b', 'c');
console.log(arr);