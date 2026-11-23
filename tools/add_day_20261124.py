#!/usr/bin/env python3
"""2026-11-24(화) 하루치 — videos.json 끝에 한국사·위인·시사상식 항목을 덧붙인다.

   영상 3편은 브라우저로 watch?v=... 페이지를 직접 열어 길이·채널·자막(스크립트 표시)을 확인했다.
   실행: python3 tools/add_day_20261124.py   (이미 들어 있으면 아무 것도 하지 않는다)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, 'videos.json')

HIST_ESSAY = (
    '고려는 거란족이 쳐들어왔을 때 몽골군과 힘을 합쳐 거란을 물리쳤어요. 그런데 몽골은 도와준 대가로 많은 양의 공물을 달라고 했어요. '
    '고려가 이를 거절하고 몽골에서 온 사신이 죽는 일까지 생기자, 몽골은 그것을 빌미로 고려를 공격했지요.\n\n'
    '세계 최강이라던 몽골군은 10만 군사를 이끌고 쳐들어왔어요. 하지만 귀주성에서는 박서와 김경손 장군이 끝까지 버텨서, 몽골군이 그 성을 빼앗지 못했어요.\n\n'
    '그래도 몽골군은 계속 밀고 들어와 수도 개경까지 위태로워졌어요. 그래서 고려의 높은 관리들은 백성을 살리려면 수도를 강화로 옮기자는 이야기를 꺼냈답니다.'
)
HIST_VOCAB = [{'w': '공물', 'm': '힘센 나라에 억지로 바치는 물건이나 돈'},
              {'w': '귀주성', 'm': '박서와 김경손 장군이 몽골군을 막아 낸 성'}]

HERO_ESSAY = (
    '김만덕은 제주도에서 살던 여성 상인이에요. 제주에서 나는 귤과 미역, 전복과 말총을 육지에 팔고, 제주에서는 구하기 어려운 쌀을 들여와 다시 팔았어요. '
    '장사가 아주 잘 되어 큰 부자가 되었지요.\n\n'
    '김만덕에게는 꼭 지키는 원칙이 있었어요. 바로 손님들에게 믿음을 주는 것이었어요. 믿음이 없으면 장사도 오래 갈 수 없다고 생각했어요.\n\n'
    '어느 해 큰 태풍이 제주를 덮치고 흉년까지 겹쳐 사람들이 굶게 되었어요. 김만덕은 자기 돈으로 쌀을 사서 백성들에게 나누어 주었어요. '
    '제주 사람들이 내 물건을 사 주었기에 내가 돈을 벌었다며, 아깝지 않은 일이라고 했답니다.'
)
HERO_VOCAB = [{'w': '객주', 'm': '상인들이 물건을 사고팔거나 머물 수 있게 해 주는 집'},
              {'w': '말총', 'm': '말의 꼬리털, 망건을 만드는 재료'}]

NEWS_ESSAY = (
    '설날에 금리는 세뱃돈을 저금하자는 엄마 말이 못내 아쉬웠어요. 그래서 할아버지께 이야기하고, 눈알 안경 젤리를 먹은 뒤 은행에 갔어요.\n\n'
    '은행에 돈을 맡겼더니 돈의 요정이 보였어요. 사람들이 돈을 맡기거나 빌릴 때마다 요정이 새로 생겼지요. 은행은 맡은 돈을 필요한 사람에게 빌려주고, '
    '빌린 돈은 다시 은행으로 들어와 또 빌려줄 수 있어요. 이렇게 돈이 늘어나는 것을 신용 창조라고 해요.\n\n'
    '그런데 요정들이 마음대로 나가자 물건값이 점점 올라갔어요. 돈이 너무 많아지면 물건값이 오른다는 뜻이에요. '
    '그래서 은행은 돈을 함부로 늘리면 안 된다는 것을 금리가 배웠답니다.'
)


def hist(vid, extra_id, q, opts, why, key):
    return {'id': extra_id, 'url': 'https://www.youtube.com/watch?v=' + vid,
            'title': HIST['title'], 'channel': HIST['channel'],
            'dur_s': HIST['dur_s'], 'dur_label': HIST['dur_label'], 'caption': HIST['caption'],
            'verified_on': '2026-11-24', 'summary': HIST['summary'], 'evidence': HIST['evidence'],
            'quiz': {'q': q, 'opts': opts, 'ans': 0, 'why': why, 'key': key},
            'topic': HIST['topic'], 'essay': HIST_ESSAY, 'vocab': HIST_VOCAB}


HIST = dict(
    vid='zqCNGrlCVWA',
    title='몽골제국의 역습 | 긴 전쟁의 서막 | 초등 이야기 한국사 고려시대 애니메이션 ★ 지니스쿨 역사',
    channel='지니스쿨 역사 GeniSchool History',
    dur_s=351, dur_label='5:51', caption='ko(자동생성)',
    summary='몽골이 거란을 함께 물리친 뒤 공물을 요구하며 고려를 공격하고, 귀주성에서 박서·김경손이 막아 낸 뒤 수도를 강화로 옮기자는 데까지 간 이야기.',
    evidence='자막 1:54 "몽골은 도와준 담내로 많은 양의 공물을 요구했고"; 2:59 "우리 자신이 공물을 받아오는 길에 … 땅에서 죽지 않았나요"; '
             '3:06 "그걸 빌미로 확 쳐들어가면"; 3:22 "고려는 세계 최강 몽골군의 공격을 받게 되었다"; 3:27 "몽골군은 무려 10만 군사를 이끌고"; '
             '3:36 "박서 김경손 장군이 버티는 귀주성을 함락하는데 실패하는 몽골군"; 5:00 "백성들을 살리려면 어쩔 수 없지 않느냐"; '
             '5:32 "수도를 가마로 옮기는 겁니다"(자동 자막이 강화를 잘못 받아쓴 것)',
    topic='몽골과의 긴 전쟁',
)

HERO = dict(
    vid='o0jyhD1dq6c',
    title='백성을 위한 큰 손! 제주의 여자 상인ㅣ조선시대 김만덕ㅣ큰별쌤 최태성 선생님ㅣ별별 역사 기차ㅣKBS 221103 방송',
    channel='KBSKids',
    dur_s=522, dur_label='8:42', caption='ko',
    summary='제주도 여성 상인 김만덕이 귤·말총을 팔고 쌀을 들여와 부자가 된 뒤, 태풍과 흉년에 자기 돈으로 쌀을 사 나눠 준 이야기.',
    evidence='자막 1:37 "상인들이 와서 물건을 사고 팔거나 또는 먹고 잘 수도 있는 집"; 2:07 "이거는 말총이야"; 2:25 "제주의 특산품을 육지에 팔고 그 돈으로 육지 물건을 사서 다시 제주에 팔고"; '
             '2:35 "제주도의 땅은 쌀농사를 짓기 힘들거든. 그래서 쌀을 들여오지"; 2:54 "손님들에게 믿음을 준다. 믿음 없는 장사는 오래 갈 수 없거든"; 3:44 "엄청난 태풍이 제주를 확 쓸어요"; '
             '4:05 "임금이었던 정조가 제주를 도우라"; 4:13 "하필 도중에 또 태풍을 만나네"; 5:11 "제주 사람들이 우리 물건을 사 주었기에 내가 돈을 벌 수 있었던 거야"; 5:18 "가치 있는 일이지"; '
             '5:29 "어서 쌀을 나눠 주도록 하세요"',
    topic='김만덕과 나눔',
)

NEWS = dict(
    vid='9H-tWOH2qhg',
    title='신용창조와 인플레이션의 개념을 알아보자!ㅣ[ep.10] 돈의 요정과 은행의 비밀ㅣ자본주의 편의점',
    channel='EBS 키즈',
    dur_s=316, dur_label='5:16', caption='ko',
    summary='은행에 돈을 맡기고 빌리는 사이 돈이 늘어나는 신용 창조와, 돈이 너무 많아지면 물건값이 오르는 까닭을 배운다.',
    evidence='자막 1:42 "돈을 맡겼더니 돈의 요정이 나타났어요"; 2:05 "사람들이 은행에 돈을 맡기거나 빌릴 때마다 돈의 요정이 새로 생기는데요"; 3:27 "돈의 요정들이 물건들의 가격을 올리고 있어요"; '
             '4:25 "은행의 돈을 맡기면 은행은 그 돈을 필요한 사람에게 빌려줘요"; 4:31 "빌린 돈은 다시 은행에 들어가고 은행은 또 빌려줄 수 있죠"; 4:36 "돈이 늘어나는 걸 신용 창조라고 해요. 그런데 돈이 너무 많아지면 물건값이 올라요"',
    topic='신용창조와 물가',
)


def main():
    data = json.load(open(VIDEOS, encoding='utf-8'))
    subs = data['subjects']
    have = {it['id'] for arr in subs.values() for it in arr}
    if HIST['vid'] in have or HERO['vid'] in have or NEWS['vid'] in have:
        print('이미 들어 있어요 — 아무 것도 하지 않았습니다.')
        return

    subs['history'] += [
        hist(HIST['vid'], HIST['vid'],
             '읽기 글에서 귀주성에서 끝까지 버텨 몽골군을 막아 낸 장군 두 사람은 누구인가요?',
             ['박서와 김경손', '이순신과 권율', '을지문덕과 강감찬'],
             '읽기 글에 귀주성에서 박서와 김경손 장군이 끝까지 버텨 몽골군이 성을 빼앗지 못했다고 나와요.',
             '귀주성을 지킨 장군은 박서와 김경손이에요.'),
        hist(HIST['vid'], HIST['vid'] + '-q2',
             '읽기 글에서 몽골이 고려를 도와준 대가로 달라고 한 것은 무엇인가요?',
             ['많은 양의 공물', '넓은 땅', '거북선'],
             '읽기 글에 몽골이 도와준 대가로 많은 양의 공물을 달라고 했다고 나와요.',
             '몽골은 많은 양의 공물을 요구했어요.'),
        hist(HIST['vid'], HIST['vid'] + '-q3',
             '읽기 글에서 높은 관리들이 백성을 살리려고 수도를 옮기자고 한 곳은 어디인가요?',
             ['강화', '제주', '울릉도'],
             '읽기 글에 수도를 강화로 옮기자는 이야기가 나왔어요.',
             '수도를 강화로 옮기자는 이야기가 나왔어요.'),
    ]

    base = {'id': HERO['vid'], 'url': 'https://www.youtube.com/watch?v=' + HERO['vid'],
            'title': HERO['title'], 'channel': HERO['channel'], 'dur_s': HERO['dur_s'],
            'dur_label': HERO['dur_label'], 'caption': HERO['caption'], 'verified_on': '2026-11-24',
            'summary': HERO['summary'], 'evidence': HERO['evidence'], 'topic': HERO['topic'],
            'essay': HERO_ESSAY, 'vocab': HERO_VOCAB}
    quizzes = [
        ('읽기 글에서 김만덕이 제주에서 육지로 들여와 다시 판 물건은 무엇인가요?',
         ['쌀', '말총', '귤'], '읽기 글에 제주에서는 구하기 어려운 쌀을 들여와 다시 팔았다고 나와요.',
         '제주에서 어려운 쌀을 들여와 팔았어요.'),
        ('읽기 글에서 김만덕이 장사에서 꼭 지킨 원칙은 무엇인가요?',
         ['손님들에게 믿음을 주는 것', '값을 자꾸 올리는 것', '혼자서만 파는 것'],
         '읽기 글에 손님들에게 믿음을 주는 것이 원칙이었다고 나와요.',
         '장사의 원칙은 손님들에게 믿음을 주는 것이었어요.'),
        ('읽기 글에서 김만덕이 자기 돈으로 쌀을 사 나누어 준 까닭은 무엇인가요?',
         ['제주 사람들이 내 물건을 사 주었기에', '상을 받고 싶어서', '임금님이 시켜서'],
         '읽기 글에 제주 사람들이 내 물건을 사 주었기에 내가 돈을 벌었다고 했어요.',
         '제주 사람들이 내 물건을 사 주었기에 나눠 주었어요.'),
    ]
    for i, (q, opts, why, key) in enumerate(quizzes):
        it = dict(base)
        it['id'] = HERO['vid'] if i == 0 else HERO['vid'] + '-q%d' % (i + 1)
        it['quiz'] = {'q': q, 'opts': opts, 'ans': 0, 'why': why, 'key': key}
        subs['hero'].append(it)

    subs['news'].append({
        'id': NEWS['vid'], 'url': 'https://www.youtube.com/watch?v=' + NEWS['vid'],
        'title': NEWS['title'], 'channel': NEWS['channel'], 'dur_s': NEWS['dur_s'],
        'dur_label': NEWS['dur_label'], 'caption': NEWS['caption'], 'verified_on': '2026-11-24',
        'summary': NEWS['summary'], 'evidence': NEWS['evidence'], 'topic': NEWS['topic'],
        'essay': NEWS_ESSAY,
        'vocab': [{'w': '신용 창조', 'm': '은행이 돈을 빌려주며 돈이 늘어나는 것'},
                  {'w': '물가', 'm': '물건값의 높낮이'}],
        'quiz': {'q': '읽기 글에서 은행이 돈을 빌려주며 돈이 늘어나는 것을 무엇이라고 하나요?',
                 'opts': ['신용 창조', '복리', '할인'],
                 'ans': 0,
                 'why': '읽기 글에 이렇게 돈이 늘어나는 것을 신용 창조라고 한다고 나와요.',
                 'key': '돈이 늘어나는 것은 신용 창조예요.'},
    })

    json.dump(data, open(VIDEOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('추가 완료 —', {k: len(v) for k, v in subs.items()})


main()
