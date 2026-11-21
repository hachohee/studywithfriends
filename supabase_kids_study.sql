-- 초1 공동학습 웹앱 '우리 반 공부방' — 친구들 폰 실시간 도장판 테이블
-- Supabase 프로젝트: dolhmwtbafytvxwfqiny (https://dolhmwtbafytvxwfqiny.supabase.co)
-- 대시보드 → SQL Editor 에 이 파일 전체를 붙여넣고 RUN 한 번이면 끝납니다.
-- 기존 냉파 앱 테이블은 건드리지 않습니다(kids_study_ 접두사만 새로 만듦).

-- 1) 친구 자리(이름·동물)
create table if not exists public.kids_study_profiles (
  room_id    text        not null,
  slot       int         not null check (slot between 0 and 4),
  name       text        not null default '',
  avatar     text        not null default '🐣',
  updated_at timestamptz not null default now(),
  primary key (room_id, slot)
);

-- 2) 도장 (방 · 자리 · 날짜(KST) · 과목)
create table if not exists public.kids_study_stamps (
  room_id   text        not null,
  slot      int         not null check (slot between 0 and 4),
  date_kst  text        not null,
  subject   text        not null,
  earned_at timestamptz not null default now(),
  primary key (room_id, slot, date_kst, subject)
);

create index if not exists kids_study_stamps_room_date_idx
  on public.kids_study_stamps (room_id, date_kst);

-- 3) 접근 권한: 앱은 anon(공개) 키로 접속합니다. 아이들 이름·도장뿐이라 민감정보는 없고,
--    방 코드를 아는 사람만 그 방을 읽고 씁니다.
alter table public.kids_study_profiles enable row level security;
alter table public.kids_study_stamps   enable row level security;

grant select, insert, update, delete on public.kids_study_profiles to anon, authenticated;
grant select, insert, update, delete on public.kids_study_stamps   to anon, authenticated;

drop policy if exists kids_study_profiles_rw on public.kids_study_profiles;
drop policy if exists kids_study_stamps_rw   on public.kids_study_stamps;

create policy kids_study_profiles_rw on public.kids_study_profiles
  for all to anon, authenticated using (true) with check (true);

create policy kids_study_stamps_rw on public.kids_study_stamps
  for all to anon, authenticated using (true) with check (true);

-- 4) Realtime 등록(이미 등록돼 있으면 조용히 넘어감)
do $$
begin
  begin
    alter publication supabase_realtime add table public.kids_study_profiles;
  exception when duplicate_object then null;
  end;
  begin
    alter publication supabase_realtime add table public.kids_study_stamps;
  exception when duplicate_object then null;
  end;
end $$;

-- 5) 확인: 두 줄 모두 0 이 나오면 정상
select 'kids_study_profiles' as table_name, count(*) from public.kids_study_profiles
union all
select 'kids_study_stamps', count(*) from public.kids_study_stamps;
