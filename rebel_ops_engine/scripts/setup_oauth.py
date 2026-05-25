"""One-time OAuth setup for Google integrations.

Run this from the PythonAnywhere Bash console (or any terminal)
to generate token files that the web app will use automatically.

Usage:
    python scripts/setup_oauth.py gmail
    python scripts/setup_oauth.py calendar
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SCOPES_MAP = {
    "gmail": ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"],
    "calendar": [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ],
}

CREDS_MAP = {
    "gmail": ("credentials/gmail_oauth.json", "credentials/gmail_token.json"),
    "calendar": ("credentials/calendar_oauth.json", "credentials/calendar_token.json"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SCOPES_MAP:
        print(f"Usage: python scripts/setup_oauth.py <{'|'.join(SCOPES_MAP)}>")
        sys.exit(1)

    service = sys.argv[1]
    creds_rel, token_rel = CREDS_MAP[service]
    base = os.path.dirname(os.path.dirname(__file__))
    creds_path = os.path.join(base, creds_rel)
    token_path = os.path.join(base, token_rel)

    if not os.path.exists(creds_path):
        print(f"Error: {creds_path} not found.")
        print(f"Download OAuth JSON from Google Cloud Console to {creds_rel}")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: google-auth-oauthlib not installed.")
        print("Run:  pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES_MAP[service])
    creds = flow.run_console()

    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w") as f:
        f.write(creds.to_json())

    print(f"\nOAuth setup complete for {service}.")
    print(f"Token saved to {token_rel}")
    print("The web app will now use this token automatically.")


if __name__ == "__main__":
    main()
