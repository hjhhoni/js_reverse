/* 
什么是promise:
    promise是一种异步任务的解决方案, 可以避免回调地狱的问题.
*/


/* 
一个promise是一个异步任务
    任务内部维护了三种状态:
        - pending: 等待状态
        - fulfilled: 成功状态
        - rejected: 失败状态

    resolve: promise对象成功时调用的函数, 可以更改promise对象的状态为fulfilled, 并返回任务的结果
    reject: promise对象失败时调用的函数, 可以更改promise对象的状态为rejected, 并返回任务的失败原因
*/
/* function simple_promise() {
    var promise = new Promise(function (resolve, reject) {
        // 用于模拟执行的任务的状态(成功/失败)
        var success = true;
        if (success) {
            resolve('成功...');
        } else {
            reject('失败...');
        }
    });
    console.log(promise);
}

simple_promise(); */


/* function task_promise() {
    // 创建了一个promise对象, 并将你需要执行的耗时任务封装到promise对象中
    var promise = new Promise(function (resolve, reject) {
        task_result = '这是一个耗时任务的结果';
        resolve(task_result);
    });

    // 将创建的promise对象返回出去
    return promise;
}

var pro = task_promise(); */
// console.log(pro);

// 获取promise执行完成之后的最终结果
/* pro.then(function (res) {
    console.log(res);
}); */

// then方法内部写的匿名函数或者箭头函数其实都是回调函数(函数引用), then方法得到这些函数引用之后可以在then自身的方法内部调用这些引用
// pro.then(res => console.log(res));


/* 带延迟的promise案例 */
/* function delay_promise() {
    var promise = new Promise(function (resolve, reject) {
        console.log('promise 开始执行...');

        // 模拟延迟
        setTimeout(function() {
            resolve('这是promise任务的最终结果, 延迟两秒后返回...')
        }, 2000);
    });

    return promise;
}


console.log('调用delay_promise之前...');
delay_promise().then(function (result) {
    console.log(result);
})
console.log('调用delay_promise之后...'); */


/* 执行失败的promise案例 */
function fail_promise() {
    var promise = new Promise(function (resolve, reject) {
        console.log('promise 开始执行...');
        reject('这是promise任务的失败结果...')
    });
    return promise;
}

// then用于获取任务成功的结果, catch用于获取任务失败的结果
fail_promise().catch(err => console.log(err));
