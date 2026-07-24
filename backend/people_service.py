"""영화인(감독) SQLite 저장·조회 및 캐시 우선 흐름."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, col, select

from kobis_client import KobisClient, kobis_client
from models import Person, PersonDetail, PersonFilmo


DIRECTOR_ROLE_NAME = "감독"


class PeopleService:
    """영화인 목록·상세의 DB 저장/조회와 KOBIS 캐시 우선 조회를 담당한다."""

    def __init__(self, client: KobisClient | None = None) -> None:
        self.client = client or kobis_client

    def save_people(self, session: Session, people: list[Person]) -> list[Person]:
        """영화인 목록을 people_code 기준으로 저장·갱신한다."""
        saved: list[Person] = []
        now = datetime.now(timezone.utc)
        for person in people:
            if not person.people_code:
                continue
            existing = session.get(Person, person.people_code)
            if existing is None:
                person.fetched_at = now
                session.add(person)
                saved.append(person)
                continue

            existing.people_name = person.people_name
            existing.people_name_english = person.people_name_english
            existing.rep_role_name = person.rep_role_name
            existing.filmo_names = person.filmo_names
            existing.fetched_at = now
            saved.append(existing)

        session.flush()
        return saved

    def find_people_in_db(
        self,
        session: Session,
        *,
        people_name: str,
        role_name: str | None = None,
    ) -> list[Person]:
        """저장된 영화인에서 이름(및 분야)으로 조회한다."""
        name = people_name.strip()
        statement = select(Person).where(Person.people_name == name)
        if role_name:
            statement = statement.where(Person.rep_role_name == role_name)
        return list(session.exec(statement).all())

    def search_or_fetch_people(
        self,
        session: Session,
        *,
        people_name: str,
        role_name: str | None = None,
        page: int = 1,
        item_per_page: int = 100,
        force_remote: bool = False,
    ) -> list[Person]:
        """캐시 우선 영화인 목록 검색. 없으면 외부 API 후 저장."""
        if not force_remote:
            cached = self.find_people_in_db(
                session,
                people_name=people_name,
                role_name=role_name,
            )
            if cached:
                return cached

        fetched, _total = self.client.search_people(
            people_name=people_name,
            page=page,
            item_per_page=item_per_page,
        )
        saved = self.save_people(session, fetched)
        if role_name:
            return [
                person
                for person in saved
                if (person.rep_role_name or "").strip() == role_name
            ]
        # 이름 일치분만 반환 (외부 API가 유사 이름을 포함할 수 있음)
        name = people_name.strip()
        return [person for person in saved if person.people_name == name]

    def resolve_director(
        self,
        session: Session,
        people_name: str,
        *,
        filmo_hint: str | None = None,
    ) -> Person | None:
        """영화인 목록에서 분야가 '감독'인 사람을 찾는다."""
        name = (people_name or "").strip()
        if not name:
            return None

        candidates = self.search_or_fetch_people(
            session,
            people_name=name,
            role_name=DIRECTOR_ROLE_NAME,
        )
        if not candidates:
            # 같은 이름 배우만 캐시된 경우에도 원격에서 감독을 다시 찾는다.
            candidates = self.search_or_fetch_people(
                session,
                people_name=name,
                role_name=DIRECTOR_ROLE_NAME,
                force_remote=True,
            )

        if not candidates:
            return None
        if len(candidates) == 1 or not filmo_hint:
            return candidates[0]

        hint = filmo_hint.strip()
        for person in candidates:
            if person.filmo_names and hint in person.filmo_names:
                return person
        return candidates[0]

    def save_people_detail(
        self,
        session: Session,
        detail_bundle: dict[str, Any],
    ) -> dict[str, Any]:
        """영화인 상세와 필모를 저장·갱신한다."""
        detail: PersonDetail = detail_bundle["detail"]
        people_code = detail.people_code
        now = datetime.now(timezone.utc)

        self._ensure_person_from_detail(session, detail)

        existing = session.get(PersonDetail, people_code)
        if existing is None:
            detail.fetched_at = now
            session.add(detail)
        else:
            existing.people_name = detail.people_name
            existing.people_name_english = detail.people_name_english
            existing.sex = detail.sex
            existing.rep_role_name = detail.rep_role_name
            existing.homepages = detail.homepages
            existing.fetched_at = now
            detail = existing

        for old in session.exec(
            select(PersonFilmo).where(PersonFilmo.people_code == people_code)
        ).all():
            session.delete(old)
        session.flush()

        for filmo in detail_bundle.get("filmos", []):
            filmo.id = None
            filmo.people_code = people_code
            session.add(filmo)

        session.flush()
        return self.get_people_detail(session, people_code) or {
            "detail": detail,
            "filmos": detail_bundle.get("filmos", []),
        }

    def get_people_detail(
        self,
        session: Session,
        people_code: str,
    ) -> dict[str, Any] | None:
        """저장된 영화인 상세와 필모를 조회한다."""
        detail = session.get(PersonDetail, people_code)
        if detail is None:
            return None
        filmos = list(
            session.exec(
                select(PersonFilmo).where(PersonFilmo.people_code == people_code)
            ).all()
        )
        return {"detail": detail, "filmos": filmos}

    def get_or_fetch_people_detail(
        self,
        session: Session,
        people_code: str,
    ) -> dict[str, Any] | None:
        """캐시 우선: DB에 상세가 있으면 반환, 없으면 외부 API 후 저장."""
        cached = self.get_people_detail(session, people_code)
        if cached is not None:
            return cached

        fetched = self.client.fetch_people_detail(people_code)
        if fetched is None:
            return None
        return self.save_people_detail(session, fetched)

    def get_or_fetch_director_by_name(
        self,
        session: Session,
        people_name: str,
        *,
        filmo_hint: str | None = None,
    ) -> dict[str, Any] | None:
        """감독명으로 영화인 목록에서 코드를 찾고 상세를 반환한다."""
        person = self.resolve_director(
            session,
            people_name,
            filmo_hint=filmo_hint,
        )
        if person is None:
            return None
        return self.get_or_fetch_people_detail(session, person.people_code)

    def _ensure_person_from_detail(
        self,
        session: Session,
        detail: PersonDetail,
    ) -> None:
        existing = session.get(Person, detail.people_code)
        if existing is not None:
            return
        session.add(
            Person(
                people_code=detail.people_code,
                people_name=detail.people_name,
                people_name_english=detail.people_name_english,
                rep_role_name=detail.rep_role_name,
            )
        )
        session.flush()


people_service = PeopleService()
