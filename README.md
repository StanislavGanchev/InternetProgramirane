# Quiz Conquest

Django 5.2 + Django REST Framework backend and React + Vite frontend.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata questions/question_bank.json
python manage.py createsuperuser   # for Django Admin
python manage.py runserver
```

Backend: http://127.0.0.1:8000/ — Admin: http://127.0.0.1:8000/admin/

### Tests

```bash
cd backend
python manage.py test                      # all apps
python manage.py test accounts questions games
```

### Loading the question bank

```bash
python backend/manage.py loaddata questions/question_bank.json
```

Expected after loading: 6 categories, 12 choice questions (48 answer options), 12 numeric questions.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173/. The Vite dev server proxies `/api` and `/admin`
to Django on port 8000, so start the backend first.

## API (M01)

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/auth/csrf/` | Public |
| POST | `/api/auth/register/` | Public |
| POST | `/api/auth/login/` | Public |
| POST | `/api/auth/logout/` | Authenticated |
| GET / PATCH | `/api/auth/me/` | Authenticated |

Errors always use the format `{"errors": {"field": ["message"]}}`.

## Milestones

| Tag | Content |
|---|---|
| `m0-setup` | Project structure, Django + DRF, React + Vite |
| `m1-auth` | Custom user, profile, session auth API, tests, UI |
| `m2-question-bank` | Categories, choice/numeric questions, admin, fixture, tests |
| `m3-games-and-rounds` | Game, GamePlayer, Round, RoundAnswer, constraints, admin, tests |
