"""문의와 신고 라우터."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Party, SupportEvent, SupportMessage, SupportThread, User
from app.schemas.support import (
    SupportEventOut,
    SupportMessageCreate,
    SupportMessageOut,
    SupportPartyOut,
    SupportStatusUpdate,
    SupportSummary,
    SupportThreadCreate,
    SupportThreadDetail,
    SupportThreadListItem,
    SupportThreadListResponse,
    SupportUserOut,
)
from app.services.admin_action import AdminActionType, AdminTargetType, log_admin_action
from app.utils.time import now_kst_naive

router = APIRouter(prefix="/api/support", tags=["support"])
admin_router = APIRouter(prefix="/api/admin/support", tags=["admin-support"])


@router.get("/threads", response_model=SupportThreadListResponse)
def list_my_support_threads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    threads = db.execute(
        base_thread_query()
        .where(SupportThread.user_id == current_user.id)
        .order_by(SupportThread.updated_at.desc(), SupportThread.id.desc())
    ).scalars().all()
    return SupportThreadListResponse(items=[to_thread_item(thread) for thread in threads], total=len(threads))


@router.post("/threads", response_model=SupportThreadDetail, status_code=status.HTTP_201_CREATED)
def create_support_thread(
    payload: SupportThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    party = None
    if payload.party_id is not None:
        party = db.get(Party, payload.party_id)
        if party is None or party.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="선택한 파티를 찾을 수 없습니다.")

    thread = SupportThread(
        kind=payload.kind,
        title=payload.title.strip(),
        content=payload.content.strip(),
        user_id=current_user.id,
        party_id=party.id if party else None,
    )
    db.add(thread)
    db.flush()

    add_support_event(
        db,
        thread,
        "created",
        "문의가 시작되었습니다. 개발자의 답변이 오기 전까지 다소 시간이 소요될 수 있습니다.",
        status_value=thread.status,
    )
    db.add(
        SupportMessage(
            thread_id=thread.id,
            sender_user_id=current_user.id,
            sender_role="user",
            content=payload.content.strip(),
        )
    )
    db.commit()

    return load_thread_detail(db, thread.id, current_user=current_user)


@router.get("/threads/{thread_id}", response_model=SupportThreadDetail)
def get_my_support_thread(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return load_thread_detail(db, thread_id, current_user=current_user)


@router.post("/threads/{thread_id}/messages", response_model=SupportThreadDetail)
def send_my_support_message(
    thread_id: int,
    payload: SupportMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    thread = get_thread_or_404(db, thread_id)
    if thread.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="문의 내역을 찾을 수 없습니다.")

    add_support_message(db, thread, payload.content, current_user.id, "user")
    return load_thread_detail(db, thread.id, current_user=current_user)


@admin_router.get("/summary", response_model=SupportSummary)
def get_support_summary(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del current_admin
    rows = db.execute(
        select(SupportThread.status, func.count(SupportThread.id)).group_by(SupportThread.status)
    ).all()
    counts = {status_value: count for status_value, count in rows}
    return SupportSummary(
        total=sum(counts.values()),
        resolved=counts.get("resolved", 0),
        in_progress=counts.get("in_progress", 0),
        open=counts.get("open", 0),
    )


@admin_router.get("/threads", response_model=SupportThreadListResponse)
def list_support_threads(
    kind: str | None = None,
    status_filter: str | None = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del current_admin
    stmt = base_thread_query()
    if kind in {"inquiry", "report"}:
        stmt = stmt.where(SupportThread.kind == kind)
    if status_filter in {"open", "in_progress", "resolved"}:
        stmt = stmt.where(SupportThread.status == status_filter)

    threads = db.execute(stmt.order_by(SupportThread.updated_at.desc(), SupportThread.id.desc())).scalars().all()
    return SupportThreadListResponse(items=[to_thread_item(thread, include_user=True) for thread in threads], total=len(threads))


@admin_router.get("/threads/{thread_id}", response_model=SupportThreadDetail)
def get_support_thread(
    thread_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del current_admin
    return load_thread_detail(db, thread_id, include_user=True)


@admin_router.post("/threads/{thread_id}/messages", response_model=SupportThreadDetail)
def send_support_reply(
    thread_id: int,
    payload: SupportMessageCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    thread = get_thread_or_404(db, thread_id)
    before_status = thread.status
    if thread.status == "open":
        thread.status = "in_progress"
        add_support_event(
            db,
            thread,
            "status",
            format_status_event_text(thread.status),
            status_value=thread.status,
        )
        log_admin_action(
            db,
            actor_admin_id=current_admin.id,
            action_type=AdminActionType.SUPPORT_STATUS_UPDATE,
            target_type=AdminTargetType.SUPPORT_THREAD,
            target_id=thread.id,
            before_value=before_status,
            after_value=thread.status,
            note="문의 답변 시작",
        )
    add_support_message(db, thread, payload.content, current_admin.id, "admin")
    return load_thread_detail(db, thread.id, include_user=True)


@admin_router.patch("/threads/{thread_id}/status", response_model=SupportThreadDetail)
def update_support_status(
    thread_id: int,
    payload: SupportStatusUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    thread = get_thread_or_404(db, thread_id)
    before_status = thread.status
    thread.status = payload.status
    thread.updated_at = now_kst_naive()
    db.add(thread)
    if before_status != thread.status:
        add_support_event(
            db,
            thread,
            "status",
            format_status_event_text(thread.status),
            status_value=thread.status,
        )
        log_admin_action(
            db,
            actor_admin_id=current_admin.id,
            action_type=AdminActionType.SUPPORT_STATUS_UPDATE,
            target_type=AdminTargetType.SUPPORT_THREAD,
            target_id=thread.id,
            before_value=before_status,
            after_value=thread.status,
            note="문의 상태 변경",
        )
    db.commit()
    return load_thread_detail(db, thread.id, include_user=True)


def base_thread_query():
    return select(SupportThread).options(
        selectinload(SupportThread.user),
        selectinload(SupportThread.party),
        selectinload(SupportThread.messages).selectinload(SupportMessage.sender),
        selectinload(SupportThread.events),
    )


def get_thread_or_404(db: Session, thread_id: int) -> SupportThread:
    thread = db.execute(base_thread_query().where(SupportThread.id == thread_id)).scalar_one_or_none()
    if thread is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="문의 내역을 찾을 수 없습니다.")
    return thread


def add_support_message(db: Session, thread: SupportThread, content: str, sender_user_id: int, sender_role: str) -> None:
    thread.updated_at = now_kst_naive()
    db.add(
        SupportMessage(
            thread_id=thread.id,
            sender_user_id=sender_user_id,
            sender_role=sender_role,
            content=content.strip(),
        )
    )
    db.add(thread)
    db.commit()


def load_thread_detail(
    db: Session,
    thread_id: int,
    current_user: User | None = None,
    include_user: bool = False,
) -> SupportThreadDetail:
    thread = get_thread_or_404(db, thread_id)
    if current_user is not None and thread.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="문의 내역을 찾을 수 없습니다.")

    item = to_thread_item(thread, include_user=include_user)
    return SupportThreadDetail(
        **item.model_dump(),
        messages=[to_message_out(message) for message in thread.messages],
        events=[to_event_out(event) for event in thread.events],
    )


def add_support_event(
    db: Session,
    thread: SupportThread,
    event_type: str,
    content: str,
    status_value: str | None = None,
) -> None:
    db.add(
        SupportEvent(
            thread_id=thread.id,
            event_type=event_type,
            status=status_value,
            content=content,
        )
    )


def to_thread_item(thread: SupportThread, include_user: bool = False) -> SupportThreadListItem:
    return SupportThreadListItem(
        id=thread.id,
        code=f"Q{thread.id:05d}",
        kind=thread.kind,
        status=thread.status,
        title=thread.title,
        content=thread.content,
        user=to_user_out(thread.user) if include_user and thread.user else None,
        party=to_party_out(thread.party) if thread.party else None,
        message_count=len(thread.messages or []),
        created_at=thread.created_at,
        updated_at=thread.updated_at,
    )


def to_message_out(message: SupportMessage) -> SupportMessageOut:
    sender_name = "시스템"
    if message.sender_role == "admin":
        sender_name = message.sender.name if message.sender else "운영팀"
    if message.sender_role == "user":
        sender_name = message.sender.name if message.sender else "사용자"

    return SupportMessageOut(
        id=message.id,
        thread_id=message.thread_id,
        sender_user_id=message.sender_user_id,
        sender_role=message.sender_role,
        sender_name=sender_name,
        content=message.content,
        created_at=message.created_at,
    )


def to_event_out(event: SupportEvent) -> SupportEventOut:
    return SupportEventOut(
        id=event.id,
        thread_id=event.thread_id,
        event_type=event.event_type,
        status=event.status,
        content=event.content,
        created_at=event.created_at,
    )


def format_status_event_text(status_value: str) -> str:
    labels = {
        "open": "접수",
        "in_progress": "진행 중",
        "resolved": "완료",
    }
    return f"현재 상태가 {labels.get(status_value, status_value)}로 변경되었습니다."


def to_user_out(user: User) -> SupportUserOut:
    return SupportUserOut(id=user.id, name=user.name, email=user.email)


def to_party_out(party: Party) -> SupportPartyOut:
    return SupportPartyOut(
        id=party.id,
        start_place=party.start_place,
        end_place=party.end_place,
        departure_time=party.departure_time,
    )
