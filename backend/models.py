"""Movie Finder 데이터베이스 모델."""

from datetime import date, datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class BoxOffice(SQLModel, table=True):
    """기준일별 박스오피스 순위와 화면 표시용 영화 정보."""

    __table_args__ = (
        UniqueConstraint("target_date", "rank", name="uq_box_office_date_rank"),
    )

    id: int | None = Field(default=None, primary_key=True)
    target_date: date = Field(index=True)
    rank: int
    movie_code: str = Field(index=True)
    movie_name: str
    director_name: str | None = None
    poster_url: str | None = None
    open_date: date | None = None
    rank_change: int = 0
    is_new: bool = False
    audience_count: int = 0
    audience_accumulated: int = 0
    sales_amount: int = 0
    sales_accumulated: int = 0
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class Movie(SQLModel, table=True):
    """영화 목록 검색 결과와 기본 정보를 저장한다."""

    movie_code: str = Field(primary_key=True)
    movie_name: str = Field(index=True)
    movie_name_english: str | None = None
    production_year: int | None = None
    open_date: date | None = Field(default=None, index=True)
    movie_type: str | None = None
    production_status: str | None = None
    nation_names: str | None = None
    genre_names: str | None = None
    representative_nation_name: str | None = None
    representative_genre_name: str | None = None
    director_names: str | None = Field(default=None, index=True)
    company_codes: str | None = None
    company_names: str | None = None
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class MovieDetail(SQLModel, table=True):
    """영화 상세 조회의 기본 정보를 저장한다."""

    movie_code: str = Field(
        primary_key=True,
        foreign_key="movie.movie_code",
    )
    movie_name: str
    movie_name_english: str | None = None
    movie_name_original: str | None = None
    production_year: int | None = None
    show_time_minutes: int | None = None
    open_date: date | None = None
    production_status: str | None = None
    movie_type: str | None = None
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class MovieNation(SQLModel, table=True):
    """영화 상세의 제작 국가."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    nation_name: str


class MovieGenre(SQLModel, table=True):
    """영화 상세의 장르."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    genre_name: str


class MovieDirector(SQLModel, table=True):
    """영화 상세의 감독 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    people_name: str
    people_name_english: str | None = None


class MovieActor(SQLModel, table=True):
    """영화 상세의 배우와 배역 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    people_name: str
    people_name_english: str | None = None
    cast_name: str | None = None
    cast_name_english: str | None = None


class MovieShowType(SQLModel, table=True):
    """영화 상세의 상영 형태 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    group_name: str
    type_name: str


class MovieAudit(SQLModel, table=True):
    """영화 상세의 심의 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    audit_number: str
    watch_grade_name: str


class MovieCompany(SQLModel, table=True):
    """영화 상세의 참여 영화사 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    company_code: str | None = None
    company_name: str
    company_name_english: str | None = None
    company_part_name: str | None = None


class MovieStaff(SQLModel, table=True):
    """영화 상세의 스태프 정보."""

    id: int | None = Field(default=None, primary_key=True)
    movie_code: str = Field(foreign_key="moviedetail.movie_code", index=True)
    people_name: str
    people_name_english: str | None = None
    staff_role_name: str


class Person(SQLModel, table=True):
    """영화인 목록 검색 결과."""

    people_code: str = Field(primary_key=True)
    people_name: str = Field(index=True)
    people_name_english: str | None = None
    rep_role_name: str | None = Field(default=None, index=True)
    filmo_names: str | None = None
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class PersonDetail(SQLModel, table=True):
    """영화인 상세 기본 정보."""

    people_code: str = Field(
        primary_key=True,
        foreign_key="person.people_code",
    )
    people_name: str
    people_name_english: str | None = None
    sex: str | None = None
    rep_role_name: str | None = None
    homepages: str | None = None
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class PersonFilmo(SQLModel, table=True):
    """영화인 상세의 참여 영화(필모) 정보."""

    id: int | None = Field(default=None, primary_key=True)
    people_code: str = Field(foreign_key="persondetail.people_code", index=True)
    movie_code: str | None = Field(default=None, index=True)
    movie_name: str
    movie_part_name: str | None = None
