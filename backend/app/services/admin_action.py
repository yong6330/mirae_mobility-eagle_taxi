"""관리자 조작 기록 헬퍼 — 명세서 v0.4 ADMIN-012 / data-model admin_actions.

ADMIN-005/006/007에서 변경을 수행할 때 같은 트랜잭션 안에서 호출한다.
(commit은 호출하는 라우터에서 한다.)
"""

from sqlalchemy.orm import Session

from app.models import AdminAction


class AdminActionType:
    USER_ROLE_UPDATE = "user_role_update"
    USER_STATUS_UPDATE = "user_status_update"
    PARTY_STATUS_UPDATE = "party_status_update"
    # ADMIN-013~027 유지보수 API
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_PASSWORD_RESET = "user_password_reset"
    USER_DELETE = "user_delete"
    PARTY_CREATE = "party_create"
    PARTY_UPDATE = "party_update"
    PARTY_DELETE = "party_delete"
    PARTY_MEMBER_ADD = "party_member_add"
    PARTY_MEMBER_REMOVE = "party_member_remove"
    PARTY_FARE_RECALCULATE = "party_fare_recalculate"
    PARTY_FARE_OVERRIDE = "party_fare_override"
    MESSAGE_HIDE = "message_hide"
    ADMIN_NOTICE_CREATE = "admin_notice_create"
    SUPPORT_STATUS_UPDATE = "support_status_update"
    ADMIN_LOGIN = "admin_login"


class AdminTargetType:
    USER = "user"
    PARTY = "party"
    PARTY_MEMBER = "party_member"
    FARE = "fare"
    MESSAGE = "message"
    SUPPORT_THREAD = "support_thread"


def log_admin_action(
    db: Session,
    *,
    actor_admin_id: int,
    action_type: str,
    target_type: str,
    target_id: int,
    before_value: str | None = None,
    after_value: str | None = None,
    note: str | None = None,
) -> AdminAction:
    """admin_actions에 조작 1건을 추가한다 (flush만, commit은 호출자 책임)."""
    action = AdminAction(
        actor_admin_id=actor_admin_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        before_value=before_value,
        after_value=after_value,
        note=note,
    )
    db.add(action)
    db.flush()  # admin_action_id를 응답에 싣기 위해 id를 즉시 확보
    return action
