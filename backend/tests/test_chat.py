"""채팅 API 테스트 — 명세서 v0.4 MSG-001, MSG-002 / F-CHAT-001~004."""

from datetime import timedelta

from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _future_iso(hours: int = 2) -> str:
    return (now_kst_naive() + timedelta(hours=hours)).isoformat()


def _party_payload(**overrides) -> dict:
    base = {
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": _future_iso(),
        "meeting_point": "정문",
        "meeting_note": "검은 가방",
        "max_members": 4,
        "gender_rule": "any",
    }
    base.update(overrides)
    return base


# ────────────────────────────────────────────────────────────────────
# MSG-001: GET /api/parties/{party_id}/messages
# ────────────────────────────────────────────────────────────────────

def test_messages_requires_auth(client):
    res = client.get("/api/parties/1/messages")
    assert res.status_code == 401


def test_messages_not_a_member_returns_403(client):
    _, host_token = register_and_login(client, "msg_host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    _, other_token = register_and_login(client, "msg_other@yonsei.ac.kr")
    res = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(other_token)
    )
    assert res.status_code == 403
    assert "참여자" in res.json()["detail"]


def test_messages_party_not_found(client):
    _, token = register_and_login(client, "msg_nf@yonsei.ac.kr")
    res = client.get("/api/parties/99999/messages", headers=auth_header(token))
    assert res.status_code == 404


def test_messages_empty_for_new_party(client):
    """파티 생성 직후 메시지 0개."""
    _, token = register_and_login(client, "msg_empty@yonsei.ac.kr")
    party = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()
    res = client.get(f"/api/parties/{party['id']}/messages", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json() == {"items": []}


# ────────────────────────────────────────────────────────────────────
# MSG-002: WebSocket
# ────────────────────────────────────────────────────────────────────

def test_websocket_rejects_without_token(client):
    """token query 없으면 연결 거부."""
    from starlette.websockets import WebSocketDisconnect
    try:
        with client.websocket_connect("/ws/parties/1") as ws:
            ws.receive_json()
        assert False, "연결이 거부되어야 함"
    except WebSocketDisconnect:
        pass


def test_websocket_rejects_invalid_token(client):
    from starlette.websockets import WebSocketDisconnect
    try:
        with client.websocket_connect("/ws/parties/1?token=invalid") as ws:
            ws.receive_json()
        assert False
    except WebSocketDisconnect:
        pass


def test_websocket_rejects_non_member(client):
    """파티 비참여자는 WebSocket 연결 거부."""
    from starlette.websockets import WebSocketDisconnect
    _, host_token = register_and_login(client, "ws_host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    _, other_token = register_and_login(client, "ws_other@yonsei.ac.kr")
    try:
        with client.websocket_connect(
            f"/ws/parties/{party['id']}?token={other_token}"
        ) as ws:
            ws.receive_json()
        assert False
    except WebSocketDisconnect:
        pass


def test_websocket_send_and_broadcast(client):
    """참여자 두 명이 연결, 한 명이 보낸 메시지를 두 명 모두 수신."""
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ws_a@yonsei.ac.kr", name="앨리스")
    party = client.post(
        "/api/parties",
        json={**_party_payload(), "departure_time": base_time.isoformat()},
        headers=auth_header(host_token),
    ).json()
    _, peer_token = register_and_login(client, "ws_b@yonsei.ac.kr", name="밥")
    client.post(f"/api/parties/{party['id']}/join", headers=auth_header(peer_token))

    with client.websocket_connect(
        f"/ws/parties/{party['id']}?token={host_token}"
    ) as ws_a, client.websocket_connect(
        f"/ws/parties/{party['id']}?token={peer_token}"
    ) as ws_b:
        ws_a.send_json({"content": "안녕하세요"})
        msg_a = ws_a.receive_json()
        msg_b = ws_b.receive_json()
        assert msg_a == msg_b
        assert msg_a["content"] == "안녕하세요"
        assert msg_a["user_name"] == "앨리스"
        assert msg_a["party_id"] == party["id"]

    # 메시지가 DB에 저장됐는지 GET으로도 확인
    res = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(host_token)
    )
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["content"] == "안녕하세요"
    assert items[0]["user_name"] == "앨리스"


def test_websocket_empty_message_ignored(client):
    """빈 메시지는 저장 안 됨."""
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ws_empty@yonsei.ac.kr")
    party = client.post(
        "/api/parties",
        json={**_party_payload(), "departure_time": base_time.isoformat()},
        headers=auth_header(host_token),
    ).json()

    with client.websocket_connect(
        f"/ws/parties/{party['id']}?token={host_token}"
    ) as ws:
        ws.send_json({"content": ""})  # 빈 메시지
        ws.send_json({"content": "   "})  # 공백만
        ws.send_json({"content": "실제 메시지"})
        received = ws.receive_json()
        assert received["content"] == "실제 메시지"

    res = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(host_token)
    )
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["content"] == "실제 메시지"


def test_messages_ordered_by_created_at_asc(client):
    """이전 메시지 조회는 created_at 오름차순."""
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ws_order@yonsei.ac.kr")
    party = client.post(
        "/api/parties",
        json={**_party_payload(), "departure_time": base_time.isoformat()},
        headers=auth_header(host_token),
    ).json()

    with client.websocket_connect(
        f"/ws/parties/{party['id']}?token={host_token}"
    ) as ws:
        ws.send_json({"content": "첫 번째"})
        ws.receive_json()
        ws.send_json({"content": "두 번째"})
        ws.receive_json()
        ws.send_json({"content": "세 번째"})
        ws.receive_json()

    res = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(host_token)
    )
    items = res.json()["items"]
    assert [m["content"] for m in items] == ["첫 번째", "두 번째", "세 번째"]
