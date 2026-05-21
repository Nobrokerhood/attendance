# Google Meet Attendance Tracker

A modern Google Meet Attendance Tracker built using FastAPI and Google Meet API.

This tool allows employees and team members to:

- Login with Google OAuth
- View recent Google Meet sessions
- Export attendance reports to Excel
- Track employee join/leave times
- Track total meeting attendance duration
- Download attendance sheets instantly

---

# Features

- Google OAuth Authentication
- Google Meet API Integration
- Export Attendance to Excel
- Employee Email Tracking
- Join & Leave Time Tracking
- Total Meeting Duration Tracking
- FastAPI Backend
- Modern Responsive UI
- Render Deployment Ready
- Multi-user Support
- Automatic Token Refresh

---

# Attendance Report Details

The exported Excel attendance report includes:

| Field | Description |
|---|---|
| Participant Name | Employee / participant full name |
| Email | Employee Google account email ID |
| Joined | Exact time employee joined the meeting |
| Left | Exact time employee left the meeting |
| Duration | Total time employee stayed in the meeting |
| Meeting Code | Google Meet meeting code |
| Meeting Link | Google Meet URL |

---

# Example Attendance Export

| Participant Name | Email | Joined | Left | Duration |
|---|---|---|---|---|
| Virendra Bodele | virendra@gmail.com | 10:00 AM | 11:15 AM | 75 mins |


---

# What This Tool Tracks

This application automatically tracks:

- Employee email ID
- Meeting join time
- Meeting leave time
- Total attendance duration
- Meeting details
- Google Meet session history

The attendance report is exported as an Excel file for easy HR and team management usage.

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
