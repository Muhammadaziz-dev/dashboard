# Dashboard (Django)

A Django-based dashboard with:
- Custom user model with roles (ADMIN, TEACHER, STUDENT)
- Session-login pages (`/login`, `/logout`), dashboard at `/`
- Persistent lessons, students, and per-lesson records
- Role-gated editing (ADMIN/TEACHER only): add/remove columns, clear all, save
- JWT auth endpoints for APIs (optional): `/api/auth/token/`, `/api/auth/token/refresh/`

## Prerequisites
- Python 3.11+
- PostgreSQL 13+ (or adjust to your local version)
- pip

## Quick Start

1) Clone and enter the project
- `git clone https://github.com/Muhammadaziz-dev/dashboard.git`
- `cd dashboard`

2) Create virtual environment and install dependencies
- `python3 -m venv env`
- `source env/bin/activate`   # Windows: `env\Scripts\activate`
- `pip install -r requirements.txt`

3) Configure database (PostgreSQL)
- Ensure Postgres is running and a user/database exist matching `config/settings.py`:
  - NAME: `dashboard`
  - USER: `postgres`
  - PASSWORD: `root`
  - HOST: `localhost`
  - PORT: `5432`

Example commands (macOS/Homebrew):
- `brew services start postgresql`
- `createdb dashboard`
- `psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'root';"`

If you prefer different credentials, update `config/settings.py` → `DATABASES['default']` accordingly.

4) Apply migrations and create a superuser
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`

5) Run the server
- `python manage.py runserver`

Open `http://127.0.0.1:8000/login` to log in. After login you’ll be redirected to `/` (dashboard).

## Usage
- Login: `/login/` (username/password, no signup UI)
- Dashboard: `/`
  - ADMIN/TEACHER see buttons to: add column, remove column, clear all, save
  - Clear all wipes all per-lesson records AND student names/notes
  - Save persists changes for all users
  - Buttons show small toasts for user feedback
- Logout: click “Chiqish” (submits a POST to `/logout/` and redirects to `/login/`)
- Admin site: `/admin/`

## API (Session-protected dashboard endpoints)
- GET `/dashboard/state/` → returns lessons, students (grouped A2/B1/B2), and records
- POST `/dashboard/save/` → bulk save table changes
- POST `/dashboard/clear/` → clears all records and student names/notes
- POST `/dashboard/lesson/add/` → adds one lesson column
- POST `/dashboard/lesson/remove/` → removes the last column (keeps a minimum of 3)

These endpoints require being logged-in via Django session. CSRF is handled by the page template.

## JWT Auth (optional)
- POST `/api/auth/token/` with `{ "username": "..", "password": ".." }`
- POST `/api/auth/token/refresh/` with `{ "refresh": ".." }`

These are present for API clients but are not used by the dashboard UI (which uses session auth).

## Roles and Permissions
- Only `ADMIN` or `TEACHER` (or superuser) can edit the dashboard.
- Others can view but inputs are disabled.

## Troubleshooting
- Cannot login to admin: ensure your superuser is `is_staff=True` (the code ensures this for superuser/ADMIN role). Recreate via `createsuperuser` if needed.
- 401 from dashboard endpoints: ensure you’re logged in via `/login/` and that CSRF cookie exists. The template embeds `{% csrf_token %}` to set it.
- Database connection errors: verify Postgres is running and credentials in `config/settings.py` match your local setup.
- Want SQLite for quick testing? Replace the `DATABASES` block in `config/settings.py` with:

```
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}
```

Then run migrations again.

## Project Structure (key parts)
- `config/settings.py` — project settings, template dir, auth redirects, database config
- `config/urls.py` — routes admin, HTML pages, and API endpoints
- `accounts/models.py` — custom `User` (roles), `Lesson`, `Student`, `Record`
- `accounts/views.py` — dashboard views + DRF endpoints
- `accounts/pages_urls.py` — login/logout/dashboard + dashboard APIs
- `templates/auth/login.html` — login page
- `templates/dashboard.html` — dashboard UI + JS

## Development Notes
- Keep `.env` secrets out of version control (see `.gitignore`).
- If you change roles or add permissions, also update the `can_edit` calculation in `DashboardView`.
- The first load of `/dashboard/state/` seeds 24 lessons and 30 students per level if empty. You can change seeding logic in `DashboardStateView.get()`.

---

If you want a Docker setup (compose for Postgres + app), let me know and I’ll add it.
