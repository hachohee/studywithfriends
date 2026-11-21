#!/usr/bin/env python3
"""Collect candidate videos per subject from the user's approved channels (dur<=600s)."""
import json, sys, re
import yt

CHANNELS = {
    'history': ['지니스쿨', '설쌤', 'KBSKids', 'EBS'],
    'hero': ['지니스쿨', '설쌤', '큰별', 'KBSKids', 'EBS'],
    'news': ['EBS'],
    'english': ['EBS', 'EBSe'],
    'math': ['EBS'],
}

QUERIES = {
    'history': [
        '지니스쿨 역사 단군 고조선',
        '지니스쿨 역사 세종대왕 한글',
        '지니스쿨 역사 이순신 거북선',
        '지니스쿨 역사 삼국시대',
        '설쌤 한국사 대모험 세종대왕',
        '큰별쌤 최태성 초등 한국사',
        'EBS 인물한국사 덩이랑 쾡이랑',
        'EBS 역사가 술술',
    ],
    'hero': [
        'EBS 올림포스의 별',
        '지니스쿨 역사 위인',
        '큰별쌤 장영실',
        '설쌤 한국사 대모험 장영실',
        'EBS 인물한국사 유관순',
        'KBS 위키와 퐁당역사 위인',
    ],
    'news': [
        'EBS 자본주의 편의점',
        'EBS 시간을 달리는 세계사',
        'EBS 어린이 경제',
        'EBS 어린이 환경 기후',
    ],
    'english': [
        'EBS 초등 영어 회화',
        'EBS 키즈 영어 노래',
        'EBSe 초등 영어',
        'EBS 초등 영어 파닉스',
        'EBS 키즈 영어 동화',
    ],
    'math': [
        'EBS 초등 수학 2학년 덧셈 뺄셈',
        'EBS 키즈 수학',
        'EBS 초등 수학 곱셈구구',
        'EBS 매쓰 초등 수학',
    ],
}


def main():
    subject = sys.argv[1]
    out = {}
    for q in QUERIES[subject]:
        try:
            res = yt.search(q, limit=20)
        except Exception as e:
            print('ERR', q, e, file=sys.stderr)
            continue
        for v in res:
            if not v['dur_s'] or v['dur_s'] > 600:
                continue
            if not any(k in v['channel'] for k in CHANNELS[subject]):
                continue
            out.setdefault(v['id'], v)
        print('ok', q, len(res), file=sys.stderr)
    for vid, v in out.items():
        print(json.dumps(v, ensure_ascii=False))


main()
