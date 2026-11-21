#!/usr/bin/env python3
"""videos.json -> index.html 의 BANKS 블록을 다시 채운다. (원본은 videos.json)"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, 'videos.json')
HTML = os.path.join(ROOT, 'index.html')

ORDER = ['math', 'english', 'history', 'hero', 'news']


def clean(v):
    return {
        'id': v['id'],
        'url': v.get('url') or ('https://www.youtube.com/watch?v=' + v['id']),
        'title': v.get('title_proper') or v['title'],
        'ch': v['channel'],
        'dur': v['dur_s'],
        'dur_label': v['dur_label'],
        'summary': v.get('summary', ''),
        'evidence': v.get('evidence', ''),
        'key': v['quiz']['key'],
        'q': v['quiz']['q'],
        'opts': v['quiz']['opts'],
        'ans': v['quiz']['ans'],
        'why': v['quiz']['why'],
    }


def main():
    data = json.load(open(VIDEOS, encoding='utf-8'))
    banks = {}
    for k in ORDER:
        items = data['subjects'].get(k, [])
        banks[k] = [clean(v) for v in items]
        bad = [v for v in banks[k] if v['dur'] > 600]
        if bad:
            print('!! 10분 초과:', [v['id'] for v in bad], file=sys.stderr)
    body = 'const BANKS = ' + json.dumps(banks, ensure_ascii=False, indent=0).replace('\n', ' ') + ';'
    html = open(HTML, encoding='utf-8').read()
    new = re.sub(r'/\*__BANKS_START__\*/.*?/\*__BANKS_END__\*/',
                 '/*__BANKS_START__*/\n' + body + '\n/*__BANKS_END__*/', html, flags=re.S)
    if '/*__BANKS_START__*/' not in html or '/*__BANKS_END__*/' not in html:
        print('!! BANKS 마커를 찾지 못했습니다.', file=sys.stderr)
        sys.exit(1)
    if new == html:
        print('(이미 최신)')
    open(HTML, 'w', encoding='utf-8', newline='').write(new)
    print('subject pools:', {k: len(v) for k, v in banks.items()}, 'total', sum(len(v) for v in banks.values()))


main()
