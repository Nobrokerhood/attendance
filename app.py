import os
import io
import json
import base64
import pandas as pd

from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
    JSONResponse
)

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from google.auth.transport.requests import Request as GRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.readonly"
]

APP_URL = os.environ.get(
    "APP_URL",
    "http://localhost:8000"
).rstrip("/")

IST_OFFSET = timedelta(hours=5, minutes=30)

TOKENS_DIR = "tokens"
os.makedirs(TOKENS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

app = FastAPI(title="Meet Attendance Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_credentials_config():

    env_val = os.environ.get("GOOGLE_CREDENTIALS_B64")

    if env_val:
        return json.loads(
            base64.b64decode(env_val).decode()
        )

    if os.path.exists("credentials.json"):
        with open("credentials.json") as f:
            return json.load(f)

    raise RuntimeError(
        "No credentials found"
    )


def token_path(user):
    return os.path.join(
        TOKENS_DIR,
        f"token_{user}.json"
    )


def load_creds(user):

    path = token_path(user)

    if not os.path.exists(path):
        return None

    creds = Credentials.from_authorized_user_file(
        path,
        SCOPES
    )

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(GRequest())

            with open(path, "w") as f:
                f.write(creds.to_json())

        except Exception:
            return None

    return creds


def to_ist(utc_str):

    if not utc_str:
        return "—"

    dt = datetime.fromisoformat(
        utc_str.replace("Z", "+00:00")
    )

    return (
        dt + IST_OFFSET
    ).strftime("%d %b %Y %I:%M %p")


def duration_mins(join_str, leave_str):

    if not join_str or not leave_str:
        return "Ongoing"

    j = datetime.fromisoformat(
        join_str.replace("Z", "+00:00")
    )

    l = datetime.fromisoformat(
        leave_str.replace("Z", "+00:00")
    )

    return round(
        (l - j).total_seconds() / 60,
        1
    )


def build_meet_service(creds):

    return build(
        "meet",
        "v2",
        credentials=creds,
        static_discovery=False
    )


def get_meeting_code(service, space_val):

    space_name = (
        space_val
        if isinstance(space_val, str)
        else space_val.get("name", "")
    )

    try:

        space_obj = service.spaces().get(
            name=space_name
        ).execute()

        return (
            space_obj.get(
                "meetingCode",
                space_name.split("/")[-1]
            ),
            space_obj.get("meetingUri", "")
        )

    except Exception:

        return (
            space_name.split("/")[-1],
            ""
        )

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    user: str = "",
    logged_in: int = 0,
    error: str = ""
):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "logged_in": logged_in,
            "error": error,
            "is_authenticated": bool(
                user and load_creds(user)
            )
        }
    )


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@app.get("/auth/login")
def login(user: str):

    if not user.strip():
        return RedirectResponse(
            "/?error=Please+enter+your+name"
        )

    config = get_credentials_config()

    redirect_uri = f"{APP_URL}/auth/callback"

    flow = Flow.from_client_config(
        config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        state=user.strip()
    )

    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def callback(
    code: str,
    state: str
):

    user = state

    config = get_credentials_config()

    redirect_uri = f"{APP_URL}/auth/callback"

    flow = Flow.from_client_config(
        config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
        state=state
    )

    flow.fetch_token(code=code)

    creds = flow.credentials

    with open(token_path(user), "w") as f:
        f.write(creds.to_json())

    return RedirectResponse(
        f"/?user={user}&logged_in=1"
    )


@app.get("/auth/logout")
def logout(user: str):

    path = token_path(user)

    if os.path.exists(path):
        os.remove(path)

    return RedirectResponse("/")


# ─────────────────────────────────────────────
# MEETINGS API
# ─────────────────────────────────────────────

@app.get("/api/meetings")
def api_meetings(user: str):

    creds = load_creds(user)

    if not creds:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    service = build_meet_service(creds)

    records = []
    page_token = None

    while len(records) < 30:

        resp = service.conferenceRecords().list(
            pageSize=25,
            pageToken=page_token
        ).execute()

        records.extend(
            resp.get("conferenceRecords", [])
        )

        page_token = resp.get("nextPageToken")

        if not page_token:
            break

    result = []

    for r in records[:30]:

        code, uri = get_meeting_code(
            service,
            r.get("space", "")
        )

        result.append({
            "name": r["name"],
            "meetingCode": code,
            "meetingUri": uri,
            "startDisplay": to_ist(
                r.get("startTime", "")
            ),
            "endDisplay":
                to_ist(r.get("endTime", ""))
                if r.get("endTime")
                else "Ongoing"
        })

    return JSONResponse(result)


# ─────────────────────────────────────────────
# EXPORT API
# ─────────────────────────────────────────────

@app.post("/api/export")
async def api_export(request: Request):

    body = await request.json()

    user = body.get("user", "")
    record_names = body.get("records", [])

    creds = load_creds(user)

    if not creds:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    if not record_names:
        raise HTTPException(
            status_code=400,
            detail="No meetings selected"
        )

    service = build_meet_service(creds)

    all_rows = []

    for record_name in record_names:

        try:
            record = service.conferenceRecords().get(
                name=record_name
            ).execute()

        except HttpError:
            continue

        code, uri = get_meeting_code(
            service,
            record.get("space", "")
        )

        participants = []
        pt = None

        while True:

            resp = service.conferenceRecords() \
                .participants() \
                .list(
                    parent=record_name,
                    pageToken=pt
                ).execute()

            participants.extend(
                resp.get("participants", [])
            )

            pt = resp.get("nextPageToken")

            if not pt:
                break

        for p in participants:

            signed_in = p.get(
                "signedinUser",
                {}
            )

            anon = p.get(
                "anonymousUser",
                {}
            )

            email = signed_in.get(
                "email",
                "—"
            )

            name = (
                signed_in.get("displayName")
                or anon.get(
                    "displayName",
                    "Anonymous"
                )
            )

            sessions = []
            st = None

            while True:

                resp = service.conferenceRecords() \
                    .participants() \
                    .participantSessions() \
                    .list(
                        parent=p["name"],
                        pageToken=st
                    ).execute()

                sessions.extend(
                    resp.get(
                        "participantSessions",
                        []
                    )
                )

                st = resp.get("nextPageToken")

                if not st:
                    break

            for s in sessions:

                join_t = s.get("startTime", "")
                leave_t = s.get("endTime", "")

                all_rows.append({
                    "Meeting Code": code,
                    "Meeting Link": uri,
                    "Participant Name": name,
                    "Email": email,
                    "Joined": to_ist(join_t),
                    "Left": to_ist(leave_t),
                    "Duration":
                        duration_mins(
                            join_t,
                            leave_t
                        )
                })

    if not all_rows:

        raise HTTPException(
            status_code=404,
            detail="No attendance found"
        )

    df = pd.DataFrame(all_rows)

    buf = io.BytesIO()

    with pd.ExcelWriter(
        buf,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Attendance"
        )

    buf.seek(0)

    filename = (
        f"attendance_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    return StreamingResponse(
        buf,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                f"attachment; filename={filename}"
        }
    )
