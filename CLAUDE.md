# billsflow



## Stack

- **Python 3.13** + Flask + Gunicorn
- **Docker** — no venvs, ever. All Python work runs in Docker.
- **Bootstrap 5** + Bootstrap Icons via CDN

## Running locally

```bash
docker compose up --build
```

## Branch structure

- `dev` — active development; all feature branches target here
- `main` — production; triggers deploy on push

## Deployment

Handled by `.github/workflows/deploy.yml` on push to `main`.
