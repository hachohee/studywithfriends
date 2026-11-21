#!/usr/bin/env python3
"""초2 수학 문제 은행(연산/사고력/서술형)을 만들어 index.html 의 MATH_BANK 블록에 넣는다.
   실행: python tools/gen_math.py   (같은 시드라 다시 실행해도 같은 결과 — 도장 번호가 바뀌지 않음)
   은행 크기를 늘리면 뒤에 새 문제가 붙고 앞 번호는 유지된다."""
import json, os, random, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
N_CALC, N_THINK, N_WORD = 140, 45, 45   # 하루 5 / 2 / 3 문제 → 각각 28일 / 22일 / 15일 주기

NAMES = [('민지', '는', '가'), ('서준', '은', '이'), ('지우', '는', '가'), ('하윤', '은', '이'), ('도윤', '은', '이'), ('서아', '는', '가')]
OBJS = [('구슬', '이', '을', '개', '를'), ('사탕', '이', '을', '개', '를'), ('스티커', '가', '를', '장', '을'),
        ('딱지', '가', '를', '장', '을'), ('색연필', '이', '을', '자루', '를'), ('풍선', '이', '을', '개', '를')]


def has_batchim(n):
    """숫자를 한글로 읽을 때 받침이 있는지 (10의 배수는 '십'이라 있음; 1일 3삼 6육 7칠 8팔 0영 → 있음, 2이 4사 5오 9구 → 없음)"""
    return n % 10 == 0 or n % 10 in (1, 3, 6, 7, 8)


def eul(n): return '을' if has_batchim(n) else '를'
def iga(n): return '이' if has_batchim(n) else '가'


def make(rng, q, ans, why, kind, unit='', wrong=()):
    """보기 3개(정답 포함, 위치는 무작위). wrong = 헷갈리기 쉬운 오답 후보(예: 연산을 잘못한 값)."""
    cands = [w for w in wrong if w != ans and w > 0]
    for d in (1, -1, 10, -10, 2, -2):
        if ans + d > 0 and ans + d not in cands:
            cands.append(ans + d)
    picks = [ans] + cands[:2]
    rng.shuffle(picks)
    return {'kind': kind, 'q': q, 'opts': [f'{v}{unit}' for v in picks], 'ans': picks.index(ans), 'why': why}


# ── 연산 ──
def calc(rng, i):
    t = i % 6
    if t == 0:    # 두 자리 + 두 자리 (받아올림 포함)
        a = rng.randint(14, 78); b = rng.randint(11, 99 - a)
        return make(rng, f'{a} + {b} = ?', a + b, f'{a}+{b}={a + b}. 일의 자리끼리 먼저 더하고, 10이 넘으면 십의 자리로 올려요.', '연산', wrong=[a + b + 10, a + b - 10])
    if t == 1:    # 두 자리 − 두 자리 (받아내림 포함)
        a = rng.randint(32, 95); b = rng.randint(11, a - 10)
        return make(rng, f'{a} − {b} = ?', a - b, f'{a}−{b}={a - b}. 일의 자리가 모자라면 십의 자리에서 10을 빌려와요.', '연산', wrong=[a - b + 10, a - b - 10])
    if t == 2:    # 곱셈구구
        m, n = rng.randint(2, 9), rng.randint(2, 9)
        return make(rng, f'{m} × {n} = ?', m * n, f'{m}×{n}={m * n}. {m}씩 {n}번 더한 것과 같아요.', '연산', wrong=[m + n, m * (n + 1)])
    if t == 3:    # 세 수 계산
        a = rng.randint(30, 80); b = rng.randint(11, 25); c = rng.randint(5, 20)
        if rng.random() < .5:
            return make(rng, f'{a} + {b} − {c} = ?', a + b - c, f'앞에서부터 차례로: {a}+{b}={a + b}, {a + b}−{c}={a + b - c}.', '연산', wrong=[a + b + c, a - b - c])
        return make(rng, f'{a} − {b} + {c} = ?', a - b + c, f'앞에서부터 차례로: {a}−{b}={a - b}, {a - b}+{c}={a - b + c}.', '연산', wrong=[a - b - c, a + b + c])
    if t == 4:    # □ 구하기
        a = rng.randint(12, 60); b = rng.randint(a + 10, 99)
        return make(rng, f'□ + {a} = {b}  에서 □는?', b - a, f'□ = {b}−{a} = {b - a}. 더하기의 □는 빼기로 구해요.', '연산', wrong=[b + a])
    a = rng.randint(30, 90); b = rng.randint(10, a - 10)   # t == 5
    return make(rng, f'{a} − □ = {a - b}  에서 □는?', b, f'□ = {a}−{a - b} = {b}.', '연산', wrong=[a + (a - b)])


# ── 사고력 ──
def think(rng, i):
    t = i % 7
    if t in (0, 1):   # 규칙 찾기 (늘어남/줄어듦)
        d = rng.randint(2, 9); up = (t == 0)
        s = rng.randint(1, 20) if up else rng.randint(40, 70)
        seq = [s + (k if up else -k) * d for k in range(5)]
        word = '씩 커지는' if up else '씩 작아지는'
        return make(rng, f'규칙을 찾아 □에 알맞은 수는?  {", ".join(map(str, seq[:4]))}, □', seq[4],
                    f'{d}{word} 규칙이에요. {seq[3]} 다음은 {seq[3]}{"+" if up else "−"}{d}={seq[4]}!', '사고력', wrong=[seq[3] + (d + 1 if up else -(d + 1))])
    if t == 2:    # 어떤 수 거꾸로 (더하기)
        x = rng.randint(10, 60); k = rng.randint(5, 30)
        return make(rng, f'어떤 수에 {k}{eul(k)} 더했더니 {x + k}{iga(x + k)} 되었어요. 어떤 수는?', x, f'거꾸로 생각해요. {x + k}−{k}={x}.', '사고력', wrong=[x + 2 * k])
    if t == 3:    # 어떤 수 거꾸로 (빼기)
        x = rng.randint(30, 90); k = rng.randint(5, 25)
        return make(rng, f'어떤 수에서 {k}{eul(k)} 뺐더니 {x - k}{iga(x - k)} 되었어요. 어떤 수는?', x, f'거꾸로 생각해요. {x - k}+{k}={x}.', '사고력', wrong=[x - 2 * k])
    if t == 4:    # 줄 서기
        a, b = rng.randint(3, 9), rng.randint(3, 9)
        return make(rng, f'줄을 섰어요. 민지는 앞에서 {a}번째, 뒤에서 {b}번째예요. 모두 몇 명일까요?', a + b - 1, f'민지가 두 번 세어졌어요! {a}+{b}−1={a + b - 1}(명).', '사고력', '명', wrong=[a + b])
    if t == 5:    # 수 카드로 가장 큰 수
        ds = rng.sample(range(1, 10), 3)
        big = int(''.join(map(str, sorted(ds, reverse=True)[:2])))
        return make(rng, f'수 카드 {ds[0]}, {ds[1]}, {ds[2]} 중 두 장으로 만들 수 있는 가장 큰 두 자리 수는?', big,
                    f'큰 수를 십의 자리에 놓아요. 십의 자리 {sorted(ds, reverse=True)[0]}, 일의 자리 {sorted(ds, reverse=True)[1]} → {big}!', '사고력',
                    wrong=[int(''.join(map(str, sorted(ds)[:2][::-1])))])
    a = rng.randint(10, 30); b = rng.randint(a + 5, 50); c = rng.randint(5, 20)   # t == 6: 양쪽이 같은 식
    return make(rng, f'□ + {a} = {b} + {c}  에서 □는?', b + c - a, f'오른쪽은 {b}+{c}={b + c}. □ = {b + c}−{a} = {b + c - a}.', '사고력', wrong=[b + c + a])


# ── 서술형 ──
def word(rng, i):
    t = i % 8
    n, o = rng.choice(NAMES), rng.choice(OBJS)
    nm, eun, ga = n; ob, oga, oeul, u, ueul = o
    if t == 0:
        a, b = rng.randint(12, 45), rng.randint(10, 40)
        return make(rng, f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있고, 동생은 {b}{u}{ueul} 가지고 있어요. 둘이 가진 것은 모두 몇 {u}일까요?',
                    a + b, f'합치는 문제예요. 식: {a}+{b}={a + b}, 답: {a + b}{u}', '서술형', u, wrong=[abs(a - b)])
    if t == 1:
        a = rng.randint(25, 60); b = rng.randint(8, 20)
        return make(rng, f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있었어요. 친구에게 {b}{u}{ueul} 주었어요. 남은 것은 몇 {u}일까요?',
                    a - b, f'덜어내는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, wrong=[a + b])
    if t == 2:
        m, k = rng.randint(2, 9), rng.randint(2, 9)
        return make(rng, f'{ob}{oga} 한 봉지에 {m}{u}씩 {k}봉지 있어요. 모두 몇 {u}일까요?',
                    m * k, f'{m}씩 {k}묶음이니까 곱셈! 식: {m}×{k}={m * k}, 답: {m * k}{u}', '서술형', u, wrong=[m + k])
    if t == 3:
        a = rng.randint(25, 60); b = rng.randint(10, a - 8)
        return make(rng, f'{nm}{eun} {ob}{oeul} {a}{u}, 동생은 {b}{u}{ueul} 가지고 있어요. {nm}{ga} 동생보다 몇 {u} 더 많을까요?',
                    a - b, f'차이를 구하는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, wrong=[a + b])
    if t == 4:
        a = rng.randint(30, 60); b = rng.randint(8, 20); c = rng.randint(5, 20)
        return make(rng, f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있었어요. 친구에게 {b}{u}{ueul} 주고, 엄마께 {c}{u}{ueul} 더 받았어요. 지금은 모두 몇 {u}일까요?',
                    a - b + c, f'차례로 계산해요. 식: {a}−{b}+{c}={a - b + c}, 답: {a - b + c}{u}', '서술형', u, wrong=[a - b - c, a + b + c])
    if t == 5:
        a, b, c = rng.randint(15, 40), rng.randint(5, 14), rng.randint(5, 20)
        return make(rng, f'버스에 {a}명이 타고 있었어요. 정류장에서 {b}명이 내리고 {c}명이 탔어요. 지금 버스에 탄 사람은 몇 명일까요?',
                    a - b + c, f'식: {a}−{b}+{c}={a - b + c}, 답: {a - b + c}명', '서술형', '명', wrong=[a + b + c, a - b - c])
    if t == 6:
        a, d = rng.randint(2, 9), rng.randint(2, 9)
        return make(rng, f'{nm}{eun} 하루에 동화책을 {a}쪽씩 읽어요. {d}일 동안 읽으면 모두 몇 쪽일까요?',
                    a * d, f'같은 수를 {d}번 더하니까 곱셈! 식: {a}×{d}={a * d}, 답: {a * d}쪽', '서술형', '쪽', wrong=[a + d])
    a, b = rng.randint(30, 60), rng.randint(15, 40)   # t == 7
    return make(rng, f'어제 줄넘기를 {a}번, 오늘은 {b}번 했어요. 이틀 동안 줄넘기를 모두 몇 번 했을까요?',
                a + b, f'식: {a}+{b}={a + b}, 답: {a + b}번', '서술형', '번', wrong=[abs(a - b)])


def build():
    rng = random.Random(20261121)
    out, seen = [], set()
    for kind_fn, n in ((calc, N_CALC), (think, N_THINK), (word, N_WORD)):
        i = 0
        kind = {calc: '연산', think: '사고력', word: '서술형'}[kind_fn]
        while sum(1 for x in out if x['kind'] == kind) < n:
            if i > 20000:
                sys.exit(f'!! {kind} 문제를 {n}개 만들 수 없어요(중복). 은행 크기를 줄이세요.')
            item = kind_fn(rng, i); i += 1
            if item['q'] in seen:
                continue
            seen.add(item['q']); out.append(item)
    return out


def main():
    bank = build()
    body = 'const MATH_BANK = ' + json.dumps(bank, ensure_ascii=False, separators=(',', ':')) + ';'
    html = open(HTML, encoding='utf-8').read()
    if '/*__MATH_START__*/' not in html:
        print('!! MATH 마커가 없습니다.', file=sys.stderr); sys.exit(1)
    html = re.sub(r'/\*__MATH_START__\*/.*?/\*__MATH_END__\*/',
                  lambda m: '/*__MATH_START__*/\n' + body + '\n/*__MATH_END__*/', html, flags=re.S)
    open(HTML, 'w', encoding='utf-8', newline='').write(html)
    from collections import Counter
    print('MATH_BANK', dict(Counter(x['kind'] for x in bank)), 'total', len(bank))


main()
