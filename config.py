
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

DEV_SERVERS = [ 909589494490087494, 415003906951610378 ]

OAUTH_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

DATA_FILE = "data.json"
TOKEN_FILE = "token.json"

YOUTUBE_PLAYLIST_LIMIT = 5000
YOUTUBE_API_QUOTA = 10000
YOUTUBE_API_QUOTA_PLAYLIST_CREATE_COST = 50
YOUTUBE_API_QUOTA_PLAYLIST_INSERT_COST = 50
