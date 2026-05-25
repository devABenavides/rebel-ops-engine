import logging
import os
from datetime import datetime, timedelta, timezone

from integrations.config import get

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    Request = Credentials = InstalledAppFlow = build = HttpError = None


logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"]

CALENDAR_CREDENTIALS_PATH = "credentials/calendar_oauth.json"
CALENDAR_TOKEN_PATH = "credentials/calendar_token.json"


def _get_service():
    import os as _os
    if _os.environ.get("PYTEST_CURRENT_TEST") or _os.environ.get("REBEL_SKIP_OAUTH"):
        return None
    if Request is None:
        logger.warning("Google API packages not installed — Calendar client unavailable")
        return None
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "..", CALENDAR_TOKEN_PATH)
    creds_path = os.path.join(os.path.dirname(__file__), "..", CALENDAR_CREDENTIALS_PATH)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                logger.warning("No Calendar OAuth credentials file at %s — Calendar client unavailable", creds_path)
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0, timeout_seconds=60)
            except Exception:
                logger.warning("Calendar OAuth browser flow failed. Run:  python scripts/setup_oauth.py calendar")
                return None
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    try:
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.error("Failed to build Calendar service: %s", e)
        return None


def check_availability(date_str: str = None) -> list[dict]:
    service = _get_service()
    if service is None:
        logger.info("[CALENDAR MOCK] check_availability(%s)", date_str)
        return [{"start": "09:00", "end": "10:00"}, {"start": "10:00", "end": "11:00"}, {"start": "14:00", "end": "15:00"}, {"start": "15:00", "end": "16:00"}]

    if date_str:
        day = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        day = datetime.now()

    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    calendar_id = get("GOOGLE_CALENDAR_ID", "primary")

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])
        slots = []
        for e in events:
            start_time = e["start"].get("datetime", e["start"].get("date"))
            end_time = e["end"].get("datetime", e["end"].get("date"))
            slots.append({
                "summary": e.get("summary", ""),
                "start": start_time,
                "end": end_time,
                "id": e.get("id"),
            })
        return slots
    except Exception as e:
        logger.error("[CALENDAR] Failed to check availability: %s", e)
        return []


def find_available_slots(date_str: str, duration_min: int = 30, max_slots: int = 3, day_start: int = 9, day_end: int = 17) -> list[str]:
    service = _get_service()
    if service is None:
        logger.info("[CALENDAR MOCK] find_available_slots(%s)", date_str)
        return [f"{h:02d}:00" for h in range(day_start, day_start + max_slots)]

    try:
        day = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return []

    cal_start = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    cal_end = cal_start + timedelta(days=1)
    calendar_id = get("GOOGLE_CALENDAR_ID", "primary")

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=cal_start.isoformat(),
            timeMax=cal_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
    except Exception as e:
        logger.error("[CALENDAR] Failed to list events: %s", e)
        return []

    busy_minutes = set()
    for e in events_result.get("items", []):
        start_str = e["start"].get("dateTime")
        end_str = e["end"].get("dateTime")
        if not start_str or not end_str:
            continue
        try:
            s = datetime.fromisoformat(start_str)
            e_end = datetime.fromisoformat(end_str)
        except ValueError:
            continue
        # Convert to UTC minutes since midnight for easy comparison
        s_utc = s.astimezone(timezone.utc)
        e_utc = e_end.astimezone(timezone.utc)
        s_min = s_utc.hour * 60 + s_utc.minute
        e_min = e_utc.hour * 60 + e_utc.minute
        # Handle events that span across midnight (use full day if needed)
        if e_min <= s_min:
            e_min = 24 * 60
        for m in range(s_min, e_min):
            busy_minutes.add(m)

    # Bogota is UTC-5, so 9 Bogota = 14 UTC, 17 Bogota = 22 UTC
    work_start_utc = day_start + 5
    work_end_utc = day_end + 5

    slots = []
    cursor = work_start_utc * 60
    limit = work_end_utc * 60
    while cursor <= limit - duration_min and len(slots) < max_slots:
        free = True
        for m in range(cursor, cursor + duration_min):
            if m in busy_minutes:
                free = False
                break
        if free:
            # Convert UTC minutes to Bogota time for display
            bogota_min = cursor - 5 * 60
            h = bogota_min // 60
            m = bogota_min % 60
            slots.append(f"{h:02d}:{m:02d}")
            cursor += duration_min
        else:
            cursor += 1

    return slots


def create_event(summary: str, date: str, time: str, attendees: list[str] = None) -> dict:
    service = _get_service()
    if service is None:
        logger.info("[CALENDAR MOCK] create_event(%s, %s, %s)", summary, date, time)
        return {"status": "mocked", "summary": summary, "date": date, "time": time}

    start_dt = f"{date}T{time}:00"
    start_parsed = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_parsed = start_parsed + timedelta(minutes=30)
    end_dt = end_parsed.strftime("%Y-%m-%dT%H:%M:%S")

    event = {
        "summary": summary,
        "start": {"dateTime": start_dt, "timeZone": get("TIMEZONE", "UTC")},
        "end": {"dateTime": end_dt, "timeZone": get("TIMEZONE", "UTC")},
    }
    if attendees:
        event["attendees"] = [{"email": a} for a in attendees]

    calendar_id = get("GOOGLE_CALENDAR_ID", "primary")
    try:
        result = service.events().insert(calendarId=calendar_id, body=event).execute()
        logger.info("[CALENDAR] Created event: %s — id=%s", summary, result.get("id"))
        return {"status": "created", "summary": summary, "date": date, "time": time, "id": result.get("id")}
    except Exception as e:
        logger.error("[CALENDAR] Failed to create event: %s", e)
        return {"status": "error", "error": str(e)}
