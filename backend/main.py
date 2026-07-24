"""
범용 보일러플레이트 - 백엔드 (FastAPI + SQLite)
================================================
'작동하는 최소 뼈대'입니다. 서버 실행 · CORS · DB 연결까지 다 되어 있어요.
여기에 **데이터 모델(도메인)만** AI(Cursor)에게 시켜서 추가하면 됩니다.

실행:
    pip install -r requirements.txt
    uvicorn main:app --reload
    → 브라우저에서 http://127.0.0.1:8000/health 로 확인
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from database import init_db
import models  # noqa: F401  # SQLModel 테이블을 메타데이터에 등록한다.
from routers import router as api_router

STATIC_DIR = Path(__file__).resolve().parent / "static"
POSTER_DIR = STATIC_DIR / "posters"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    # 서버가 켜질 때, 정의된 모델들의 테이블을 자동으로 만든다.
    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="Movie Finder API", lifespan=lifespan)
app.include_router(api_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# [배선] 브라우저의 React(다른 포트)에서 이 API를 부를 수 있게 허용 (없으면 CORS 에러)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 교육용 전체 허용. 실무에선 도메인 지정
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "API 살아있음. /health 로 확인하세요."}


@app.get("/health")
def health():
    """서버가 살아있는지 확인하는 용도. 화면(React)이 이걸 불러서 '연결됨'을 표시한다."""
    return {"status": "ok"}


# ==========================================================================
# 여기서부터 여러분이 (AI에게 시켜서) 만듭니다.
#   DB 연결은 위에 이미 되어 있으니, 데이터 모델과 API만 추가하면 됩니다.
#   예: "축제(Festival) 모델을 만들어줘. 이름·장소·기간·좌표를 담고 SQLite에 저장되게."
# ==========================================================================
