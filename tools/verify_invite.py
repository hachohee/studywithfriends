#!/usr/bin/env python3
"""초대 링크(?join=1&slot=N&room=…)가 '홈 화면에 추가' 뒤에도 살아 있는지 실행해서 확인한다.

  1) 초대 링크로 열면 주소의 초대 정보가 그대로 남는다 (지우지 않는다)
  2) 참여를 마쳐도 주소에 초대 정보가 남는다 (그 화면에서 홈 화면에 추가해도 같은 자리)
  3) 파라미터 없이 열려도(=홈 화면 아이콘) 이 폰에 기억된 초대 자리로 참여 화면이 뜬다
  4) 초대 정보가 하나도 없으면 막다른 화면이 아니라 '먼저 둘러보기'가 있는 안내 화면
  5) manifest.webmanifest 에 고정 start_url 이 없다
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

from browser_probe import PRELUDE  # noqa: E402

PASS, FAIL = [], []


def check(cond, msg):
    (PASS if cond else FAIL).append(msg)
    print(('✅ ' if cond else '❌ ') + msg)
    return bool(cond)


def load(search='', store=None):
    import quickjs
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    src = re.search(r'<script>(.*)</script>', html, re.S).group(1)
    pre = PRELUDE.replace("location: { search: '', protocol: 'https:'",
                          "location: { search: %s, protocol: 'https:'" % json.dumps(search).replace('"', "'"))
    pre = pre.replace('history: { replaceState: function () {} }',
                      'history: { replaceState: function (a, b, u) { __lastReplace = u; } }')
    pre = pre.replace('var __store = {};', 'var __store = {};\nvar __lastReplace = null;')
    ctx = quickjs.Context()
    ctx.eval(pre)
    for k, v in (store or {}).items():
        ctx.eval("__store[%s] = %s;" % (json.dumps(k), json.dumps(v)))
    ctx.eval(src)
    return ctx


def run_case(search='', store=None):
    """startJoin()을 실제로 돌려 참여 화면 상태를 돌려준다."""
    ctx = load(search, store)
    return ctx.eval("""
    (function () {
      state.joined = false;
      startJoin();
      return JSON.stringify({
        needLink: joinNeedLink,
        slot: joinSlot + 1,
        html: document.querySelector('#view-join').innerHTML,
        lastReplace: __lastReplace,
        urlSearch: location.search
      });
    })()
    """)


def main():
    # 1) 초대 링크로 열면 초대 정보가 남는다
    r = json.loads(run_case('?join=1&slot=3&room=test'))
    check(r['needLink'] is False, '초대 링크: 안내 화면이 아니라 참여 화면')
    check(r['slot'] == 3, '초대 링크: 3번 자리로 참여 화면 (slot=%s)' % r['slot'])
    check(r['urlSearch'] == '?join=1&slot=3&room=test', '초대 링크: 주소의 ?join=… 유지 (%s)' % r['urlSearch'])

    # 1-b) ?d= 같은 실험용 파라미터는 떼고 초대만 남긴다
    ctx = load('?join=1&slot=4&room=test&d=2026-11-28')
    inv = json.loads(ctx.eval("JSON.stringify(inviteFromSearch())"))
    ctx.eval("tidyInviteUrl(inviteFromSearch());")
    check(ctx.eval("__lastReplace") == '/?join=1&slot=4&room=test',
          '초대 링크: 주소를 ?join=1&slot=4&room=test 로 정리 (%s)' % ctx.eval("__lastReplace"))
    check(inv['slot'] == 4, '초대 링크: 자리 번호 읽기 (slot=%s)' % inv['slot'])

    # 2) 참여를 마쳐도 주소에 초대 정보가 남는다
    r2 = load('?join=1&slot=2&room=test')
    out = json.loads(r2.eval("""
    (function () {
      state.joined = false; startJoin();
      document.getElementById('joinName').value = '서준';
      joinPick = '🐣';
      joinSubmit();
      return JSON.stringify({ lastReplace: __lastReplace, joined: state.joined,
                              name: state.profiles[joinSlot].name,
                              stored: localStorage.getItem('kidsStudyApp.invite.v1') });
    })()
    """))
    check(out['joined'] is True and out['name'] == '서준', '참여 완료: 프로필·joined 유지 (%s)' % out['name'])
    check('/?join=1&slot=2&room=test' in (out['lastReplace'] or ''),
          '참여 완료: 주소에 초대 정보 유지 (%s)' % out['lastReplace'])
    check(bool(out['stored']) and '"slot":2' in out['stored'].replace(' ', ''),
          '참여 완료: 이 폰에 초대 자리 기억 (%s)' % out['stored'])

    # 3) 파라미터 없이 열려도(홈 화면 아이콘) 기억된 초대로 참여 화면
    saved = json.dumps({'slot': 4, 'room': 'test', 'at': 1}, ensure_ascii=False)
    r3 = json.loads(run_case('', {'kidsStudyApp.invite.v1': saved}))
    check(r3['needLink'] is False, '홈 화면(파라미터 없음): 안내 화면 아님')
    check(r3['slot'] == 4, '홈 화면(파라미터 없음): 기억된 4번 자리로 참여 화면 (%s)' % r3['slot'])
    check('4번' in r3['html'], '홈 화면(파라미터 없음): 화면에 "4번" 자리 표시')

    # 4) 초대 정보가 없으면 막다른 화면이 아니다
    r4 = json.loads(run_case('', {}))
    check(r4['needLink'] is True and '초대 링크로 들어와 줘' in r4['html'], '초대 없음: 안내 화면')
    check('join-later' in r4['html'], '초대 없음: "먼저 둘러보기" 버튼 있음(막다른 화면 아님)')
    check('join-resume' not in r4['html'], '초대 없음: 이어가기 버튼은 없음')

    # 4-b) 기억된 초대가 있으면 안내 화면에서도 이어가기 버튼
    r5 = load('', {'kidsStudyApp.invite.v1': saved})
    out5 = json.loads(r5.eval("""
    (function () { state.joined = false; startJoin(true);
      var html = document.querySelector('#view-join').innerHTML;
      return JSON.stringify({ html: html }); })()
    """))
    check('join-resume' in out5['html'] and '4번 자리로 이어서' in out5['html'],
          '주인 바꾸기(초대 없음 강제): 기억된 자리로 이어가기 버튼')

    # 5) manifest 에 고정 start_url 이 없고, 앱 identity(scope)는 유지
    man = json.load(open(os.path.join(ROOT, 'manifest.webmanifest'), encoding='utf-8'))
    check('start_url' not in man, 'manifest: 고정 start_url 없음(현재 주소로 열림)')
    check(man.get('scope') == './' and man.get('display') == 'standalone', 'manifest: scope·standalone 유지')
    check(len(man.get('icons') or []) >= 1, 'manifest: 아이콘 유지')

    # 6) index.html: 참여를 마칠 때 주소를 지우지 않는다 (지우는 곳은 '이미 내 자리가 있는 폰'·'먼저 둘러보기' 뿐)
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    body = re.search(r'function joinSubmit\(\)\s*\{(.*?)\n\}', html, re.S).group(1)
    check('location.pathname + inviteQuery(' in body and "replaceState(null, '', location.pathname)" not in body,
          'index.html: 참여 완료 후 주소에 초대 정보 유지(통째로 지우지 않음)')
    check(len(re.findall(r"history\.replaceState\(null, '', location\.pathname\)", html)) == 2,
          'index.html: 주소 전체 삭제는 2곳(이미 내 자리 있음·먼저 둘러보기)만')
    check('INVITE_STORE' in html and 'kidsStudyApp.invite.v1' in html, 'index.html: 초대 기억(localStorage) 구현')

    print('\n전부 통과' if not FAIL else '\n실패 %d건' % len(FAIL))
    return 0 if not FAIL else 1


if __name__ == '__main__':
    sys.exit(main())
