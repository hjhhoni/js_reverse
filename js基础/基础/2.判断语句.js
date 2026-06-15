// var num_1 = '1';
// var num_2 = 1;

// // 只是判断值是否相等, 不考虑类型
// if (num_1 == num_2) {
//     console.log('相等...');
// } else {
//     console.log('不相等...');
// }

// // 判断值是否相等, 且考虑类型
// if (num_1 === num_2) {
//     console.log('相等...');
// } else {
//     console.log('不相等...');
// }

// console.log('-'.repeat(30));

// // 三目运算
// var num_3 = 1;
// var num_4 = 2;

// // 三目运算符: 条件 ? 表达式1 : 表达式2 (如果条件为true, 则执行表达式1, 否则执行表达式2)
// var max_num = num_3 > num_4 ? num_3 : num_4;
// console.log(max_num);

// var result  = num_3 > num_4 ? 1 < num_4 ? 3 < num_3 ? 'a': 'b' : 'c' : 'd';
// console.log(result);
/*
    开始
        ├─ num_3 < num_4 ?
        │  ├─ false → 'd'
        │  └─ true → 1 < num_4 ?
        │     ├─ false → 'c'
        │     └─ true → 3 < num_3 ?
        │        ├─ true → 'a'
        │        └─ false → 'b'


    var result;
    if (num_3 < num_4) {
        if (1 < num_4) {
            if (3 < num_3) {
                result = 'a';
            } else {
                result = 'b';
            }
        } else {
            result = 'c';
        }
    } else {
        result = 'd';
    }

    console.log(result);
*/

console.log('-'.repeat(30));

// 逻辑运算符: 在python中的逻辑运算符的表现形式(and or not), 在js中的表现形式为(&& || !)
var x = 1;
var y = 2;

var result = x > y && x < y;
console.log(result);

var result = x > y || x < y;
console.log(result);

var result = !(x > y);
console.log(result);

console.log('-'.repeat(30));


/* 控制流 */
var day = new Date().getDay();
console.log(day);

switch (day) {
    case 0:
        console.log('星期日');
        break;
    case 1:
        console.log('星期一');
        break;
    case 2:
        console.log('星期二');
        break;
    case 3:
        console.log('星期三');
        break;
    case 4:
        console.log('星期四');
        break;
    case 5:
        console.log('星期五');
        break;
    case 6:
        console.log('星期六');
        break;
    default:
        console.log('未知日期');
        break;
};
