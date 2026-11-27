#!/usr/bin/env python3
"""2026-11-28(토) 하루치 — 한자 세트(hj1-10)·예쁘게 말하기(sp1-11)·영어 Step 13을 덧붙인다.

   실행: python3 tools/add_day_20261128_extra.py   (이미 들어 있으면 아무 것도 하지 않는다)
   끝난 뒤 python3 tools/build.py (한자·말하기 반영) 를 실행한다.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANJA = os.path.join(ROOT, 'data', 'hanja.json')
SPEAK = os.path.join(ROOT, 'data', 'levels_speak.json')
HTML = os.path.join(ROOT, 'index.html')

HANJA_SET = {
    'id': 'hj1-10',
    'title': '다섯, 여섯, 일곱',
    'topic': '숫자를 세는 한자 五 六 七',
    'essay': (
        '우리는 숫자를 셀 때 한자도 함께 써요. 다섯은 五(다섯 오), 여섯은 六(여섯 육), 일곱은 七(일곱 칠)이라고 써요.\n\n'
        '五는 가로획 두 개와 세로획, 꺾어 내리는 획으로 이루어져 있어요. 六은 위의 점 하나와 가로획, 아래의 삐침과 점으로 되어 있고, '
        '七은 가로획 하나와 갈고리처럼 꺾어 내리는 획 하나로 아주 간단해요.\n\n'
        '달력에도 이 글자가 숨어 있어요. 오월은 五月, 유월은 六月, 칠월은 七月이라고 쓰지요. 주사위에서 다섯 눈이 나왔을 때도 五라고 적어요.\n\n'
        '오늘 배운 五 六 七을 손가락으로 공중에 크게 써 보세요. 몇 획인지 세면서 쓰면 더 잘 기억나요.'
    ),
    'vocab': [{'w': '주사위', 'm': '던져서 나온 눈의 수로 노는 작은 정육면체'},
              {'w': '획', 'm': '글자를 이루는 한 번의 선'}],
    'key': '五(다섯 오) · 六(여섯 육) · 七(일곱 칠) — 달력과 주사위에 숨어 있는 숫자 한자!',
    'chars': [
        {'c': '五', 'eum': '오', 'hun': '다섯', 'bushu': '二', 'bushu_name': '두 이',
         'strokes': [[22, 18, 78, 18], [50, 18, 50, 44], [26, 44, 72, 44, 72, 74], [20, 74, 80, 74]],
         'steps': ['맨 위에 긴 가로획을 그어요.', '가운데에서 아래로 세로획을 내려요.',
                   '가로획을 긋고 오른쪽에서 아래로 꺾어 내려요.', '맨 아래에 긴 가로획으로 닫아요.'],
         'words': [{'w': '오월', 'm': '五月 · 한 해의 다섯째 달'}, {'w': '오십', 'm': '五十 · 쉰'}],
         'sentence': '오월은 한자로 五月이라고 써요.'},
        {'c': '六', 'eum': '육', 'hun': '여섯', 'bushu': '八', 'bushu_name': '여덟 팔',
         'strokes': [[52, 12, 48, 24], [22, 32, 80, 32], [54, 38, 26, 82], [58, 48, 78, 78]],
         'steps': ['가운데 위에 짧은 점을 찍어요.', '그 아래에 가로획을 길게 그어요.',
                   '가운데에서 왼쪽 아래로 삐쳐 내려요.', '오른쪽에 짧은 점을 찍어 내려요.'],
         'words': [{'w': '유월', 'm': '六月 · 한 해의 여섯째 달'}, {'w': '육십', 'm': '六十 · 예순'}],
         'sentence': '유월은 한자로 六月이라고 써요.'},
        {'c': '七', 'eum': '칠', 'hun': '일곱', 'bushu': '一', 'bushu_name': '한 일',
         'strokes': [[18, 30, 82, 26], [62, 14, 62, 62, 50, 78, 40, 74]],
         'steps': ['가로획을 살짝 올라가게 그어요.', '위에서 아래로 내려오다가 왼쪽으로 갈고리처럼 꺾어요.'],
         'words': [{'w': '칠월', 'm': '七月 · 한 해의 일곱째 달'}, {'w': '칠십', 'm': '七十 · 일흔'}],
         'sentence': '칠월은 한자로 七月이라고 써요.'},
    ],
    'quiz': [
        {'q': '읽기 글에서 다섯을 한자로 쓰면 무엇인가요?', 'opts': ['五', '六', '七'], 'ans': 0,
         'why': '읽기 글에 다섯은 五(다섯 오)라고 쓴다고 나와요.'},
        {'q': '읽기 글에서 유월을 한자로 쓰면 어떻게 쓸까요?', 'opts': ['六月', '五月', '七月'], 'ans': 0,
         'why': '읽기 글에 유월은 六月이라고 쓴다고 나와요.'},
        {'q': '한자 카드에서 五의 부수는 무엇인가요?', 'opts': ['두 이', '여덟 팔', '한 일'], 'ans': 0,
         'why': '한자 카드에 五의 부수가 두 이(二)라고 나와요.'},
    ],
}

SPEAK_SIT = {
    'id': 'sp1-11',
    'scene': '가게',
    'emoji': '🛒',
    'title': '마트에서 물건이 어디 있는지 물어요',
    'situation': '마트에서 사고 싶은 딸기 잼을 찾지 못했어요. 마침 점원 아저씨가 지나가세요.',
    'q': '이럴 때 뭐라고 말하면 좋을까요?',
    'opts': [
        '실례지만, 딸기 잼은 어느 쪽에 있나요?',
        '야, 딸기 잼 어디 있어요? 빨리 찾아 주세요.',
        '아무 말 없이 진열대를 이리저리 뒤적인다.'
    ],
    'ans': 0,
    'why': '점원에게 물을 때는 먼저 실례라고 부르고, 무엇을 찾는지 또박또박 말하면 금방 찾을 수 있어요. '
           '반말로 재촉하면 점원은 기분이 상하고, 허락 없이 진열대를 뒤지면 물건이 엉망이 되어 다른 사람이 불편해져요.',
    'say': '실례지만, 딸기 잼은 어느 쪽에 있나요?',
    'tip': '부탁할 때는 ①실례지만 하고 부르기 ②찾는 물건 말하기 ③고맙다고 인사하기 순서로 하면 좋아요.',
}

STEP13_BLOCK = '''  {
    id: 's13', name: 'Step 13', short: '13 길·장소', title: '길과 장소', hint: '어디에 있는지 묻고 알려 줄 때',
    sentences: [
      { en: 'Where is the bathroom?', ko: '화장실이 어디예요?', tip: '웨어-이즈-더-배스룸 · Where is ~는 "~가 어디예요?"', emoji: '🚻' },
      { en: 'Go straight.', ko: '곧장 가.', tip: '고-스트레이트 · straight는 "곧장"', emoji: '⬆️' },
      { en: 'It is next to the door.', ko: '문 옆에 있어.', tip: '잇-이즈-넥스트-투-더-도어 · next to는 "옆에"', emoji: '🚪' }
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

    # 3) 영어 Step 13
    html = open(HTML, encoding='utf-8').read()
    if "id: 's13'" in html:
        print('영어 Step 13 이미 있음')
    else:
        old_tail = "emoji: '🐱' }\n    ]\n  }\n];\n\nconst SUBJECTS = ["
        new_tail = "emoji: '🐱' }\n    ]\n  },\n" + STEP13_BLOCK + "\n];\n\nconst SUBJECTS = ["
        assert old_tail in html, 'ENGLISH_STEPS 끝(Step 12)을 찾지 못했어요'
        html = html.replace(old_tail, new_tail, 1)
        open(HTML, 'w', encoding='utf-8', newline='').write(html)
        print('영어 Step 13 추가')


main()
