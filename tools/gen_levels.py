#!/usr/bin/env python3
"""2~4단계 읽기 글(한국사·위인·시사상식)·영어 문장·예쁘게 말하기 데이터를 index.html 의 LEVEL_POOLS 블록에 넣는다.

   1단계는 손대지 않는다 — 한국사·위인·시사는 videos.json(BANKS)을, 영어는 ENGLISH_STEPS 30문장을 그대로 쓴다.
   원본: data/levels_read.json · data/levels_english.json · data/levels_speak.json

   실행: python3 tools/gen_levels.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
DATA = os.path.join(ROOT, 'data')
FAIL = []


def norm(s):
    s = str(s or '').lower().replace(',', '')
    return re.sub(r'[\s\.\,\!\?\"\'“”‘’·…~\-—\(\)\[\]<>:/]', '', s)


def err(msg):
    FAIL.append(msg)


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def check_essay_item(subj, lv, it):
    tag = f'{subj} {lv}단계 {it.get("id", "?")}'
    essay = it.get('essay') or ''
    paras = [p for p in essay.split('\n\n') if p.strip()]
    if not (3 <= len(paras) <= 4):
        err(f'{tag}: 문단 {len(paras)}개(3~4)')
    if not (200 <= len(essay) <= 420):
        err(f'{tag}: 분량 {len(essay)}자(200~420)')
    if '영상' in essay:
        err(f'{tag}: 글에 "영상" 언급')
    topic = it.get('topic') or ''
    if not (2 <= len(topic) <= 24):
        err(f'{tag}: 주제 이름 "{topic}"')
    vocab = it.get('vocab') or []
    if not (1 <= len(vocab) <= 2) or any(not v.get('w') or not v.get('m') for v in vocab):
        err(f'{tag}: 낱말 1~2개(뜻 포함)')
    opts = it.get('opts') or []
    if len(opts) != 3 or len(set(opts)) != 3:
        err(f'{tag}: 보기 3개·중복 없음')
    ans = it.get('ans')
    if not isinstance(ans, int) or not (0 <= ans < 3):
        err(f'{tag}: 정답 번호')
    if not it.get('why'):
        err(f'{tag}: 풀이 없음')
    if not it.get('key'):
        err(f'{tag}: 핵심 한 줄 없음')
    if opts and isinstance(ans, int) and 0 <= ans < len(opts) and norm(opts[ans]) not in norm(essay):
        err(f'{tag}: 정답 "{opts[ans]}"가 글 안에 없음')


def check_english(lv, sents):
    if len(sents) < 10:
        err(f'english {lv}단계: 문장 {len(sents)}개(>=10)')
    ens = [s.get('en', '') for s in sents]
    kos = [s.get('ko', '') for s in sents]
    if len(set(ens)) != len(ens):
        err(f'english {lv}단계: 영어 문장 중복')
    if len(set(kos)) != len(kos):
        err(f'english {lv}단계: 우리말 뜻 중복(보기 3개가 겹침)')
    for s in sents:
        if not (s.get('en') and s.get('ko') and s.get('tip')):
            err(f'english {lv}단계: en/ko/tip 빠짐 -> {s.get("en")}')


def check_speak(lv, items):
    if len(items) < 4:
        err(f'speak {lv}단계: 상황 {len(items)}개(>=4)')
    for it in items:
        tag = f'speak {lv}단계 {it.get("id", "?")}'
        for k in ('scene', 'title', 'situation', 'q', 'why', 'say', 'tip'):
            if not it.get(k):
                err(f'{tag}: {k} 없음')
        opts = it.get('opts') or []
        if len(opts) != 3 or len(set(opts)) != 3:
            err(f'{tag}: 보기 3개·중복 없음')
        if it.get('ans') != 0:
            err(f'{tag}: 정답은 0번(가장 좋은 말)로 써 주세요')
        if it.get('scene') not in ('가족', '친구', '이웃', '학교', '가게', '식당', '온라인'):
            err(f'{tag}: 장소 "{it.get("scene")}"')


def main():
    read = load('levels_read.json')
    eng = load('levels_english.json')
    spk = load('levels_speak.json')

    levels = {'history': {}, 'hero': {}, 'news': {}, 'english': {}, 'speak': {}}

    for subj in ('history', 'hero', 'news'):
        for lv, items in read[subj].items():
            for it in items:
                check_essay_item(subj, lv, it)
            levels[subj][lv] = items
    for lv, sents in eng['english'].items():
        check_english(lv, sents)
        levels['english'][lv] = sents
    for lv, items in spk['speak'].items():
        check_speak(lv, items)
        levels['speak'][lv] = items

    # 위인: 한 인물의 문제가 3개 이상이어야 하루 3문제가 된다 · 한국사: 한 주제 2개 이상
    for lv, items in levels['hero'].items():
        g = {}
        for it in items:
            g.setdefault(str(it['id']).split('-q')[0], []).append(it)
        for vid, arr in g.items():
            if len(arr) < 3:
                err(f'hero {lv}단계 {vid}: 문제 {len(arr)}개(하루 3문제 → 3개 이상)')
    for lv, items in levels['history'].items():
        g = {}
        for it in items:
            g.setdefault(str(it['id']).split('-q')[0], []).append(it)
        for vid, arr in g.items():
            if len(arr) < 2:
                err(f'history {lv}단계 {vid}: 문제 {len(arr)}개(하루 2문제 → 2개 이상)')

    if FAIL:
        print('\n'.join('❌ ' + m for m in FAIL))
        print(f'\n데이터 오류 {len(FAIL)}건 — index.html 을 쓰지 않았어요.')
        sys.exit(1)

    html = open(HTML, encoding='utf-8').read()
    if '/*__POOLS_START__*/' not in html:
        print('!! POOLS 마커가 없습니다.', file=sys.stderr)
        sys.exit(1)
    body = 'const LEVEL_POOLS = ' + json.dumps(levels, ensure_ascii=False, separators=(',', ':')) + ';'
    html = re.sub(r'/\*__POOLS_START__\*/.*?/\*__POOLS_END__\*/',
                  lambda m: '/*__POOLS_START__*/\n' + body + '\n/*__POOLS_END__*/', html, flags=re.S)
    open(HTML, 'w', encoding='utf-8', newline='').write(html)
    print('LEVEL_POOLS', {k: {lv: len(v) for lv, v in d.items()} for k, d in levels.items()})


main()
