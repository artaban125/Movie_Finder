"""REST API 응답/요청 스키마 (PRD 기준)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class BoxOfficeItem(BaseModel):
    rank: int
    movie_code: str
    movie_name: str
    movie_name_english: str | None = None
    director_name: str | None = None
    poster_url: str | None = None
    production_year: int | None = None
    open_date: date | None = None
    movie_type: str | None = None
    genre: str | None = None
    target_date: date


class BoxOfficeResponse(BaseModel):
    period: Literal["daily", "weekly"]
    target_date: date | None = None
    items: list[BoxOfficeItem]


class MovieSearchItem(BaseModel):
    movie_code: str
    movie_name: str = Field(description="영화명(국문)")
    movie_name_english: str | None = Field(default=None, description="영화명(영문)")
    poster_url: str | None = Field(default=None, description="로컬 캐시 포스터 URL")
    production_year: int | None = Field(default=None, description="제작연도")
    open_date: date | None = Field(default=None, description="개봉일")
    movie_type: str | None = Field(default=None, description="영화유형")
    genre: str | None = Field(default=None, description="장르")
    director_name: str | None = Field(default=None, description="감독명")
    company_name: str | None = Field(default=None, description="제작사명")


class MovieSearchResponse(BaseModel):
    total: int
    page: int = 1
    page_size: int = 10
    items: list[MovieSearchItem]


class DirectorInfo(BaseModel):
    name: str
    name_english: str | None = None


class ActorInfo(BaseModel):
    name: str
    name_english: str | None = None
    cast_name: str | None = None
    cast_name_english: str | None = None


class ShowTypeInfo(BaseModel):
    group_name: str
    type_name: str


class AuditInfo(BaseModel):
    audit_number: str
    watch_grade_name: str


class CompanyInfo(BaseModel):
    company_code: str | None = None
    company_name: str
    company_name_english: str | None = None
    company_part_name: str | None = None


class StaffInfo(BaseModel):
    name: str
    name_english: str | None = None
    role_name: str


class MovieDetailResponse(BaseModel):
    movie_code: str
    movie_name: str
    movie_name_english: str | None = None
    poster_url: str | None = None
    production_year: int | None = None
    show_time_minutes: int | None = None
    open_date: date | None = None
    production_status: str | None = None
    movie_type: str | None = None
    nation_names: list[str] = Field(default_factory=list)
    genre_names: list[str] = Field(default_factory=list)
    directors: list[DirectorInfo] = Field(default_factory=list)
    actors: list[ActorInfo] = Field(default_factory=list)
    show_types: list[ShowTypeInfo] = Field(default_factory=list)
    audits: list[AuditInfo] = Field(default_factory=list)
    companies: list[CompanyInfo] = Field(default_factory=list)
    staffs: list[StaffInfo] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


class PersonListItem(BaseModel):
    people_code: str
    people_name: str
    people_name_english: str | None = None
    rep_role_name: str | None = None
    filmo_names: str | None = None


class PersonSearchResponse(BaseModel):
    total: int
    items: list[PersonListItem]


class PersonFilmoInfo(BaseModel):
    movie_code: str | None = None
    movie_name: str
    movie_part_name: str | None = None


class PersonDetailResponse(BaseModel):
    people_code: str
    people_name: str
    people_name_english: str | None = None
    sex: str | None = None
    rep_role_name: str | None = None
    homepages: str | None = None
    filmos: list[PersonFilmoInfo] = Field(default_factory=list)
