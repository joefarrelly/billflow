# Billflow

Personal subscription and bill tracker. Tracks monthly, quarterly, and annual subscriptions with a calendar view, list view, and yearly spend overview.

Live at [billflow.fazz.uk](https://billflow.fazz.uk).

## Stack

- **Python 3.13** + Flask 3.1.1 + Gunicorn
- **PostgreSQL 17** via Flask-SQLAlchemy 3.1.1 + psycopg2-binary — `billflow` database, `billflow` user (Docker-managed)
- **Flask-Login 0.6.3** + **Authlib 1.3.2** — Google SSO required; demo user for try-without-signup
- **Alembic 1.14.1** — database migrations (`alembic upgrade head` runs on container start)
- **Docker** — no venvs, ever. All Python work runs in Docker.
- Custom CSS frontend (no framework) — DM Sans / Playfair Display / DM Mono fonts

## Project structure

```
app.py              Flask app + REST API + auth routes
models.py           SQLAlchemy User and Subscription models
templates/
  index.html        Full standalone template (all CSS/JS inline, no base inheritance)
  login.html        Standalone login page (Google SSO + demo)
static/
  icons/            Favicon/logo cache (gitignored)
requirements.txt
Dockerfile
docker-compose.yml
.env                Local secrets — never commit (gitignored)
```

## Running locally

Create a `.env` file (see Environment below), then:

```bash
docker compose up --build
```

App runs at http://localhost:5003.

## Environment

`.env` is loaded by docker-compose and must define:

```
SECRET_KEY=any-random-string
GOOGLE_CLIENT_ID=      # from Google Cloud Console (demo mode works without it)
GOOGLE_CLIENT_SECRET=  # from Google Cloud Console (demo mode works without it)
```

`AUTHLIB_INSECURE_TRANSPORT=1` and `OAUTH_REDIRECT_URI=http://localhost:5003/auth/callback` are set automatically in docker-compose for local HTTP development.

### OAuth session workaround

Flask does not emit a `Set-Cookie` header on the 302 redirect response from `/auth/google` in this local Docker setup, so Authlib's state/nonce can't be carried to `/auth/callback` via a cookie. The workaround: `auth_google` copies Authlib's session entries into a module-level `_oauth_states` dict; `auth_callback` restores them into the current request's session before calling `authorize_access_token`. Authlib's full state + nonce verification still runs normally. This is not needed in production (nginx handles it correctly).

## Auth model

Login is required. Unauthenticated requests to `/` redirect to `/login`.

- **Google SSO** — via `/auth/google`. Creates a user row on first sign-in. Full read/write access.
- **Demo** — via `/auth/demo`. Logs in as `demo@billflow.app`, seeded at startup with 5 sample subscriptions. Write routes return `403` for this account.

`/login` redirects to `/` if already authenticated. `/logout` redirects to `/login`.

## API

All subscription routes require authentication (Google SSO). Returns `401` if not authenticated.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/me` | Returns `{email}` if authenticated, 401 otherwise |
| GET | `/api/subscriptions` | List user's subscriptions |
| POST | `/api/subscriptions` | Create subscription (403 for demo) |
| PUT | `/api/subscriptions/<id>` | Update subscription (403 for demo) |
| DELETE | `/api/subscriptions/<id>` | Delete subscription (403 for demo) |

### Subscription shape (JSON)

```json
{
  "id": 1,
  "name": "Netflix",
  "amount": 15.99,
  "freq": "monthly",
  "day": 3,
  "startMonth": 0,
  "category": "entertainment",
  "color": "#2E5FA3",
  "icon": null
}
```

`freq`: `monthly` | `quarterly` | `annual`  
`startMonth`: 0–11 (January–December) — used as first billing month for quarterly/annual  
`icon`: `null` or a Google favicon URL (`https://www.google.com/s2/favicons?domain=...&sz=64`)

## Data model

`User` columns: `id`, `email`, `created_at`  
`Subscription` columns: `id`, `user_id` (FK), `name`, `amount`, `frequency`, `day`, `start_month`, `category`, `color`, `icon`

## Frontend behaviour

- Calendar view shows bills due per day, with month total banner
- List view is searchable/filterable by category; shows days-until for monthly subs
- Yearly view shows bar chart + monthly breakdown table
- Modal auto-fetches logo via Google favicon API with 400ms debounce — falls back to colour initials. × button dismisses the auto-fetched logo for the session.
- All native `<select>` elements are replaced by a custom JS dropdown (`CustomSelect` class) for consistent cross-browser styling. Sidebar selects get a dark variant automatically.
- Storage abstraction (`storage.load/create/update/remove`) always calls the API. 403 responses surface as inline errors in the relevant modal rather than browser dialogs.
- Settings modal (gear icon in sidebar / mobile header) controls theme, currency, and categories.

## User preferences (localStorage)

| Key | Default | Values |
|-----|---------|--------|
| `bf_currency` | `£` | `£` `$` `€` `¥` `₹` `A$` `C$` `Fr` |
| `bf_theme` | `sand` | `sand` `slate` `midnight` `forest` `rose` |
| `bf_categories` | see below | JSON array of `{id, label, color}` objects |

## Categories

Categories are user-configurable, stored in `bf_categories`. Default set: Entertainment (`#2D5C9E`), Utilities (`#B07E18`), Other (`#8C8278`). Each category has an `id` (CSS-safe slug), `label`, and `color` (hex). Pill CSS (`.pill.cat-{id}`) is injected dynamically by `injectCatStyles()` — background is the color at 15% opacity (`color + '26'`), text is the color. Category selects in the subscription modal and list filter are populated by `populateCatSelects()`. Both are called on init and whenever categories are modified.

Custom category IDs are generated as `c{timestamp}` to ensure CSS safety.

## Themes

Themes swap CSS custom properties on `:root` via `data-theme` attribute on `<html>`. All colour tokens (`--bg`, `--surface`, `--ink`, `--accent`, etc.) are defined per theme in `index.html`. The sidebar always uses a dark background via `--sidebar-bg` (overrides `--ink` for midnight where `--ink` is light).

| Theme | Character |
|-------|-----------|
| `sand` | Warm parchment + terracotta (default) |
| `slate` | Cool blue-grey |
| `midnight` | Dark mode, purple accent |
| `forest` | Deep greens |
| `rose` | Soft pink/mauve |

## Branch structure

- `dev` — active development; all feature branches target here
- `main` — production; triggers deploy on push

## Deployment

Handled by `.github/workflows/deploy.yml` on push to `main`.
