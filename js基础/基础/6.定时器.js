/* 
什么是js中的定时器
    在js环境中内置了一个定时器对象, 功能是在用户指定的时间内'重复'运行指定的代码块
*/


// 定时器的使用: setTimeout() [这个函数会执行用户指定的时间段内的代码块, 但是只会执行一次]
function run_test() {
    console.log('定时器测试...');
}


// var set_timeout = setTimeout(run_test, 3000); // 3秒
// clearTimeout(set_timeout);  // 可以取消定时器的执行


// 循环执行的定时器: setInterval()
// var set_interval = setInterval(run_test, 3000);
// clearInterval(set_interval);  // 可以取消定时器的执行


// 将node内置的定时器函数置空完成关闭定时器
setInterval = function () {}
setInterval(run_test, 3000);
