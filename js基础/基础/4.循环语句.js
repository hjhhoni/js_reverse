var arr = [1, 2, 3, 4, 5]
/* for (var i = 0; i < arr.length; i++) {
    console.log(arr[i]);
} */

// 简化版本的for循环, item是数组元素的下标
/* for (item in arr) {
    console.log(arr[item]);
} */

// while循环
/* var i = 0;
while (i < arr.length) {
    console.log(arr[i]);
    i++;
} */


// 使用forEach方法遍历数组中的每个元素
arr.forEach(function (item) {
    console.log(item);
})
