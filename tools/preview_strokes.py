#!/usr/bin/env python3
"""한자 획 좌표 미리보기 — 획마다 다른 색으로 그려 0~100 상자 안 모양을 눈으로 확인한다.
   실행: python3 tools/preview_strokes.py <출력파일.png>
"""
import sys, json
from PIL import Image, ImageDraw

CHARS = {
    '百': [
        [28, 20, 74, 20],
        [52, 22, 46, 32],
        [46, 32, 46, 78],
        [46, 36, 72, 36, 72, 78],
        [48, 54, 70, 54],
        [42, 78, 74, 78],
    ],
    '千': [
        [58, 16, 44, 26],
        [22, 34, 78, 34],
        [50, 34, 50, 84],
    ],
    '万': [
        [20, 24, 80, 24],
        [22, 42, 58, 42, 58, 76, 50, 72],
        [78, 32, 34, 84],
    ],
}

COLORS = ['#e63946', '#1d3557', '#2a9d8f', '#e9c46a', '#9b5de5', '#f4a261', '#000000']

W = 320
img = Image.new('RGB', (W * len(CHARS), W + 40), 'white')
dr = ImageDraw.Draw(img)

for k, (ch, strokes) in enumerate(CHARS.items()):
    ox = k * W
    for i, poly in enumerate(strokes):
        pts = []
        for j in range(0, len(poly), 2):
            pts.append((ox + 20 + poly[j] * (W - 40) / 100, 20 + poly[j + 1] * (W - 40) / 100))
        dr.line(pts, fill=COLORS[i % len(COLORS)], width=7, joint='curve')
        mid = pts[-1]
        dr.text((mid[0] + 5, mid[1] - 16), str(i + 1), fill=COLORS[i % len(COLORS)])
    dr.rectangle([ox + 20, 20, ox + W - 20, W - 20], outline='#cccccc')
    dr.text((ox + 20, W - 20), ch, fill='black')

out = sys.argv[1] if len(sys.argv) > 1 else 'strokes.png'
img.save(out)
print('saved', out)
