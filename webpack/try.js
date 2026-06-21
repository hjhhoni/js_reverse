window = global;  // 创建全局变量window

!function (e) {
    var t = {};

    function n(r) {
        if (t[r]) {  // 若存在则导出模块
            return t[r].exports;
        }

        var o = t[r] = {
            i: r,
            l: false,
            exports: {}
        };
        // 调用函数，call里是传参
        e[r].call(o.exports, o, o.exports, n);
        o.l = true;
        return o.exports;
    }

    // 在自执行函数内部调用模块加载器
    // n('模块1');

    // 导出加载器
    window.loader = n;
}({
    '模块1': function () {
        console.log('模块1执行了...');
    },
    '模块2': function () {
        console.log('模块2执行了...');
    }
})

// 声明全局变量导出加载器函数
window.loader('模块2');