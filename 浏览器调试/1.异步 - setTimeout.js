/* 
console.log('异步任务开始...')

function print_message() {
    console.log('延迟两秒后输出...')
}


setTimeout(print_message, 2000);

console.log('异步任务结束...') 
*/


// 存在多个定时器的情况
/* console.log('异步任务开始...')

function print_message_1() {
    console.log('这是第一个函数任务, 延迟2秒后输出...')
}


function print_message_2() {
    console.log('这是第二个函数任务, 延迟1秒后输出...')
}


setTimeout(print_message_1, 2000);
setTimeout(print_message_2, 1000);
console.log('异步任务结束...'); */


// 回调地狱
console.log('\n=== 回调地狱示例 ===');
setTimeout(() => {
    console.log('第一层');
    setTimeout(() => {
        console.log('第二层');
        setTimeout(() => {
            console.log('第三层');
        }, 1000);
    }, 1000);
}, 1000);