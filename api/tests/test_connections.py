import os
from unittest.mock import Mock, patch
import pytest
from app import main


@pytest.mark.parametrize("operation", [
    lambda: main.create_ticket(main.TicketCreate(
        employee_name="Awais", issue="Example issue", priority="High")),
    lambda: main.get_tickets(search="", status="", priority=""),
    lambda: main.update_ticket_status(
        1, main.TicketStatusUpdate(status="Closed")),
    main.dashboard_summary,
])
def test_query_failure_rolls_back_and_closes(operation):
    db = Mock()
    cursor = db.cursor.return_value
    cursor.execute.side_effect = RuntimeError("query failed")
    cache = Mock()
    cache.get.return_value = None
    with patch("app.main.get_database_connection", return_value=db), \
         patch("app.main.get_redis_connection", return_value=cache):
        with pytest.raises(RuntimeError, match="query failed"):
            operation()
    db.rollback.assert_called_once()
    cursor.close.assert_called_once()
    db.close.assert_called_once()


def test_cursor_creation_failure_closes_connection():
    db = Mock()
    db.cursor.side_effect = RuntimeError("cursor failed")
    with patch("app.main.get_database_connection", return_value=db):
        with pytest.raises(RuntimeError, match="cursor failed"):
            with main.database_session():
                pytest.fail("Unexpected session entry")
    db.rollback.assert_called_once()
    db.close.assert_called_once()


def test_cursor_close_failure_still_closes_connection():
    db = Mock()
    db.cursor.return_value.close.side_effect = RuntimeError("close failed")
    with patch("app.main.get_database_connection", return_value=db):
        with pytest.raises(RuntimeError, match="close failed"):
            with main.database_session():
                pass
    db.close.assert_called_once()


def test_dependency_timeouts_and_required_password():
    with patch.dict(os.environ, {"DATABASE_PASSWORD": "test-only"}, clear=True):
        with patch("app.main.psycopg2.connect") as connect:
            main.get_database_connection()
            settings = connect.call_args.kwargs
            assert settings["connect_timeout"] == 5
            assert "statement_timeout=5000" in settings["options"]
            assert "lock_timeout=3000" in settings["options"]
        with patch("app.main.redis.Redis") as connect:
            main.get_redis_connection()
            settings = connect.call_args.kwargs
            assert settings["socket_connect_timeout"] == 2
            assert settings["socket_timeout"] == 2
            assert "retry" in settings

    with patch.dict(os.environ, {}, clear=True):
        with patch("app.main.psycopg2.connect") as connect:
            with pytest.raises(KeyError):
                main.get_database_connection()
            connect.assert_not_called()
