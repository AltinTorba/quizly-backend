# Quizly Backend

Django REST API that converts YouTube videos into AI-generated quizzes
(FFmpeg -> Whisper AI -> Gemini Flash AI). Frontend is provided separately;
this repo covers backend only, communicating via REST API.

## Structure
- `core/` - main settings, root urls
- `auth_app/` - registration, login, logout, token refresh (JWT in HTTP-only cookies)
- `quiz_app/` - Quiz/Question models, quiz CRUD endpoints, YouTube->Whisper->Gemini pipeline

## Commands
- `python manage.py runserver` - start local dev server
- `python manage.py makemigrations <app>` - generate migrations
- `python manage.py migrate` - apply migrations
- `python manage.py createsuperuser` - create admin user

## Critical conventions (mentor's Definition of Done)
- Authentication is ALWAYS via JWT in HTTP-only cookies, NEVER in the
  Authorization header or localStorage
- On login: generate access_token + refresh_token, send both as HTTP-only cookies
- On logout: blacklist the refresh_token, delete both cookies
- views.py contains ONLY views that return a Response
- functions.py or utils.py holds all helper functions (create if missing)
- Every function is max 14 lines and does exactly ONE task
- All function names use snake_case
- Variable names are descriptive (no single-letter names except loop counters)
- No unused variables or functions
- No commented-out code left in the codebase
- Every function/class has a docstring, written in English
- All Python code is PEP-8 compliant (https://pep8.org/)
- Every ForeignKey uses an explicit related_name
- The User model is always referenced via settings.AUTH_USER_MODEL, never imported directly
- Users can only access/edit/delete their OWN quizzes (403 otherwise)
- Admin Panel must allow editing Quizzes AND individual Questions (inline)

## External tools required
- FFmpeg must be installed globally (required by Whisper AI) - document this in README
- yt-dlp for YouTube -> audio only (https://github.com/yt-dlp/yt-dlp)
- Whisper AI for transcription, used locally (https://github.com/openai/whisper)
- Gemini Flash AI for quiz generation (free tier, needs API key) (https://github.com/googleapis/python-genai)

## Don't
- Never hardcode API keys (Gemini) in code - use .env only
- Never use User.objects.create() for new users - always use create_user()
- Never leave debug prints or commented-out code in commits

## README.md must exist and clearly state
- FFmpeg is required and must be installed globally
- How to set up .env (Gemini API key)
- How to run the project locally