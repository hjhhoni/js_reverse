const https = require('https');
const vm = require('vm');

const LIB_URLS = [
  'https://raw.d.cn/membersystem/2016/static/js/BigInt.js',
  'https://raw.d.cn/membersystem/2016/static/js/Barrett.js',
  'https://raw.d.cn/membersystem/2016/static/js/RSA.js',
];

const PUBLIC_EXPONENT = '10001';
const MODULUS = 'be44aec4d73408f6b60e6fe9e3dc55d0e1dc53a1e171e071b547e2e8e0b7da01c56e8c9bcf0521568eb111adccef4e40124b76e33e7ad75607c227af8f8e0b759c30ef283be8ab17a84b19a051df5f94c07e6e7be5f77866376322aac944f45f3ab532bb6efc70c1efa524d821d16cafb580c5a901f0defddea3692a4e68e6cd';

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`GET ${url} failed: ${res.statusCode}`));
        res.resume();
        return;
      }

      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function loadLegacyRsaContext() {
  const context = {
    console,
    Math,
    Array,
    String,
    Number,
    parseInt,
    parseFloat,
    isNaN,
    Date,
  };
  vm.createContext(context);

  for (const url of LIB_URLS) {
    const source = await fetchText(url);
    vm.runInContext(source, context, { filename: url });
  }

  return context;
}

async function encryptPassword(password) {
  const context = await loadLegacyRsaContext();
  context.setMaxDigits(130);
  const key = new context.RSAKeyPair(PUBLIC_EXPONENT, '', MODULUS);
  return context.encryptedString(key, password);
}

async function main() {
  const password = process.argv[2] || '123456';
  const encrypted = await encryptPassword(password);
  console.log(JSON.stringify({ password, encrypted }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
