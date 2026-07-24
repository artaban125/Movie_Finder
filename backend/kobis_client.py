"""KOBIS 공공데이터 API 클라이언트."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import requests

from config import Settings, settings
from kobis_exceptions import (
    KobisConfigError,
    KobisRequestError,
    KobisResponseError,
    KobisTimeoutError,
)
from kobis_mapper import (
    map_box_office_item,
    map_movie_detail,
    map_movie_list_item,
    map_people_detail,
    map_people_list_item,
)
from models import BoxOffice, Movie, Person

DEFAULT_TIMEOUT_SECONDS = 10


class KobisClient:
    """일별 박스오피스 · 영화 검색 · 영화 상세를 조회한다."""

    def __init__(
        self,
        app_settings: Settings | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.settings = app_settings or settings
        self.timeout_seconds = timeout_seconds

    def fetch_daily_box_office(
        self,
        target_date: date | None = None,
        item_per_page: int = 10,
    ) -> list[BoxOffice]:
        """일별 박스오피스 Top N을 조회한다."""
        query_date = target_date or (date.today() - timedelta(days=1))
        payload = self._get(
            "boxoffice/searchDailyBoxOfficeList.json",
            {
                "targetDt": query_date.strftime("%Y%m%d"),
                "itemPerPage": str(item_per_page),
            },
        )
        result = payload.get("boxOfficeResult") or {}
        items = result.get("dailyBoxOfficeList") or []
        if not items:
            return []
        return [map_box_office_item(item, query_date) for item in items]

    def fetch_weekly_box_office(
        self,
        target_date: date | None = None,
        item_per_page: int = 10,
    ) -> list[BoxOffice]:
        """가장 최근 완료 주간의 박스오피스 Top N을 조회한다."""
        today = date.today()
        previous_sunday = today - timedelta(days=today.weekday() + 1)
        query_date = target_date or previous_sunday
        payload = self._get(
            "boxoffice/searchWeeklyBoxOfficeList.json",
            {
                "targetDt": query_date.strftime("%Y%m%d"),
                "weekGb": "0",
                "itemPerPage": str(item_per_page),
            },
        )
        result = payload.get("boxOfficeResult") or {}
        items = result.get("weeklyBoxOfficeList") or []
        if not items:
            return []
        return [map_box_office_item(item, query_date) for item in items]

    def search_movies(
        self,
        *,
        movie_name: str | None = None,
        director_name: str | None = None,
        open_date: date | str | None = None,
        page: int = 1,
        item_per_page: int = 10,
    ) -> tuple[list[Movie], int]:
        """제목·감독명·개봉일(연도) 조건으로 영화 목록을 검색한다.

        Returns:
            (영화 목록, 전체 건수)
        """
        params: dict[str, str] = {
            "curPage": str(page),
            "itemPerPage": str(item_per_page),
        }
        if movie_name:
            params["movieNm"] = movie_name.strip()
        if director_name:
            params["directorNm"] = director_name.strip()

        open_year = self._to_open_year(open_date)
        if open_year:
            params["openStartDt"] = open_year
            params["openEndDt"] = open_year

        if not any(key in params for key in ("movieNm", "directorNm", "openStartDt")):
            raise KobisRequestError("검색 조건(제목, 감독명, 개봉일) 중 하나 이상이 필요합니다.")

        payload = self._get("movie/searchMovieList.json", params)
        result = payload.get("movieListResult") or {}
        items = result.get("movieList") or []
        total_raw = result.get("totCnt", len(items))
        try:
            total = int(total_raw)
        except (TypeError, ValueError):
            total = len(items)
        if not items:
            return [], total
        return [map_movie_list_item(item) for item in items], total

    def fetch_movie_detail(self, movie_code: str) -> dict[str, Any] | None:
        """영화코드로 상세 정보를 조회한다. 결과가 없으면 None."""
        code = (movie_code or "").strip()
        if not code:
            raise KobisRequestError("movie_code는 필수입니다.")

        payload = self._get(
            "movie/searchMovieInfo.json",
            {"movieCd": code},
        )
        result = payload.get("movieInfoResult") or {}
        info = result.get("movieInfo")
        if not info:
            return None
        return map_movie_detail(info)

    def search_people(
        self,
        *,
        people_name: str | None = None,
        filmo_names: str | None = None,
        page: int = 1,
        item_per_page: int = 100,
    ) -> tuple[list[Person], int]:
        """영화인명·필모로 영화인 목록을 검색한다.

        Returns:
            (영화인 목록, 전체 건수)
        """
        params: dict[str, str] = {
            "curPage": str(page),
            "itemPerPage": str(item_per_page),
        }
        if people_name:
            params["peopleNm"] = people_name.strip()
        if filmo_names:
            params["filmoNames"] = filmo_names.strip()

        if not any(key in params for key in ("peopleNm", "filmoNames")):
            raise KobisRequestError("검색 조건(영화인명, 필모) 중 하나 이상이 필요합니다.")

        payload = self._get("people/searchPeopleList.json", params)
        result = payload.get("peopleListResult") or {}
        items = result.get("peopleList") or []
        total_raw = result.get("totCnt", len(items))
        try:
            total = int(total_raw)
        except (TypeError, ValueError):
            total = len(items)
        if not items:
            return [], total
        return [map_people_list_item(item) for item in items], total

    def fetch_people_detail(self, people_code: str) -> dict[str, Any] | None:
        """영화인코드로 상세 정보를 조회한다. 결과가 없으면 None."""
        code = (people_code or "").strip()
        if not code:
            raise KobisRequestError("people_code는 필수입니다.")

        payload = self._get(
            "people/searchPeopleInfo.json",
            {"peopleCd": code},
        )
        result = payload.get("peopleInfoResult") or {}
        info = result.get("peopleInfo")
        if not info:
            return None
        return map_people_detail(info)

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        base_url = (self.settings.kobis_api_base_url or "").rstrip("/")
        api_key = self.settings.movie_api_key or ""
        if not base_url or not api_key:
            raise KobisConfigError("MOVIE_API_KEY와 KOBIS_API_BASE_URL을 설정하세요.")

        query = {"key": api_key, **params}
        url = f"{base_url}/{path.lstrip('/')}"
        try:
            response = requests.get(url, params=query, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise KobisTimeoutError("KOBIS API 요청이 시간 초과되었습니다.") from exc
        except requests.RequestException as exc:
            raise KobisRequestError(f"KOBIS API 요청에 실패했습니다: {exc}") from exc
        except ValueError as exc:
            raise KobisResponseError("KOBIS API 응답 JSON을 파싱하지 못했습니다.") from exc

        fault = payload.get("faultInfo") or payload.get("error")
        if fault:
            message = fault.get("message") if isinstance(fault, dict) else str(fault)
            raise KobisResponseError(f"KOBIS API 오류: {message}")

        return payload

    @staticmethod
    def _to_open_year(open_date: date | str | None) -> str | None:
        """개봉일 입력을 KOBIS openStartDt/openEndDt용 YYYY로 변환한다."""
        if open_date is None:
            return None
        if isinstance(open_date, date):
            return f"{open_date.year:04d}"

        text = str(open_date).strip()
        if not text:
            return None
        if len(text) == 4 and text.isdigit():
            return text
        for fmt in ("%Y%m%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt).strftime("%Y")
            except ValueError:
                continue
        raise KobisRequestError("개봉일은 YYYY, YYYYMMDD, YYYY-MM-DD 형식이어야 합니다.")


kobis_client = KobisClient()
