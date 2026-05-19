"""파티별 WebSocket 라우터 — 명세서 v0.4 MSG-002 / F-CHAT-002, F-CHAT-004.

명세 §7 (WebSocket 인증):
  - 일반 fetch Authorization 헤더를 못 쓰므로 query token 방식 사용.
  - 토큰 없음 / 만료 / 비활성 사용자 / 비참여자 / 존재하지 않는 파티 → 모두 연결 거부.

명세 MSG-002 송신/수신 형식:
  - 송신: {"content": "..."}
  - 수신: {id, party_id, user_id, user_name, content, created_at}
"""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import SessionLocal
from app.models import Message, Party, PartyMember, User
from app.schemas.message import MessageSendIn
from app.security import decode_access_token
from app.services.chat import manager

router = APIRouter(tags=["chat"])


def _authenticate(token: str) -> int | None:
    """JWT를 디코드해 user_id 반환. 실패 시 None."""
    try:
        payload = decode_access_token(token)
    except JWTError:
        return None
    sub = payload.get("sub")
    try:
        return int(sub) if sub is not None else None
    except (TypeError, ValueError):
        return None


@router.websocket("/ws/parties/{party_id}")
async def chat_socket(
    websocket: WebSocket,
    party_id: int,
    token: str | None = Query(default=None),
):
    """파티 채팅 WebSocket.

    연결 시 검증 단계:
      1) token 디코드 → user_id 확보
      2) DB에서 사용자 조회, is_active 확인
      3) 파티 존재 확인
      4) 사용자가 해당 파티 참여자인지 확인
    이후 송수신 루프:
      - 클라가 보내는 {"content": "..."} JSON을 검증·저장하고 방 전체에 브로드캐스트
      - 빈 메시지는 저장하지 않고 무시
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = _authenticate(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # DB 검증 — 동기 SQLAlchemy 세션을 짧게 열어 처리
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        party = db.get(Party, party_id)
        if party is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        is_member = db.execute(
            select(PartyMember).where(
                PartyMember.party_id == party_id, PartyMember.user_id == user_id
            )
        ).scalar_one_or_none()
        if is_member is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 검증 통과 — 이름은 미리 캐시 (각 메시지마다 user 조회 안 함)
        user_name = user.name

    await manager.connect(party_id, websocket)
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                msg_in = MessageSendIn.model_validate(raw)
            except Exception:
                # 빈 메시지 또는 형식 오류 — 명세: 저장하지 않고 무시
                continue
            content = msg_in.content.strip()
            if not content:
                continue

            with SessionLocal() as db:
                message = Message(party_id=party_id, user_id=user_id, content=content)
                db.add(message)
                db.commit()
                db.refresh(message)
                payload = {
                    "id": message.id,
                    "party_id": message.party_id,
                    "user_id": message.user_id,
                    "user_name": user_name,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                }

            await manager.broadcast(party_id, payload)

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(party_id, websocket)
