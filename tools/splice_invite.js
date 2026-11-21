/* ─────────────────────────── 11-b. 친구 초대 · 참여 ─────────────────────────── */

let welcomeName = '';
let joinSlot = 0;
let joinPick = '';

function appBaseUrl() {
  try {
    const u = location.origin + location.pathname;
    return /^https?:/.test(u) ? u.replace(/index\.html$/, '') : '';
  } catch (e) { return ''; }
}
function inviteUrl(slot) { return appBaseUrl() + '?join=1&slot=' + (slot + 1); }

function inviteMessage(slot) {
  const p = state.profiles[slot];
  return '안녕! 우리 애들 공부방 초대 링크야 📚\n' +
    '하루 1문제 + 딱 맞는 영상 1개, 5과목(수학·영어·한국사·위인·시사상식)이에요.\n' +
    '아래 링크 누르고 이름이랑 동물만 고르면 바로 시작!' +
    (p && p.name && p.name.indexOf('친구') !== 0 ? ' (' + p.name + ' 자리)' : '') + '\n' +
    inviteUrl(slot);
}

async function copyText(text, btn, okMsg) {
  let ok = false;
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text); ok = true;
    }
  } catch (e) { ok = false; }
  if (!ok) {
    try {
      const ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', '');
      ta.style.position = 'fixed'; ta.style.top = '-1000px'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, text.length);
      ok = document.execCommand('copy'); ta.remove();
    } catch (e) { ok = false; }
  }
  if (ok) {
    if (btn) fx('📋 복사!', btn);
    toast(okMsg || '복사했어요! 단톡방에 붙여넣기 하세요 📋');
  } else {
    showManualCopy(text);
  }
}

async function shareText(text, btn) {
  if (navigator.share) {
    try { await navigator.share({ title: '우리 반 공부방', text: text }); return; } catch (e) {
      if (e && e.name === 'AbortError') return;
    }
  }
  await copyText(text, btn, '초대 링크를 복사했어요! 단톡방에 붙여넣기 하세요 📋');
}

function nextEmptySlot() {
  const i = state.profiles.findIndex(p => !p.name || p.name.indexOf('친구') === 0 || p.name === '');
  return i >= 0 ? i : 0;
}

function openInvite() {
  const url = appBaseUrl();
  const rows = state.profiles.map((p, i) =>
    '<div class="slot-row"><span class="sr-ava">' + p.emoji + '</span>' +
      '<span class="sr-name">' + esc(p.name) + '</span>' +
      '<span class="sr-tag">' + (i + 1) + '번</span>' +
      '<button data-action="invite-share" data-slot="' + i + '">공유</button></div>'
  ).join('');
  showModal(
    '<h3>👋 친구 초대 링크</h3>' +
    '<p>' + (url ? '자리별 링크예요. 보내려는 친구 자리의 [공유]를 누르면 단톡방 문구까지 한 번에 돼요.' : '주소(https)로 열었을 때만 링크를 만들 수 있어요.') + '</p>' +
    rows +
    '<div class="m-btns">' +
      '<button data-action="close-modal">닫기</button>' +
      '<button class="primary" data-action="invite-copy" data-slot="' + nextEmptySlot() + '">빈자리 링크 복사</button>' +
    '</div>' +
    '<p class="note" style="text-align:left">친구가 링크를 열면 이름·동물을 고르는 화면이 나오고, 고른 자리에 그 친구가 들어와요.</p>'
  );
}

function showModal(html) {
  const wrap = $('#modalWrap');
  wrap.hidden = false;
  wrap.className = 'modal-bg';
  wrap.innerHTML = '<div class="modal" role="dialog" aria-modal="true">' + html + '</div>';
}

/* ── 참여 화면 ── */
function joinSlotFromUrl() {
  const m = /[?&]slot=(\d+)/.exec(location.search);
  const n = m ? Number(m[1]) : (nextEmptySlot() + 1);
  return Math.min(5, Math.max(1, n || 1)) - 1;
}

function startJoin() {
  welcomeName = '';
  joinSlot = joinSlotFromUrl();
  joinPick = '';
  showView('join');
}

function renderJoin() {
  const p = state.profiles[joinSlot] || state.profiles[0];
  const used = state.profiles.filter(x => x.id !== p.id).map(x => x.emoji);
  const emojis = EMOJI_CHOICES.map(e =>
    '<button class="' + (joinPick === e ? 'on' : '') + (used.indexOf(e) >= 0 ? ' taken' : '') + '"' +
    ' data-action="join-emoji" data-e="' + e + '"' + (used.indexOf(e) >= 0 ? ' aria-disabled="true"' : '') + '>' + e + '</button>'
  ).join('');
  const takenName = (p.name && p.name.indexOf('친구') !== 0) ? p.name : '';

  $('#view-join').innerHTML =
    '<div class="join-wrap">' +
      '<div class="join-hero">' + (joinPick || '🐣') + '</div>' +
      '<h1>반가워! 우리 반 공부방에 초대됐어 🎉</h1>' +
      '<p class="join-sub">이름(별명)을 적고, 내 동물 친구를 골라 줘.<br>내 자리는 <b>' + (joinSlot + 1) + '번</b>으로 준비돼 있어!' +
        (takenName ? '<br>(지금 ' + esc(takenName) + ' 이름이 있어요 — 새 이름으로 바꿀 수 있어)' : '') + '</p>' +

      '<div class="join-field">' +
        '<label>내 이름</label>' +
        '<input id="joinName" maxlength="8" placeholder="예: 서준" autocomplete="off" autocapitalize="off" spellcheck="false" value="">' +
        '<div class="join-err" id="joinErr"></div>' +
      '</div>' +

      '<div class="join-field">' +
        '<label>내 동물 친구 (하나만 골라 줘)</label>' +
        '<div class="emoji-grid">' + emojis + '</div>' +
      '</div>' +

      '<button class="btn-primary" data-action="join-submit">이 이름으로 시작하기 🚀</button>' +
      '<button class="btn-ghost" data-action="join-later">이미 들어왔어요 → 그냥 볼래요</button>' +
      '<p class="note">이름과 도장은 이 폰에만 저장돼요. 인터넷 없이도 열려요.</p>' +
    '</div>';

  const el = $('#joinName');
  if (el) {
    el.addEventListener('input', () => {
      const err = $('#joinErr'); if (err) err.textContent = '';
    });
  }
}

function joinSubmit() {
  const input = $('#joinName');
  const err = $('#joinErr');
  const name = (input ? input.value : '').trim().replace(/\s+/g, ' ');
  const len = Array.from(name).length;
  if (!len) { if (err) err.textContent = '이름(별명)을 적어 줘!'; if (input) input.focus(); return; }
  if (len > 8) { if (err) err.textContent = '이름은 8글자까지 쓸 수 있어요.'; return; }
  const dup = state.profiles.some(p => p.id !== state.profiles[joinSlot].id && p.name && p.name.trim() === name);
  if (dup) { if (err) err.textContent = '「' + name + '」는 이미 친구가 쓰고 있어. 다른 이름으로 해 줘!'; return; }
  if (!joinPick) { if (err) err.textContent = '동물 친구를 하나 골라 줘!'; return; }
  const used = state.profiles.filter(p => p.id !== state.profiles[joinSlot].id).map(p => p.emoji);
  if (used.indexOf(joinPick) >= 0) { if (err) err.textContent = '그 동물은 다른 친구가 쓰고 있어. 다른 동물로 골라 줘!'; return; }

  const p = state.profiles[joinSlot];
  p.name = name;
  p.emoji = joinPick;
  state.activeId = p.id;
  persist();
  try { history.replaceState(null, '', location.pathname); } catch (e) {}
  welcomeName = name;
  showView('home');
  toast(name + '야, 반가워! 🎉');
}

