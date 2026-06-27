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
각 탭에서 **이 도구로 추가한 항목만** 보인다 (게임 기본 번들은 제외).

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
폰트는 폰트 파일을 찾아 대상 폴더로 복사하고 `.cdda_added` 마커로 표시해 번들과 구분한다.

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
pip install pyinstaller
pyinstaller --onefile --noconsole --name CDDA-Manager cdda_installer.pyw
```
결과물은 `dist/CDDA-Manager.exe`.
`v*` 태그를 푸시하면 GitHub Actions(`.github/workflows/build.yml`)가 자동으로
exe를 빌드해 해당 Release에 첨부한다.

> `--onefile` exe는 백신이 가끔 오탐(false positive)할 수 있다 (PyInstaller 특성).

## 제한

- Windows 전용. Linux/macOS는 실행/폴더 열기 부분 수정 필요.
- 최신 experimental 빌드는 에셋 업로드 중일 수 있어 목록에서 자동 제외된다.
