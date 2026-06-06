"""채팅 메시지 스키마 — 명세서 v0.4 MSG-001, MSG-002."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageOut(BaseModel):
    """채팅 메시지 응답 — 명세 v0.4 MSG-001 / MSG-002 응답 형식.

    user_name은 작성자의 사용자 이름. password_hash 등 민감 정보는 포함하지 않는다.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    party_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime


class MessageListResponse(BaseModel):
    """GET /api/parties/{party_id}/messages 응답 — items 배열."""

    items: list[MessageOut]


class MessageSendIn(BaseModel):
    """WebSocket 송신 형식 — `{"content": "..."}`. 명세 v0.4 MSG-002."""

    content: str = Field(min_length=1, max_length=1000)
