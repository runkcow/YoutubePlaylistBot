
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import config as Config

creds : Credentials = Credentials.from_authorized_user_file(Config.TOKEN_FILE, Config.OAUTH_SCOPES)

def get_creds() -> Credentials:
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(Config.TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise Exception("OAuth credentials invalid. Re-run auth flow.")
    return creds
