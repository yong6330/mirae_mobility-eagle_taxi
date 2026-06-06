"""환경 변수 로딩 — backend/.env 파일에서 값을 읽어 Settings 인스턴스로 노출한다.

새 환경 변수를 추가하려면:
  1) 이 파일 Settings 클래스에 필드 추가
  2) .env.example에도 동일한 키 추가
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─ JWT ─────────────────────────────────────────────────────────
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 1440

    # ─ Database ────────────────────────────────────────────────────
    database_url: str = "sqlite:///./eagle_taxi.db"

    # ─ CORS (콤마 구분) ───────────────────────────────────────────
    cors_origins: str = "http://localhost:5173"

    # ─ External mobility API ───────────────────────────────────────
    mobility_rest_api_key: str = ""
    allow_fare_fallback: bool = False

    # ─ 관리자 이메일 (콤마 구분) ─────────────────────────────────
    admin_emails: str = ""
    master_admin_emails: str = ""

    @property
    def mobility_api_key_configured(self) -> bool:
        """외부 요금 API Key 설정 여부."""
        return bool(self.mobility_rest_api_key.strip())

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