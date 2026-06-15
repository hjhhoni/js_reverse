var str_json = '{"name":"张三","age":18}';
console.log(str_json, typeof str_json);

// 字符串转对象
var json_obj = JSON.parse(str_json);
console.log(json_obj, typeof json_obj);  // 可以完成我们的数据加密定位
console.log(json_obj.name);


// 对象转字符串
var str_json = JSON.stringify(json_obj);
console.log(str_json, typeof str_json);
