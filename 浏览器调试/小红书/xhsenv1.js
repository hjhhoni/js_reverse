(()=>{
    const origin_log = console.log;;
    console_log = function(){
        return origin_log(...arguments)
    }
})();;;

const globalRef = globalThis;
globalRef.window = globalRef;
globalRef.self = globalRef;
globalRef.top = globalRef;
globalRef.parent = globalRef;
globalRef.globalThis = globalRef;
globalRef.slef = globalRef;

function watch(obj, name) {
    return new Proxy(obj, {
        get: function (target, property, receiver) {
            try {
                if (typeof target[property] === "function") {
                    console.log("对象 => " + name + ",读取属性:" + property + ",值为:" + 'function' + ",类型为:" + (typeof target[property]))
                } else {
                    console.log("对象 => " + name + ",读取属性:" + property + ",值为:" + target[property] + ",类型为:" + (typeof target[property]))
                }
            } catch (e) {
            }
            return target[property]
        },
        set: (target, property, newValue, receiver) => {
            try {
                console.log("对象 => " + name + ",设置属性:" + property + ",值为:" + newValue + ",类型为:" + (typeof newValue))
            } catch (e) {
            }
            return Reflect.set(target, property, newValue, receiver)
        }
    })
}

function makeFunction(name) {
    // 动态创建一个函数
    var func = new Function(`
        return function ${name}() {
            console_log('函数传参.${name}',arguments)
        }
    `)();
    safeFunctions(func)
    func.prototype = watch(func.prototype, `方法原型:${name}.prototype`)
    func = watch(func, `方法本身:${name}`)
    return func;
};

(() => {
    Function.prototype.$call = Function.prototype.call
    const $toString = Function.toString;
    const myFunction_toString_symbol = Symbol('('.concat('', ')_'));
    const myToString = function toString() {
        return typeof this == 'function' && this[myFunction_toString_symbol] || $toString.$call(this);
    };

    function set_native(func, key, value) {
        Object.defineProperty(func, key, {
            "enumerable": false,
            "configurable": true,
            "writable": true,
            "value": value
        })
    }

    delete Function.prototype['toString'];

    set_native(Function.prototype, "toString", myToString);

    set_native(Function.prototype.toString, myFunction_toString_symbol, "function toString() { [native code] }");

    safeFunctions = (func) => {
        set_native(func, myFunction_toString_symbol, `function ${func.name}() { [native code] }`);
    };
})();;;

try {
    XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;
} catch (e) {
    XMLHttpRequest = function XMLHttpRequest() {};
}

class DocumentAll {
    constructor(document) {
        this.document = document;
        this._elements = [];
        this.length = 0;
        this._updateElements();

        // 设置为类数组对象
        this._setupArrayLike();

        // 绑定方法的 this 上下文
        this.item = this.item.bind(this);
        this.namedItem = this.namedItem.bind(this);
        this.tags = this.tags.bind(this);
    }

    /**
     * 更新元素列表
     */
    _updateElements() {
        // 获取文档中的所有元素，按照 DOM 树顺序
        this._elements = this._getAllElementsInOrder();
        this.length = this._elements.length;

        // 清除旧的数字索引属性
        this._clearNumericProperties();

        // 设置新的数字索引属性
        this._setNumericProperties();
    }

    /**
     * 按 DOM 树顺序获取所有元素
     */
    _getAllElementsInOrder() {
        const elements = [];

        // 从根元素开始遍历
        const traverse = (node) => {
            if (node.nodeType === 1) { // Element node
                elements.push(node);
            }

            // 遍历子节点
            for (let i = 0; i < node.childNodes.length; i++) {
                traverse(node.childNodes[i]);
            }
        };

        // 从 documentElement 开始（html 元素）
        if (this.document.documentElement) {
            traverse(this.document.documentElement);
        }

        return elements;
    }

    /**
     * 清除数字属性
     */
    _clearNumericProperties() {
        for (let i = 0; i < this.length; i++) {
            if (this.hasOwnProperty(i)) {
                delete this[i];
            }
        }
    }

    /**
     * 设置数字索引属性
     */
    _setNumericProperties() {
        for (let i = 0; i < this._elements.length; i++) {
            this[i] = this._elements[i];
        }
    }

    /**
     * 设置类数组对象特性
     */
    _setupArrayLike() {
        // 确保 length 属性可配置
        Object.defineProperty(this, 'length', {
            get: () => this._elements.length,
            enumerable: false,
            configurable: true
        });
    }

    /**
     * item 方法 - 通过索引或名称获取元素
     */
    item(indexOrName) {
        if (typeof indexOrName === 'number') {
            return this._elements[indexOrName] || null;
        }

        if (typeof indexOrName === 'string') {
            return this.namedItem(indexOrName);
        }

        return null;
    }

    /**
     * namedItem 方法 - 通过名称或 ID 获取元素
     */
    namedItem(name) {
        if (!name) return null;

        // 首先尝试通过 ID 查找
        const byId = this.document.getElementById(name);
        if (byId) return byId;

        // 然后尝试通过 name 属性查找
        const byName = this.document.getElementsByName(name);
        if (byName.length > 0) return byName[0];

        // 最后尝试通过其他属性查找
        for (let element of this._elements) {
            if (element.getAttribute &&
                (element.getAttribute('name') === name ||
                 element.getAttribute('id') === name)) {
                return element;
            }
        }

        return null;
    }

    /**
     * tags 方法 - 通过标签名获取元素集合
     */
    tags(tagName) {
        if (!tagName) return [];

        const result = [];
        const upperTagName = tagName.toUpperCase();

        for (let element of this._elements) {
            if (element.tagName && element.tagName.toUpperCase() === upperTagName) {
                result.push(element);
            }
        }

        // 返回类似 HTMLCollection 的对象
        return this._createHTMLCollection(result);
    }

    /**
     * 创建类似 HTMLCollection 的对象
     */
    _createHTMLCollection(elements) {
        const collection = {
            length: elements.length,
            item: function(index) {
                return elements[index] || null;
            },
            namedItem: function(name) {
                for (let element of elements) {
                    if (element.id === name || element.getAttribute('name') === name) {
                        return element;
                    }
                }
                return null;
            }
        };

        // 添加数字索引
        for (let i = 0; i < elements.length; i++) {
            collection[i] = elements[i];
        }

        return collection;
    }

    /**
     * 支持 for...of 遍历
     */
    *[Symbol.iterator]() {
        for (let i = 0; i < this.length; i++) {
            yield this._elements[i];
        }
    }

    /**
     * 支持 forEach 方法
     */
    forEach(callback, thisArg) {
        for (let i = 0; i < this.length; i++) {
            callback.call(thisArg, this._elements[i], i, this);
        }
    }

    /**
     * 支持函数调用形式访问 - document.all(index) 或 document.all(name)
     */
    valueOf() {
        const self = this;
        const callable = function(indexOrName) {
            return self.item(indexOrName);
        };

        // 复制所有属性到函数对象
        Object.setPrototypeOf(callable, Object.getPrototypeOf(self));
        Object.assign(callable, self);

        return callable;
    }
}

window = globalRef
// window = watch(window, 'window')
globalThis = slef = top = parent = window
null_fun = function (){}

window.performance = globalRef.performance || {
    now: () => Date.now(),
    timeOrigin: Date.now(),
    timing: {},
    navigation: {}
}

window.atob = globalRef.atob || function(str) {
    return Buffer.from(String(str), 'base64').toString('binary')
}
window.btoa = globalRef.btoa || function(str) {
    return Buffer.from(String(str), 'binary').toString('base64')
}
window.TextEncoder = globalRef.TextEncoder || require('util').TextEncoder
window.TextDecoder = globalRef.TextDecoder || require('util').TextDecoder
window.crypto = globalRef.crypto || require('crypto').webcrypto
window.Uint8Array = globalRef.Uint8Array || Uint8Array
window.ArrayBuffer = globalRef.ArrayBuffer || ArrayBuffer
window.Int8Array = globalRef.Int8Array || Int8Array
window.Uint8ClampedArray = globalRef.Uint8ClampedArray || Uint8ClampedArray
window.URL = globalRef.URL || require('url').URL
window.encodeURIComponent = globalRef.encodeURIComponent || encodeURIComponent
window.decodeURIComponent = globalRef.decodeURIComponent || decodeURIComponent
window.parseInt = globalRef.parseInt || parseInt
window.unescape = globalRef.unescape || unescape
window.escape = globalRef.escape || escape
window.Buffer = globalRef.Buffer || Buffer
window.Promise = globalRef.Promise || Promise
window.Date = globalRef.Date || Date
window.Math = globalRef.Math || Math
window.RegExp = globalRef.RegExp || RegExp
window.Object = globalRef.Object || Object
window.Array = globalRef.Array || Array
window.JSON = globalRef.JSON || JSON
window.String = globalRef.String || String
window.Number = globalRef.Number || Number
window.Boolean = globalRef.Boolean || Boolean
window.Symbol = globalRef.Symbol || Symbol
window.TypeError = globalRef.TypeError || TypeError
window.localStorage = {
    getItem(key) { return this[key] ?? null },
    setItem(key, value) { this[key] = String(value) },
    removeItem(key) { delete this[key] },
    clear() { for (const key of Object.keys(this)) if (typeof this[key] !== 'function') delete this[key] }
}
window.sessionStorage = {
    getItem(key) { return this[key] ?? null },
    setItem(key, value) { this[key] = String(value) },
    removeItem(key) { delete this[key] },
    clear() { for (const key of Object.keys(this)) if (typeof this[key] !== 'function') delete this[key] }
}

window.addEventListener = makeFunction("addEventListener")
// window.addEventListener = function addEventListener(){}
window.MouseEvent = makeFunction("MouseEvent")
// window.MouseEvent = function MouseEvent(){}


function XMLHttpRequest() {
}
window.XMLHttpRequest =watch(XMLHttpRequest, 'XMLHttpRequest')
XMLHttpRequest.prototype.open = null_fun
XMLHttpRequest.prototype.send = null_fun
XMLHttpRequest.prototype.setRequestHeader = null_fun
XMLHttpRequest.prototype.addEventListener = null_fun
XMLHttpRequest.prototype.DONE = 4
XMLHttpRequest.prototype.HEADERS_RECEIVED = 2


requestIdleCallback = null_fun
setTimeout = null_fun
clearTimeout = null_fun
setInterval = null_fun
InstallTrigger  = null_fun
requestAnimationFrame = null_fun

Navigator = makeFunction("Navigator")
// Navigator = function Navigator(){}
Navigator.prototype.toString = function () {
    return '[object Navigator]'
}
Navigator.prototype.webdriver = false
Navigator.prototype.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
Navigator.prototype.appName = 'Netscape'
navigator = new Navigator()
window.navigator = navigator

function EventTarget() {}
EventTarget.prototype.addEventListener = function(type, listener) {
if (!this._eventListeners) this._eventListeners = {};
if (!this._eventListeners[type]) this._eventListeners[type] = [];
this._eventListeners[type].push(listener);
};
EventTarget.prototype.dispatchEvent = function(event) {
if (!this._eventListeners || !this._eventListeners[event.type]) return true;
this._eventListeners[event.type].forEach(listener => {
  if (typeof listener === 'function') listener.call(this, event);
});
return !event.defaultPrevented;
};
EventTarget.prototype.removeEventListener = function(type, listener) {
if (!this._eventListeners || !this._eventListeners[type]) return;
const index = this._eventListeners[type].indexOf(listener);
if (index > -1) this._eventListeners[type].splice(index, 1);
};

// Node
function Node() {}
Node.prototype = Object.create(EventTarget.prototype);
Node.prototype.appendChild = function(child) {
if (!this.childNodes) this.childNodes = [];
this.childNodes.push(child);
child.parentNode = this;
return child;
};
Node.prototype.removeChild = function(child) {
if (!this.childNodes) return null;
const index = this.childNodes.indexOf(child);
if (index > -1) {
  this.childNodes.splice(index, 1);
  child.parentNode = null;
}
return child;
};

// Element
function Element() {}
Element.prototype = Object.create(Node.prototype);
Element.prototype.getAttribute = function(name) {
if (!this.attributes) this.attributes = {};
return this.attributes[name] || null;
};
Element.prototype.setAttribute = function(name, value) {
if (!this.attributes) this.attributes = {};
this.attributes[name] = String(value);
};
Element.prototype.removeAttribute = function(name) {
if (!this.attributes) return;
delete this.attributes[name];
};
Element.prototype.hasAttribute = function(name) {
if (!this.attributes) return false;
return name in this.attributes;
};
Element.prototype.querySelector = function(selector) { return null; };
Element.prototype.querySelectorAll = function(selector) { return []; };
Element.prototype.getElementsByTagName = function(tagName) {
    console.log(tagName)
    return []
};
Element.prototype.getElementsByClassName = function(className) { return []; };
Element.prototype.getBoundingClientRect = function() {
return { x: 0, y: 0, width: 0, height: 0, top: 0, right: 0, bottom: 0, left: 0 };
};
Element.prototype.scrollIntoView = function() {};
Element.prototype.scrollIntoViewIfNeeded = function() {};
Element.prototype.remove = function() {
if (this.parentNode) this.parentNode.removeChild(this);
};

// 定义属性访问器
Object.defineProperties(Element.prototype, {
id: {
  get: function() { return this.getAttribute('id') || ''; },
  set: function(value) { this.setAttribute('id', value); },
  enumerable: true
},
className: {
  get: function() { return this.getAttribute('class') || ''; },
  set: function(value) { this.setAttribute('class', value); },
  enumerable: true
},
innerHTML: {
  get: function() { return this._innerHTML || ''; },
  set: function(value) { this._innerHTML = value; },
  enumerable: true
},
textContent: {
  get: function() { return this._textContent || ''; },
  set: function(value) { this._textContent = value; },
  enumerable: true
}
});

// HTMLElement
function HTMLElement() {}
HTMLElement.prototype = Object.create(Element.prototype);
Object.defineProperties(HTMLElement.prototype, {
style: {
  get: function() {
    if (!this._style) this._style = {};
    return this._style;
  },
  enumerable: true
},
offsetWidth: { get: function() { return 0; }, enumerable: true },
offsetHeight: { get: function() { return 0; }, enumerable: true },
clientWidth: { get: function() { return 0; }, enumerable: true },
clientHeight: { get: function() { return 0; }, enumerable: true }
});
HTMLElement.prototype.click = function() {};
HTMLElement.prototype.focus = function() {};
HTMLElement.prototype.blur = function() {};

// Document
function Document() {}
Document.prototype = Object.create(Node.prototype);
Document.prototype.createElement = function(tagName) {
const element = Object.create(HTMLElement.prototype);
element.tagName = tagName.toUpperCase();
element.nodeName = tagName.toUpperCase();
element.nodeType = 1;
element.childNodes = [];
element.attributes = {};

// Canvas 特殊处理
if (tagName.toLowerCase() === 'canvas') {
  element.width = 300;
  element.height = 150;
  element.getContext = function(type) {
    if (type === '2d') {
      return {
        canvas: this,
        fillStyle: '#000',
        strokeStyle: '#000',
        fillRect: function() {},
        strokeRect: function() {},
        clearRect: function() {},
        fillText: function() {},
        measureText: function(text) { return { width: text.length * 7 }; },
        getImageData: function(x, y, w, h) {
          return { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) };
        }
      };
    } else if (type === 'webgl' || type === 'experimental-webgl') {
      return {
        canvas: this,
        createBuffer: function() { return {}; },
        createShader: function() { return {}; },
        createProgram: function() { return {}; },
        getParameter: function() { return 'WebGL'; },
        getExtension: function() { return null; }
      };
    }
    return null;
  };
  element.toDataURL = function() {
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
  };
}

return element;
};
Document.prototype.createTextNode = function(data) {
const textNode = Object.create(Node.prototype);
textNode.nodeType = 3;
textNode.nodeName = '#text';
textNode.nodeValue = data;
textNode.textContent = data;
return textNode;
};
Document.prototype.getElementById = function(id) { return null; };
Document.prototype.getElementsByTagName = function(tagName) { return []; };
Document.prototype.getElementsByClassName = function(className) { return []; };
Document.prototype.querySelector = function(selector) { return null; };
Document.prototype.querySelectorAll = function(selector) { return []; };

// 创建全局对象
document = Object.create(Document.prototype);
window.document = document;

document.nodeType = 9;
document.all = new DocumentAll(document);
document.nodeName = '#document';
document.body = Object.create(HTMLElement.prototype);
document.body.tagName = 'BODY';
document.head = Object.create(HTMLElement.prototype);
document.head.tagName = 'HEAD';
document.documentElement = Object.create(HTMLElement.prototype);
document.documentElement.tagName = 'HTML';
document.childNodes = [document.documentElement];
document.documentElement.childNodes = [document.head, document.body];
document.head.parentNode = document.documentElement;
document.body.parentNode = document.documentElement;
document.documentElement.parentNode = document;
document.defaultView = window;
document.cookie= 'abRequestId=435da070-a8ca-5eb6-9456-004b44d3f6ac'

// document = watch(document, 'document')

Screen = makeFunction("Screen")
// Screen = function Screen(){}
screen = new Screen();
window.screen = screen;
Object.assign(Screen.prototype,  {
  width: 1920,
  height: 1080,
  availWidth: 1920,
  availHeight: 1040,
  colorDepth: 24
})

Location = function Location(){}
location = new Location();
window.location = location;
Object.assign(Location.prototype,{
    "ancestorOrigins": {},
    "href": "https://www.xiaohongshu.com/explore?channel_id=homefeed.fashion_v3",
    "origin": "https://www.xiaohongshu.com",
    "protocol": "https:",
    "host": "www.xiaohongshu.com",
    "hostname": "www.xiaohongshu.com",
    "port": "",
    "pathname": "/explore",
    "search": "?channel_id=homefeed.fashion_v3",
    "hash": ""
})

window.HTMLElement = HTMLElement
window.Element = Element
window.Node = Node
window.EventTarget = EventTarget
window.Document = Document
window.Navigator = Navigator
window.Location = Location
window.Screen = Screen
window.XMLHttpRequest = XMLHttpRequest
window.Image = function Image() {
    return document.createElement('img')
}
window.getComputedStyle = function() {
    return {
        getPropertyValue() { return '' }
    }
}



