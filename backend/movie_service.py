"""영화·박스오피스 SQLite 저장·조회 및 캐시 우선 흐름."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlmodel import Session, col, select

from kobis_client import KobisClient, kobis_client
from models import (
    BoxOffice,
    Movie,
    MovieActor,
    MovieAudit,
    MovieCompany,
    MovieDetail,
    MovieDirector,
    MovieGenre,
    MovieNation,
    MovieShowType,
    MovieStaff,
)


class MovieService:
    """DB 저장/조회와 KOBIS 캐시 우선 조회를 담당한다."""

    def __init__(self, client: KobisClient | None = None) -> None:
        self.client = client or kobis_client

    # ------------------------------------------------------------------
    # 박스오피스
    # ------------------------------------------------------------------
    def save_box_office(self, session: Session, items: list[BoxOffice]) -> list[BoxOffice]:
        """동일 일자 기존 순위를 지우고 새 결과를 저장한다."""
        if not items:
            return []

        target_date = items[0].target_date
        existing = session.exec(
            select(BoxOffice).where(BoxOffice.target_date == target_date)
        ).all()
        for row in existing:
            session.delete(row)
        session.flush()

        saved: list[BoxOffice] = []
        now = datetime.now(timezone.utc)
        for item in items:
            row = BoxOffice(
                target_date=item.target_date,
                rank=item.rank,
                movie_code=item.movie_code,
                movie_name=item.movie_name,
                director_name=item.director_name,
                poster_url=item.poster_url,
                open_date=item.open_date,
                rank_change=item.rank_change,
                is_new=item.is_new,
                audience_count=item.audience_count,
                audience_accumulated=item.audience_accumulated,
                sales_amount=item.sales_amount,
                sales_accumulated=item.sales_accumulated,
                fetched_at=now,
            )
            session.add(row)
            saved.append(row)
        session.flush()
        return saved

    def get_box_office_by_date(
        self,
        session: Session,
        target_date: date,
    ) -> list[BoxOffice]:
        """특정 일자의 박스오피스를 순위순으로 조회한다."""
        return list(
            session.exec(
                select(BoxOffice)
                .where(BoxOffice.target_date == target_date)
                .order_by(col(BoxOffice.rank))
            ).all()
        )

    def get_latest_box_office(self, session: Session) -> list[BoxOffice]:
        """DB에 저장된 가장 일자의 박스오피스를 조회한다."""
        latest_date = session.exec(
            select(BoxOffice.target_date).order_by(col(BoxOffice.target_date).desc())
        ).first()
        if latest_date is None:
            return []
        return self.get_box_office_by_date(session, latest_date)

    def get_or_fetch_box_office(
        self,
        session: Session,
        target_date: date | None = None,
    ) -> list[BoxOffice]:
        """캐시 우선: DB에 있으면 반환, 없으면 외부 API 조회 후 저장."""
        if target_date is not None:
            cached = self.get_box_office_by_date(session, target_date)
            if cached:
                return cached
            fetched = self.client.fetch_daily_box_office(target_date)
            return self.save_box_office(session, fetched)

        cached = self.get_latest_box_office(session)
        if cached:
            return cached
        fetched = self.client.fetch_daily_box_office()
        return self.save_box_office(session, fetched)

    def fetch_weekly_box_office(
        self,
        target_date: date | None = None,
    ) -> list[BoxOffice]:
        """최근 완료 주간 또는 지정일이 속한 주간의 Top 10을 조회한다."""
        return self.client.fetch_weekly_box_office(target_date)

    # ------------------------------------------------------------------
    # 영화 검색
    # ------------------------------------------------------------------
    def save_movies(self, session: Session, movies: list[Movie]) -> list[Movie]:
        """검색 결과를 movie_code 기준으로 저장·갱신한다."""
        saved: list[Movie] = []
        now = datetime.now(timezone.utc)
        for movie in movies:
            existing = session.get(Movie, movie.movie_code)
            if existing is None:
                movie.fetched_at = now
                session.add(movie)
                saved.append(movie)
                continue

            existing.movie_name = movie.movie_name
            existing.movie_name_english = movie.movie_name_english
            existing.production_year = movie.production_year
            existing.open_date = movie.open_date
            existing.movie_type = movie.movie_type
            existing.production_status = movie.production_status
            existing.nation_names = movie.nation_names
            existing.genre_names = movie.genre_names
            existing.representative_nation_name = movie.representative_nation_name
            existing.representative_genre_name = movie.representative_genre_name
            existing.director_names = movie.director_names
            existing.company_codes = movie.company_codes
            existing.company_names = movie.company_names
            existing.fetched_at = now
            saved.append(existing)

        session.flush()
        return saved

    def search_movies_in_db(
        self,
        session: Session,
        *,
        movie_name: str | None = None,
        director_name: str | None = None,
        open_date: date | str | None = None,
    ) -> list[Movie]:
        """저장된 영화에서 제목·감독·개봉연도 조건으로 조회한다."""
        statement = select(Movie)
        if movie_name:
            statement = statement.where(col(Movie.movie_name).contains(movie_name.strip()))
        if director_name:
            statement = statement.where(
                col(Movie.director_names).contains(director_name.strip())
            )
        open_year = self._to_open_year(open_date)
        if open_year is not None:
            year_start = date(open_year, 1, 1)
            year_end = date(open_year, 12, 31)
            statement = statement.where(
                Movie.open_date >= year_start,
                Movie.open_date <= year_end,
            )
        return list(session.exec(statement).all())

    def search_or_fetch_movies(
        self,
        session: Session,
        *,
        movie_name: str | None = None,
        director_name: str | None = None,
        open_date: date | str | None = None,
        page: int = 1,
        item_per_page: int = 10,
    ) -> tuple[list[Movie], int]:
        """페이징 검색: 외부 API로 해당 페이지를 조회하고 DB에 저장한다.

        Returns:
            (현재 페이지 영화 목록, 전체 건수)
        """
        fetched, total = self.client.search_movies(
            movie_name=movie_name,
            director_name=director_name,
            open_date=open_date,
            page=page,
            item_per_page=item_per_page,
        )
        if not fetched:
            return [], total
        return self.save_movies(session, fetched), total

    # ------------------------------------------------------------------
    # 영화 상세
    # ------------------------------------------------------------------
    def save_movie_detail(
        self,
        session: Session,
        detail_bundle: dict[str, Any],
    ) -> dict[str, Any]:
        """영화 상세와 연관 테이블을 저장·갱신한다."""
        detail: MovieDetail = detail_bundle["detail"]
        movie_code = detail.movie_code
        now = datetime.now(timezone.utc)

        self._ensure_movie_from_detail(session, detail)

        existing = session.get(MovieDetail, movie_code)
        if existing is None:
            detail.fetched_at = now
            session.add(detail)
        else:
            existing.movie_name = detail.movie_name
            existing.movie_name_english = detail.movie_name_english
            existing.movie_name_original = detail.movie_name_original
            existing.production_year = detail.production_year
            existing.show_time_minutes = detail.show_time_minutes
            existing.open_date = detail.open_date
            existing.production_status = detail.production_status
            existing.movie_type = detail.movie_type
            existing.fetched_at = now
            detail = existing

        self._replace_related(
            session,
            MovieNation,
            movie_code,
            detail_bundle.get("nations", []),
        )
        self._replace_related(
            session,
            MovieGenre,
            movie_code,
            detail_bundle.get("genres", []),
        )
        self._replace_related(
            session,
            MovieDirector,
            movie_code,
            detail_bundle.get("directors", []),
        )
        self._replace_related(
            session,
            MovieActor,
            movie_code,
            detail_bundle.get("actors", []),
        )
        self._replace_related(
            session,
            MovieShowType,
            movie_code,
            detail_bundle.get("show_types", []),
        )
        self._replace_related(
            session,
            MovieAudit,
            movie_code,
            detail_bundle.get("audits", []),
        )
        self._replace_related(
            session,
            MovieCompany,
            movie_code,
            detail_bundle.get("companies", []),
        )
        self._replace_related(
            session,
            MovieStaff,
            movie_code,
            detail_bundle.get("staffs", []),
        )
        session.flush()
        return self.get_movie_detail(session, movie_code) or {
            "detail": detail,
            "nations": detail_bundle.get("nations", []),
            "genres": detail_bundle.get("genres", []),
            "directors": detail_bundle.get("directors", []),
            "actors": detail_bundle.get("actors", []),
            "show_types": detail_bundle.get("show_types", []),
            "audits": detail_bundle.get("audits", []),
            "companies": detail_bundle.get("companies", []),
            "staffs": detail_bundle.get("staffs", []),
        }

    def get_movie_detail(
        self,
        session: Session,
        movie_code: str,
    ) -> dict[str, Any] | None:
        """저장된 영화 상세와 연관 데이터를 조회한다."""
        detail = session.get(MovieDetail, movie_code)
        if detail is None:
            return None
        return {
            "detail": detail,
            "nations": self._list_related(session, MovieNation, movie_code),
            "genres": self._list_related(session, MovieGenre, movie_code),
            "directors": self._list_related(session, MovieDirector, movie_code),
            "actors": self._list_related(session, MovieActor, movie_code),
            "show_types": self._list_related(session, MovieShowType, movie_code),
            "audits": self._list_related(session, MovieAudit, movie_code),
            "companies": self._list_related(session, MovieCompany, movie_code),
            "staffs": self._list_related(session, MovieStaff, movie_code),
        }

    def get_or_fetch_movie_detail(
        self,
        session: Session,
        movie_code: str,
    ) -> dict[str, Any] | None:
        """캐시 우선: DB에 상세가 있으면 반환, 없으면 외부 API 후 저장."""
        cached = self.get_movie_detail(session, movie_code)
        if cached is not None:
            return cached

        fetched = self.client.fetch_movie_detail(movie_code)
        if fetched is None:
            return None
        return self.save_movie_detail(session, fetched)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _ensure_movie_from_detail(self, session: Session, detail: MovieDetail) -> None:
        existing = session.get(Movie, detail.movie_code)
        if existing is not None:
            return
        session.add(
            Movie(
                movie_code=detail.movie_code,
                movie_name=detail.movie_name,
                movie_name_english=detail.movie_name_english,
                production_year=detail.production_year,
                open_date=detail.open_date,
                movie_type=detail.movie_type,
                production_status=detail.production_status,
            )
        )
        session.flush()

    @staticmethod
    def _replace_related(
        session: Session,
        model: type,
        movie_code: str,
        rows: list[Any],
    ) -> None:
        for old in session.exec(
            select(model).where(model.movie_code == movie_code)
        ).all():
            session.delete(old)
        session.flush()
        for row in rows:
            row.id = None
            row.movie_code = movie_code
            session.add(row)

    @staticmethod
    def _list_related(session: Session, model: type, movie_code: str) -> list[Any]:
        return list(
            session.exec(select(model).where(model.movie_code == movie_code)).all()
        )

    @staticmethod
    def _to_open_year(open_date: date | str | None) -> int | None:
        if open_date is None:
            return None
        if isinstance(open_date, date):
            return open_date.year
        text = str(open_date).strip()
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
        return None


movie_service = MovieService()
