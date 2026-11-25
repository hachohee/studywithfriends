#!/usr/bin/env python3
"""index.html 스크립트를 가짜 DOM(quickjs) 위에서 실제로 돌려 보는 점검.

   확인하는 것
   1) 7과목(기존 5 + 한자 비문학 + 예쁘게 말하기)이 모두 문제를 낸다
   2) 오늘 문제·홈·과목 화면(한자 획순 SVG·예쁘게 말하기)이 오류 없이 그려진다
   3) 난이도: 연속 정답 5 → 내일부터 +1단계, 연속 오답 3 → 내일부터 -1단계, 1~4단계 범위
   4) 단계를 올리면 그 단계의 문제·글이 실제로 바뀐다
   5) 도장판에는 난이도가 드러나지 않는다 (완료 도장만)
"""
import json, sys

from browser_probe import run

JS = r"""
(function () {
  var out = { errors: [] };
  function safe(name, fn) { try { return fn(); } catch (e) { out.errors.push(name + ': ' + e); return null; } }

  out.subjects = SUBJECTS.map(function (s) { return s.id + ':' + s.name; });
  out.subjectCount = SUBJECTS.length;
  out.pools = SUBJECTS.map(function (s) { return s.id + ' L1=' + quizPool(s.id, 1).length + ' L2=' + quizPool(s.id, 2).length + ' L3=' + quizPool(s.id, 3).length + ' L4=' + quizPool(s.id, 4).length; });

  out.todayCounts = SUBJECTS.map(function (s) { return s.id + '=' + dailyQuizIdxs(s).length; });
  out.levelsDefault = window.__kids.levels().map(function (x) { return x.id + ':' + x.lv; });

  out.hanjaToday = window.__kids.hanjaToday();
  out.speakToday = window.__kids.speakToday();

  // 화면 그리기
  safe('home', function () { showView('home'); out.homeLen = document.querySelector('#view-home').innerHTML.length; });
  safe('study', function () { showView('study'); out.studyLen = document.querySelector('#view-study').innerHTML.length; });
  var hanjaHTML = safe('hanjaSubject', function () { openSubject('hanja'); return document.querySelector('#view-subject').innerHTML; });
  out.hanjaHTML = hanjaHTML || '';
  out.hanjaChecks = {
    svg: (out.hanjaHTML.match(/<svg class="hj-svg"/g) || []).length,
    paths: (out.hanjaHTML.match(/<path class="st"/g) || []).length,
    steps: (out.hanjaHTML.match(/<li>/g) || []).length,
    words: (out.hanjaHTML.match(/hj-word/g) || []).length,
    levelChip: out.hanjaHTML.indexOf('lv-badge') >= 0,
    essay: out.hanjaHTML.indexOf('오늘의 읽기 글') >= 0,
    problems: (out.hanjaHTML.match(/class="opt /g) || []).length
  };
  var speakHTML = safe('speakSubject', function () { openSubject('speak'); return document.querySelector('#view-subject').innerHTML; });
  out.speakHTML = speakHTML || '';
  out.speakChecks = {
    scene: out.speakHTML.indexOf('sp-scene') >= 0,
    options: (out.speakHTML.match(/class="opt /g) || []).length,
    listen: out.speakHTML.indexOf('speak-read') >= 0
  };
  safe('mathSubject', function () { openSubject('math'); out.mathHTML = document.querySelector('#view-subject').innerHTML.length; });
  safe('englishSubject', function () { openSubject('english'); out.engHTML = document.querySelector('#view-subject').innerHTML.length; });
  safe('historySubject', function () { openSubject('history'); out.histHTML = document.querySelector('#view-subject').innerHTML.length; });
  safe('heroSubject', function () { openSubject('hero'); out.heroHTML = document.querySelector('#view-subject').innerHTML.length; });
  safe('newsSubject', function () { openSubject('news'); out.newsHTML = document.querySelector('#view-subject').innerHTML.length; });
  safe('board', function () { showView('board'); out.boardLen = document.querySelector('#view-board').innerHTML.length; out.boardText = document.querySelector('#view-board').innerHTML; });
  safe('settings', function () { showView('settings'); out.setLen = document.querySelector('#view-settings').innerHTML.length; });

  // 난이도: 연속 정답 5 → 다음 날 +1
  out.lvBefore = levelOf('p1', 'math');
  var ups = [];
  for (var i = 0; i < 5; i++) ups.push(noteAnswer('math', true));
  out.upEvents = ups;
  out.nextAfterUp = nextLevelOf('p1', 'math');
  out.lvSameDay = levelOf('p1', 'math');
  // 예약된 단계를 오늘로 당겨 적용되는지 (from 을 어제로 바꿔 확인)
  if (out.nextAfterUp) { state.levelNext['p1']['math'].from = '2000-01-01'; }
  out.lvNextDay = levelOf('p1', 'math');
  out.mathPoolAt2 = quizPool('math', 2).length;
  out.mathIdxAt2 = dailyQuizIdxs(SUBJECT_BY_ID.math).length;

  // 연속 오답 3 → 다음 날 -1
  noteAnswer('math', false); noteAnswer('math', false); noteAnswer('math', false);
  out.nextAfterDown = nextLevelOf('p1', 'math');
  if (state.levelNext['p1']['math']) state.levelNext['p1']['math'].from = '2000-01-01';
  out.lvAfterDown = levelOf('p1', 'math');

  // 아래로는 1단계 밑으로 안 내려감
  state.levelNext = {}; state.streaks = {};
  noteAnswer('math', false); noteAnswer('math', false); noteAnswer('math', false);
  out.lvFloor = levelOf('p1', 'math');

  // 위로는 4단계 위로 안 올라감
  window.__kids.setLevel('math', 4);
  state.streaks = {};
  for (var k = 0; k < 5; k++) noteAnswer('math', true);
  out.nextAtCap = nextLevelOf('p1', 'math');

  // 단계를 올리면 한자·예쁘게 말하기 내용이 바뀐다
  window.__kids.setLevel('hanja', 1);
  var h1 = window.__kids.hanjaToday();
  window.__kids.setLevel('hanja', 3);
  var h3 = window.__kids.hanjaToday();
  out.hanjaLevelChange = { lv1: h1 && h1.title, lv3: h3 && h3.title, diff: !!(h1 && h3 && h1.title !== h3.title) };
  window.__kids.setLevel('hanja', 1);

  // 도장판에 난이도가 드러나는가 (단계/난이도 글자가 없어야 함)
  out.boardHasLevelWord = (out.boardText || '').indexOf('단계') >= 0;
  out.boardHasLevel = (out.boardText || '').indexOf('난이도') >= 0;

  // 완료 판정: 오늘 문제를 모두 맞히면 완료 · 도장은 서버로 한 번만
  state.progress = {}; state.levels = {}; state.levelNext = {}; state.streaks = {};
  var sub = SUBJECT_BY_ID['speak'];
  var id0 = dailyQuizIdxs(sub)[0];
  var before = subProgress(sub).complete;
  awardQuiz('speak', id0);
  out.speakComplete = { before: before, after: subProgress(sub).complete, stamps: quizCount('p1', 'speak') };

  // 한자: 하루 3문제
  var hsub = SUBJECT_BY_ID['hanja'];
  out.hanjaSetCount = dailyQuizIdxs(hsub).length;
  var ids = dailyQuizIdxs(hsub);
  for (var j = 0; j < ids.length; j++) awardQuiz('hanja', ids[j]);
  out.hanjaComplete = subProgress(hsub).complete;

  // 수학: 화면에 보여 주는 문제 목록과 완료 판정 목록이 같은가 · 단계가 달라도 다 풀면 완료되는가
  out.mathByLevel = [1, 2, 3, 4].map(function (lv) {
    state.progress = {}; state.mathDay = {}; state.levelNext = {}; state.streaks = {};
    window.__kids.setLevel('math', lv);
    var sets = mathDaySets(undefined, 'p1');
    var shown = sets.reduce(function (a, g) { return a.concat(g.list); }, []);
    var prog = mathIdxs(undefined, lv, 'p1');
    var same = JSON.stringify(shown) === JSON.stringify(prog);
    shown.forEach(function (qi) { awardQuiz('math', qi); });
    var p = subProgress(SUBJECT_BY_ID['math'], 'p1');
    var badge = (dailyCardHTML(SUBJECT_BY_ID['math']).match(/d-badge">([^<]*)/) || [])[1];
    return { lv: lv, n: shown.length, same: same, solved: p.solved, complete: p.complete, badge: badge };
  });

  // 은행 맨 뒤에 문제가 덧붙어도(매일 10문제) 하루 중간에 오늘 목록이 바뀌지 않는가
  state.progress = {}; state.mathDay = {};
  window.__kids.setLevel('math', 2);
  var idxBefore = JSON.stringify(mathIdxs(undefined, 2, 'p1'));
  var mbank = MATH_LEVELS[2], mlen = mbank.length;
  for (var z = 0; z < 10; z++) mbank.push({ kind: '연산', q: '덧붙인 문제 ' + z, opts: ['1', '2', '3'], ans: 0, why: 'x' });
  var idxAfter = JSON.stringify(mathIdxs(undefined, 2, 'p1'));
  mbank.length = mlen;
  out.mathGrowSame = idxBefore === idxAfter;

  // 한자: 오늘 문제 3개가 언제나 '한 세트' 안에서만 나오는가 (단계 × 날짜)
  out.hanjaOneSet = (function () {
    var bad = [];
    for (var lv = 1; lv <= 4; lv++) {
      window.__kids.setLevel('hanja', lv);
      for (var off = 0; off < 10; off++) {
        var d = new Date(refNow().getTime() + off * 86400000);
        var idx = dailyIdxs(SUBJECT_BY_ID['hanja'], d, 'p1');
        var ids = idx.map(function (i) { var it = poolItem(SUBJECT_BY_ID['hanja'], i, 'p1'); return it && it.hjSet ? it.hjSet.id : 'NULL'; });
        var uniq = ids.filter(function (v, i) { return ids.indexOf(v) === i; });
        if (idx.length !== 3 || uniq.length !== 1 || uniq[0] === 'NULL') bad.push(lv + '단계/' + off + '일:' + uniq.join(','));
      }
    }
    window.__kids.setLevel('hanja', 1);
    return bad;
  })();

  out.pageErrs = window.__errs || [];
  return JSON.stringify(out);
})()
"""


def main():
    ctx = run()
    ctx.eval('var fetch = function () { return Promise.resolve({ ok: false, status: 404, json: function () { return Promise.resolve({}); } }); };')
    res = json.loads(ctx.eval(JS))
    ok = True
    def check(cond, msg):
        nonlocal ok
        print(('✅ ' if cond else '❌ ') + msg)
        if not cond:
            ok = False
    check(not res['errors'], '화면 그리기 오류 없음 ' + str(res['errors'])[:400])
    check(res['subjectCount'] == 7, '과목 7개: ' + ', '.join(res['subjects']))
    check(all(int(x.split('L1=')[1].split()[0]) > 0 for x in res['pools']), '모든 과목 1단계 문제 있음: ' + ' | '.join(res['pools']))
    check(all(int(x.split('L4=')[1]) > 0 for x in res['pools']), '모든 과목 4단계 문제 있음')
    check(res['todayCounts'] == ['math=10', 'english=3', 'history=2', 'hero=3', 'news=1', 'hanja=3', 'speak=1'], '오늘 문제 수: ' + str(res['todayCounts']))
    check(all(x.endswith(':1') for x in res['levelsDefault']), '모두 1단계에서 시작: ' + str(res['levelsDefault']))
    h = res['hanjaChecks']
    check(h['svg'] == 3 and h['paths'] >= 6, '한자 카드 3개 · 획순 SVG path %d개' % h['paths'])
    check(h['steps'] >= 6, '획순 단계 설명 %d개' % h['steps'])
    check(h['words'] >= 6, '예문 낱말 %d개' % h['words'])
    check(h['levelChip'] and h['essay'] and h['problems'] == 9, '한자 화면: 단계 배지·읽기 글·문제 3개(보기 9개)')
    s = res['speakChecks']
    check(s['scene'] and s['options'] == 3 and s['listen'], '예쁘게 말하기 화면: 상황·보기 3개·읽어주기')
    check(res['upEvents'][-1] == 'up' and res['nextAfterUp'] and res['nextAfterUp']['lv'] == 2, '연속 정답 5 → 다음 날 2단계 예약')
    check(res['lvSameDay'] == 1, '단계 변경은 다음 날부터 (오늘은 1단계 유지)')
    check(res['lvNextDay'] == 2, '다음 날 2단계 적용')
    check(res['mathPoolAt2'] > 0, '2단계 수학 문제 %d개' % res['mathPoolAt2'])
    check(res['nextAfterDown'] and res['nextAfterDown']['lv'] == 1, '연속 오답 3 → 다음 날 1단계 예약')
    check(res['lvAfterDown'] == 1 and res['lvFloor'] == 1, '1단계 아래로는 내려가지 않음')
    check(res['nextAtCap'] is None, '4단계 위로는 올라가지 않음')
    check(res['hanjaLevelChange']['diff'], '단계가 바뀌면 한자 세트도 바뀜: %s → %s' % (res['hanjaLevelChange']['lv1'], res['hanjaLevelChange']['lv3']))
    check(not res['boardHasLevelWord'] and not res['boardHasLevel'], '도장판에 난이도·단계 표시 없음')
    check(res['speakComplete']['before'] is False and res['speakComplete']['after'] is True, '예쁘게 말하기: 1문제 맞히면 오늘 완료')
    check(res['hanjaSetCount'] == 3 and res['hanjaComplete'] is True, '한자: 3문제 맞히면 오늘 완료')
    ml = res['mathByLevel']
    check(all(x['n'] == 10 for x in ml), '수학: 단계별 오늘 문제 10개 ' + str([x['n'] for x in ml]))
    check(all(x['same'] for x in ml), '수학: 화면 문제 목록 = 완료 판정 목록(1~4단계)')
    check(all(x['complete'] and x['solved'] == 10 for x in ml), '수학: 단계가 달라도 10문제를 다 맞히면 오늘 완료 ' + str([(x['lv'], x['solved'], x['complete']) for x in ml]))
    check(all(('완료' in (x['badge'] or '')) for x in ml), '수학: 다 풀면 홈 카드가 완료 표시 ' + str([x['badge'] for x in ml]))
    check(res['mathGrowSame'], '수학: 은행에 문제가 덧붙어도 오늘 문제 목록은 그대로')
    check(not res['hanjaOneSet'], '한자: 오늘 문제 3개가 한 세트 안에서만 나옴 ' + str(res['hanjaOneSet'])[:200])
    check(not res['pageErrs'], '페이지 오류 없음 ' + str(res['pageErrs'])[:300])
    if not ok:
        sys.exit(1)
    print('\n전부 통과')


main()
