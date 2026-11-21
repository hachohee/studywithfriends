function renderSubject() {
  const sub = SUBJECT_BY_ID[currentSubjectId];
  if (!sub) { showView('study'); return; }
  const head =
    '<button class="back-btn" data-action="back" aria-label="뒤로">←</button>' +
    '<div class="detail-head" style="--soft:' + sub.soft + '">' +
      '<span class="d-ico">' + sub.emoji + '</span>' +
      '<div><h2>' + sub.name + '</h2><p>' + esc(sub.line) + '</p></div>' +
    '</div>' +
    '<div class="seg2">' +
      '<button class="' + (subjectTab === 'today' ? 'on' : '') + '" data-action="subtab" data-tab="today">🎯 오늘</button>' +
      '<button class="' + (subjectTab === 'learn' ? 'on' : '') + '" data-action="subtab" data-tab="learn">📚 배우기</button>' +
      '<button class="' + (subjectTab === 'review' ? 'on' : '') + '" data-action="subtab" data-tab="review">🔁 복습</button>' +
    '</div>';

  const body = subjectTab === 'today' ? todayHTML(sub) : (subjectTab === 'learn' ? learnHTML(sub) : quizHTML(sub));
  $('#view-subject').innerHTML = head + body;
  renderTopbar();
}

/* ── 오늘의 학습(문제 1 + 영상 1) ── */
function videoCardHTML(v, unlocked, anchor) {
  if (!v) return '';
  return '<a class="vidcard' + (unlocked ? ' unlock' : '') + '"' + (anchor ? ' id="' + anchor + '"' : '') +
    ' href="' + v.url + '" target="_blank" rel="noopener noreferrer">' +
    '<span class="v-thumb">▶️</span>' +
    '<span class="v-body"><span class="v-t">' + esc(v.title) + '</span>' +
      '<span class="v-d">' + esc(v.ch) + ' · ' + v.dur_label + ' · 유튜브에서 보기</span></span>' +
    '<span class="v-go">↗</span></a>';
}

function todayHTML(sub) {
  const item = dailyItem(sub);
  if (!item) {
    return '<div class="qcard"><div class="result"><div class="big">🌱</div>' +
      '<h3>이 과목 영상은 준비 중이에요</h3><p>검증된 영상이 아직 없어서 오늘은 배우기 카드로 공부해요.</p></div></div>' +
      '<button class="btn-ghost" data-action="subtab" data-tab="learn">📚 배우기 카드 보기</button>';
  }
  const qi = dailyIndex(sub);
  const rec = (subRec(state.activeId, sub.id) || { q: {} }).q || {};
  const got = !!rec[qi];

  let h = '<div class="keyline" style="--soft:' + sub.soft + ';--deep:' + sub.deep + ';--line2:' + sub.color + '33">' +
    '<span class="k-label">오늘의 핵심 한 줄</span>' + esc(item.key) + '</div>';

  if (sub.id === 'english') h += todaySentenceHTML();

  h += '<div class="sec-head"><h3>🎯 오늘의 퀴즈</h3><span class="more">1문제</span></div>';
  h += todayQuizHTML(sub, item, qi, got);
  h += '<div class="sec-head"><h3>🎬 오늘의 영상</h3><span class="more">퀴즈와 이어지는 영상</span></div>';
  h += videoCardHTML(item.video, got, 'today-video');
  h += '<p class="note">' + esc(item.video.summary || '') + '</p>';
  h += got
    ? '<p class="note" style="color:#0F6B4C;font-weight:900">🏅 도장 받았어요! 영상으로 한 번 더 확인해 봐요.</p>'
    : '<p class="note">영상을 먼저 보고 문제를 풀어도 좋아요 😊</p>';
  h += '<button class="btn-ghost" data-action="subtab" data-tab="review" style="margin-top:14px">🔁 지난 문제 전체 복습 (' + sub.quiz.length + '개)</button>';
  return h;
}

function todayQuizHTML(sub, item, qi, got) {
  const picked = (quiz.i === qi) ? quiz.picked : null;
  let h = '<div class="qcard">' +
    '<div class="qnum">오늘의 문제 · ' + dateLabel() + '</div>' +
    '<div class="qtext">' + esc(item.q) + '</div>' +
    '<div class="opts">' + item.opts.map((o, i) => {
      let cls = '';
      if (picked !== null) {
        if (i === item.ans) cls = 'right';
        else if (i === picked) cls = 'wrong';
      }
      return '<button class="opt ' + cls + '" data-action="answer" data-i="' + i + '"' + (picked !== null ? ' disabled' : '') + '>' +
        '<span class="num">' + (i + 1) + '</span><span>' + esc(o) + '</span></button>';
    }).join('') + '</div>';

  if (picked !== null) {
    const ok = picked === item.ans;
    h += '<div class="feedback ' + (ok ? 'ok' : 'no') + '">' +
      '<span class="fb-t">' + (ok ? (got ? '정답이야! 🏅 도장 받았어요' : '정답이야! 🏅 도장 +1') : '아쉬워! 정답은 "' + esc(item.opts[item.ans]) + '"') + '</span>' +
      esc(item.why) + '</div>' +
      '<button class="btn-primary" data-action="scroll-video">🎬 오늘의 영상 보러 가기</button>';
  }
  h += '</div>';
  return h;
}

function todaySentenceHTML() {
  const idx = dailySentIdx();
  const s = ALL_SENTENCES[idx];
  const done = !!(((subRec(state.activeId, 'english', todayKey()) || {}).s) || {})[idx];
  return '<div class="sec-head"><h3>🗣️ 오늘의 영어 문장</h3><span class="more">듣고 따라 말해요</span></div>' +
    '<article class="sent ' + (done ? 'done' : '') + '" data-sent="' + idx + '">' +
      '<div class="sent-head"><span class="sent-e">' + s.emoji + '</span>' +
        '<div class="sent-main"><div class="sent-en">' + esc(s.en) + '</div>' +
          '<div class="sent-ko">' + esc(s.ko) + '</div>' +
          '<div class="sent-tip">🗣️ ' + esc(s.tip) + '</div></div></div>' +
      '<div class="sent-btns">' +
        '<button data-action="say" data-idx="' + idx + '">🔊 듣기</button>' +
        '<button class="mic" data-action="practice" data-idx="' + idx + '">🎤 따라 말하기</button></div>' +
      '<div class="practice" hidden></div>' +
      '<div class="sent-stamp">🏅 오늘 따라읽기 도장 받았어요</div>' +
    '</article>';
}

function learnHTML(sub) {
  let h = '<div class="keyline" style="--soft:' + sub.soft + ';--deep:' + sub.deep + ';--line2:' + sub.color + '33">' +
    '<span class="k-label">핵심 한 줄</span>' + esc(sub.keyline) + '</div>';

  if (sub.id === 'english') {
    h += englishHTML();
  } else {
    h += sub.stories.map(st =>
      '<div class="story"><span class="st-e">' + st.e + '</span>' +
      '<div><div class="st-t">' + esc(st.t) + '</div><div class="st-d">' + esc(st.d) + '</div></div></div>'
    ).join('');
  }
  h += '<div class="sec-head"><h3>🎬 이 과목 영상 모음</h3><span class="more">' + bankOf(sub).length + '편 · 10분 이내</span></div>' +
    videoListHTML(sub);
  return h;
}

function videoListHTML(sub) {
  const b = bankOf(sub);
  if (!b.length) return '<p class="note">아직 검증된 영상이 없어요.</p>';
  return '<div class="yt-list">' + b.map(it =>
    '<a class="yt" href="' + it.url + '" target="_blank" rel="noopener noreferrer">' +
      '<span class="yt-ico">▶️</span>' +
      '<span class="yt-t">' + esc(it.title) + '<span class="yt-d">' + esc(it.ch) + ' · ' + it.dur_label + '</span></span>' +
      '<span class="yt-go">↗</span></a>'
  ).join('') + '</div>';
}

function ytListHTML(sub) {
  return sub.links.map(y => {
    const url = y.url ? y.url : yt(y.q);
    const isSite = !!y.url;
    return '<a class="yt' + (isSite ? ' site' : '') + '" href="' + url + '" target="_blank" rel="noopener noreferrer">' +
      '<span class="yt-ico">' + (isSite ? '🌐' : '▶️') + '</span>' +
      '<span class="yt-t">' + esc(y.label) + (y.d ? '<span class="yt-d">' + esc(y.d) + '</span>' : '') + '</span>' +
      '<span class="yt-go">↗</span></a>';
  }).join('');
}

