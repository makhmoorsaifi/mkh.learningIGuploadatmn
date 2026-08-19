from database import get_connection

with get_connection() as c:
    rows = c.execute(
        "SELECT id, filename, status, error_message, attempt_count FROM reels WHERE status='failed'"
    ).fetchall()
    for r in rows:
        print(dict(r))