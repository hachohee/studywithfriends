#!/usr/bin/env python3
"""2026-11-27(금) 하루치 — 한자 세트(hj1-9)·예쁘게 말하기(sp1-10)·영어 Step 12를 덧붙인다.

   실행: python3 tools/add_day_20261127_extra.py   (이미 들어 있으면 아무 것도 하지 않는다)
   끝난 뒤 python3 tools/build.py (한자·말하기 반영) 를 실행한다.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANJA = os.path.join(ROOT, 'data', 'hanja.json')
SPEAK = os.path.join(ROOT, 'data', 'levels_speak.json')
HTML = os.path.join(ROOT, 'index.html')

HANJA_SET = {
    'id': 'hj1-9',
    'title': '백, 천, 만',
    'topic': '큰 수를 세는 한자 百 千 万',
    'essay': (
        '옛날 사람들은 수가 커지면 새 글자를 만들었어요. 열이 열 번 모이면 백, 백이 열 번 모이면 천, 천이 열 번 모이면 만이 되지요. '
        '이 큰 수를 쓸 때 百(일백 백), 千(일천 천), 万(일만 만)을 써요.\n\n'
        '百은 흰 백(白)이 부수이고, 千은 열 십(十)이 부수예요. 万은 한 일(一)이 부수예요. '
        '부수를 알면 그 글자가 어떤 뜻과 이어지는지 짐작할 수 있어요.\n\n'
        '우리 생활에도 이 글자가 숨어 있어요. 가게에서 백 원은 百 원, 천 원은 千 원, 만 원은 万 원이라고 써요. '
        '백성(百姓)은 나라를 이루는 사람들이고, 만세(萬歲)는 오래오래 건강하게 살라는 기쁜 인사예요.\n\n'
        '큰 수를 한자로 익혀 두면 시장 간판이나 물건값을 볼 때 훨씬 빨리 알 수 있어요. 오늘 배운 세 글자로 백에서 만까지 세어 보세요.'
    ),
    'vocab': [{'w': '부수', 'm': '글자의 뜻을 알려 주는 부분'},
              {'w': '간판', 'm': '가게 이름이나 물건 이름을 적어 붙인 판'}],
    'key': '百(일백 백) · 千(일천 천) · 万(일만 만) — 열 번씩 모이면 다음 큰 수!',
    'chars': [
        {'c': '百', 'eum': '백', 'hun': '일백', 'bushu': '白', 'bushu_name': '흰 백',
         'strokes': [[28, 20, 74, 20], [52, 22, 46, 32], [46, 32, 46, 78],
                     [46, 36, 72, 36, 72, 78], [48, 54, 70, 54], [42, 78, 74, 78]],
         'steps': ['맨 위에 긴 가로획을 그어요.', '그 아래에서 왼쪽 아래로 짧게 삐쳐요.',
                   '삐침 끝에서 아래로 세로획을 그어요.', '위쪽 가로획을 긋고 오른쪽에서 아래로 꺾어 내려요.',
                   '가운데에 짧은 가로획을 그어요.', '맨 아래에 긴 가로획으로 닫아요.'],
         'words': [{'w': '백성', 'm': '百姓 · 나라를 이루는 사람들'}, {'w': '백년', 'm': '百年 · 백 해'}],
         'sentence': '백 원은 한자로 百 원이라고 써요.'},
        {'c': '千', 'eum': '천', 'hun': '일천', 'bushu': '十', 'bushu_name': '열 십',
         'strokes': [[58, 16, 44, 26], [22, 34, 78, 34], [50, 34, 50, 84]],
         'steps': ['위에서 왼쪽 아래로 짧게 삐쳐요.', '가로로 길게 그어요.', '가운데에서 아래로 세로획을 길게 그어요.'],
         'words': [{'w': '천리', 'm': '千里 · 천 리나 되는 먼 길'}, {'w': '천만', 'm': '千萬 · 아주 많은 수'}],
         'sentence': '천 원은 한자로 千 원이라고 써요.'},
        {'c': '万', 'eum': '만', 'hun': '일만', 'bushu': '一', 'bushu_name': '한 일',
         'strokes': [[20, 24, 80, 24], [22, 42, 58, 42, 58, 76, 50, 72], [78, 32, 34, 84]],
         'steps': ['맨 위에 가로획을 그어요.', '가운데에서 오른쪽으로 갔다가 아래로 꺾어 갈고리처럼 맺어요.',
                   '오른쪽 위에서 왼쪽 아래로 길게 삐쳐요.'],
         'words': [{'w': '만세', 'm': '萬歲 · 오래오래 건강하게 살라는 기쁜 인사'}, {'w': '만원', 'm': '萬圓 · 만 원'}],
         'sentence': '만 원은 한자로 万 원이라고 써요.'},
    ],
    'quiz': [
        {'q': '읽기 글에서 천 원을 한자로 쓰면 어떻게 쓸까요?', 'opts': ['千 원', '百 원', '万 원'], 'ans': 0,
         'why': '읽기 글에 천 원은 千 원이라고 쓴다고 나와요.'},
        {'q': '읽기 글에서 百의 부수는 무엇인가요?', 'opts': ['흰 백(白)', '열 십(十)', '한 일(一)'], 'ans': 0,
         'why': '읽기 글에 百은 흰 백(白)이 부수라고 나와요.'},
        {'q': "읽기 글에서 '만세'를 한자로 쓰면 무엇인가요?", 'opts': ['萬歲', '百姓', '千里'], 'ans': 0,
         'why': '읽기 글에 만세(萬歲)는 오래오래 건강하게 살라는 기쁜 인사라고 나와요.'},
    ],
}

SPEAK_SIT = {
    'id': 'sp1-10',
    'scene': '학교',
    'emoji': '📚',
    'title': '친구가 숙제를 베끼게 해 달라고 해요',
    'situation': '아침에 친구가 다가와서 "네 숙제 좀 보여 줘. 그냥 베끼게만 해 줘." 하고 말했어요.',
    'q': '이럴 때 뭐라고 말하면 좋을까요?',
    'opts': [
        '같이 풀어 보자. 내 답을 그대로 베끼면 너도 나도 배우는 게 없어.',
        '알았어, 그냥 다 베껴 가.',
        '싫어! 너는 왜 숙제를 안 했어?'
    ],
    'ans': 0,
    'why': '숙제를 베끼면 친구는 오늘 배울 것을 놓치고, 선생님은 친구가 할 수 있는 줄 잘못 알게 돼요. '
           '거절하되 함께 푸는 방법을 내밀면 친구는 미안해하지 않고 도움을 받을 수 있어요. '
           '그냥 베껴 주면 둘 다 손해이고, 화난 말로 거절하면 친구 마음만 상해요.',
    'say': '같이 풀어 보자. 내 답을 그대로 베끼면 너도 나도 배우는 게 없어.',
    'tip': '거절할 때는 ①따뜻하게 시작 ②왜 어려운지 ③대신 같이 할 일 순서로 말하면 마음이 상하지 않아요.',
}

STEP12_BLOCK = '''  {
    id: 's12', name: 'Step 12', short: '12 집에서', title: '집에서 쓰는 말', hint: '집 안에서 자주 하는 부탁과 말',
    sentences: [
      { en: "Let's wash our hands.", ko: '손을 씻자.', tip: '렛츠-워시-아우어-핸즈 · our는 "우리"', emoji: '🧼' },
      { en: 'Can I have some water?', ko: '물 좀 마셔도 돼요?', tip: '캔-아이-해브-썸-워터 · 부탁할 때 쓰는 말', emoji: '💧' },
      { en: 'The cat is sleeping.', ko: '고양이가 자고 있어.', tip: '더-캣-이즈-슬리핑 · is ~ing는 "~하는 중"', emoji: '🐱' }
    ]
  }'''


def main():
    # 1) 한자 세트
    d = json.load(open(HANJA, encoding='utf-8'))
    sets = d['levels']['1']['sets']
    if any(s['id'] == HANJA_SET['id'] for s in sets):
        print('한자 세트 이미 있음')
    else:
        sets.append(HANJA_SET)
        json.dump(d, open(HANJA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('한자 세트 추가 —', len(sets), '세트')

    # 2) 예쁘게 말하기
    s = json.load(open(SPEAK, encoding='utf-8'))
    arr = s['speak']['1']
    if any(x['id'] == SPEAK_SIT['id'] for x in arr):
        print('말하기 상황 이미 있음')
    else:
        arr.append(SPEAK_SIT)
        json.dump(s, open(SPEAK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('말하기 상황 추가 —', len(arr), '상황')

    # 3) 영어 Step 12
    html = open(HTML, encoding='utf-8').read()
    if "id: 's12'" in html:
        print('영어 Step 12 이미 있음')
    else:
        old_tail = "emoji: '⛄' }\n    ]\n  }\n];\n\nconst SUBJECTS = ["
        new_tail = "emoji: '⛄' }\n    ]\n  },\n" + STEP12_BLOCK + "\n];\n\nconst SUBJECTS = ["
        assert old_tail in html, 'ENGLISH_STEPS 끝(Step 11)을 찾지 못했어요'
        html = html.replace(old_tail, new_tail, 1)
        open(HTML, 'w', encoding='utf-8', newline='').write(html)
        print('영어 Step 12 추가')


main()
