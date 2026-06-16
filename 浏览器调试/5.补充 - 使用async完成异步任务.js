function run_async_task() {
    return new Promise(function (resolve, reject) {
        var result = '这是promise任务的最终结果';
        resolve(result);
    });
}


/* run_async_task().then(function (res) {
    console.log(res);
}) */

async function run_task() {
    var res = await run_async_task();
    // console.log(res);
    
    return res;
}

// run_task();

// console.log(run_task());
run_task().then(function (res) {
    console.log(res);
})



