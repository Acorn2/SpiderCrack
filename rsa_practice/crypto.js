var CryptoJS = require("crypto-js");

function encrypt(){
    var e = new Date,
        t = e.getTime();
    var n = "5c44c819" + "appsapi0",
        i = CryptoJS.enc.Utf8.parse(n),
        o = CryptoJS.enc.Utf8.parse(t),
        r = CryptoJS.AES.encrypt(o, i, {
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7
        });
    return r.toString();
}


function encryption(data) {
    let strs=[];
    for(let i in data){
        strs.push(i+'='+data[i]);
    }
    strs.sort();  // 数组排序
    strs=strs.join('&'); // 数组变字符串
    let endData=strs+'&sign='+CryptoJS.MD5(strs+'ADfj3kcadc2349akvm1CPFFCD84f')
    .toString(); // MD5加密
    let key = CryptoJS.enc.Utf8.parse("0880076B18D7EE81"); // 加密秘钥
    let iv = CryptoJS.enc.Utf8.parse("CB3EC842D7C69578");  //  矢量
    let encryptResult = CryptoJS.AES.encrypt(endData,key, {   //  AES加密
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7  // 后台用的是pad.Pkcs5,前台对应为Pkcs7
    });
    return encodeURIComponent(CryptoJS.enc.Base64.stringify(encryptResult.ciphertext));  // Base64加密再 encode;
}