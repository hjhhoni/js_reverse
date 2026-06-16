var str_json = '{"name":"张三","age":18}';  
console.log(str_json, typeof str_json);  // 这个时候还是字符串string

// 字符串转对象
var json_obj = JSON.parse(str_json);
console.log(json_obj, typeof json_obj);  // 这个JSON.parse()可以把字符串转换为对象，很多爬虫
console.log(json_obj.name);


// 对象转字符串
var str_json = JSON.stringify(json_obj);
console.log(str_json, typeof str_json);
