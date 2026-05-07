
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from urllib.parse import urlparse, parse_qs
import asyncio
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import config as Config
from handle_token import get_creds
from database import get_data_quota, update_quota_data

VIDEO_ID_REGEX = re.compile(r"^[A-Za-z0-9_-]{11}$")

def extract_video_id (url: str) -> str | None:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        host = host.replace("m.", "")
        if host == "youtu.be":
            vid = parsed.path.lstrip("/")
            return vid if VIDEO_ID_REGEX.match(vid) else None
        if "youtube.com" in host:
            # /watch?v=VIDEOID
            if parsed.path == "/watch":
                vid = parse_qs(parsed.query).get("v", [None])[0]
                return vid if vid and VIDEO_ID_REGEX.match(vid) else None
            # /shorts/VIDEOID
            if parsed.path.startswith("/shorts/"):
                vid = parsed.path.split("/")[2]
                return vid if VIDEO_ID_REGEX.match(vid) else None
            # /embed/VIDEOID
            if parsed.path.startswith("/embed/"):
                vid = parsed.path.split("/")[2]
                return vid if VIDEO_ID_REGEX.match(vid) else None
        match = re.search(r"(?:v=|/)([A-Za-z0-9_-]{11})", url)
        if match:
            return match.group(1)
        # print(f'Error @ extract_video_id | Video id not found')
    except Exception as e:
        print(f'Exception @ extract_video_id: {e}')
    return None

def pacific_time_from_unix (ts: int) -> tuple[int, int, int]:
    dt = datetime.fromtimestamp(ts, timezone.utc).astimezone(ZoneInfo("America/Los_Angeles"))
    return (dt.year, dt.month, dt.day)

def quota_reset_passed (last_check: int) -> bool:
    return pacific_time_from_unix(int(time.time())) != pacific_time_from_unix(last_check)

def get_youtube ():
    return build("youtube", "v3", credentials=get_creds())

def _add_playlist_video_sync (playlist_id: str, video_id: str):
    return get_youtube().playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                }
            }
        }
    ).execute()

async def add_playlist_video (playlist_id: str, video_id: str) -> tuple[bool, str]:
    quota_data = dict(get_data_quota())
    if quota_reset_passed(quota_data["last_check"]):
        quota_data["remaining_quota"] = Config.YOUTUBE_API_QUOTA
    quota_data["last_check"] = int(time.time())
    if quota_data["remaining_quota"] < Config.YOUTUBE_API_QUOTA_PLAYLIST_INSERT_COST:
        return (False, f'Error @ add_playlist_video | Insufficient quota')
    try:
        await asyncio.to_thread(_add_playlist_video_sync, playlist_id, video_id)
        # assume this worked if no httperror is thrown
        quota_data["remaining_quota"] -= Config.YOUTUBE_API_QUOTA_PLAYLIST_INSERT_COST
        update_quota_data(quota_data["remaining_quota"], quota_data["last_check"])
        return (True, "")
    except HttpError as e:
        # NOTE: maybe I should raise error, don't really want the bot to be repeatedly breaking tho
        if e.resp.status == 409:
            return (False, f'Status error @ add_playlist_video | Duplicate video (409): {e}')
        elif e.resp.status == 403:
            return (False, f'Status error @ add_playlist_video | Quota exceeded (403): {e}')
        elif e.resp.status == 404:
            print(f'Status notice @ add_playlist_video | Video {video_id} not found (404): {e}')
            return (True, "")
        else:
            return (False, f'Status error @ add_playlist_video | Unknown ({e.resp.status}): {e}')
    
def _create_playlist_sync (playlist_name: str, playlist_description: str):
    return get_youtube().playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name[:150],
                "description": playlist_description[:5000],
            },
            "status": {
                "privacyStatus": "unlisted"
            }
        }
    ).execute()

async def create_playlist (playlist_name: str, playlist_description: str = "") -> tuple[bool, str]:
    quota_data = dict(get_data_quota())
    if quota_reset_passed(quota_data["last_check"]):
        quota_data["remaining_quota"] = Config.YOUTUBE_API_QUOTA
    quota_data["last_check"] = int(time.time())
    if quota_data["remaining_quota"] < Config.YOUTUBE_API_QUOTA_PLAYLIST_CREATE_COST:
        return (False, f'Error @ create_playlist | Insufficient quota')
    try:
        response = await asyncio.to_thread(_create_playlist_sync, playlist_name, playlist_description)
        quota_data["remaining_quota"] -= Config.YOUTUBE_API_QUOTA_PLAYLIST_CREATE_COST
        update_quota_data(quota_data["remaining_quota"], quota_data["last_check"])
        return (True, response["id"])
    except HttpError as e:
        if e.resp.status == 403:
            return (False, f'Status error @ add_playlist_video | Quota exceeded (403): {e}')
        else:
            return (False, f'Status error @ add_playlist_video | Unknown ({e.resp.status}): {e}')

# TODO: rename the playlist if message channel gets renamed 