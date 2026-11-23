#!/usr/bin/env python3
"""한자 비문학(단계별 세트) 데이터를 index.html 의 HANJA_SETS 블록에 넣는다.

   원본: data/hanja.json (1~2단계) + data/hanja_advanced.json (3~4단계)
   한 세트 = 오늘의 한자 3개(음/훈·부수·획순 좌표·예문) + 짧은 비문학 글 + 문제 3개
   획순 좌표는 0~100 상자 위의 점 목록(획 하나에 [x1,y1,x2,y2,...])이고,
   앱이 이 점들을 SVG 획으로 그려 '획순 따라가기'로 한 획씩 보여 준다.

   실행: python3 tools/gen_hanja.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
DATA = os.path.join(ROOT, 'data')
FAIL = []


def norm(s):
    s = str(s or '').lower().replace(',', '')
    return re.sub(r'[\s\.\,\!\?\"\'“”‘’·…~\-—\(\)\[\]<>:/]', '', s)


def err(m):
    FAIL.append(m)


def main():
    levels = {}
    for name in ('hanja.json', 'hanja_advanced.json'):
        with open(os.path.join(DATA, name), encoding='utf-8') as f:
            d = json.load(f)
        for lv, blk in d['levels'].items():
            levels.setdefault(lv, []).extend(blk['sets'])

    for lv in sorted(levels, key=int):
        sets_ = levels[lv]
        if len(sets_) < 2:
            err(f'{lv}단계: 세트 {len(sets_)}개(>=2)')
        for st in sets_:
            tag = f'{lv}단계 {st.get("id", "?")}'
            for k in ('title', 'topic', 'essay', 'key'):
                if not st.get(k):
                    err(f'{tag}: {k} 없음')
            essay = st.get('essay') or ''
            paras = [p for p in essay.split('\n\n') if p.strip()]
            if not (3 <= len(paras) <= 4):
                err(f'{tag}: 글 문단 {len(paras)}개(3~4)')
            if not (180 <= len(essay) <= 430):
                err(f'{tag}: 글 분량 {len(essay)}자(180~430)')
            vocab = st.get('vocab') or []
            if not (1 <= len(vocab) <= 2):
                err(f'{tag}: 낱말 1~2개')
            chars = st.get('chars') or []
            if len(chars) != 3:
                err(f'{tag}: 오늘의 한자 {len(chars)}개(3)')
            for ch in chars:
                ctag = f'{tag}/{ch.get("c", "?")}'
                for k in ('c', 'eum', 'hun', 'bushu', 'bushu_name', 'sentence'):
                    if not ch.get(k):
                        err(f'{ctag}: {k} 없음')
                if len(str(ch.get('c', ''))) != 1:
                    err(f'{ctag}: 한자 한 글자가 아님')
                strokes = ch.get('strokes') or []
                if not (1 <= len(strokes) <= 20):
                    err(f'{ctag}: 획 {len(strokes)}개')
                for k, pts in enumerate(strokes):
                    if not isinstance(pts, list) or len(pts) < 4 or len(pts) % 2:
                        err(f'{ctag}: {k + 1}번째 획 좌표 형식')
                        continue
                    if any((not isinstance(v, (int, float))) or v < 0 or v > 100 for v in pts):
                        err(f'{ctag}: {k + 1}번째 획 좌표 범위(0~100)')
                steps = ch.get('steps') or []
                if len(steps) != len(strokes):
                    err(f'{ctag}: 획 {len(strokes)}개인데 설명 {len(steps)}개')
                words = ch.get('words') or []
                if len(words) < 2 or any(not w.get('w') or not w.get('m') for w in words):
                    err(f'{ctag}: 예문 낱말 2개 이상(뜻 포함)')
                if ch.get('c') and ch['c'] not in st.get('chars', [{}])[0].get('c', ch['c']) and False:
                    pass
            quiz = st.get('quiz') or []
            if len(quiz) != 3:
                err(f'{tag}: 문제 {len(quiz)}개(3)')
            # 한자 과목은 '글 이해' 문제와 '한자 자체(모양·음·훈·부수)' 문제가 섞여 있다.
            # 정답은 글 + 오늘 한자 카드(뜻·설명·예문) 안에서 찾을 수 있어야 하고,
            # 그중 최소 1문제는 글만 읽어도 답이 나와야 한다.
            card_text = ' '.join(
                [st.get('key', '')] +
                [f"{ch.get('hun', '')} {ch.get('eum', '')} {ch.get('bushu_name', '')} {ch.get('sentence', '')} " +
                 ' '.join(f"{w.get('w', '')} {w.get('m', '')}" for w in (ch.get('words') or [])) +
                 ' '.join(ch.get('steps') or []) for ch in chars]
            )
            in_essay = 0
            for z in quiz:
                opts = z.get('opts') or []
                if len(opts) != 3 or len(set(opts)) != 3:
                    err(f'{tag}: 보기 3개·중복 없음')
                if not isinstance(z.get('ans'), int) or not (0 <= z.get('ans', -1) < 3):
                    err(f'{tag}: 정답 번호')
                if not z.get('why'):
                    err(f'{tag}: 풀이 없음')
                if opts and 0 <= z.get('ans', -1) < 3:
                    a = opts[z['ans']]
                    if norm(a) in norm(essay):
                        in_essay += 1
                    elif norm(a) not in norm(essay + ' ' + card_text):
                        err(f'{tag}: 정답 "{a}"를 글·한자 카드에서 찾을 수 없음')
            if in_essay < 1:
                err(f'{tag}: 글만 읽어도 답이 나오는 문제가 없음(1문제 이상)')
            # 글은 오늘의 한자 3개를 실제로 다뤄야 한다 (글자 또는 그 낱말이 나와야 함)
            covered = 0
            for ch in chars:
                if ch.get('c', '') and ch['c'] in essay:
                    covered += 1
                    continue
                if any(str(w.get('w', '')) and str(w.get('w')) in essay for w in (ch.get('words') or [])):
                    covered += 1
            if covered < 3:
                err(f'{tag}: 글에서 다루지 않은 한자가 있음(한자 또는 낱말이 글에 나와야 함, {covered}/3)')

    if FAIL:
        print('\n'.join('❌ ' + m for m in FAIL))
        print(f'\n데이터 오류 {len(FAIL)}건 — index.html 을 쓰지 않았어요.')
        sys.exit(1)

    html = open(HTML, encoding='utf-8').read()
    if '/*__HANJA_START__*/' not in html:
        print('!! HANJA 마커가 없습니다.', file=sys.stderr)
        sys.exit(1)
    ordered = {lv: levels[lv] for lv in sorted(levels, key=int)}
    body = 'const HANJA_SETS = ' + json.dumps(ordered, ensure_ascii=False, separators=(',', ':')) + ';'
    html = re.sub(r'/\*__HANJA_START__\*/.*?/\*__HANJA_END__\*/',
                  lambda m: '/*__HANJA_START__*/\n' + body + '\n/*__HANJA_END__*/', html, flags=re.S)
    open(HTML, 'w', encoding='utf-8', newline='').write(html)
    total_chars = sum(len(s['chars']) for v in ordered.values() for s in v)
    print('HANJA_SETS', {lv: len(v) for lv, v in ordered.items()}, '세트 합계', sum(len(v) for v in ordered.values()), '· 한자', total_chars)


main()
