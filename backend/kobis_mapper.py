"""KOBIS 외부 응답을 내부 모델로 변환한다."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

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
    Person,
    PersonDetail,
    PersonFilmo,
)


def _to_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default


def _to_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"00000000", "null"}:
        return None
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    if len(text) == 4 and text.isdigit():
        try:
            return date(int(text), 1, 1)
        except ValueError:
            return None
    return None


def _join_names(items: list[dict[str, Any]], key: str) -> str | None:
    names = [str(item.get(key, "")).strip() for item in items if item.get(key)]
    return ", ".join(names) if names else None


def map_box_office_item(item: dict[str, Any], target_date: date) -> BoxOffice:
    """일별 박스오피스 한 건을 BoxOffice 모델로 변환한다."""
    return BoxOffice(
        target_date=target_date,
        rank=_to_int(item.get("rank")),
        movie_code=str(item.get("movieCd", "")),
        movie_name=str(item.get("movieNm", "")),
        open_date=_parse_date(item.get("openDt")),
        rank_change=_to_int(item.get("rankInten")),
        is_new=str(item.get("rankOldAndNew", "")).upper() == "NEW",
        audience_count=_to_int(item.get("audiCnt")),
        audience_accumulated=_to_int(item.get("audiAcc")),
        sales_amount=_to_int(item.get("salesAmt")),
        sales_accumulated=_to_int(item.get("salesAcc")),
    )


def map_movie_list_item(item: dict[str, Any]) -> Movie:
    """영화 목록 검색 한 건을 Movie 모델로 변환한다."""
    directors = item.get("directors") or []
    companies = item.get("companys") or []
    return Movie(
        movie_code=str(item.get("movieCd", "")),
        movie_name=str(item.get("movieNm", "")),
        movie_name_english=item.get("movieNmEn") or None,
        production_year=_to_optional_int(item.get("prdtYear")),
        open_date=_parse_date(item.get("openDt")),
        movie_type=item.get("typeNm") or None,
        production_status=item.get("prdtStatNm") or None,
        nation_names=item.get("nationAlt") or None,
        genre_names=item.get("genreAlt") or None,
        representative_nation_name=item.get("repNationNm") or None,
        representative_genre_name=item.get("repGenreNm") or None,
        director_names=_join_names(directors, "peopleNm"),
        company_codes=_join_names(companies, "companyCd"),
        company_names=_join_names(companies, "companyNm"),
    )


def map_movie_detail(info: dict[str, Any]) -> dict[str, Any]:
    """영화 상세 응답을 기본·연관 모델 묶음으로 변환한다."""
    movie_code = str(info.get("movieCd", ""))
    detail = MovieDetail(
        movie_code=movie_code,
        movie_name=str(info.get("movieNm", "")),
        movie_name_english=info.get("movieNmEn") or None,
        movie_name_original=info.get("movieNmOg") or None,
        production_year=_to_optional_int(info.get("prdtYear")),
        show_time_minutes=_to_optional_int(info.get("showTm")),
        open_date=_parse_date(info.get("openDt")),
        production_status=info.get("prdtStatNm") or None,
        movie_type=info.get("typeNm") or None,
    )

    nations = [
        MovieNation(movie_code=movie_code, nation_name=str(item.get("nationNm", "")))
        for item in (info.get("nations") or [])
        if item.get("nationNm")
    ]
    genres = [
        MovieGenre(movie_code=movie_code, genre_name=str(item.get("genreNm", "")))
        for item in (info.get("genres") or [])
        if item.get("genreNm")
    ]
    directors = [
        MovieDirector(
            movie_code=movie_code,
            people_name=str(item.get("peopleNm", "")),
            people_name_english=item.get("peopleNmEn") or None,
        )
        for item in (info.get("directors") or [])
        if item.get("peopleNm")
    ]
    actors = [
        MovieActor(
            movie_code=movie_code,
            people_name=str(item.get("peopleNm", "")),
            people_name_english=item.get("peopleNmEn") or None,
            cast_name=item.get("cast") or None,
            cast_name_english=item.get("castEn") or None,
        )
        for item in (info.get("actors") or [])
        if item.get("peopleNm")
    ]
    show_types = [
        MovieShowType(
            movie_code=movie_code,
            group_name=str(item.get("showTypeGroupNm", "")),
            type_name=str(item.get("showTypeNm", "")),
        )
        for item in (info.get("showTypes") or [])
        if item.get("showTypeGroupNm") or item.get("showTypeNm")
    ]
    audits = [
        MovieAudit(
            movie_code=movie_code,
            audit_number=str(item.get("auditNo", "")),
            watch_grade_name=str(item.get("watchGradeNm", "")),
        )
        for item in (info.get("audits") or [])
        if item.get("auditNo") or item.get("watchGradeNm")
    ]
    companies = [
        MovieCompany(
            movie_code=movie_code,
            company_code=item.get("companyCd") or None,
            company_name=str(item.get("companyNm", "")),
            company_name_english=item.get("companyNmEn") or None,
            company_part_name=item.get("companyPartNm") or None,
        )
        for item in (info.get("companys") or [])
        if item.get("companyNm")
    ]
    staffs = [
        MovieStaff(
            movie_code=movie_code,
            people_name=str(item.get("peopleNm", "")),
            people_name_english=item.get("peopleNmEn") or None,
            staff_role_name=str(item.get("staffRoleNm", "")),
        )
        for item in (info.get("staffs") or [])
        if item.get("peopleNm")
    ]

    return {
        "detail": detail,
        "nations": nations,
        "genres": genres,
        "directors": directors,
        "actors": actors,
        "show_types": show_types,
        "audits": audits,
        "companies": companies,
        "staffs": staffs,
    }


def map_people_list_item(item: dict[str, Any]) -> Person:
    """영화인 목록 한 건을 Person 모델로 변환한다."""
    return Person(
        people_code=str(item.get("peopleCd", "")),
        people_name=str(item.get("peopleNm", "")),
        people_name_english=item.get("peopleNmEn") or None,
        rep_role_name=item.get("repRoleNm") or None,
        filmo_names=item.get("filmoNames") or None,
    )


def map_people_detail(info: dict[str, Any]) -> dict[str, Any]:
    """영화인 상세 응답을 기본·필모 모델 묶음으로 변환한다."""
    people_code = str(info.get("peopleCd", ""))
    detail = PersonDetail(
        people_code=people_code,
        people_name=str(info.get("peopleNm", "")),
        people_name_english=info.get("peopleNmEn") or None,
        sex=info.get("sex") or None,
        rep_role_name=info.get("repRoleNm") or None,
        homepages=info.get("homepages") or None,
    )
    filmos = [
        PersonFilmo(
            people_code=people_code,
            movie_code=item.get("movieCd") or None,
            movie_name=str(item.get("movieNm", "")),
            movie_part_name=item.get("moviePartNm") or None,
        )
        for item in (info.get("filmos") or [])
        if item.get("movieNm")
    ]
    return {"detail": detail, "filmos": filmos}
