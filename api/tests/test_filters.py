import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ROW = (1, "Awais", "Example issue", "High", "Open", "2026-10-16")


class MemoryCache:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def setex(self, key, ttl, value):
        self.data[key] = value


def test_filter_case_and_request_order():
    for field, values in (
        ("priority", ("High", "high")),
        ("priority", ("high", "High")),
        ("status", ("Open", "open")),
        ("status", ("open", "Open")),
    ):
        cache = MemoryCache()
        db = Mock()
        db.cursor.return_value.fetchall.return_value = [ROW]
        with patch("app.main.get_redis_connection", return_value=cache), \
             patch("app.main.get_database_connection", return_value=db) as connect:
            first = client.get("/tickets", params={field: values[0]})
            second = client.get("/tickets", params={field: values[1]})
        assert first.status_code == second.status_code == 200
        assert first.json()["tickets"] == second.json()["tickets"]
        assert second.json()["source"] == "redis-cache"
        assert connect.call_count == 1
        query, parameters = db.cursor.return_value.execute.call_args.args
        assert f"LOWER({field}) = %s" in query
        assert parameters == [values[0].lower()]


def test_filter_delimiters_do_not_collide():
    cache = MemoryCache()
    db = Mock()
    db.cursor.return_value.fetchall.return_value = []
    with patch("app.main.get_redis_connection", return_value=cache), \
         patch("app.main.get_database_connection", return_value=db) as connect:
        for filters in (
            {"search": "a:status:b", "status": "c"},
            {"search": "a", "status": "b:status:c"},
        ):
            assert client.get("/tickets", params=filters).status_code == 200
    assert connect.call_count == 2
    assert len(cache.data) == 2
