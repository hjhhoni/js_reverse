function step_1() {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            console.log('step_1 执行完成...');
            resolve('step_1 执行完成的结果...');
        }, 1000);
    })
}


function step_2() {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            console.log('step_2 执行完成...');
            resolve('step_2 执行完成的结果...');
        }, 1000);
    })
}

function step_3() {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            console.log('step_3 执行完成...');
            resolve('step_3 执行完成的结果...');
        }, 1000);
    })
}

// res 是 step_3 执行完成的结果... 这个字符串
step_1().then(step_2).then(step_3).then(function (res) {
    console.log(res);
})
