require('./xhsenv1')
require("./2026xhs")

aa = '/api/sec/v1/scripting{"callFrom":"web","callback":"seccallback"}'
bb = "3d08093c65de13679b96a87493e1ed41"
cc = "30075585641997ca77efa138e473890d"
console.log("mnsv2-->" + window.mnsv2)

console_log("mnsv2-->", window.mnsv2(aa, bb, cc))


for (var l = [], _ = "ZmserbBoHQtNP+wOcza/LpngG8yJq42KWYj0DSfdikx3VT16IlUAFM97hECvuRX5", m = 0, w = _.length; m < w; ++m)
    l[m] = _[m];
var crc32 = function crc32(e) {
    for (var a, c = [], l = 0; l < 256; l++) {
        a = l;
        for (var _ = 0; _ < 8; _++)
            a = 1 & a ? 0xedb88320 ^ a >>> 1 : a >>> 1;
        c[l] = a
    }
    for (var m = -1, w = 0; w < e.length; w++)
        m = m >>> 8 ^ c[255 & (m ^ e.charCodeAt(w))];
    return (-1 ^ m) >>> 0
};

function tripletToBase64(e) {
    return l[e >> 18 & 63] + l[e >> 12 & 63] + l[e >> 6 & 63] + l[63 & e]
}

function encodeChunk(e, a, c) {
    for (var l, _ = [], m = a; m < c; m += 3)
        l = (e[m] << 16 & 0xff0000) + (e[m + 1] << 8 & 65280) + (255 & e[m + 2]),
            _.push(tripletToBase64(l));
    return _.join("")
}

function encodeUtf8(e) {
    for (var a = encodeURIComponent(e), c = [], l = 0; l < a.length; l++) {
        var _ = a.charAt(l);
        if ("%" === _) {
            var m = parseInt(a.charAt(l + 1) + a.charAt(l + 2), 16);
            c.push(m),
                l += 2
        } else
            c.push(_.charCodeAt(0))
    }
    return c
}

function b64Encode(e) {
    for (var a, c = e.length, _ = c % 3, m = [], w = 16383, E = 0, R = c - _; E < R; E += w)
        m.push(encodeChunk(e, E, E + w > R ? R : E + w));
    return 1 === _ ? (a = e[c - 1],
        m.push(l[a >> 2] + l[a << 4 & 63] + "==")) : 2 === _ && (a = (e[c - 2] << 8) + e[c - 1],
        m.push(l[a >> 10] + l[a >> 4 & 63] + l[a << 2 & 63] + "=")),
        m.join("")
}

function get_sign(aa, bb, cc) {
    w = window.mnsv2(aa, bb, cc)
    R = {
        x0: "4.3.4",
        x1: "xhs-pc-web",
        x2: "Windows",
        x3: w,
        x4: "object"
    };
    // return console.log(b64Encode(encodeUtf8(JSON.stringify(R))));
    return "XYS_" + b64Encode(encodeUtf8(JSON.stringify(R)))
}

// "XYS_" + (0,G.xE)((0,G.lz)(JSON.stringify(R)))


