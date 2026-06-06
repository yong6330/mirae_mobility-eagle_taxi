"""환경 변수 로딩 — .env 파일에서 값을 읽어 Settings 인스턴스로 노출한다.

새 환경 변수를 추가하려면:
  1) 이 파일 Settings 클래스에 필드 추가
  2) .env.example에도 동일한 키 추가
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ─ JWT ─────────────────────────────────────────────────────────
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 1440  # 24시간

    # ─ Database ────────────────────────────────────────────────────
    database_url: str = "sqlite:///./eagle_taxi.db"

    # ─ CORS (콤마 구분) ───────────────────────────────────────────
    cors_origins: str = "http://localhost:5173"

    # ─ External mobility API ───────────────────────────────────────
    mobility_rest_api_key: str = ""
    # 명세서 §10-3 요금 산정 fallback 표준:
    #   기본은 Key 누락 시 500(FARE_CONFIG_MISSING), 호출 실패 시 502.
    #   ALLOW_FARE_FALLBACK=true일 때만 fallback(요금 0)을 허용한다 (로컬·시연용).
    allow_fare_fallback: bool = False

    # ─ 관리자 이메일 (콤마 구분) — 가입 시 자동 admin 부여 ──────────
    admin_emails: str = ""
    # 마스터 관리자 이메일 — role 변경 권한 + 보호 대상 (명세 §3주차 보완).
    master_admin_emails: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """콤마 구분 문자열을 리스트로 변환한다."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @staticmethod
    def _email_set(raw: str) -> set[str]:
        return {email.strip().lower() for email in raw.split(",") if email.strip()}

    @property
    def master_admin_email_set(self) -> set[str]:
        """소문자 정규화된 마스터 관리자 이메일 집합."""
        return self._email_set(self.master_admin_emails)

    @property
    def admin_email_set(self) -> set[str]:
        """가입 시 자동 admin 부여 대상 — 일반 admin + 마스터 admin 이메일 합집합."""
        return self._email_set(self.admin_emails) | self.master_admin_email_set


settings = Settings()
