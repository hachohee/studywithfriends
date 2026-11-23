#!/usr/bin/env python3
"""수학 2~4단계 문제 은행을 만들어 index.html 의 MATH_LEVELS 블록에 넣는다.

   1단계 = tools/gen_math.py 가 만드는 기존 MATH_BANK (초1 2학기) 그대로
   2단계 = 초2 1학기 (받아올림·받아내림 있는 두 자리 계산, 2~5단 곱셈, 5분 단위 시각)
   3단계 = 초2 2학기 ~ 초3 (곱셈구구 전체, 나눗셈, 세 자리 수)
   4단계 = 초4 (두 자리×한 자리, 나머지 있는 나눗셈, 분수·소수, 각도)

   실행: python3 tools/gen_math_levels.py   (같은 시드라 다시 실행해도 같은 결과)
"""
import json, os, random, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')

NAMES = [('민지', '는', '가'), ('서준', '은', '이'), ('지우', '는', '가'), ('하윤', '은', '이'), ('도윤', '은', '이'), ('서아', '는', '가')]
OBJS = [('구슬', '개'), ('사탕', '개'), ('스티커', '장'), ('딱지', '장'), ('색연필', '자루'), ('풍선', '개')]


def has_batchim(n):
    return n % 10 == 0 or n % 10 in (1, 3, 6, 7, 8)


def eul(n):
    return '을' if has_batchim(n) else '를'


def mk(rng, q, ans, why, kind, unit='', wrong=(), maxv=9999, text=False):
    """보기 3개(정답 포함, 위치는 무작위). text=True면 답이 글자(시각·분수·소수)일 때."""
    if text:
        uniq = [ans]
        for w in wrong:
            if w != ans and w not in uniq:
                uniq.append(w)
        if len(uniq) < 3:
            raise ValueError('보기가 3개가 안 됩니다: ' + q)
        picks = uniq[:3]
        rng.shuffle(picks)
        return {'kind': kind, 'q': q, 'opts': picks, 'ans': picks.index(ans), 'why': why}
    cands = []
    for w in list(wrong) + [ans + 1, ans - 1, ans + 10, ans - 10, ans + 2, ans - 2, ans + 100, ans - 100]:
        if 0 < w <= maxv and w != ans and w not in cands:
            cands.append(w)
    if len(cands) < 2:
        raise ValueError('보기가 3개가 안 됩니다: ' + q)
    picks = [ans] + cands[:2]
    rng.shuffle(picks)
    return {'kind': kind, 'q': q, 'opts': [f'{v}{unit}' for v in picks], 'ans': picks.index(ans), 'why': why}


def tstr(h, m):
    h = ((h - 1) % 12) + 1
    return f'{h}시 {m}분' if m else f'{h}시'


# ─────────────────────────── 2단계: 초2 1학기 ───────────────────────────
def calc2(rng, t):
    if t == 0:          # 두 자리 + 두 자리 (받아올림 있음)
        a, b = rng.randint(14, 68), rng.randint(15, 28)
        ans = a + b
        why = f'{a}+{b}={ans}. 일의 자리 {a % 10}+{b % 10}={a % 10 + b % 10}이라 받아올림이 있고, 십의 자리는 {a // 10}+{b // 10}+1={a // 10 + b // 10 + 1}이에요.'
        return mk(rng, f'{a} + {b} = ?', ans, why, '연산', maxv=199, wrong=[a + b + 10, a + b - 10])
    if t == 1:          # 두 자리 − 두 자리 (받아내림 있음)
        a, b = rng.randint(42, 95), rng.randint(13, 38)
        if a <= b:
            a, b = b + 10, a
        ans = a - b
        why = f'{a}−{b}={ans}. 일의 자리에서 뺄 수 없으면 십의 자리에서 10을 받아 내려서 빼요.'
        return mk(rng, f'{a} − {b} = ?', ans, why, '연산', maxv=99, wrong=[a - b + 10, a - b - 10])
    if t == 2:          # 곱셈 2~5단
        a, b = rng.randint(2, 5), rng.randint(2, 9)
        ans = a * b
        why = f'{a}×{b}={ans}. {a}씩 {b}번 더한 것과 같아요. 구구단 {a}단을 떠올려요.'
        return mk(rng, f'{a} × {b} = ?', ans, why, '연산', maxv=99, wrong=[a * b + a, a * b - a])
    if t == 3:          # 두 자리 + 한 자리 (받아올림)
        a, b = rng.randint(15, 88), rng.randint(2, 9)
        if a % 10 + b <= 9:
            a = a - a % 10 + (10 - b + 1)
        ans = a + b
        why = f'{a}+{b}={ans}. 일의 자리 {a % 10}+{b}={a % 10 + b} → 받아올림 1, 십의 자리는 {a // 10}+1={a // 10 + 1}.'
        return mk(rng, f'{a} + {b} = ?', ans, why, '연산', maxv=99, wrong=[a + b - 10, a + b + 10])
    if t == 4:          # 세 수 (덧셈·뺄셈 섞기)
        a, b, c = rng.randint(20, 60), rng.randint(10, 30), rng.randint(5, 19)
        ans = a + b - c
        why = f'앞에서부터 차례로: {a}+{b}={a + b}, {a + b}−{c}={ans}.'
        return mk(rng, f'{a} + {b} − {c} = ?', ans, why, '연산', maxv=199, wrong=[a + b + c, ans + 10])
    # □ 구하기
    a, b = rng.randint(14, 59), rng.randint(41, 98)
    if b <= a:
        b = a + rng.randint(5, 30)
    ans = b - a
    return mk(rng, f'□ + {a} = {b}  에서 □는?', ans, f'더한 수를 구할 때는 빼요. {b}−{a}={ans}.', '연산', maxv=99, wrong=[b + a, ans + 10])


def think2(rng, t):
    if t == 0:          # 규칙
        d, up = rng.choice([3, 4, 6, 7]), rng.random() < .5
        if up:
            s = rng.randint(5, 60)
            seq = [s + k * d for k in range(5)]
            why = f'{d}씩 커지는 규칙이에요. {seq[3]}+{d}={seq[4]}!'
            wrong = [seq[4] - d, seq[3]]
        else:
            s = rng.randint(4 * d + 10, 98)
            seq = [s - k * d for k in range(5)]
            why = f'{d}씩 작아지는 규칙이에요. {seq[3]}−{d}={seq[4]}!'
            wrong = [seq[4] + d, seq[3]]
        return mk(rng, f'규칙을 찾아 □에 알맞은 수는?  {", ".join(map(str, seq[:4]))}, □', seq[4], why, '사고력', maxv=199, wrong=wrong)
    if t == 1:          # 시각 5분 단위
        h, m = rng.randint(1, 9), rng.choice([5, 10, 15, 20, 25, 35, 40, 45])
        k = rng.choice([10, 15, 20, 25, 30])
        total = h * 60 + m + k
        nh, nm = (total // 60) % 12, total % 60
        ans = tstr(nh if nh else 12, nm)
        q = f'지금은 {h}시 {m}분이에요. {k}분 뒤는 몇 시 몇 분일까요?'
        wrong = [tstr(h, m + k if m + k < 60 else m + k - 60), tstr(h + 1, m), tstr(h, m)]
        why = f'{m}분에서 {k}분이 지나면 {m + k}분이에요. {"60분이 넘어 1시간이 돼요. " if m + k >= 60 else ""}그래서 {ans}예요.'
        return mk(rng, q, ans, why, '사고력', text=True, wrong=wrong)
    if t == 2:          # 거꾸로 구하기
        x, k = rng.randint(20, 60), rng.randint(11, 30)
        total = x + k
        q = f'어떤 수에 {k}{eul(k)} 더했더니 {total}이 되었어요. 어떤 수는?'
        return mk(rng, q, x, f'거꾸로 생각해요. {total}−{k}={x}.', '사고력', maxv=99, wrong=[total + k, x + 10])
    # 줄 서기
    nm, eun, ga = rng.choice(NAMES)
    a, b = rng.randint(3, 9), rng.randint(4, 11)
    return mk(rng, f'줄을 섰어요. {nm}{eun} 앞에서 {a}번째, 뒤에서 {b}번째예요. 모두 몇 명일까요?',
              a + b - 1, f'{nm}{ga} 두 번 세어졌어요! {a}+{b}−1={a + b - 1}(명).', '사고력', '명', maxv=40, wrong=[a + b, a + b - 2])


def word2(rng, t):
    nm, eun, ga = rng.choice(NAMES)
    ob, u = rng.choice(OBJS)
    if t == 0:
        a, b = rng.randint(24, 58), rng.randint(17, 39)
        return mk(rng, f'{nm}{eun} {ob} {a}{u}{eul(a)} 가지고 있고, 동생은 {b}{u}{eul(b)} 가지고 있어요. 둘이 가진 것은 모두 몇 {u}일까요?',
                  a + b, f'합치는 문제예요. 식: {a}+{b}={a + b}, 답: {a + b}{u}', '서술형', u, maxv=199, wrong=[abs(a - b)])
    if t == 1:
        a, b = rng.randint(52, 94), rng.randint(18, 47)
        return mk(rng, f'{nm}{eun} {ob} {a}{u}{eul(a)} 모았어요. 그중 {b}{u}{eul(b)} 동생에게 주었어요. 남은 것은 몇 {u}일까요?',
                  a - b, f'덜어내는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, maxv=99)
    if t == 2:
        a, b = rng.randint(3, 9), rng.randint(3, 9)
        return mk(rng, f'한 봉지에 {ob} {a}{u}씩 들어 있어요. {b}봉지에는 모두 몇 {u}일까요?',
                  a * b, f'똑같은 것이 {b}묶음이에요. 식: {a}×{b}={a * b}, 답: {a * b}{u}', '서술형', u, maxv=99, wrong=[a + b])
    a, b = rng.randint(45, 92), rng.randint(12, 40)
    return mk(rng, f'{nm}{eun} {ob} {a}{u}, 동생은 {b}{u}{eul(b)} 가지고 있어요. {nm}{ga} 동생보다 몇 {u} 더 많을까요?',
              a - b, f'차이를 구하는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, maxv=99, wrong=[a + b])


# ─────────────────────────── 3단계: 초2 2학기 ~ 초3 ───────────────────────────
def calc3(rng, t):
    if t == 0:          # 세 자리 + 두 자리
        a, b = rng.randint(120, 780), rng.randint(23, 190)
        ans = a + b
        return mk(rng, f'{a} + {b} = ?', ans, f'{a}+{b}={ans}. 백의 자리부터 같은 자리끼리 더해요.', '연산', maxv=999, wrong=[ans + 100, ans - 10])
    if t == 1:          # 세 자리 − 두 자리
        a, b = rng.randint(320, 960), rng.randint(45, 290)
        ans = a - b
        return mk(rng, f'{a} − {b} = ?', ans, f'{a}−{b}={ans}. 같은 자리끼리 빼고, 모자라면 윗자리에서 10을 받아 내려요.', '연산', maxv=999, wrong=[ans + 100, ans - 10])
    if t == 2:          # 곱셈 6~9단
        a, b = rng.randint(6, 9), rng.randint(2, 9)
        ans = a * b
        return mk(rng, f'{a} × {b} = ?', ans, f'{a}×{b}={ans}. {a}단 구구를 떠올려요.', '연산', maxv=99)
    if t == 3:          # 나눗셈 (나누어떨어짐)
        b = rng.randint(2, 9); q = rng.randint(2, 9)
        a = b * q
        return mk(rng, f'{a} ÷ {b} = ?', q, f'{a}÷{b}={q}. {b}×{q}={a}이니까 {a} 안에 {b}가 {q}번 들어가요.', '연산', maxv=20, wrong=[a - b, q + 1])
    if t == 4:          # □ × a = b
        a, q = rng.randint(2, 9), rng.randint(2, 9)
        return mk(rng, f'□ × {a} = {a * q}  에서 □는?', q, f'곱해서 {a * q}가 되는 수예요. {a * q}÷{a}={q}.', '연산', maxv=20, wrong=[a * q, q + 1])
    # 세 수 (곱셈이 섞인 계산)
    a, b, c = rng.randint(2, 5), rng.randint(2, 5), rng.randint(2, 9)
    return mk(rng, f'{a} × {b} + {c} = ?', a * b + c, f'곱셈을 먼저 해요. {a}×{b}={a * b}, {a * b}+{c}={a * b + c}.', '연산', maxv=99)


def think3(rng, t):
    if t == 0:          # 2배씩 커지는 규칙
        s = rng.randint(1, 9)
        seq = [s * (2 ** k) for k in range(5)]
        return mk(rng, f'규칙을 찾아 □에 알맞은 수는?  {", ".join(map(str, seq[:4]))}, □', seq[4],
                  f'앞의 수에 2를 곱하는 규칙이에요. {seq[3]}×2={seq[4]}!', '사고력', maxv=200, wrong=[seq[4] + 2, seq[3] + 2])
    if t == 1:          # 시각 (몇 시간 몇 분 뒤)
        h, m = rng.randint(1, 9), rng.choice([10, 20, 30, 40, 50])
        k = rng.choice([40, 50, 70, 80, 90])
        total = h * 60 + m + k
        ans = tstr(total // 60, total % 60)
        q = f'지금은 {h}시 {m}분이에요. {k}분 뒤는 몇 시 몇 분일까요?'
        wrong = [tstr(h + 1, m), tstr(h + k // 60, (m + k % 60) % 60), tstr(h, m)]
        return mk(rng, q, ans, f'{k}분은 {k // 60}시간 {k % 60}분이에요. {h}시 {m}분에서 {k // 60}시간 {k % 60}분 뒤는 {ans}예요.', '사고력', text=True, wrong=wrong)
    if t == 2:          # 수 카드 세 장으로 가장 큰 세 자리 수
        ds = rng.sample(range(1, 10), 3)
        big = int(''.join(map(str, sorted(ds, reverse=True))))
        return mk(rng, f'수 카드 {ds[0]}, {ds[1]}, {ds[2]}를 한 번씩 써서 만들 수 있는 가장 큰 세 자리 수는?', big,
                  f'큰 수부터 백·십·일의 자리에 놓아요. {sorted(ds, reverse=True)} → {big}.', '사고력', maxv=999,
                  wrong=[int(''.join(map(str, sorted(ds))))])
    # 거꾸로 곱셈
    a, q = rng.randint(3, 8), rng.randint(3, 9)
    return mk(rng, f'어떤 수에 {a}{eul(a)} 곱했더니 {a * q}이 되었어요. 어떤 수는?', q,
              f'거꾸로 나누어요. {a * q}÷{a}={q}.', '사고력', maxv=50, wrong=[a * q, q + 1])


def word3(rng, t):
    nm, eun, ga = rng.choice(NAMES)
    ob, u = rng.choice(OBJS)
    if t == 0:
        a, b = rng.randint(3, 9), rng.randint(3, 9)
        return mk(rng, f'{nm}{eun} 한 줄에 {a}명씩 {b}줄로 앉았어요. 모두 몇 명일까요?', a * b,
                  f'{a}명이 {b}줄이에요. 식: {a}×{b}={a * b}, 답: {a * b}명', '서술형', '명', maxv=99, wrong=[a + b])
    if t == 1:
        b, q = rng.randint(2, 6), rng.randint(2, 8)
        a = b * q
        return mk(rng, f'{ob} {a}{u}{eul(a)} {b}명이 똑같이 나누어 가졌어요. 한 명은 몇 {u}씩 가질까요?', q,
                  f'똑같이 나누는 문제예요. 식: {a}÷{b}={q}, 답: {q}{u}', '서술형', u, maxv=20, wrong=[a - b])
    if t == 2:
        a, b = rng.randint(140, 390), rng.randint(120, 260)
        return mk(rng, f'도서관에 책이 {a}권 있었어요. 오늘 {b}권을 더 들여왔어요. 지금은 몇 권일까요?', a + b,
                  f'합치는 문제예요. 식: {a}+{b}={a + b}, 답: {a + b}권', '서술형', '권', maxv=999)
    a, b = rng.randint(48, 96), rng.randint(13, 45)
    return mk(rng, f'가게에 {ob} {a}{u} 있었어요. 오전에 {b}{u}{eul(b)} 팔았어요. 남은 것은 몇 {u}일까요?', a - b,
              f'덜어내는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, maxv=99)


# ─────────────────────────── 4단계: 초4 ───────────────────────────
def calc4(rng, t):
    if t == 0:          # 두 자리 × 한 자리
        a, b = rng.randint(12, 49), rng.randint(3, 9)
        ans = a * b
        return mk(rng, f'{a} × {b} = ?', ans, f'{a}×{b}={ans}. 십의 자리와 일의 자리를 따로 곱해 더해요.', '연산', maxv=999, wrong=[ans + 10, ans - 10])
    if t == 1:          # 나머지 있는 나눗셈
        b = rng.randint(3, 9); q = rng.randint(2, 8); r = rng.randint(1, b - 1)
        a = b * q + r
        if rng.random() < .5:
            return mk(rng, f'{a} ÷ {b}의 나머지는?', r, f'{b}×{q}={b * q}, {a}−{b * q}={r}. 나머지는 {r}이에요.', '연산', maxv=20, wrong=[q, r + 1 if r + 1 < b else r - 1, b])
        return mk(rng, f'{a} ÷ {b}의 몫은?', q, f'{b}×{q}={b * q}이고 {a}보다 크지 않아요. 몫은 {q}, 나머지는 {r}.', '연산', maxv=20, wrong=[q + 1, r, q - 1])
    if t == 2:          # 소수 덧셈
        a = rng.randint(1, 8) + rng.randint(1, 9) / 10
        b = rng.randint(1, 8) + rng.randint(1, 9) / 10
        ans = round(a + b, 1)
        ans_s = f'{ans:.1f}'
        wrong = [f'{round(ans + 1, 1):.1f}', f'{round(ans - 0.1, 1):.1f}', f'{round(a + b + 0.9, 1):.1f}']
        return mk(rng, f'{a:.1f} + {b:.1f} = ?', ans_s, f'소수점 자리를 맞춰 더해요. {a:.1f}+{b:.1f}={ans_s}.', '연산', text=True, wrong=wrong)
    if t == 3:          # 세 자리 × 한 자리
        a, b = rng.randint(102, 320), rng.randint(2, 6)
        ans = a * b
        return mk(rng, f'{a} × {b} = ?', ans, f'{a}×{b}={ans}. 일의 자리부터 차례로 곱하고 자리를 맞춰요.', '연산', maxv=2000, wrong=[ans + 100, ans - 10])
    # 분수 비교
    pairs = [('1/2', '1/3', '1/2'), ('1/3', '1/4', '1/3'), ('2/3', '1/3', '2/3'), ('1/4', '1/5', '1/4'), ('3/4', '1/2', '3/4'),
             ('2/5', '1/5', '2/5'), ('3/5', '1/5', '3/5'), ('1/2', '1/4', '1/2'), ('1/3', '1/6', '1/3'), ('7/8', '3/8', '7/8'),
             ('5/7', '2/7', '5/7'), ('4/9', '2/9', '4/9'), ('3/4', '1/2', '3/4'), ('8/9', '2/9', '8/9'), ('5/8', '3/8', '5/8')]
    a, b, ans = rng.choice(pairs)
    return mk(rng, f'{a}과 {b} 중 더 큰 분수는?', ans, f'같은 것을 나눌 때 조각 수가 적을수록 한 조각이 커요. 그래서 {ans}이 더 커요.', '연산', text=True, wrong=[b, '같다'])


def think4(rng, t):
    if t == 0:          # 2배·3배 규칙
        s, m = rng.randint(1, 4), rng.choice([2, 3])
        seq = [s * (m ** k) for k in range(5)]
        return mk(rng, f'규칙을 찾아 □에 알맞은 수는?  {", ".join(map(str, seq[:4]))}, □', seq[4],
                  f'앞의 수에 {m}을 곱하는 규칙이에요. {seq[3]}×{m}={seq[4]}!', '사고력', maxv=500, wrong=[seq[4] + m, seq[3] * 2])
    if t == 1:          # 시간 계산
        h, m = rng.randint(1, 9), rng.choice([5, 15, 25, 35, 45])
        k = rng.choice([95, 100, 105, 110, 120])
        total = h * 60 + m + k
        ans = tstr(total // 60, total % 60)
        q = f'지금은 {h}시 {m}분이에요. {k}분 뒤는 몇 시 몇 분일까요?'
        wrong = [tstr(h + 1, m), tstr(h + 2, (m + 30) % 60), tstr(h, m)]
        return mk(rng, q, ans, f'{k}분은 1시간 {k - 60}분이에요. {h}시 {m}분에서 1시간 {k - 60}분 뒤는 {ans}예요.', '사고력', text=True, wrong=wrong)
    if t == 2:          # 각도
        q, ans, wrong = rng.choice([
            ('직각은 몇 도일까요?', '90도', ['180도', '45도', '360도']),
            ('한 바퀴는 몇 도일까요?', '360도', ['180도', '90도', '270도']),
            ('직선은 몇 도일까요?', '180도', ['90도', '360도', '45도']),
            ('반 바퀴는 몇 도일까요?', '180도', ['90도', '360도', '45도']),
            ('직각의 두 배는 몇 도일까요?', '180도', ['90도', '270도', '360도']),
            ('직각의 네 배는 몇 도일까요?', '360도', ['180도', '90도', '270도']),
        ])
        return mk(rng, q, ans, f'{ans}가 맞아요. 직각은 90도, 직선은 180도, 한 바퀴는 360도예요.', '사고력', text=True, wrong=wrong)
    # 큰 수 비교
    xs = rng.sample(range(100, 999), 3)
    big = max(xs)
    return mk(rng, f'{xs[0]}, {xs[1]}, {xs[2]} 중 가장 큰 수는?', big, f'백의 자리부터 비교해요. {big}이 가장 커요.', '사고력', maxv=999, wrong=[min(xs), sorted(xs)[1]])


def word4(rng, t):
    nm, eun, ga = rng.choice(NAMES)
    ob, u = rng.choice(OBJS)
    if t == 0:
        a, b, c = rng.randint(12, 24), rng.randint(3, 6), rng.randint(5, 15)
        return mk(rng, f'{nm}{eun} 한 상자에 {ob} {a}{u}씩 {b}상자를 준비했어요. 그중 {c}{u}{eul(c)} 친구에게 나눠 주었어요. 남은 것은 몇 {u}일까요?',
                  a * b - c, f'곱한 뒤 빼요. 식: {a}×{b}−{c}={a * b - c}, 답: {a * b - c}{u}', '서술형', u, maxv=500, wrong=[a * b + c])
    if t == 1:
        b, q, r = rng.randint(3, 6), rng.randint(4, 8), rng.randint(1, 3)
        a = b * q + r
        return mk(rng, f'{ob} {a}{u}{eul(a)} {b}명이 똑같이 나누면 남는 {u}은 몇 {u}일까요?',
                  r, f'{a}÷{b}={q} 나머지 {r}. 한 명이 {q}{u}씩 가지고 {r}{u}이 남아요.', '서술형', u, maxv=20, wrong=[q])
    if t == 2:
        a = rng.randint(11, 29) / 10
        b = rng.randint(11, 29) / 10
        ans = f'{round(a + b, 1):.1f}L'
        return mk(rng, f'물 {a:.1f}L와 주스 {b:.1f}L를 한 통에 부었어요. 모두 몇 L일까요?', ans,
                  f'소수점을 맞춰 더해요. {a:.1f}+{b:.1f}={round(a + b, 1):.1f}, 답: {ans}', '서술형', text=True,
                  wrong=[f'{round(a + b + 1, 1):.1f}L', f'{round(a + b - 0.1, 1):.1f}L', f'{round(a + b + 2, 1):.1f}L'])
    a, b = rng.randint(2, 5), rng.randint(20, 45)
    return mk(rng, f'버스가 한 번에 {b}명씩 태울 수 있어요. {a * b}명이 타려면 버스가 몇 번 와야 할까요?', a,
              f'{a * b}÷{b}={a}. 버스가 {a}번 와야 해요.', '서술형', '번', maxv=20, wrong=[a + 1, b])


QUOTA = {'연산': 12, '사고력': 4, '서술형': 4}   # 단계마다 20문제 × 4유형 순환


def fill(rng, fn, quota, seen):
    out = {k: [] for k in quota}
    for kind, (types, n) in quota.items():
        for t in types:
            tries = 0
            while sum(1 for x in out[kind] if x.get('_t') == t) < n:
                tries += 1
                if tries > 3000:
                    sys.exit(f'!! {fn.__name__}[{t}] 문제를 만들 수 없어요(중복).')
                item = fn(rng, t)
                if item['q'] in seen:
                    continue
                seen.add(item['q'])
                item['_t'] = t
                out[kind].append(item)
    for kind in out:
        for x in out[kind]:
            x.pop('_t', None)
    return out


def interleave(banks, order):
    out, i = [], 0
    while any(banks[t] for t in order):
        t = order[i % len(order)]
        if banks[t]:
            out.append(banks[t].pop(0))
        i += 1
    return out


def build_level(lv):
    rng = random.Random(20261123 + lv * 97)
    seen = set()
    calc_fn, think_fn, word_fn = {2: (calc2, think2, word2), 3: (calc3, think3, word3), 4: (calc4, think4, word4)}[lv]
    n_types = {2: (6, 4, 4), 3: (6, 4, 4), 4: (5, 4, 4)}[lv]
    banks = {
        '연산': fill(rng, calc_fn, {'연산': (list(range(n_types[0])), 14)}, seen)['연산'],
        '사고력': fill(rng, think_fn, {'사고력': (list(range(n_types[1])), 4)}, seen)['사고력'],
        '서술형': fill(rng, word_fn, {'서술형': (list(range(n_types[2])), 4)}, seen)['서술형'],
    }
    return (interleave({'연산': banks['연산']}, ['연산']) +
            interleave({'사고력': banks['사고력']}, ['사고력']) +
            interleave({'서술형': banks['서술형']}, ['서술형']))


def main():
    levels = {str(lv): build_level(lv) for lv in (2, 3, 4)}
    html = open(HTML, encoding='utf-8').read()
    if '/*__MATHL_START__*/' not in html:
        print('!! MATHL 마커가 없습니다.', file=sys.stderr); sys.exit(1)
    body = 'const MATH_LEVELS = ' + json.dumps(levels, ensure_ascii=False, separators=(',', ':')) + ';'
    html = re.sub(r'/\*__MATHL_START__\*/.*?/\*__MATHL_END__\*/',
                  lambda m: '/*__MATHL_START__*/\n' + body + '\n/*__MATHL_END__*/', html, flags=re.S)
    open(HTML, 'w', encoding='utf-8', newline='').write(html)
    from collections import Counter
    print('MATH_LEVELS', {k: dict(Counter(x['kind'] for x in v)) for k, v in levels.items()})


main()
