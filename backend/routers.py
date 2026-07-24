"""Movie Finder REST API 라우터."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from database import get_session
from kobis_exceptions import (
    KobisConfigError,
    KobisError,
    KobisRequestError,
    KobisResponseError,
    KobisTimeoutError,
)
from models import Movie
from movie_service import movie_service
from people_service import people_service
from poster_service import ensure_poster_urls
from schemas import (
    ActorInfo,
    AuditInfo,
    BoxOfficeItem,
    BoxOfficeResponse,
    CompanyInfo,
    DirectorInfo,
    MovieDetailResponse,
    MovieSearchItem,
    MovieSearchResponse,
    PersonDetailResponse,
    PersonFilmoInfo,
    PersonListItem,
    PersonSearchResponse,
    ShowTypeInfo,
    StaffInfo,
)

router = APIRouter(prefix="/api")


def _raise_kobis_http(exc: KobisError) -> None:
    if isinstance(exc, KobisConfigError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, KobisTimeoutError):
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    if isinstance(exc, (KobisRequestError, KobisResponseError)):
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    raise HTTPException(status_code=502, detail=str(exc)) from exc


def _parse_target_date(value: str | None) -> date | None:
    if value is None or not value.strip():
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise HTTPException(
        status_code=422,
        detail="target_date는 YYYY-MM-DD 또는 YYYYMMDD 형식이어야 합니다.",
    )


def _movie_summary_for_code(session: Session, movie_code: str) -> dict:
    """박스오피스 카드용으로 영화 기본 정보를 DB/상세에서 보강한다."""
    movie = session.get(Movie, movie_code)
    if movie is None:
        bundle = movie_service.get_or_fetch_movie_detail(session, movie_code)
        if bundle is None:
            return {}
        detail = bundle["detail"]
        directors = [d.people_name for d in bundle.get("directors", []) if d.people_name]
        genres = [g.genre_name for g in bundle.get("genres", []) if g.genre_name]
        return {
            "movie_name_english": detail.movie_name_english,
            "production_year": detail.production_year,
            "movie_type": detail.movie_type,
            "genre": ", ".join(genres) if genres else None,
            "director_name": ", ".join(directors) if directors else None,
            "open_date": detail.open_date,
        }

    return {
        "movie_name_english": movie.movie_name_english,
        "production_year": movie.production_year,
        "movie_type": movie.movie_type,
        "genre": movie.representative_genre_name or movie.genre_names,
        "director_name": movie.director_names,
        "open_date": movie.open_date,
    }


@router.get("/box-office", response_model=BoxOfficeResponse)
def get_box_office(
    period: Literal["daily", "weekly"] = Query(
        default="daily",
        description="박스오피스 구분: daily(어제) 또는 weekly(최근 완료 주간)",
    ),
    target_date: str | None = Query(
        default=None,
        description="조회 기준일 (YYYY-MM-DD 또는 YYYYMMDD)",
    ),
    session: Session = Depends(get_session),
) -> BoxOfficeResponse:
    """어제 또는 최근 완료 주간의 박스오피스 Top 10을 반환한다."""
    parsed = _parse_target_date(target_date)
    try:
        if period == "weekly":
            rows = movie_service.fetch_weekly_box_office(parsed)
        else:
            daily_date = parsed or (date.today() - timedelta(days=1))
            rows = movie_service.get_or_fetch_box_office(session, daily_date)
        items = []
        top_rows = rows[:10]
        poster_map = ensure_poster_urls([row.movie_code for row in top_rows])

        for row in top_rows:
            poster_url = poster_map.get(row.movie_code)
            if poster_url and hasattr(row, "poster_url"):
                row.poster_url = poster_url
            summary = _movie_summary_for_code(session, row.movie_code)
            director_name = row.director_name or summary.get("director_name")
            if director_name and hasattr(row, "director_name"):
                row.director_name = director_name
            items.append(
                BoxOfficeItem(
                    rank=row.rank,
                    movie_code=row.movie_code,
                    movie_name=row.movie_name,
                    movie_name_english=summary.get("movie_name_english"),
                    director_name=director_name,
                    poster_url=poster_url,
                    production_year=summary.get("production_year"),
                    open_date=row.open_date or summary.get("open_date"),
                    movie_type=summary.get("movie_type"),
                    genre=summary.get("genre"),
                    target_date=row.target_date,
                )
            )
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    response_date = items[0].target_date if items else parsed
    return BoxOfficeResponse(period=period, target_date=response_date, items=items)


@router.get("/movies/search", response_model=MovieSearchResponse)
def search_movies(
    title: str | None = Query(default=None, description="영화 제목"),
    director: str | None = Query(default=None, description="감독명"),
    open_date: str | None = Query(
        default=None,
        description="개봉일/개봉연도 (YYYY, YYYY-MM-DD, YYYYMMDD)",
    ),
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터)"),
    page_size: int = Query(
        default=10,
        description="페이지당 결과 수 (10, 20, 30, 40, 50)",
    ),
    session: Session = Depends(get_session),
) -> MovieSearchResponse:
    """제목·감독명·개봉일로 영화를 검색한다."""
    if not any([(title or "").strip(), (director or "").strip(), (open_date or "").strip()]):
        raise HTTPException(
            status_code=422,
            detail="title, director, open_date 중 하나 이상을 입력하세요.",
        )
    if page_size not in (10, 20, 30, 40, 50):
        raise HTTPException(
            status_code=422,
            detail="page_size는 10, 20, 30, 40, 50 중 하나여야 합니다.",
        )

    try:
        movies, total = movie_service.search_or_fetch_movies(
            session,
            movie_name=title,
            director_name=director,
            open_date=open_date,
            page=page,
            item_per_page=page_size,
        )
        poster_map = ensure_poster_urls([movie.movie_code for movie in movies])
        items = [
            MovieSearchItem(
                movie_code=movie.movie_code,
                movie_name=movie.movie_name,
                movie_name_english=movie.movie_name_english,
                poster_url=poster_map.get(movie.movie_code),
                production_year=movie.production_year,
                open_date=movie.open_date,
                movie_type=movie.movie_type,
                genre=movie.representative_genre_name or movie.genre_names,
                director_name=movie.director_names,
                company_name=movie.company_names,
            )
            for movie in movies
        ]
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    return MovieSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get("/movies/{movie_code}", response_model=MovieDetailResponse)
def get_movie_detail(
    movie_code: str,
    session: Session = Depends(get_session),
) -> MovieDetailResponse:
    """영화코드로 상세 정보를 조회한다."""
    try:
        bundle = movie_service.get_or_fetch_movie_detail(session, movie_code)
        if bundle is None:
            raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")

        detail = bundle["detail"]
        poster_url = ensure_poster_urls([detail.movie_code]).get(detail.movie_code)
        response = MovieDetailResponse(
            movie_code=detail.movie_code,
            movie_name=detail.movie_name,
            movie_name_english=detail.movie_name_english,
            poster_url=poster_url,
            production_year=detail.production_year,
            show_time_minutes=detail.show_time_minutes,
            open_date=detail.open_date,
            production_status=detail.production_status,
            movie_type=detail.movie_type,
            nation_names=[n.nation_name for n in bundle["nations"]],
            genre_names=[g.genre_name for g in bundle["genres"]],
            directors=[
                DirectorInfo(name=d.people_name, name_english=d.people_name_english)
                for d in bundle["directors"]
            ],
            actors=[
                ActorInfo(
                    name=a.people_name,
                    name_english=a.people_name_english,
                    cast_name=a.cast_name,
                    cast_name_english=a.cast_name_english,
                )
                for a in bundle["actors"]
            ],
            show_types=[
                ShowTypeInfo(group_name=s.group_name, type_name=s.type_name)
                for s in bundle["show_types"]
            ],
            audits=[
                AuditInfo(
                    audit_number=a.audit_number,
                    watch_grade_name=a.watch_grade_name,
                )
                for a in bundle["audits"]
            ],
            companies=[
                CompanyInfo(
                    company_code=c.company_code,
                    company_name=c.company_name,
                    company_name_english=c.company_name_english,
                    company_part_name=c.company_part_name,
                )
                for c in bundle["companies"]
            ],
            staffs=[
                StaffInfo(
                    name=s.people_name,
                    name_english=s.people_name_english,
                    role_name=s.staff_role_name,
                )
                for s in bundle["staffs"]
            ],
        )
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    return response


def _to_person_detail_response(bundle: dict) -> PersonDetailResponse:
    detail = bundle["detail"]
    return PersonDetailResponse(
        people_code=detail.people_code,
        people_name=detail.people_name,
        people_name_english=detail.people_name_english,
        sex=detail.sex,
        rep_role_name=detail.rep_role_name,
        homepages=detail.homepages,
        filmos=[
            PersonFilmoInfo(
                movie_code=filmo.movie_code,
                movie_name=filmo.movie_name,
                movie_part_name=filmo.movie_part_name,
            )
            for filmo in bundle.get("filmos", [])
        ],
    )


@router.get("/people/search", response_model=PersonSearchResponse)
def search_people(
    name: str = Query(..., min_length=1, description="영화인명"),
    role: str | None = Query(
        default=None,
        description="분야명 필터 (예: 감독)",
    ),
    session: Session = Depends(get_session),
) -> PersonSearchResponse:
    """영화인 목록을 검색하고 SQLite에 저장한다."""
    try:
        people = people_service.search_or_fetch_people(
            session,
            people_name=name,
            role_name=(role or "").strip() or None,
        )
        items = [
            PersonListItem(
                people_code=person.people_code,
                people_name=person.people_name,
                people_name_english=person.people_name_english,
                rep_role_name=person.rep_role_name,
                filmo_names=person.filmo_names,
            )
            for person in people
        ]
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    return PersonSearchResponse(total=len(items), items=items)


@router.get("/directors", response_model=PersonDetailResponse)
def get_director_detail_by_name(
    name: str = Query(..., min_length=1, description="감독명"),
    movie_name: str | None = Query(
        default=None,
        description="동명이인 구분용 영화명(필모) 힌트",
    ),
    session: Session = Depends(get_session),
) -> PersonDetailResponse:
    """영화인 목록에서 분야가 '감독'인 코드를 찾아 상세 정보를 반환한다."""
    try:
        bundle = people_service.get_or_fetch_director_by_name(
            session,
            name,
            filmo_hint=movie_name,
        )
        if bundle is None:
            raise HTTPException(status_code=404, detail="감독을 찾을 수 없습니다.")
        response = _to_person_detail_response(bundle)
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    return response


@router.get("/people/{people_code}", response_model=PersonDetailResponse)
def get_people_detail(
    people_code: str,
    session: Session = Depends(get_session),
) -> PersonDetailResponse:
    """영화인코드로 상세 정보를 조회하고 SQLite에 저장한다."""
    try:
        bundle = people_service.get_or_fetch_people_detail(session, people_code)
        if bundle is None:
            raise HTTPException(status_code=404, detail="영화인을 찾을 수 없습니다.")
        response = _to_person_detail_response(bundle)
        session.commit()
    except KobisError as exc:
        session.rollback()
        _raise_kobis_http(exc)

    return response
