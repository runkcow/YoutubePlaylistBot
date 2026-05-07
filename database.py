
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"
def getconn (dbpath: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(dbpath, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_channels () -> list[int]:
    with getconn() as conn:
        row = conn.execute("SELECT channel_id FROM channel_playlists").fetchall()
        return [ i["channel_id"] for i in row ]

def get_active_channels () -> list[int]:
    with getconn() as conn:
        row = conn.execute("SELECT channel_id FROM channel_playlists WHERE active = 1").fetchall()
        return [ i["channel_id"] for i in row ]

def get_channel (channel_id: int) -> list[dict]:
    with getconn() as conn:
        row = conn.execute("SELECT * from channel_playlists WHERE channel_id = ?", (channel_id, )).fetchone()
        return row

def get_channel_playlist (channel_id: int) -> str | None:
    with getconn() as conn:
        row = conn.execute("SELECT playlist_id FROM channel_playlists WHERE channel_id = ?", (channel_id, )).fetchone()
        return row["playlist_id"] if row else None

def get_playlist_contains_video (playlist_id: str, video_id: str) -> bool:
    with getconn() as conn:
        row = conn.execute("SELECT 1 FROM playlist_videos WHERE playlist_id = ? AND video_id = ?", (playlist_id, video_id)).fetchone()
        return row is not None

def get_channel_last_message (channel_id: int) -> int | None:
    with getconn() as conn:
        row = conn.execute("SELECT last_message_id FROM channel_playlists WHERE channel_id = ?", (channel_id, )).fetchone()
        return row["last_message_id"] if row else None

def get_data_quota () -> dict[str, int] | None:
    with getconn() as conn:
        row = conn.execute("SELECT * FROM quota_data LIMIT 1").fetchone()
        return row

def add_channel (channel_id: int, playlist_id: str, last_message_id: int = None) -> bool:
    with getconn() as conn:
        # NOTE: this could fail, enabling the if statement and creating a duplicate row, unlikely
        cursor = conn.execute("UPDATE channel_playlists SET active = 1 WHERE channel_id = ?", (channel_id, ))
        if cursor.rowcount == 0:
            cursor = conn.execute("INSERT INTO channel_playlists (channel_id, playlist_id, last_message_id, active) VALUES (?, ?, ?, ?)", (channel_id, playlist_id, last_message_id, 1))
            return cursor.rowcount > 0
        return True

def add_playlist_video (playlist_id: str, video_id: str) -> bool:
    try:
        with getconn() as conn:
            cursor = conn.execute("INSERT INTO playlist_videos (playlist_id, video_id) VALUES (?, ?)", (playlist_id, video_id))
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False

def update_channel_last_message (channel_id: int, message_id: int) -> bool:
    with getconn() as conn:
        cursor = conn.execute("UPDATE channel_playlists SET last_message_id = ? WHERE channel_id = ?", (message_id, channel_id))
        return cursor.rowcount > 0

def update_quota_data (remaining_quota: int, last_check: int) -> bool:
    with getconn() as conn:
        cursor = conn.execute("UPDATE quota_data SET remaining_quota = ?, last_check = ?", (remaining_quota, last_check))
        return cursor.rowcount > 0

def remove_channel (channel_id: int) -> bool:
    with getconn() as conn:
        cursor = conn.execute("UPDATE channel_playlists SET active = 0 WHERE channel_id = ?", (channel_id, ))
        return cursor.rowcount > 0

# NOTE: videos won't be removed from playlists even if the message is deleted for simplicity
