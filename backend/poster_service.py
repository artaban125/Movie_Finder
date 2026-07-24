"""영화 포스터를 한 번만 다운로드해 로컬에 저장한다."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

import requests

POSTER_DIR = Path(__file__).resolve().parent / "static" / "posters"
KOBIS_ORIGIN = "https://www.kobis.or.kr"
DETAIL_URL = f"{KOBIS_ORIGIN}/kobis/business/mast/mvie/searchMovieDtl.do"
USER_AGENT = "MovieFinder/1.0 (educational local app)"
POSTER_HREF_RE = re.compile(
    r'class="fl thumb"[^>]*href="(/common/mast/movie/[^"]+)"',
    flags=re.IGNORECASE,
)
_download_locks: dict[str, Lock] = {}
_download_locks_guard = Lock()


def ensure_poster_url(movie_code: str) -> str | None:
    """영화 포스터를 로컬에 저장하고 API에서 쓸 경로를 반환한다."""
    code = (movie_code or "").strip()
    if not code:
        return None

    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    existing = _find_local_poster(code)
    if existing is not None:
        return f"/static/posters/{existing.name}"

    with _lock_for(code):
        # 검색과 박스오피스 요청이 겹쳐도 같은 포스터를 중복 다운로드하지 않는다.
        existing = _find_local_poster(code)
        if existing is not None:
            return f"/static/posters/{existing.name}"

        remote_url = _fetch_kobis_poster_url(code)
        if not remote_url:
            return None

        extension = _guess_extension(remote_url)
        target = POSTER_DIR / f"{code}{extension}"
        temporary = target.with_suffix(f"{target.suffix}.part")
        try:
            response = requests.get(
                remote_url,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if content_type and not content_type.startswith("image/"):
                return None
            if not response.content:
                return None
            temporary.write_bytes(response.content)
            temporary.replace(target)
        except (OSError, requests.RequestException):
            temporary.unlink(missing_ok=True)
            return None

        return f"/static/posters/{target.name}"


def ensure_poster_urls(
    movie_codes: list[str],
    *,
    max_workers: int = 5,
) -> dict[str, str | None]:
    """여러 영화의 로컬 포스터 URL을 병렬로 준비한다."""
    codes = list(dict.fromkeys(code.strip() for code in movie_codes if code.strip()))
    if not codes:
        return {}
    with ThreadPoolExecutor(max_workers=min(max_workers, len(codes))) as pool:
        urls = pool.map(ensure_poster_url, codes)
        return dict(zip(codes, urls))


def _lock_for(movie_code: str) -> Lock:
    with _download_locks_guard:
        return _download_locks.setdefault(movie_code, Lock())


def _find_local_poster(movie_code: str) -> Path | None:
    for path in POSTER_DIR.glob(f"{movie_code}.*"):
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def _fetch_kobis_poster_url(movie_code: str) -> str | None:
    try:
        response = requests.get(
            DETAIL_URL,
            params={"code": movie_code},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    match = POSTER_HREF_RE.search(response.text)
    if not match:
        return None
    path = match.group(1)
    if "noimage" in path.lower():
        return None
    return f"{KOBIS_ORIGIN}{path}"


def _guess_extension(url: str) -> str:
    lowered = url.lower().split("?", 1)[0]
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if lowered.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"
