# Google Meet Attendance Tracker

A modern Google Meet Attendance Tracker built using FastAPI and Google Meet API.

This tool allows team members to:

- Login with Google OAuth
- View recent Google Meet sessions
- Export attendance reports to Excel
- Track participant join/leave times
- Download attendance sheets instantly

---

# Features

- Google OAuth Authentication
- Google Meet API Integration
- Export Attendance to Excel
- FastAPI Backend
- Modern Responsive UI
- Render Deployment Ready
- Multi-user Support
- Automatic Token Refresh

---

# Tech Stack

## Backend
- FastAPI
- Uvicorn
- Google Meet API
- Pandas
- OpenPyXL

## Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

## Deployment
- Render

---

# Project Structure

```bash
attendance/
│
├── app.py
├── requirements.txt
├── render.yaml
├── .gitignore
├── credentials.json
│
├── templates/
│   └── index.html
│
└── tokens/
