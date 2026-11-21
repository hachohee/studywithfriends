#!/usr/bin/env python3
"""YouTube public-data helper: search, video info (duration/channel), timedtext captions."""
import urllib.request, urllib.parse, json, re, gzip, html, sys, time

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')


def _get(url, data=None, headers=None):
    h = {'User-Agent': UA, 'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=40) as r:
        d = r.read()
        enc = (r.headers.get('Content-Encoding') or '').lower()
        if enc == 'gzip':
            d = gzip.decompress(d)
        elif enc == 'br':
            try:
                import brotli
                d = brotli.decompress(d)
            except Exception:
                pass
        return d.decode('utf-8', 'replace')


def _runs_text(node):
    if not node:
        return ''
    if 'simpleText' in node:
        return node['simpleText']
    return ''.join(r.get('text', '') for r in node.get('runs', []))


def search(q, filt='EgIQAQ%3D%3D', limit=25):
    """filt: EgIQAQ%3D%3D = video only. Returns list of dicts."""
    url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(q)
    if filt:
        url += '&sp=' + filt
    page = _get(url)
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', page, re.S)
    if not m:
        return []
    data = json.loads(m.group(1))
    out = []

    def walk(n):
        if isinstance(n, dict):
            if 'videoRenderer' in n:
                v = n['videoRenderer']
                vid = v.get('videoId')
                if vid:
                    length = _runs_text(v.get('lengthText'))
                    out.append({
                        'id': vid,
                        'title': _runs_text(v.get('title')),
                        'channel': _runs_text(v.get('ownerText')),
                        'channel_id': (((v.get('ownerText') or {}).get('runs') or [{}])[0].get('navigationEndpoint', {})
                                       .get('browseEndpoint', {}).get('browseId', '')),
                        'length': length,
                        'dur_s': _len_to_s(length),
                        'views': _runs_text(v.get('viewCountText')),
                        'published': _runs_text(v.get('publishedTimeText')),
                    })
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(data)
    # dedupe keep order
    seen, res = set(), []
    for v in out:
        if v['id'] not in seen:
            seen.add(v['id'])
            res.append(v)
    return res[:limit]


def _len_to_s(t):
    if not t:
        return None
    parts = [p for p in t.split(':')]
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    s = 0
    for p in parts:
        s = s * 60 + p
    return s


def info(vid):
    page = _get('https://www.youtube.com/watch?v=' + vid + '&hl=ko')
    out = {'id': vid, 'url': 'https://www.youtube.com/watch?v=' + vid}
    m = re.search(r'"videoDetails":\{(.*?)"isLiveContent"', page, re.S)
    if m:
        blob = '{' + m.group(1) + '"isLiveContent":false}'
        try:
            d = json.loads(blob)
            out.update({
                'title': d.get('title'),
                'channel': d.get('author'),
                'channel_id': d.get('channelId'),
                'dur_s': int(d.get('lengthSeconds') or 0),
                'desc': (d.get('shortDescription') or '')[:1500],
            })
        except Exception:
            pass
    if 'dur_s' not in out:
        mm = re.search(r'"lengthSeconds":"(\d+)"', page)
        if mm:
            out['dur_s'] = int(mm.group(1))
    caps = {}
    for m2 in re.finditer(r'"captionTracks":\[(\{.*?\})\]', page, re.S):
        try:
            arr = json.loads('[' + m2.group(1) + ']')
        except Exception:
            continue
        for c in arr:
            caps[c.get('languageCode')] = c
    out['caps'] = {k: {'kind': v.get('kind', ''), 'name': _runs_text(v.get('name'))} for k, v in caps.items()}
    out['_capurls'] = {k: v.get('baseUrl') for k, v in caps.items()}
    out['dur_label'] = _fmt(out.get('dur_s'))
    return out


def _fmt(s):
    if not s:
        return ''
    return '%d:%02d' % (s // 60, s % 60)


def transcript(vid, prefer=('ko', 'en')):
    inf = info(vid)
    urls = inf.get('_capurls') or {}
    pick = None
    for lang in prefer:
        for k in urls:
            if k == lang:
                pick = urls[k]
                break
        if pick:
            break
        for k in urls:
            if k.startswith(lang):
                pick = urls[k]
                break
        if pick:
            break
    if not pick:
        return inf, ''
    xml = _get(pick)
    txt = re.sub(r'<br\s*/?>', ' ', xml)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = html.unescape(txt)
    txt = re.sub(r'\s+', ' ', txt).strip()
    return inf, txt


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'search':
        for v in search(' '.join(sys.argv[2:])):
            print(json.dumps(v, ensure_ascii=False))
    elif cmd == 'info':
        inf = info(sys.argv[2])
        inf.pop('_capurls', None)
        print(json.dumps(inf, ensure_ascii=False, indent=1))
    elif cmd == 'tr':
        inf, txt = transcript(sys.argv[2])
        print('TITLE:', inf.get('title'))
        print('CH:', inf.get('channel'), '| DUR:', inf.get('dur_label'), '| CAPS:', inf.get('caps'))
        print('DESC:', (inf.get('desc') or '')[:600])
        print('TRANSCRIPT:', txt[:6000])
