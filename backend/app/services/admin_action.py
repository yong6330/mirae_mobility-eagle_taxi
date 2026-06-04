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


class AdminTargetType:
    USER = "user"
    PARTY = "party"


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
    return action
