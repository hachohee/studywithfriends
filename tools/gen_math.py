#!/usr/bin/env python3
"""초1 2학기 수학 문제 은행(연산/사고력/서술형)을 만들어 index.html 의 MATH_BANK 블록에 넣는다.

   범위(초1 2학기) — 곱셈구구는 넣지 않는다.
     연산  ① 받아올림 없는 (두 자리)+(한 자리)·(두 자리)+(두 자리)
           ② 받아내림 없는 (두 자리)−(한 자리)·(두 자리)−(두 자리)
           ③ 받아올림 있는 (한 자리)+(한 자리) — 10 만들어 더하기
           ④ 받아내림 있는 (십몇)−(한 자리) — 10에서 빼기
           ⑤ 한 자리 수 세 수의 덧셈·뺄셈(결과는 양수)
           ⑥ 쉬운 □ 구하기
     사고력 수 규칙(1·2·5·10씩), 시각(몇 시·몇 시 30분), 어떤 수 거꾸로 구하기,
            작은 수 줄 서기, 수 카드 두 장으로 가장 큰/작은 두 자리 수
     서술형 위 연산 범위 안의 친근한 문장제

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
    cands = []
    for w in list(wrong) + [ans + d for d in (1, -1, 10, -10, 2, -2)]:
        if 0 < w <= 99 and w != ans and w not in cands:
            cands.append(w)
    picks = [ans] + cands[:2]
    rng.shuffle(picks)
    return {'kind': kind, 'q': q, 'opts': [f'{v}{unit}' for v in picks], 'ans': picks.index(ans), 'why': why}


def make_text(rng, q, ans, wrongs, why, kind):
    """보기가 숫자가 아니라 글자일 때(시각 등)."""
    uniq = [ans]
    for w in wrongs:
        if w != ans and w not in uniq:
            uniq.append(w)
    if len(uniq) < 3:
        raise ValueError('보기가 3개가 안 됩니다: ' + q)
    picks = uniq[:3]
    rng.shuffle(picks)
    return {'kind': kind, 'q': q, 'opts': picks, 'ans': picks.index(ans), 'why': why}


def tstr(h, m):
    """몇 시 몇 분 (12시간제, 0시는 12시로)"""
    h = ((h - 1) % 12) + 1
    return f'{h}시 {m}분' if m else f'{h}시'


# ── 수 만들기 도우미 (받아올림·받아내림 없음) ──
def plus_two_one(rng):
    th, on = rng.randint(1, 8), rng.randint(1, 7)
    return th * 10 + on, rng.randint(2, 9 - on)


def plus_two_two(rng):
    ah, ao = rng.randint(1, 8), rng.randint(0, 9)
    bh, bo = rng.randint(1, 9 - ah), rng.randint(0, 9 - ao)
    return ah * 10 + ao, bh * 10 + bo


def minus_two_one(rng):
    th, on = rng.randint(2, 8), rng.randint(3, 9)
    return th * 10 + on, rng.randint(2, on)


def minus_two_two(rng):
    ah, ao = rng.randint(3, 9), rng.randint(0, 9)
    bh = rng.randint(1, ah - 1)
    return ah * 10 + ao, bh * 10 + rng.randint(0, ao)


# ── 연산 ──
def calc(rng, t):
    if t == 0:      # (두 자리) + (한 자리), 받아올림 없음
        a, b = plus_two_one(rng)
        on = a % 10
        why = (f'{a}+{b}={a + b}. 일의 자리끼리 {on}+{b}={on + b}이고 '
               f'십의 자리는 {a // 10} 그대로예요. 받아올림이 없어요.')
        return make(rng, f'{a} + {b} = ?', a + b, why, '연산', wrong=[a + b + 10, a + b - 1])

    if t == 1:      # (두 자리) + (두 자리), 받아올림 없음
        a, b = plus_two_two(rng)
        why = (f'{a}+{b}={a + b}. 십의 자리끼리 {a // 10}+{b // 10}={a // 10 + b // 10}, '
               f'일의 자리끼리 {a % 10}+{b % 10}={a % 10 + b % 10}. 받아올림이 없어요.')
        return make(rng, f'{a} + {b} = ?', a + b, why, '연산', wrong=[a + b + 10, a + b - 10])

    if t == 2:      # (두 자리) − (한 자리), 받아내림 없음
        a, b = minus_two_one(rng)
        why = (f'{a}−{b}={a - b}. 일의 자리 {a % 10}에서 {b}{eul(b)} 빼면 {a % 10 - b}, '
               f'십의 자리는 {a // 10} 그대로예요.')
        return make(rng, f'{a} − {b} = ?', a - b, why, '연산', wrong=[a - b + 10, a - b - 1])

    if t == 3:      # (두 자리) − (두 자리), 받아내림 없음
        a, b = minus_two_two(rng)
        why = (f'{a}−{b}={a - b}. 십의 자리끼리 {a // 10}−{b // 10}={a // 10 - b // 10}, '
               f'일의 자리끼리 {a % 10}−{b % 10}={a % 10 - b % 10}. 받아내림이 없어요.')
        return make(rng, f'{a} − {b} = ?', a - b, why, '연산', wrong=[a - b + 10, a - b - 10])

    if t == 4:      # (한 자리) + (한 자리), 받아올림 — 10 만들어 더하기
        a = rng.randint(5, 9)
        b = rng.randint(11 - a, 9)
        need, rest = 10 - a, b - (10 - a)
        why = (f'{a}+{b}={a + b}. {a}에 {need}{eul(need)} 더하면 10이에요. '
               f'{b}에서 {need}{eul(need)} 떼어 10을 만들고, 남은 {rest}{eul(rest)} 더하면 10+{rest}={a + b}.')
        return make(rng, f'{a} + {b} = ?', a + b, why, '연산', wrong=[a + b - 10, a + b + 1])

    if t == 5:      # (십몇) − (한 자리), 받아내림 — 10에서 빼기
        on = rng.randint(1, 8)
        a, b = 10 + on, rng.randint(on + 1, 9)
        why = (f'{a}−{b}={a - b}. 먼저 10−{b}={10 - b}, '
               f'여기에 남은 {on}{eul(on)} 더하면 {10 - b}+{on}={a - b}.')
        return make(rng, f'{a} − {b} = ?', a - b, why, '연산', wrong=[b - on, 10 - b])

    if t == 6:      # 한 자리 수 세 수
        form = rng.choice(['++', '+-', '-+', '--', '10--'])
        if form == '++':
            a, b, c = rng.randint(2, 6), rng.randint(2, 6), rng.randint(2, 6)
            q, ans = f'{a} + {b} + {c} = ?', a + b + c
            why = f'앞에서부터 차례로: {a}+{b}={a + b}, {a + b}+{c}={ans}.'
        elif form == '+-':
            a = rng.randint(5, 9); b = rng.randint(2, 4); c = rng.randint(2, 5)
            q, ans = f'{a} − {b} + {c} = ?', a - b + c
            why = f'앞에서부터 차례로: {a}−{b}={a - b}, {a - b}+{c}={ans}.'
        elif form == '-+':
            a = rng.randint(6, 9); b = rng.randint(2, 4); c = rng.randint(2, 5)
            q, ans = f'{a} − {b} + {c} = ?', a - b + c
            why = f'앞에서부터 차례로: {a}−{b}={a - b}, {a - b}+{c}={ans}.'
        elif form == '--':
            b = rng.randint(2, 4); c = rng.randint(2, 3)
            a = b + c + rng.randint(1, 4)
            q, ans = f'{a} − {b} − {c} = ?', a - b - c
            why = f'앞에서부터 차례로: {a}−{b}={a - b}, {a - b}−{c}={ans}.'
        else:
            b = rng.randint(2, 4); c = rng.randint(2, 9 - b)
            q, ans = f'10 − {b} − {c} = ?', 10 - b - c
            why = f'앞에서부터 차례로: 10−{b}={10 - b}, {10 - b}−{c}={ans}.'
        return make(rng, q, ans, why, '연산', wrong=[ans + 10, ans - 2])

    # t == 7: 쉬운 □ 구하기
    form = rng.choice(['plus', 'minus', 'front'])
    if form == 'plus':          # □ + a = b
        a = rng.randint(2, 8); b = rng.randint(max(11, a + 3), 18)
        q, ans = f'□ + {a} = {b}  에서 □는?', b - a
        why = f'□ = {b}−{a} = {ans}. 더한 수를 구할 때는 빼요.'
    elif form == 'minus':       # a − □ = b
        b = rng.randint(2, 8); a = rng.randint(max(11, b + 2), 19)
        q, ans = f'{a} − □ = {b}  에서 □는?', a - b
        why = f'□ = {a}−{b} = {ans}.'
    else:                       # □ − a = b
        a = rng.randint(2, 9); b = rng.randint(2, 9)
        q, ans = f'□ − {a} = {b}  에서 □는?', a + b
        why = f'□ = {a}+{b} = {ans}. 뺀 수를 구할 때는 더해요.'
    return make(rng, q, ans, why, '연산', wrong=[ans + 1, ans - 1])


# ── 사고력 ──
def think(rng, t):
    if t == 0:      # 수 규칙 찾기 — 1·2·5·10씩 커지거나 작아지기
        d = rng.choice([1, 2, 5, 10])
        up = rng.random() < .55
        if up:
            s = rng.randint(1, 99 - 4 * d)
            seq = [s + k * d for k in range(5)]
            why = f'{d}씩 커지는 규칙이에요. {seq[3]}+{d}={seq[4]}!'
            wrong = [seq[4] - d, seq[3]]
        else:
            s = rng.randint(4 * d + 1, min(99, 4 * d + 40))
            seq = [s - k * d for k in range(5)]
            why = f'{d}씩 작아지는 규칙이에요. {seq[3]}−{d}={seq[4]}!'
            wrong = [seq[4] + d, seq[3]]
        return make(rng, f'규칙을 찾아 □에 알맞은 수는?  {", ".join(map(str, seq[:4]))}, □',
                    seq[4], why, '사고력', wrong=wrong)

    if t == 1:      # 시각 — 몇 시 · 몇 시 30분
        form = rng.choice(['hour', 'hour30', 'half', 'half30', 'read'])
        if form == 'hour':
            h, k = rng.randint(2, 8), rng.randint(1, 3)
            q, ans = f'지금은 {h}시예요. {k}시간 뒤는 몇 시일까요?', tstr(h + k, 0)
            wrongs = [tstr(h, 0), tstr(h + k + 1, 0), tstr(h + k - 1, 0)]
            why = f'{h}시에서 {k}시간 지나면 {h}+{k}={h + k}시예요.'
        elif form == 'hour30':
            h = rng.randint(2, 9)
            q, ans = f'지금은 {h}시 30분이에요. 1시간 뒤는 몇 시 몇 분일까요?', tstr(h + 1, 30)
            wrongs = [tstr(h, 30), tstr(h + 2, 30), tstr(h + 1, 0)]
            why = f'{h}시 30분에서 1시간 지나면 {h + 1}시 30분이에요. 분은 그대로예요.'
        elif form == 'half':
            h = rng.randint(2, 9)
            q, ans = f'지금은 {h}시예요. 30분 뒤는 몇 시 몇 분일까요?', tstr(h, 30)
            wrongs = [tstr(h + 1, 0), tstr(h, 0), tstr(h + 1, 30)]
            why = f'{h}시에서 30분 지나면 {h}시 30분이에요.'
        elif form == 'half30':
            h = rng.randint(2, 9)
            q, ans = f'지금은 {h}시 30분이에요. 30분 뒤는 몇 시 몇 분일까요?', tstr(h + 1, 0)
            wrongs = [tstr(h, 30), tstr(h + 1, 30), tstr(h, 0)]
            why = f'{h}시 30분에서 30분 지나면 {h + 1}시가 돼요. 분이 0이 되면 정각이에요.'
        else:
            h = rng.randint(1, 9)
            q, ans = f'짧은바늘이 {h}를 가리키고 있어요. 몇 시일까요?', tstr(h, 0)
            wrongs = [tstr(h + 1, 0), tstr(h - 1, 0), tstr(h, 30)]
            why = f'짧은바늘은 시를 가리켜요. {h}를 가리키면 {h}시예요.'
        return make_text(rng, q, ans, wrongs, why, '사고력')

    if t == 2:      # 어떤 수 거꾸로 구하기 (한 자리·십몇 범위)
        if rng.random() < .5:
            x = rng.randint(2, 9)
            k = rng.randint(max(2, 11 - x), 9)
            total = x + k
            q = f'어떤 수에 {k}{eul(k)} 더했더니 {total}{iga(total)} 되었어요. 어떤 수는?'
            why = f'거꾸로 생각해요. {total}−{k}={x}.'
            return make(rng, q, x, why, '사고력', wrong=[x + 2 * k, total + k])
        k = rng.randint(2, 6); x = rng.randint(k + 3, 19)
        q = f'어떤 수에서 {k}{eul(k)} 뺐더니 {x - k}{iga(x - k)} 되었어요. 어떤 수는?'
        why = f'거꾸로 생각해요. {x - k}+{k}={x}.'
        return make(rng, q, x, why, '사고력', wrong=[x - 2 * k, x + k])

    if t == 3:      # 작은 수 줄 서기
        nm, eun, ga = rng.choice(NAMES)
        a, b = rng.randint(2, 7), rng.randint(2, 7)
        q = f'줄을 섰어요. {nm}{eun} 앞에서 {a}번째, 뒤에서 {b}번째예요. 모두 몇 명일까요?'
        why = f'{nm}{ga} 두 번 세어졌어요! {a}+{b}−1={a + b - 1}(명).'
        return make(rng, q, a + b - 1, why, '사고력', '명', wrong=[a + b, a + b - 2])

    # t == 4: 수 카드 두 장으로 가장 큰/작은 두 자리 수
    ds = rng.sample(range(1, 10), 3)
    srt = sorted(ds)
    big = srt[-1] * 10 + srt[-2]
    small = srt[0] * 10 + srt[1]
    if rng.random() < .5:
        q = f'수 카드 {ds[0]}, {ds[1]}, {ds[2]} 중 두 장으로 만들 수 있는 가장 큰 두 자리 수는?'
        why = f'큰 수를 십의 자리에 놓아요. 십의 자리 {srt[-1]}, 일의 자리 {srt[-2]} → {big}!'
        return make(rng, q, big, why, '사고력', wrong=[small, srt[0] * 10 + srt[-1]])
    q = f'수 카드 {ds[0]}, {ds[1]}, {ds[2]} 중 두 장으로 만들 수 있는 가장 작은 두 자리 수는?'
    why = f'작은 수를 십의 자리에 놓아요. 십의 자리 {srt[0]}, 일의 자리 {srt[1]} → {small}!'
    return make(rng, q, small, why, '사고력', wrong=[big, srt[0] * 10 + srt[-1]])


# ── 서술형 ──
_NAME_I = [0]    # 한날 문제끼리 이름이 겹치지 않게 차례로 돌려 쓴다


def word(rng, t):
    nm, eun, ga = NAMES[_NAME_I[0] % len(NAMES)]
    _NAME_I[0] += 1
    ob, oga, oeul, u, ueul = rng.choice(OBJS)

    if t == 0:      # 합치기 — (두 자리)+(한 자리)
        a, b = plus_two_one(rng)
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있고, 동생은 {b}{u}{ueul} 가지고 있어요. 둘이 가진 것은 모두 몇 {u}일까요?'
        return make(rng, q, a + b, f'합치는 문제예요. 식: {a}+{b}={a + b}, 답: {a + b}{u}', '서술형', u, wrong=[abs(a - b)])

    if t == 1:      # 합치기 — (두 자리)+(두 자리)
        a, b = plus_two_two(rng)
        q = f'{nm}{eun} 어제 동화책을 {a}쪽 읽고, 오늘은 {b}쪽 읽었어요. 이틀 동안 모두 몇 쪽 읽었을까요?'
        return make(rng, q, a + b, f'합치는 문제예요. 식: {a}+{b}={a + b}, 답: {a + b}쪽', '서술형', '쪽', wrong=[abs(a - b)])

    if t == 2:      # 덜어내기 — (두 자리)−(한 자리)
        a, b = minus_two_one(rng)
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있었어요. 동생에게 {b}{u}{ueul} 주었어요. 남은 것은 몇 {u}일까요?'
        return make(rng, q, a - b, f'덜어내는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u)

    if t == 3:      # 덜어내기 — (두 자리)−(두 자리)
        a, b = minus_two_two(rng)
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 모았어요. 그중 {b}{u}{ueul} 동생에게 주었어요. 남은 것은 몇 {u}일까요?'
        return make(rng, q, a - b, f'덜어내는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u)

    if t == 4:      # 몇 개 더 많은지 (차이)
        a, b = minus_two_two(rng)
        q = f'{nm}{eun} {ob}{oeul} {a}{u}, 동생은 {b}{u}{ueul} 가지고 있어요. {nm}{ga} 동생보다 몇 {u} 더 많을까요?'
        return make(rng, q, a - b, f'차이를 구하는 문제예요. 식: {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u,
                    wrong=[a + b] if a + b <= 99 else [])

    if t == 5:      # 10 만들어 더하기 (한 자리 + 한 자리)
        a = rng.randint(5, 9); b = rng.randint(11 - a, 9)
        who = rng.choice(['엄마', '아빠', '할머니'])
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있어요. {who}께서 {b}{u}{ueul} 더 주셨어요. 모두 몇 {u}일까요?'
        return make(rng, q, a + b, f'10을 만들어 더해요. {a}+{b}={a + b}, 답: {a + b}{u}', '서술형', u, wrong=[a + b - 10])

    if t == 6:      # 10에서 빼기 (십몇 − 한 자리)
        on = rng.randint(1, 8); a = 10 + on; b = rng.randint(on + 1, 9)
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있었어요. 친구에게 {b}{u}{ueul} 주었어요. 남은 것은 몇 {u}일까요?'
        return make(rng, q, a - b, f'10에서 빼요. {a}−{b}={a - b}, 답: {a - b}{u}', '서술형', u, wrong=[b - on])

    if t == 7:      # 세 수 (한 자리)
        a = rng.randint(6, 9); b = rng.randint(2, 3)
        c = rng.choice([x for x in range(2, 6) if x != b])
        q = f'{nm}{eun} {ob}{oeul} {a}{u} 가지고 있었어요. 동생에게 {b}{u}{ueul} 주고, 엄마께 {c}{u}{ueul} 더 받았어요. 지금은 모두 몇 {u}일까요?'
        return make(rng, q, a - b + c, f'차례로 계산해요. 식: {a}−{b}+{c}={a - b + c}, 답: {a - b + c}{u}', '서술형', u,
                    wrong=[a - b - c])

    # t == 8: 몇 개 더 있어야 하는지 (10이 되는 수)
    need = rng.choice([9, 10]); have = rng.randint(2, need - 3)
    q = f'{nm}{eun} {ob} {need}{u}{ueul} 사려고 해요. 지금 {have}{u}{ueul} 가지고 있어요. 몇 {u} 더 사야 할까요?'
    return make(rng, q, need - have, f'모자란 만큼 더 사요. 식: {need}−{have}={need - have}, 답: {need - have}{u}', '서술형', u,
                wrong=[need + have])


# ── 은행 만들기 ──
QUOTA_CALC = {0: 18, 1: 20, 2: 18, 3: 16, 4: 20, 5: 20, 6: 14, 7: 14}   # 합 140
QUOTA_THINK = {0: 9, 1: 9, 2: 9, 3: 9, 4: 9}                            # 합 45
QUOTA_WORD = {t: 5 for t in range(9)}                                    # 합 45

# 뒤에 덧붙이는 몫(하루치 10문제 = 연산 5 · 사고력 2 · 서술형 3).
# 기존 문제 번호가 바뀌지 않도록 새 시드로 따로 만들어 '맨 뒤'에 붙인다.
EXTRA_CALC = {0: 1, 2: 1, 4: 1, 5: 1, 6: 1}
EXTRA_THINK = {0: 1, 2: 1}
EXTRA_WORD = {0: 1, 4: 1, 8: 1}

# 2026-11-25(수) 하루치 — 앞의 240문제는 그대로 두고 맨 뒤에 10문제를 더 붙인다.
EXTRA2_CALC = {1: 1, 3: 1, 5: 1, 6: 1, 7: 1}
EXTRA2_THINK = {1: 1, 3: 1}
EXTRA2_WORD = {1: 1, 5: 1, 6: 1}

# 2026-11-26(목) 하루치 — 앞의 250문제는 그대로 두고 맨 뒤에 10문제를 더 붙인다.
EXTRA3_CALC = {0: 1, 2: 1, 4: 1, 3: 1, 7: 1}
EXTRA3_THINK = {2: 1, 4: 1}
EXTRA3_WORD = {2: 1, 3: 1, 7: 1}


def fill(rng, fn, quota, seen):
    """종류별로 quota 개씩, 서로 다른 문제를 만들어 둔다."""
    out = {t: [] for t in quota}
    for t, n in quota.items():
        tries = 0
        while len(out[t]) < n:
            tries += 1
            if tries > 5000:
                sys.exit(f'!! {fn.__name__}[{t}] 문제를 {n}개 만들 수 없어요(중복).')
            item = fn(rng, t)
            if item['q'] in seen:
                continue
            seen.add(item['q'])
            out[t].append(item)
    return out


def interleave(banks, order):
    """종류가 골고루 섞이도록 한 문제씩 번갈아 붙인다(하루 5문제가 서로 다른 유형이 되도록)."""
    out, i = [], 0
    while any(banks[t] for t in order):
        t = order[i % len(order)]
        if banks[t]:
            out.append(banks[t].pop(0))
        i += 1
    return out


def build():
    rng = random.Random(20261122)
    _NAME_I[0] = 0
    seen = set()
    calc_b = fill(rng, calc, QUOTA_CALC, seen)
    think_b = fill(rng, think, QUOTA_THINK, seen)
    word_b = fill(rng, word, QUOTA_WORD, seen)
    base = (interleave(calc_b, sorted(calc_b)) +
            interleave(think_b, sorted(think_b)) +
            interleave(word_b, sorted(word_b)))
    # 매일 덧붙이는 몫 — 앞 번호(기존 230문제)는 그대로 두고 뒤에만 붙는다
    rng2 = random.Random(20261124)
    extra = (interleave(fill(rng2, calc, EXTRA_CALC, seen), sorted(EXTRA_CALC)) +
             interleave(fill(rng2, think, EXTRA_THINK, seen), sorted(EXTRA_THINK)) +
             interleave(fill(rng2, word, EXTRA_WORD, seen), sorted(EXTRA_WORD)))
    # 2026-11-25 몫 — 역시 앞 문제 번호는 그대로, 맨 뒤에만 붙는다
    rng3 = random.Random(20261125)
    extra2 = (interleave(fill(rng3, calc, EXTRA2_CALC, seen), sorted(EXTRA2_CALC)) +
              interleave(fill(rng3, think, EXTRA2_THINK, seen), sorted(EXTRA2_THINK)) +
              interleave(fill(rng3, word, EXTRA2_WORD, seen), sorted(EXTRA2_WORD)))
    # 2026-11-26 몫 — 역시 앞 문제 번호는 그대로, 맨 뒤에만 붙는다
    rng4 = random.Random(20261126)
    extra3 = (interleave(fill(rng4, calc, EXTRA3_CALC, seen), sorted(EXTRA3_CALC)) +
              interleave(fill(rng4, think, EXTRA3_THINK, seen), sorted(EXTRA3_THINK)) +
              interleave(fill(rng4, word, EXTRA3_WORD, seen), sorted(EXTRA3_WORD)))
    return base + extra + extra2 + extra3


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
