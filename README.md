# Movie Finder

영화진흥위원회 KOBIS Open API를 활용해 박스오피스 순위와 영화 정보를 조회하는 웹 애플리케이션입니다. 영화 제목, 감독명, 개봉일로 영화를 검색하고 상세 정보와 감독의 필모그래피를 확인할 수 있습니다.

## 주요 기능

- 일간·주간 박스오피스 Top 10 조회
- 제목, 감독명, 개봉일을 조합한 영화 검색
- 감독, 배우, 장르, 상영시간, 심의정보, 제작사, 스태프 등 영화 상세 조회
- 감독 기본 정보와 참여 영화 조회
- 브라우저 `localStorage` 기반 즐겨찾기
- 반응형 박스오피스 캐러셀
- 외부 API 조회 결과의 SQLite 캐싱

## 기술 스택

- **Frontend:** React 18, Vite, React Router, Swiper
- **Backend:** Python, FastAPI, SQLModel, Uvicorn
- **Database:** SQLite
- **Data:** 영화진흥위원회 KOBIS Open API

## 프로젝트 구조

```text
movie_finder/
├── backend/              # FastAPI 애플리케이션, 데이터 모델, 외부 API 연동
│   ├── main.py
│   ├── routers.py
│   ├── models.py
│   └── requirements.txt
├── frontend/             # React 애플리케이션
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
└── docs/                 # 기획서, 개발 계획, 작업 목록
```

## 시작하기

### 사전 준비

- Python 3.10 이상
- Node.js 18 이상
- KOBIS Open API 키 ([KOBIS Open API](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do))

### 1. 백엔드 설정 및 실행

`backend/.env` 파일을 만들고 다음 환경 변수를 설정합니다.

```env
MOVIE_API_KEY=발급받은_API_키
KOBIS_API_BASE_URL=https://www.kobis.or.kr/kobisopenapi/webservice/rest
```

프로젝트 루트에서 아래 명령을 실행합니다.

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

백엔드는 `http://127.0.0.1:8000`에서 실행됩니다.

- 상태 확인: `http://127.0.0.1:8000/health`
- Swagger API 문서: `http://127.0.0.1:8000/docs`

SQLite 데이터베이스(`backend/app.db`)와 포스터 저장 디렉터리는 서버를 처음 실행할 때 자동으로 준비됩니다.

### 2. 프론트엔드 설정 및 실행

새 터미널에서 프로젝트 루트를 기준으로 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173`에 접속합니다. 프론트엔드를 사용하려면 백엔드가 함께 실행 중이어야 합니다.

## 주요 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/api/box-office` | 일간·주간 박스오피스 Top 10 조회 |
| `GET` | `/api/movies/search` | 제목·감독명·개봉일로 영화 검색 |
| `GET` | `/api/movies/{movie_code}` | 영화 상세 조회 |
| `GET` | `/api/directors` | 감독명으로 감독 상세 조회 |
| `GET` | `/api/people/search` | 영화인 검색 |
| `GET` | `/api/people/{people_code}` | 영화인 상세 조회 |

자세한 요청 파라미터와 응답 스키마는 서버 실행 후 Swagger 문서(`/docs`)에서 확인할 수 있습니다.

## 빌드

```bash
cd frontend
npm run build
```

빌드 결과는 `frontend/dist`에 생성됩니다.

## 관련 문서

- [제품 요구사항](docs/PRD.md)
- [개발 계획](docs/DEVELOPMENT_PLAN.md)
- [작업 목록](docs/TASKS.md)
