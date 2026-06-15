var a,b,c,d,e,f,g;
// // 变量
// var a=1,b=2,c=3; // var变量只在函数内有效，函数外为全局变量 
// let d=4,e=5,f=6;// let变量只在块级作用域内有效，直接用var即可
// const g=7,h=8,i=9;// const定义常量，定义后不可变
// console.log(a,b,c,d,e,f,g,h,i);  输出


// a = 3.14; // 浮点型
// b = true; // 布尔类型 true flase
// c = undefined; // 未定义
// d = null; // null类型
// console.log(a,b,c,d);

// 对象
// var car = {
//     name:'玛莎拉蒂',
//     price: 1888888,
//     owner: 'hjh'
// };
// console.log(car.name);
// console.log(car['name']);

// 打印对象类型
// a = 18;
// console.log(typeof(a)); // number

// 重复输出
// console.log('-'.repeat(20)); // --------------------

// 变量和字符一起输出
// a = 'HJH';
// console.log(`${a}是个大帅哥`); // HJH是个大帅哥

// 函数
function func(a,b){
    console.log(1);
    console.info(1); // 下面三个效果都是一样打印1，不同的是在浏览器会携带样式
    // console.error(2);
    console.warn(1);
    console.log(a+b); // 输出3
    console.log('arguments',arguments); // arguments是一个对象
    return 1,2,3;  // 只会返回最后一个值
};
// func(1,2); 
// (0,func)(1,2);  // 两种调用效果是一样的
// func.apply(null,[1,2]); // 这样子也行
// func(1,2,3,4,5,6); // 从3开始3-6都会被变量arguments接收

// 自执行函数
// (function tt() {
//     console.log('自执行函数1')
// })()
// !function tt() {
//     console.log('自执行函数2')
// }()
// // 自执行函数可用于闭包
// var ttt;
// !function tq() {
//     function _func(){
//         console.log('闭包函数') 
//     };
//     ttt = _func;
// }()
// ttt();

