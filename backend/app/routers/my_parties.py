"""내 파티 목록 라우터 — 기능명세서 F-PARTY-012.

로그인 사용자가 자신이 생성한 파티와 참여한 파티를 한 번에 확인하는 API.
생성자는 자동으로 party_members에 속하지만, 응답 시 joined_parties에 중복 표시하지 않는다.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Party, PartyMember, User
from app.schemas.party import MyPartiesResponse
from app.services.party import to_summary

router = APIRouter(prefix="/api/my", tags=["my"])


@router.get("/parties", response_model=MyPartiesResponse)
def list_my_parties(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내가 만든 파티(created)와 참여한 파티(joined)를 구분해 반환한다.

    처리 순서 — F-PARTY-012:
      1) creator_id == 현재 사용자인 파티 조회 → created_parties
      2) party_members에 현재 사용자가 있고, 본인이 생성하지 않은 파티 조회 → joined_parties
    각 파티는 최신순(created_at desc)으로 정렬한다.
    """
    created_stmt = (
        select(Party)
        .where(Party.creator_id == current_user.id)
        .options(selectinload(Party.members))
        .order_by(Party.created_at.desc(), Party.id.desc())
    )
    created_parties = db.execute(created_stmt).scalars().all()

    joined_stmt = (
        select(Party)
        .join(PartyMember, PartyMember.party_id == Party.id)
        .where(PartyMember.user_id == current_user.id)
        .where(Party.creator_id != current_user.id)
        .options(selectinload(Party.members))
        .order_by(Party.created_at.desc(), Party.id.desc())
    )
    joined_parties = db.execute(joined_stmt).scalars().all()

    return MyPartiesResponse(
        created_parties=[to_summary(p) for p in created_parties],
        joined_parties=[to_summary(p) for p in joined_parties],
    )
