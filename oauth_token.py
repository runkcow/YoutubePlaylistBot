
from google_auth_oauthlib.flow import InstalledAppFlow
import config as Config

def main():
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": Config.CLIENT_ID,
                "client_secret": Config.CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        Config.OAUTH_SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(Config.TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print("OAuth flow complete! token.json created with refresh token.")

if __name__ == "__main__":
    main()