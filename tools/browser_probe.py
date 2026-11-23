#!/usr/bin/env python3
"""index.html 의 스크립트를 가짜 DOM 위에서 실행해 보는 개발용 점검 스크립트.
   - 새로 넣은 난이도·한자·예쁘게 말하기 화면이 오류 없이 그려지는지
   - 단계가 규칙대로 오르고 내리는지
   를 실제 앱 코드로 확인한다. (테스트 도구가 없으면 test_app.py 는 이 검사를 건너뛴다)
"""
import json, re, sys

PRELUDE = r"""
var __store = {};
var localStorage = {
  getItem: function (k) { return (k in __store) ? __store[k] : null; },
  setItem: function (k, v) { __store[k] = String(v); },
  removeItem: function (k) { delete __store[k]; }
};
function __mkEl(sel) {
  var el = {
    sel: sel, innerHTML: '', textContent: '', hidden: false, value: '', checked: false,
    dataset: {}, style: {}, children: [], offsetWidth: 10,
    classList: { add: function () {}, remove: function () {}, contains: function () { return false; }, toggle: function () {} },
    addEventListener: function () {}, removeEventListener: function () {},
    appendChild: function (x) { this.children.push(x); return x; }, removeChild: function () {},
    setAttribute: function () {}, focus: function () {}, select: function () {},
    setSelectionRange: function () {}, scrollIntoView: function () {}, remove: function () {},
    click: function () {}, getTotalLength: function () { return 300; },
    querySelector: function () { return __mkEl('sub'); },
    querySelectorAll: function () { return []; },
    closest: function () { return null; }
  };
  return el;
}
var __els = {};
var document = {
  getElementById: function (id) { var k = '#' + id; if (!__els[k]) __els[k] = __mkEl(k); return __els[k]; },
  querySelector: function (s) { if (!__els[s]) __els[s] = __mkEl(s); return __els[s]; },
  querySelectorAll: function () { return []; },
  createElement: function (t) { return __mkEl(t); },
  addEventListener: function () {}, removeEventListener: function () {},
  head: __mkEl('head'), body: __mkEl('body'), execCommand: function () { return false; },
  documentElement: { style: {} }, hidden: false
};
var window = {
  addEventListener: function () {}, removeEventListener: function () {},
  location: { search: '', protocol: 'https:', pathname: '/', href: 'https://x/' },
  history: { replaceState: function () {} },
  navigator: { onLine: true },
  localStorage: localStorage,
  requestAnimationFrame: function (fn) { try { fn(); } catch (e) {} return 1; },
  setTimeout: function (fn, ms) { return 0; },
  clearTimeout: function () {}, setInterval: function () { return 0; }, clearInterval: function () {},
  confirm: function () { return true; }, alert: function () {},
  SpeechSynthesisUtterance: undefined, speechSynthesis: undefined,
  matchMedia: function () { return { matches: false, addListener: function () {} }; },
  scrollTo: function () {}, getComputedStyle: function () { return {}; }
};
var location = window.location, navigator = window.navigator, history = window.history;
function setTimeout(fn, ms) { return 0; }
function clearTimeout() {}
function setInterval() { return 0; }
function clearInterval() {}
function requestAnimationFrame(fn) { try { fn(); } catch (e) {} return 1; }
window.window = window; window.document = document;
"""


def run(html_path='index.html'):
    import quickjs
    html = open(html_path, encoding='utf-8').read()
    src = re.search(r'<script>(.*)</script>', html, re.S).group(1)
    ctx = quickjs.Context()
    ctx.eval(PRELUDE)
    ctx.eval('var __errs = [];')
    ctx.eval(src + '\n;window.__errs = window.__errs || [];')
    return ctx


if __name__ == '__main__':
    ctx = run()
    print('loaded')
