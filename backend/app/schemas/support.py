"""문의와 신고 API 스키마."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SupportKind = Literal["inquiry", "report"]
SupportStatus = Literal["open", "in_progress", "resolved"]


class SupportThreadCreate(BaseModel):
    kind: SupportKind = "inquiry"
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=2000)
    party_id: int | None = None


class SupportMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class SupportStatusUpdate(BaseModel):
    status: SupportStatus


class SupportPartyOut(BaseModel):
    id: int
    start_place: str
    end_place: str
    departure_time: datetime


class SupportUserOut(BaseModel):
    id: int
    name: str
    email: str


class SupportMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_id: int
    sender_user_id: int | None = None
    sender_role: str
    sender_name: str
    content: str
    created_at: datetime


class SupportEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_id: int
    event_type: str
    status: str | None = None
    content: str
    created_at: datetime


class SupportThreadListItem(BaseModel):
    id: int
    code: str
    kind: str
    status: str
    title: str
    content: str
    user: SupportUserOut | None = None
    party: SupportPartyOut | None = None
    message_count: int
    created_at: datetime
    updated_at: datetime


class SupportThreadDetail(SupportThreadListItem):
    messages: list[SupportMessageOut]
    events: list[SupportEventOut] = []


class SupportThreadListResponse(BaseModel):
    items: list[SupportThreadListItem]
    total: int


class SupportSummary(BaseModel):
    total: int
    resolved: int
    in_progress: int
    open: int
