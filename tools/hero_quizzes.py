#!/usr/bin/env python3
"""위인(great/hero) 하루 1명 · 3문제: videos.json 의 위인 항목을 주제별 3문제로 맞춘다.
   - 기존 문제(quiz)는 그대로 두고, 같은 글(essay)에서 답을 찾을 수 있는 문제 2개를 더 붙인다.
   - id 는 '<영상id>-q2' · '<영상id>-q3' (한국사와 같은 규칙). 같은 영상 = 같은 주제 = 같은 글.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, 'videos.json')

MORE = {
    '1Z19a8JmFEM': [
        dict(q='읽기 글에서 장영실이 만든 해시계의 이름은 무엇인가요?',
             opts=['앙부일구', '자격루', '측우기'], ans=0,
             why='읽기 글에 해시계 앙부일구는 해 그림자를 보고 시간을 알려 주었다고 나와요.',
             key='앙부일구는 해 그림자로 시간을 알려 주는 해시계예요.'),
        dict(q='읽기 글에서 장영실에게 과학 기구를 만들라고 한 임금님은 누구인가요?',
             opts=['세종대왕', '단군왕검', '정조'], ans=0,
             why='읽기 글에 세종대왕이 장영실을 불러 과학 기구를 만들게 했다고 나와요.',
             key='세종대왕이 장영실에게 과학 기구를 만들게 했어요.'),
    ],
    'EqoFG-yBZHU': [
        dict(q='읽기 글에서 두정갑은 쇠조각을 무엇으로 고정해 만들었나요?',
             opts=['쇠못', '나무못', '실'], ans=0,
             why='읽기 글에 쇠조각을 쇠못으로 꾹꾹 눌러 고정했다고 나와요. 그래서 이름이 "두정갑"이에요.',
             key='두정갑은 쇠조각을 쇠못으로 고정한 갑옷이에요.'),
        dict(q='읽기 글에서 광화문 이순신 동상의 갑옷은 어느 나라 모양이라고 했나요?',
             opts=['중국', '일본', '인도'], ans=0,
             why='읽기 글에 동상의 갑옷이 조선 갑옷이 아니라 중국식 갑옷 모양이라고 나와요.',
             key='광화문 동상의 갑옷은 중국식이라 역사와 달라요.'),
    ],
}


def main():
    data = json.load(open(VIDEOS, encoding='utf-8'))
    hero = data['subjects']['hero']
    base = {}
    for it in hero:
        base.setdefault(it['id'].split('-q')[0], it)

    out = []
    for vid, head in base.items():
        items = [it for it in hero if it['id'].split('-q')[0] == vid]
        items.sort(key=lambda x: int(x['id'].split('-q')[1]) if '-q' in x['id'] else 1)
        out.append(items[0])
        for n, extra in enumerate(MORE.get(vid, []), start=2):
            it = {
                'id': vid + '-q%d' % n,
                'url': items[0].get('url') or ('https://www.youtube.com/watch?v=' + vid),
                'title': items[0]['title'],
                'channel': items[0]['channel'],
                'dur_s': items[0]['dur_s'],
                'dur_label': items[0]['dur_label'],
                'caption': items[0].get('caption', ''),
                'verified_on': items[0].get('verified_on', ''),
                'summary': items[0].get('summary', ''),
                'evidence': items[0].get('evidence', ''),
                'quiz': extra,
                'topic': items[0].get('topic', ''),
                'essay': items[0].get('essay', ''),
                'vocab': items[0].get('vocab', []),
            }
            out.append(it)
    data['subjects']['hero'] = out
    json.dump(data, open(VIDEOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    groups = {}
    for it in out:
        groups.setdefault(it['id'].split('-q')[0], []).append(it['id'])
    print('hero items:', len(out), groups)

    # 점검: 하루 3문제가 모두 같은 글에서 답을 찾을 수 있는지
    bad = []
    for vid, items in groups.items():
        essay = next(it for it in out if it['id'] == items[0])['essay']
        for qid in items:
            it = next(x for x in out if x['id'] == qid)
            ans = it['quiz']['opts'][it['quiz']['ans']]
            if ans not in essay:
                bad.append((qid, ans))
    if bad:
        print('!! 글에서 답을 찾을 수 없는 문제:', bad, file=sys.stderr)
        sys.exit(1)


main()
