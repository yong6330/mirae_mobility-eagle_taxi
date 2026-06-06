"""채팅 메시지 라우터 — 명세서 v0.4 MSG-001 / F-CHAT-001, F-CHAT-003.

이전 메시지 조회만 HTTP. 실시간 송수신은 chat_ws.py의 WebSocket에서 처리.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Message, Party, PartyMember, User
from app.schemas.message import MessageListResponse, MessageOut

router = APIRouter(tags=["chat"])


def _ensure_party_member(db: Session, party_id: int, user_id: int) -> None:
    """파티 존재 확인 + 현재 사용자가 참여자인지 확인.

    명세 v0.4 MSG-001 처리 로직:
      - 존재하지 않는 파티 → 404
      - 참여자가 아님 → 403
    """
    party = db.get(Party, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 파티입니다.")

    is_member = db.execute(
        select(PartyMember).where(
            PartyMember.party_id == party_id, PartyMember.user_id == user_id
        )
    ).scalar_one_or_none()
    if is_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="파티 참여자만 채팅을 이용할 수 있습니다.",
        )


@router.get(
    "/api/parties/{party_id}/messages",
    response_model=MessageListResponse,
)
def list_messages(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """채팅 메시지 목록 조회 — 명세 v0.4 MSG-001.

    created_at 오름차순 정렬. items 배열에 메시지 + user_name 함께 반환.
    """
    _ensure_party_member(db, party_id, current_user.id)

    stmt = (
        select(Message)
        .where(Message.party_id == party_id, Message.is_hidden.is_(False))
        .options(selectinload(Message.user))
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    messages = db.execute(stmt).scalars().all()

    items = [
        MessageOut(
            id=m.id,
            party_id=m.party_id,
            user_id=m.user_id,
            user_name=m.user.name,
            content=m.content,
            created_at=m.created_at,
        )
        for m in messages
    ]
    return MessageListResponse(items=items)
