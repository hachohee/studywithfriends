#!/usr/bin/env python3
"""videos.json -> index.html 의 BANKS 블록을 다시 채운다. (원본은 videos.json)
   essay/topic/vocab = 과목 화면의 '오늘의 읽기 글' 데이터(퀴즈 정답이 글 안에 있음)."""
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
        'topic': v.get('topic', ''),
        'essay': v.get('essay', ''),
        'vocab': v.get('vocab', []),
        'key': v['quiz']['key'],
        'q': v['quiz']['q'],
        'opts': v['quiz']['opts'],
        'ans': v['quiz']['ans'],
        'why': v['quiz']['why'],
    }


def run_tool(name):
    """tools/ 아래 생성기(gen_levels·gen_hanja·gen_math_levels)를 불러 실행한다.
       각 파일은 끝에서 main() 을 부르므로, 본문만 잘라 실행한 뒤 main() 을 직접 부른다."""
    path = os.path.join(ROOT, 'tools', name)
    src = open(path, encoding='utf-8').read()
    src = re.sub(r'\nmain\(\)\s*$', '\n', src)
    ns = {'__name__': 'build_' + name.replace('.py', ''), '__file__': path}
    exec(compile(src, path, 'exec'), ns)
    ns['main']()


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
    if '/*__BANKS_START__*/' not in html or '/*__BANKS_END__*/' not in html:
        print('!! BANKS 마커를 찾지 못했습니다.', file=sys.stderr)
        sys.exit(1)
    # 람다로 넣어야 에세이 안의 \n·\" 같은 이스케이프가 re.sub replacement로 해석되지 않음
    new = re.sub(r'/\*__BANKS_START__\*/.*?/\*__BANKS_END__\*/',
                 lambda m: '/*__BANKS_START__*/\n' + body + '\n/*__BANKS_END__*/', html, flags=re.S)
    if new == html:
        print('(이미 최신)')
    open(HTML, 'w', encoding='utf-8', newline='').write(new)
    print('subject pools:', {k: len(v) for k, v in banks.items()}, 'total', sum(len(v) for v in banks.values()))
    # 2~4단계 데이터(읽기 글·영어 문장·예쁘게 말하기 / 한자 비문학 / 수학)
    for tool in ('gen_levels.py', 'gen_hanja.py', 'gen_math_levels.py'):
        run_tool(tool)


main()
