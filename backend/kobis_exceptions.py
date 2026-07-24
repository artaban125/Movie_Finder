"""KOBIS 공공데이터 API 연동 예외."""


class KobisError(Exception):
    """KOBIS API 연동 중 발생하는 기본 예외."""


class KobisConfigError(KobisError):
    """API 키 또는 베이스 URL이 설정되지 않았을 때."""


class KobisTimeoutError(KobisError):
    """외부 API 요청이 시간 초과되었을 때."""


class KobisRequestError(KobisError):
    """외부 API HTTP/네트워크 요청이 실패했을 때."""


class KobisResponseError(KobisError):
    """외부 API가 오류 응답 또는 잘못된 본문을 반환했을 때."""
