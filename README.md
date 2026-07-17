# Quizly Backend

Django REST API that converts YouTube videos into AI-generated quizzes.
Users submit a YouTube URL; the backend downloads the audio, transcribes
it with Whisper AI, and generates a 10-question quiz using Gemini Flash AI.

## Tech Stack

- Django + Django REST Framework
- JWT authentication via HTTP-only cookies (djangorestframework-simplejwt)
- yt-dlp for YouTube audio extraction
- Whisper AI (OpenAI, local) for transcription
- Gemini Flash AI for quiz generation
- django-cors-headers for local frontend integration

## Requirements

- Python 3.10+
- **FFmpeg must be installed globally on your system** (required by both
  yt-dlp and Whisper AI for audio processing). Without it, quiz generation
  will fail.
  - Windows: download from https://ffmpeg.org/download.html and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Setup

1. Clone the repository and navigate into it:
```bash
   git clone <repo-url>
   cd quizly-backend
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   source venv/Scripts/activate   # Git Bash on Windows
   # or: venv\Scripts\activate    # CMD/PowerShell on Windows
   # or: source venv/bin/activate # macOS/Linux
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

44. Create a `.env` file in the project root (see `.env.example` for the
   required variables) and fill in your own values:
```bash
   cp .env.example .env
```
   Then edit `.env` and add your actual `SECRET_KEY` and `GEMINI_API_KEY`.
   Get a free Gemini API key at https://aistudio.google.com/apikey

   `GEMINI_MODEL` defaults to `gemini-flash-latest` (Google's auto-updating
   alias for the current stable Flash model). If you get a 404 error saying
   a model is no longer available, check https://ai.google.dev/gemini-api/docs/models
   for currently available models and override `GEMINI_MODEL` in your `.env`.
   
5. Apply migrations:
```bash
   python manage.py migrate
```

6. Create an admin user:
```bash
   python manage.py createsuperuser
```

7. Run the development server:
```bash
   python manage.py runserver
```

## CORS Configuration

If you're running the frontend locally with a tool like Live Server, make
sure its origin (e.g., `http://127.0.0.1:5500`) is listed in
`CORS_ALLOWED_ORIGINS` in `core/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
CORS_ALLOW_CREDENTIALS = True
```

Adjust the port to match whatever your local frontend server actually uses.

## API Endpoints

See the endpoint documentation for full details on request/response formats.

- `POST /api/register/` — register a new user
- `POST /api/login/` — log in, sets JWT cookies
- `POST /api/logout/` — log out, blacklists refresh token
- `POST /api/token/refresh/` — refresh the access token
- `POST /api/quizzes/` — create a quiz from a YouTube URL
- `GET /api/quizzes/` — list the authenticated user's quizzes
- `GET /api/quizzes/{id}/` — retrieve a specific quiz
- `PATCH /api/quizzes/{id}/` — partially update a quiz
- `DELETE /api/quizzes/{id}/` — delete a quiz

## Admin Panel

Available at `/admin/`. Allows editing of Quizzes and their individual
Questions (inline).