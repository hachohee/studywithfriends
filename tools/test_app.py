#!/usr/bin/env python3
"""우리 반 공부방 · 자동 검증
   실행: python3 tools/test_app.py   (통과하면 exit 0)

   검사 항목
   1) gen_math.py — 연산 정답·보기 구성·조사(을/를·이/가)
   2) videos.json — 읽기 글(essay) 존재/분량/문단, 낱말(vocab), 퀴즈 정합성(정답이 글 안에 있음),
      같은 주제(영상)의 문제는 같은 글을 씀, 영상 길이 10분 이내
   3) 오늘의 문제 순환(dailyIdxs) — 날짜별 문제 수·범위·중복·시대순 진행·전체 순환
   4) index.html 구조 — 읽기 글 화면, 영상방 탭, 완료 판정(전부 맞혀야 도장), 빌드 동기화, sw 캐시 버전
"""
import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
VIDEOS = os.path.join(ROOT, 'videos.json')
SW = os.path.join(ROOT, 'sw.js')
DOWNLOADS_COPY = os.path.abspath(os.path.join(ROOT, '..', '..', 'downloads', '초1_공동학습_웹앱_틀.html'))

FAIL = []
PASS = []


def check(cond, msg):
    if cond:
        PASS.append(msg)
    else:
        FAIL.append(msg)
    return bool(cond)


def norm(s):
    s = str(s or '').lower()
    s = s.replace(',', '')
    return re.sub(r'[\s\.\,\!\?\"\'“”‘’·…~\-—\(\)\[\]<>:/]', '', s)


# ─────────────────────────── 1. 수학 문제 은행 ───────────────────────────
def load_math_bank():
    path = os.path.join(ROOT, 'tools', 'gen_math.py')
    src = open(path, encoding='utf-8').read()
    src = re.sub(r'\nmain\(\)\s*$', '\n', src)          # 파일 끝의 main() 호출은 건너뜀(index.html 덮어쓰기 방지)
    ns = {'__name__': 'gen_math_probe', '__file__': path}
    exec(compile(src, path, 'exec'), ns)
    return ns['build'](), ns['has_batchim']


def test_math():
    bank, has_batchim = load_math_bank()
    check(len(bank) >= 200, 'gen_math: 문제 은행 %d개(>=200)' % len(bank))
    kinds = {}
    bad_ans, bad_opt, bad_josa = [], [], []
    for it in bank:
        kinds[it['kind']] = kinds.get(it['kind'], 0) + 1
        q, opts, ans = it['q'], it['opts'], it['ans']
        if not (len(opts) == 3 and 0 <= ans < 3 and len(set(opts)) == 3):
            bad_opt.append(q)
            continue
        if not it.get('why'):
            bad_opt.append(q)

        def val(s):
            m = re.match(r'^(-?\d+)', s.replace(' ', ''))
            return int(m.group(1)) if m else None

        got = val(opts[ans])

        def expect(v):
            if got != v:
                bad_ans.append('%s | 정답 %s (기대 %d)' % (q, opts[ans], v))

        m = re.match(r'^(\d+) \+ (\d+) = \?$', q)
        if m:
            expect(int(m.group(1)) + int(m.group(2)))
        m = re.match(r'^(\d+) − (\d+) = \?$', q)
        if m:
            expect(int(m.group(1)) - int(m.group(2)))
        m = re.match(r'^(\d+) × (\d+) = \?$', q)
        if m:
            expect(int(m.group(1)) * int(m.group(2)))
        m = re.match(r'^(\d+) \+ (\d+) − (\d+) = \?$', q)
        if m:
            expect(int(m.group(1)) + int(m.group(2)) - int(m.group(3)))
        m = re.match(r'^(\d+) − (\d+) \+ (\d+) = \?$', q)
        if m:
            expect(int(m.group(1)) - int(m.group(2)) + int(m.group(3)))
        m = re.match(r'^□ \+ (\d+) = (\d+)\s+에서 □는\?$', q)
        if m:
            expect(int(m.group(2)) - int(m.group(1)))
        m = re.match(r'^(\d+) − □ = (\d+)\s+에서 □는\?$', q)
        if m:
            expect(int(m.group(1)) - int(m.group(2)))
        m = re.match(r'^□ \+ (\d+) = (\d+) \+ (\d+)\s+에서 □는\?$', q)
        if m:
            expect(int(m.group(2)) + int(m.group(3)) - int(m.group(1)))
        # 규칙 찾기
        m = re.search(r'([\d, ]+), □$', q)
        if m and '규칙' in q:
            seq = [int(x) for x in re.findall(r'\d+', m.group(1))]
            if len(seq) >= 2:
                d = seq[1] - seq[0]
                expect(seq[-1] + d) if all(seq[i + 1] - seq[i] == d for i in range(len(seq) - 1)) else None
        # 조사: '12를 더했더니' · '23이 되었어요'
        for mm in re.finditer(r'(\d+)(을|를) (더했더니|뺐더니)', q):
            n, josa = int(mm.group(1)), mm.group(2)
            if (josa == '을') != has_batchim(n):
                bad_josa.append(q)
        for mm in re.finditer(r'(\d+)(이|가) 되었어요', q):
            n, josa = int(mm.group(1)), mm.group(2)
            if (josa == '이') != has_batchim(n):
                bad_josa.append(q)
    check(not bad_ans, 'gen_math: 연산 정답 일치 (%s)' % ('실패 %d건: %s' % (len(bad_ans), bad_ans[:3]) if bad_ans else '전건 통과'))
    check(not bad_opt, 'gen_math: 보기 3개·중복 없음·풀이 존재 (%s)' % ('실패 %d건' % len(bad_opt) if bad_opt else '전건 통과'))
    check(not bad_josa, 'gen_math: 숫자 뒤 조사(을/를·이/가) (%s)' % ('실패 %d건: %s' % (len(bad_josa), bad_josa[:3]) if bad_josa else '전건 통과'))
    check(kinds.get('연산', 0) >= 100 and kinds.get('사고력', 0) >= 30 and kinds.get('서술형', 0) >= 30,
          'gen_math: 종류별 구성 %s' % kinds)


# ─────────────────────────── 2. videos.json 읽기 글 ───────────────────────────
# 정답 보기가 너무 짧아 글에서 찾기 어려운 문제는 글에 있어야 할 표현을 따로 지정
ANSWER_NEEDLE = {
    'yqNbmtBr4c8-q2': '알에서 태어난',
}


def test_videos(data):
    totals = {}
    for subj in ('history', 'hero', 'news'):
        items = data['subjects'][subj]
        totals[subj] = len(items)
        check(len(items) > 0, 'videos.json[%s]: 항목 %d개' % (subj, len(items)))
        by_video = {}
        for it in items:
            iid = it['id']
            essay = it.get('essay') or ''
            paras = [p for p in essay.split('\n\n') if p.strip()]
            check(bool(essay), 'videos.json[%s/%s]: essay 존재' % (subj, iid))
            check(3 <= len(paras) <= 4, 'videos.json[%s/%s]: 문단 %d개(3~4)' % (subj, iid, len(paras)))
            check(220 <= len(essay) <= 350, 'videos.json[%s/%s]: 분량 %d자(220~350)' % (subj, iid, len(essay)))
            check('영상' not in essay, 'videos.json[%s/%s]: 글 본문에 영상 언급 없음' % (subj, iid))
            topic = it.get('topic') or ''
            check(2 <= len(topic) <= 24, 'videos.json[%s/%s]: 주제 이름 "%s"' % (subj, iid, topic))
            vocab = it.get('vocab') or []
            check(1 <= len(vocab) <= 2 and all(v.get('w') and v.get('m') for v in vocab),
                  'videos.json[%s/%s]: 낱말 %d개(1~2, 뜻 포함)' % (subj, iid, len(vocab)))
            quiz = it['quiz']
            check(len(quiz['opts']) == 3 and 0 <= quiz['ans'] < 3, 'videos.json[%s/%s]: 보기 3개·정답 번호' % (subj, iid))
            check('영상' not in quiz['q'] and '영상' not in quiz['why'],
                  'videos.json[%s/%s]: 문제·풀이가 영상이 아니라 읽기 글을 가리킴' % (subj, iid))
            answer = quiz['opts'][quiz['ans']]
            needle = ANSWER_NEEDLE.get(iid) or answer
            check(norm(needle) in norm(essay),
                  'videos.json[%s/%s]: 정답 "%s"가 글 안에 있음' % (subj, iid, answer))
            check(it['dur_s'] <= 600, 'videos.json[%s/%s]: 영상 %s(10분 이내)' % (subj, iid, it['dur_label']))
            vid = iid.split('-q')[0]
            if vid in by_video:
                check(by_video[vid] == essay, 'videos.json[%s]: 같은 주제(%s)는 같은 글' % (subj, vid))
            else:
                by_video[vid] = essay
            # 같은 글을 쓰는 문제는 모두 그 글에서 답을 찾을 수 있어야 함
    # 같은 글을 쓰는 문제는 모두 그 글에서 답을 찾을 수 있어야 함
    # 한국사 2문제 · 위인 3문제: 하루에 내는 문제가 모두 같은 글 안에서 풀려야 한다
    for subj, per in (('history', 2), ('hero', 3)):
        groups = {}
        for it in data['subjects'][subj]:
            groups.setdefault(it['id'].split('-q')[0], []).append(it)
        for vid, g in groups.items():
            check(len(g) >= per, 'videos.json[%s/%s]: 문제 %d개(하루 %d문제)' % (subj, vid, len(g), per))
            for it in g:
                answer = it['quiz']['opts'][it['quiz']['ans']]
                needle = ANSWER_NEEDLE.get(it['id']) or answer
                check(norm(needle) in norm(g[0].get('essay', '')),
                      'videos.json[%s/%s]: 하루 문제 모두 같은 글에서 답 확인' % (subj, it['id']))
    return totals


# ─────────────────────────── 3. dailyIdxs 순환 ───────────────────────────
def js_day_number(day='2026-11-21'):
    y, m, d = map(int, day.split('-'))
    return datetime.date(y, m, d).toordinal()   # KST 정오 기준 floor(UTCms/86400000)와 같은 값


HISTORY_START = '2026-11-21'


def parse_cfg(js):
    """index.html 의 하루 분량 상수를 읽어 온다."""
    daily = int(re.search(r'const DAILY_SENTENCES = (\d+);', js).group(1))
    per_src = re.search(r'const PER_DAY = \{([^}]*)\}', js).group(1)
    per = {k: int(v) for k, v in re.findall(r'(\w+)\s*:\s*(\d+)', per_src)}
    plan_src = re.search(r'const MATH_PLAN = \[(.*?)\];', js, re.S).group(1)
    math_total = sum(int(n) for n in re.findall(r"\[\s*'[^']+',\s*(\d+)\]", plan_src))
    rot = {'math': 0, 'english': 2, 'history': 4, 'hero': 6, 'news': 8}   # SUBJECTS.forEach: rot = i*2
    block = re.search(r'const ENGLISH_STEPS = \[(.*?)\n\];', js, re.S).group(1)
    pair = re.findall(r"\{\s*en:\s*('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),\s*ko:\s*('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", block)
    ens = [eval(a) for a, _ in pair]
    kos = [eval(b) for _, b in pair]
    return {'per_day': per, 'daily_sentences': daily, 'math_total': math_total,
            'rot': rot, 'english_sentences': len(pair), 'ens': ens, 'kos': kos}


def test_english(cfg):
    ens, kos, per = cfg['ens'], cfg['kos'], cfg['daily_sentences']
    check(len(ens) >= 30, 'ENGLISH_STEPS: 문장 %d개(>=30, 하루 %d문장이면 %d일 주기)' % (len(ens), per, len(ens) // per))
    check(len(set(ens)) == len(ens), 'ENGLISH_STEPS: 영어 문장 중복 없음')
    check(len(set(kos)) == len(kos), 'ENGLISH_STEPS: 우리말 뜻 중복 없음(퀴즈 보기 3개가 서로 다름)')
    check(all(tip for tip in re.findall(r"tip:\s*'([^']*)'", re.search(r'const ENGLISH_STEPS = \[(.*?)\n\];', open(INDEX, encoding='utf-8').read(), re.S).group(1))),
          'ENGLISH_STEPS: 모든 문장에 발음 팁(tip)')
    check(per == 3 and len(ens) % per == 0, 'ENGLISH: 하루 %d문장 × %d일 = %d문장' % (per, len(ens) // per, len(ens)))


def test_rotation(data, cfg):
    hist = data['subjects']['history']
    hero = data['subjects']['hero']
    news = data['subjects']['news']
    per_day = cfg['per_day']['history']

    def groups_of(bank):
        g, order = {}, []
        for i, it in enumerate(bank):
            v = it['id'].split('-q')[0]
            if v not in g:
                g[v] = []
                order.append(v)
            g[v].append(i)
        return [g[v] for v in order]

    check(per_day == 2, 'PER_DAY.history = %d (하루 2문제)' % per_day)
    hg = groups_of(hist)
    check(all(len(g) >= per_day for g in hg), 'dailyIdxs: 한국사 주제마다 문제 %d개 이상' % per_day)

    seen_groups = []
    for n in range(0, 16):
        g = hg[n % len(hg)]
        rnd = n // len(hg)
        idxs = [g[(rnd + k) % len(g)] for k in range(per_day)]
        if not check(len(idxs) == per_day and len(set(idxs)) == per_day, 'dailyIdxs: %d일차 한국사 문제 2개(중복 없음)' % n):
            break
        if not check(all(0 <= i < len(hist) for i in idxs), 'dailyIdxs: %d일차 한국사 문제 번호 범위' % n):
            break
        seen_groups.append(n % len(hg))
    check(seen_groups[:len(hg)] == list(range(len(hg))),
          'dailyIdxs: 한국사는 시대순으로 하루에 주제 하나씩 (%s)' % seen_groups[:len(hg)])
    check(len(set(seen_groups[:len(hg)])) == len(hg), 'dailyIdxs: 한 바퀴에 모든 주제를 한 번씩')

    # 두 번째 바퀴에서는 같은 주제의 다른 문제 2개
    g = hg[0]
    first_round = [g[k % len(g)] for k in range(per_day)]
    second_round = [g[(1 + k) % len(g)] for k in range(per_day)]
    check(first_round != second_round, 'dailyIdxs: 같은 주제 두 번째 바퀴는 다른 문제 2개')

    # 위인: 하루 1명(한 주제)에서 3문제 — 하루 문제는 그 인물의 문제 3개 전부
    per_hero = cfg['per_day']['hero']
    check(per_hero == 3, 'PER_DAY.hero = %d (위인 하루 3문제)' % per_hero)
    hg2 = groups_of(hero)
    check(all(len(g) >= per_hero for g in hg2), 'dailyIdxs: 위인 인물마다 문제 %d개 이상' % per_hero)
    hero_topics = []
    for day in range(0, 2 * len(hg2)):
        g2 = hg2[(day + cfg['rot']['hero']) % len(hg2)]
        idxs = g2[:per_hero]
        if not check(len(idxs) == per_hero and len(set(idxs)) == per_hero, 'dailyIdxs: %d일차 위인 문제 3개(중복 없음)' % day):
            break
        if not check(all(0 <= i < len(hero) for i in idxs), 'dailyIdxs: %d일차 위인 문제 번호 범위' % day):
            break
        hero_topics.append((day + cfg['rot']['hero']) % len(hg2))
    check(sorted(set(hero_topics)) == list(range(len(hg2))), 'dailyIdxs: 위인은 인물을 하루씩 번갈아 (%s)' % hero_topics)

    # 시사상식: 하루 1문제, 은행 크기만큼 돌면 전부 한 번씩
    rot = cfg['rot']['news']
    cycle = [((js_day_number() + d) + rot) % len(news) for d in range(len(news))]
    check(sorted(cycle) == list(range(len(news))), 'dailyIdxs: 시사상식은 %d일 동안 모든 문제를 한 번씩' % len(news))

    # 수학: 하루 5+2+3, 종류별 순환
    plan = [('연산', 5), ('사고력', 2), ('서술형', 3)]
    total = sum(n for _, n in plan)
    check(total == cfg['math_total'] == 10, 'MATH_PLAN: 하루 %d문제' % total)
    bank_len = {'연산': 140, '사고력': 45, '서술형': 45}
    for day in range(0, 28):
        for kind, n in plan:
            ids = list(range(bank_len[kind]))
            sel = [ids[(day * n + j) % len(ids)] for j in range(n)]
            if not check(len(set(sel)) == n, 'mathDaily: %d일차 %s %d문제 중복 없음' % (day, kind, n)):
                break

    # 영어: 하루 3문장 — 날마다 3개가 서로 다르고, 10일이면 30문장을 한 번씩
    per_en, n_sent = cfg['daily_sentences'], cfg['english_sentences']
    check(per_en == 3, 'DAILY_SENTENCES = %d (영어 하루 3문장)' % per_en)
    check(n_sent >= 30, 'ENGLISH_STEPS: 문장 %d개(>=30)' % n_sent)
    used = []
    for d in range(0, n_sent // per_en):
        idxs = [((d * per_en + j) * 7 + 3) % n_sent for j in range(per_en)]
        if not check(len(set(idxs)) == per_en, 'dailySentIdxs: %d일차 영어 문장 3개(중복 없음)' % d):
            break
        used += idxs
    check(len(used) == n_sent and sorted(used) == list(range(n_sent)),
          'dailySentIdxs: %d일 동안 영어 문장 %d개를 겹치지 않고 한 번씩' % (n_sent // per_en, n_sent))


# ─────────────────────────── 4. index.html 구조 ───────────────────────────
def test_index():
    html = open(INDEX, encoding='utf-8').read()
    js = re.search(r'<script>(.*)</script>', html, re.S).group(1)
    nav = re.search(r'<nav class="tabbar".*?</nav>', html, re.S).group(0)
    check(nav.count('data-nav=') == 5, 'index.html: 하단 탭 %d개(홈·공부·영상방·도장판·설정)' % nav.count('data-nav='))
    check('data-view="videos"' in nav and '🎬' in nav, 'index.html: 영상방 탭 존재')
    check('data-view="videos" id="view-videos"' in html, 'index.html: 영상방 화면 섹션 존재')
    check('📖 오늘의 읽기 글' in js, 'index.html: 과목 화면에 📖 오늘의 읽기 글 카드')
    check('data-action="read-essay"' in js and "'ko-KR'" in js, 'index.html: 한국어 읽어주기(TTS) 버튼')
    check('📖 오늘의 이야기 · ' in js, 'index.html: 홈 과목 카드가 읽기 글(주제) 표시')
    check('진행 중' in js, 'index.html: 진행 중 표시(예: 3/10 진행 중)')
    m = re.search(r'function essayDayHTML\(sub\)\s*\{(.*?)\n\}', js, re.S)
    check(m is not None and 'videoCardHTML' not in m.group(1) and 'youtube' not in m.group(1), 'index.html: 읽기 글 화면에 영상 카드 없음')
    check('checkSubjectComplete' in js and 'markSubStamp' in js, 'index.html: 완료 판정 함수')
    m = re.search(r'function awardQuiz\(sid, qi\)\s*\{(.*?)\n\}', js, re.S)
    check(m and 'checkSubjectComplete' in m.group(1) and 'pushStampFor' not in m.group(1),
          'index.html: awardQuiz는 다 맞혔을 때만 완료 도장(checkSubjectComplete)')
    m = re.search(r'function awardSpeak\(sid, si\)\s*\{(.*?)\n\}', js, re.S)
    check(m and 'pushStampFor' not in m.group(1), 'index.html: 따라 말하기만으로 완료 도장을 올리지 않음')
    check('solved >= idxs.length' in js, 'index.html: 완료 = 오늘 문제 전부 맞힘')
    check(re.search(r"PER_DAY\s*=\s*\{\s*history:\s*2\b", js) is not None, 'index.html: PER_DAY.history = 2')
    check(re.search(r"PER_DAY\s*=\s*\{.*?hero:\s*3", js) is not None, 'index.html: PER_DAY.hero = 3')
    check(re.search(r"const DAILY_SENTENCES = 3;", js) is not None, 'index.html: DAILY_SENTENCES = 3')
    check("'읽기 + ' + prog.total + '문제'" in js, 'index.html: 홈 카드에 오늘 문제 수(읽기 + N문제)')
    check("'문장 ' + ix.length + ' + 퀴즈 ' + ix.length" in js, 'index.html: 홈 카드에 영어 문장·퀴즈 수')
    check("prog.solved + '/' + prog.total" in js, 'index.html: 홈 카드에 진행률(x/y 진행 중)')
    check(re.search(r"HISTORY_START\s*=\s*'%s'" % HISTORY_START, js) is not None, 'index.html: 한국사 시작일 %s' % HISTORY_START)
    check(re.search(r"SB_URL = 'https://[a-z0-9]+\.supabase\.co'", js) is not None and 'kids_study_stamps' in js,
          'index.html: Supabase 연동(kids_study_profiles/stamps) 유지')
    check('kidsStudyApp.snake.v1' in js and "emoji: '🐍'" in js, 'index.html: 찬우 🐍 캐릭터 유지')
    check("'p1', name: '찬우'" in js, 'index.html: 기본 자리 고정(state.joined) 유지')

    sw = open(SW, encoding='utf-8').read()
    m_ver = re.search(r"kids-study-app-v(\d+)", sw)
    check(m_ver is not None and int(m_ver.group(1)) >= 7,
          'sw.js: 캐시 버전 v%s(>=7)' % (m_ver.group(1) if m_ver else '?'))

    # index.html의 BANKS가 videos.json + build.py 결과와 같은지
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_mod', os.path.join(ROOT, 'tools', 'build.py'))
    # build.py는 import 시 main()을 실행하므로 본문만 잘라 실행
    bsrc = open(os.path.join(ROOT, 'tools', 'build.py'), encoding='utf-8').read()
    bsrc = re.sub(r'\nmain\(\)\s*$', '\n', bsrc)
    ns = {'__name__': 'build_probe', '__file__': os.path.join(ROOT, 'tools', 'build.py')}
    exec(compile(bsrc, 'build.py', 'exec'), ns)
    data = json.load(open(VIDEOS, encoding='utf-8'))
    banks = {k: [ns['clean'](v) for v in data['subjects'].get(k, [])] for k in ns['ORDER']}
    body = 'const BANKS = ' + json.dumps(banks, ensure_ascii=False, indent=0).replace('\n', ' ') + ';'
    embedded = re.search(r'/\*__BANKS_START__\*/\n(.*)\n/\*__BANKS_END__\*/', html, re.S).group(1)
    check(embedded == body, 'index.html: BANKS가 videos.json과 동기화(tools/build.py 실행 결과와 동일)')
    check('"essay":' in embedded and '"topic":' in embedded and '"vocab":' in embedded,
          'index.html: BANKS에 essay·topic·vocab 포함')

    return html


def test_downloads_copy(html):
    if not os.path.exists(DOWNLOADS_COPY):
        FAIL.append('downloads/초1_공동학습_웹앱_틀.html: 파일 없음')
        return
    same = open(DOWNLOADS_COPY, encoding='utf-8').read() == html
    check(same, 'downloads/초1_공동학습_웹앱_틀.html: index.html과 동일')


def main():
    data = json.load(open(VIDEOS, encoding='utf-8'))
    js = re.search(r'<script>(.*)</script>', open(INDEX, encoding='utf-8').read(), re.S).group(1)
    cfg = parse_cfg(js)
    test_math()
    totals = test_videos(data)
    test_english(cfg)
    test_rotation(data, cfg)
    html = test_index()
    test_downloads_copy(html)
    print('\n'.join('✅ ' + m for m in PASS))
    if FAIL:
        print('\n' + '\n'.join('❌ ' + m for m in FAIL))
        print('\n실패 %d건 / 통과 %d건' % (len(FAIL), len(PASS)))
        sys.exit(1)
    print('\n전부 통과 %d건' % len(PASS))


main()
