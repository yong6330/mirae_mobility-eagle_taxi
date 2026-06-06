"""채팅 연결 관리자 — 명세서 v0.4 MSG-002.

파티별 WebSocket 연결 풀을 관리하고, 같은 party_id 참여자에게만 메시지를 브로드캐스트한다.
프로세스 내 메모리에 저장 (멀티 프로세스 환경에서는 Redis 등 필요, MVP 범위에서는 단일 워커).
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """파티별 WebSocket 연결 풀."""

    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, party_id: int, ws: WebSocket) -> None:
        """WebSocket을 수락하고 해당 파티 방에 추가한다."""
        await ws.accept()
        async with self._lock:
            self._rooms[party_id].add(ws)

    async def disconnect(self, party_id: int, ws: WebSocket) -> None:
        """파티 방에서 해당 연결을 제거한다."""
        async with self._lock:
            self._rooms[party_id].discard(ws)
            if not self._rooms[party_id]:
                self._rooms.pop(party_id, None)

    async def broadcast(self, party_id: int, payload: dict) -> None:
        """같은 party_id 모든 연결에 JSON 메시지 전송. 죽은 연결은 자동 정리."""
        async with self._lock:
            targets = list(self._rooms.get(party_id, ()))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                room = self._rooms.get(party_id)
                if room:
                    for ws in dead:
                        room.discard(ws)


# 앱 단일 인스턴스
manager = ConnectionManager()
