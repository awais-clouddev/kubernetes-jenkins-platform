from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Containerized Help Desk Platform API is running"

from unittest.mock import MagicMock, patch
from redis.exceptions import ConnectionError as RedisConnectionError


def test_ticket_cache_invalidation_when_redis_down():
    with patch("app.main.get_redis_connection") as mock_redis:
        mock_redis.return_value.scan_iter.side_effect = RedisConnectionError()
        from app.main import clear_ticket_cache
        clear_ticket_cache()


def test_ticket_listing_when_redis_down():
    row = (1, "Test User", "Test issue", "High", "Open", "2026-10-11")
    db = MagicMock()
    db.cursor.return_value.fetchall.return_value = [row]

    with patch("app.main.get_redis_connection") as mock_redis, \
         patch("app.main.get_database_connection", return_value=db):
        mock_redis.return_value.get.side_effect = RedisConnectionError()
        mock_redis.return_value.setex.side_effect = RedisConnectionError()
        response = client.get("/tickets")

    assert response.status_code == 200
    assert response.json()["source"] == "postgresql"
    assert len(response.json()["tickets"]) == 1


def test_health_when_redis_down():
    with patch("app.main.get_database_connection"), \
         patch("app.main.get_redis_connection") as mock_redis:
        mock_redis.return_value.ping.side_effect = RedisConnectionError()
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["redis"] == "unavailable"


def test_health_when_database_down():
    with patch("app.main.get_database_connection", side_effect=Exception("DB down")):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"
