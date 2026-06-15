var a = 1,b='1',c=3,d=4;
if (a==b){
    console.log('相等');  // 会输出这个，两个等于号只判断值想不想等
}else{
    console.log('不相等');
}
if (a===b){
    console.log('相等');  // 会输出这个，两个等于号只判断值想不想等
}else{
    console.log('不相等'); // 会输出这个，三个等号会判断值和数据类型
}

// 三目运算
var kk = c>d?c:d; // ?前成立取:前值，否则取后值
console.log(kk);
var result  = num_3 > num_4 ? 1 < num_4 ? 3 < num_3 ? 'a': 'b' : 'c' : 'd';
console.log(result);
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