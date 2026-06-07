# Billflow

A personal subscription and bill tracker. See what you're spending, when each payment hits, and how costs stack up across the year.

## Features

- **Calendar view** — bills plotted on their due dates, month total at a glance
- **List view** — searchable and filterable by category; highlights bills due within 5 days
- **Yearly overview** — bar chart and month-by-month breakdown table
- **Logo auto-detection** — fetches service logos as you type; falls back to colour initials
- Monthly, quarterly, and annual billing frequencies
- **Five themes** — Sand, Slate, Midnight (dark), Forest, Rose
- **No account required** — works immediately, data stored locally in the browser
- **Google sign-in** — optional, syncs data to the server so it's available across devices

## Running locally

Requires Docker.

```bash
git clone <repo>
cd billflow
cp .env.example .env   # fill in SECRET_KEY; add Google OAuth creds to enable sign-in
docker compose up --build
```

Open http://localhost:5003.

### Google sign-in setup (optional)

1. Create an OAuth 2.0 Client ID at [console.cloud.google.com](https://console.cloud.google.com) → APIs & Services → Credentials
2. Add `http://localhost:5003/auth/callback` as an authorised redirect URI
3. Add your client ID and secret to `.env`:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
SECRET_KEY=any-random-string
```

## Tech

- Python 3.13 / Flask / SQLite
- Flask-Login + Authlib for Google OAuth
- Custom CSS — no frontend framework
