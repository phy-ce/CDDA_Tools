**한국어** | [English](README.en.md)

# Cataclysm 설치 & 버전 매니저 (CDDA / CDBN)

Windows용 GUI. 공식 GitHub 릴리스에서 원하는 버전을 받아 설치하고,
설치된 여러 버전을 목록에서 골라 실행·삭제·모드 관리한다.

**두 게임 지원**:
- **CDDA** — Cataclysm: Dark Days Ahead (본가)
- **CDBN** — Cataclysm: Bright Nights (포크/변형판)

게임마다 설치 폴더가 분리된다 (`~/Games/Cataclysm-DDA`, `~/Games/Cataclysm-BN`).
**언어 / Language**: 창 맨 위 토글로 **한국어 / English** 실시간 전환.

## 설치 / 실행

**방법 1 — exe (Python 불필요)**
[Releases](../../../releases) 페이지에서 최신 `CDDA-Manager.exe` 를 받아 더블클릭.

**방법 2 — 소스로 실행** (Python만 있으면 됨, Windows에는 보통 tkinter 포함)
```
cdda_installer.pyw  더블클릭
```
또는: `python cdda_installer.pyw`

> 모던 테마는 선택 의존성 **ttkbootstrap**으로 적용된다 (`pip install ttkbootstrap`).
> 없으면 표준 tkinter 모양으로 자동 폴백하므로 그냥 실행해도 동작한다. exe 빌드본엔 포함됨.
> 창 상단 우측 토글로 **밝게 / 다크 / 보라** 테마를 실시간 전환할 수 있다 (ttkbootstrap 있을 때).

## 화면 구성 (탭 2개)

### [Library] 탭 — 첫 화면
**CDDA·CDBN 모든 설치본**이 한 표에 통합되어 보인다 (게임 / 버전 / 채널 / 설치일).
- **더블클릭** 또는 **▶ 실행** : 해당 버전 게임 실행
- **🧩 콘텐츠** : 선택한 버전의 콘텐츠 관리 창 열기 (모드/사운드팩/타일셋/폰트, 아래 참고)
- **폴더 열기** : 설치 폴더 탐색기로 열기
- **🗑 삭제** : 버전 + 세이브 완전 삭제

### [Install] 탭
1. **게임**: CDDA / CDBN 선택
2. **채널**: experimental(매일 빌드) / 정식 릴리스(stable)
3. **버전**: 드롭다운에서 특정 빌드 선택
4. **에디션**: 그래픽+사운드(권장) / 그래픽만 / 터미널 (디버그 심볼 `pdb` 는 자동 제외)
5. **설치 기본 폴더**: 이 폴더 안에 버전별 하위 폴더가 자동 생성됨

설치하면 `기본폴더/<버전태그>/` 에 풀린다. 이미 설치된 버전은 버튼이 **Installed ✓** 로 바뀐다.

## 콘텐츠 관리 (모드 / 사운드팩 / 타일셋 / 폰트)

Library 탭에서 버전을 고르고 **🧩 콘텐츠**를 누르면 탭 4개짜리 관리 창이 열린다.
번들·추가 항목이 **모두** 보이고 "구분" 열로 표시되며, **기본(번들) 항목은 삭제가 보호**되고
이 도구로 추가한 항목만 제거할 수 있다.

| 자원 | 설치 위치 | 식별 |
|---|---|---|
| 모드 | `data/mods/<폴더>/` | `modinfo.json` |
| 사운드팩 | `data/sound/<폴더>/` | `soundpack.txt` |
| 타일셋 | `gfx/<폴더>/` | `tileset.txt` |
| 폰트 | `data/font/*.ttf .otf .ttc` | 개별 파일 |

- **🌐 URL에서 추가** : GitHub 저장소 주소나 직접 zip(폰트는 .ttf 링크도) 입력 → 다운로드·설치.
- **➕ zip 추가 / 파일 추가** : 로컬 zip(폰트 탭은 폰트 파일도) 골라 추가.
- **🗑 제거** / **폴더 열기**

추가 시 zip 안에서 식별 파일(`modinfo.json`/`soundpack.txt`/`tileset.txt`)을 가진 폴더를,
폰트는 폰트 파일을 찾아 대상 폴더로 복사하고 `.cdda_added` 마커로 표시한다.
마커가 있는 항목만 "추가됨"으로 보고 삭제를 허용하며, 마커 없는 번들은 보호한다.

### 폰트 적용

CDDA는 `data/font/`에 파일이 있어도 **`config/fonts.json`이 가리키는 폰트만** 사용한다
(게임 내 폰트 선택기 없음). 폰트 탭 버튼:

- **🪟 시스템**: **Windows에 설치된 폰트**를 검색·복수 선택해 `data/font/`로 복사
- **➕ 파일 추가**: 로컬 폰트 파일/zip 추가
- **🅰 편집/적용**: 폰트와 크기를 게임 설정에 반영

**🅰 편집/적용** 동작:
1. 적용할 영역 선택 — 기본(게임 텍스트) / 메뉴(GUI) / 지도 / 전체지도
2. (선택) **폰트 크기** 입력 — 폭(FONT_WIDTH)/높이(FONT_HEIGHT)/크기(FONT_SIZE)
3. 적용하면:
   - **글꼴**: `config/fonts.json`에 그 폰트를 주 글꼴로 맨 앞에 넣음 (기존은 폴백 유지)
   - **크기**: `config/options.json`의 `FONT_WIDTH/HEIGHT/SIZE` 값을 변경
   - 이전 설정은 각각 `.bak`로 백업, 게임 재시작 시 반영

> 기본값: 글꼴은 4영역 모두 **Terminus.ttf**(+unifont 폴백), 크기는 **폭 8 / 높이 16 / 크기 16**.
> 폭·높이는 글자 한 칸(셀)의 픽셀 크기, 크기는 칸 안 글리프 렌더링 크기다 (보통 같이 올림).
> 글꼴은 4영역(기본/메뉴/지도/전체지도) 각각 다르게 지정 가능하고, 크기는 기본/지도/전체지도
> 3세트가 따로다(메뉴는 별도 크기 없음). 우리 창은 글꼴 4영역 + 기본 크기를 노출한다.

`config/fonts.json`은 첫 실행 시 `data/fontdata.json` 기본값으로, `config/options.json`도
첫 실행 시 생성된다. 형식은 CDDA 공식 문서/소스(`doc/user-guides/FONT_OPTIONS.md`,
`src/options.cpp`)를 따른다. 크기 입력은 `options.json`이 있어야(게임 1회 실행) 활성화된다.
기본 폰트(Terminus/unifont 등)는 삭제 보호된다.

> 참고: 지도/전체지도 폰트 크기 등 더 세밀한 설정은 게임 안 **Options → Graphics**에서도
> 그대로 조절할 수 있다 (둘 다 같은 `options.json`에 저장됨).

> CDDA는 중앙 콘텐츠 저장소/API가 없어 "목록을 띄워 고르는" 방식은 불가능하다.
> 대신 GitHub 주소나 zip/파일 링크로 받는다 (대부분 GitHub에 있다).

## 버전별 독립 세이브

각 버전이 자기 폴더 안에 독립적으로 설치되므로 세이브도 분리된다.
experimental 빌드는 세이브 호환이 자주 깨지는데, 이 구조라 서로 영향 없다.
(폴더마다 `.cdda_meta.json` 으로 버전·게임 정보를 기록해 Library 탭이 이를 읽는다.)

## 동작 원리

각 게임의 GitHub Releases API에서 릴리스 목록을 가져오고, Windows zip 에셋을
**이름으로 동적 파싱**한다 (CDDA·CDBN 이름 규칙을 모두 처리, `pdb` 디버그 심볼 제외).
정식(stable) 릴리스는 매일 올라오는 experimental에 밀려 목록 깊숙이 묻히므로,
`/releases/latest` + 알려진 정식 태그 직접 조회 방식으로 가져온다.
새 정식 메이저가 나오면 코드의 `GAMES[...]["stable_tags"]` 에 태그를 한 줄 추가하면 된다.

## .exe로 직접 빌드

```
pip install pyinstaller ttkbootstrap
pyinstaller --onefile --noconsole --name CDDA-Manager --collect-all ttkbootstrap cdda_installer.pyw
```
결과물은 `dist/CDDA-Manager.exe`. (`--collect-all ttkbootstrap` 으로 테마 리소스 포함)
`v*` 태그를 푸시하면 GitHub Actions(`.github/workflows/build.yml`)가 자동으로
exe를 빌드해 해당 Release에 첨부한다.

> `--onefile` exe는 백신이 가끔 오탐(false positive)할 수 있다 (PyInstaller 특성).

## 제한

- Windows 전용. Linux/macOS는 실행/폴더 열기 부분 수정 필요.
- 최신 experimental 빌드는 에셋 업로드 중일 수 있어 목록에서 자동 제외된다.
