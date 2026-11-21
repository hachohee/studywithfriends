function dailyCardHTML(sub) {
  const item = dailyItem(sub);
  const done = quizCount(state.activeId, sub.id) > 0;
  const q = item ? item.q : (sub.line || '');
  return '<button class="daily' + (done ? ' done' : '') + '" data-action="open-subject" data-id="' + sub.id + '">' +
    '<span class="d-top"><span class="d-ico" style="--soft:' + sub.soft + '">' + sub.emoji + '</span>' +
      '<span class="d-name">' + sub.name + '</span>' +
      '<span class="d-badge">' + (done ? '🏅 오늘 완료' : '1문제 + 영상 1') + '</span></span>' +
    '<span class="d-q">' + esc(q) + '</span>' +
    '<span class="d-vid">🎬 ' + esc(item ? item.video.title : '영상 준비 중') + (item ? ' · ' + item.video.dur_label : '') + '</span>' +
  '</button>';
}

function inviteCardHTML() {
  return '<div class="invite-card">' +
    '<div class="ic-top"><span class="ic-emoji">👋</span>' +
      '<div><b>친구 초대하기</b><small>링크만 보내면 이름 적고 바로 시작!</small></div></div>' +
    '<button class="btn-primary" data-action="invite-open" style="margin-top:10px;padding:13px">🔗 초대 링크 만들기</button>' +
    (appBaseUrl() ? '' : '<p class="note" style="text-align:left">파일로 열었을 땐 링크 공유가 안 돼요. https 주소로 열어 주세요.</p>') +
  '</div>';
}

function renderHome() {
  const me = activeProfile();
  const todayStamp = dayStamps(state.activeId);
  const doneSubjects = SUBJECTS.filter(s => quizCount(state.activeId, s.id) > 0).length;
  const greet =
    doneSubjects === 0 ? '오늘 첫 문제부터 풀어 볼까?' :
    doneSubjects >= 5 ? '5과목 전부 도장! 오늘 최고야 🎉' :
    doneSubjects >= 3 ? doneSubjects + '과목 완료! 기세 좋다 🔥' :
    '오늘 ' + doneSubjects + '과목 완료! 조금만 더 가자 💪';

  const welcome = welcomeName
    ? '<div class="welcome"><span>🎉</span><div><b>' + esc(welcomeName) + '</b>야, 반가워! 아래 오늘의 문제부터 하나 풀어 봐 😊</div>' +
      '<button data-action="dismiss-welcome" aria-label="닫기">✕</button></div>'
    : '';

  $('#view-home').innerHTML =
    '<div class="hero">' +
      '<div class="hero-top"><span class="hero-date">' + dateLabel() + '</span>' +
        '<span class="hero-date">🏅 누적 ' + totalStamps(state.activeId) + '개</span></div>' +
      '<div class="hero-hi">' + greeting() + ', ' + esc(me.name) + '! ' + me.emoji + '</div>' +
      '<div class="hero-sub">' + greet + '</div>' +
      '<div class="hero-stats">' +
        '<span class="hero-stat"><em>🏅</em>오늘 ' + todayStamp + '개</span>' +
        '<span class="hero-stat"><em>📖</em>' + doneSubjects + '/5 과목 완료</span>' +
      '</div>' +
    '</div>' +
    welcome +

    '<div class="sec-head"><h3>🎯 오늘의 학습 5과목</h3><span class="more">하루 1문제 + 영상 1개</span></div>' +
    '<div class="subj-grid">' + SUBJECTS.map(dailyCardHTML).join('') + '</div>' +

    inviteCardHTML() +

    '<div class="sec-head"><h3>우리 반 오늘</h3>' +
      '<button class="more" data-action="go" data-view="board">도장판 →</button></div>' +
    boardMiniHTML();

  renderTopbar();
}

