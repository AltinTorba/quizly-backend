"""Helper functions for downloading, transcribing, and generating quizzes."""
import json
import os
import uuid

import whisper
import yt_dlp
from google import genai
from yt_dlp.utils import DownloadError

from .models import Quiz, Question


QUIZ_PROMPT_TEMPLATE = """Based on the following video transcript, generate a quiz.
Return ONLY valid JSON, no markdown, no explanation, in this exact format:
{{
  "title": "short quiz title",
  "description": "one sentence description",
  "questions": [
    {{
      "question_title": "question text",
      "question_options": ["option A", "option B", "option C", "option D"],
      "answer": "the correct option, must match one of question_options exactly"
    }}
  ]
}}
Generate exactly 10 questions, each with exactly 4 options.

Transcript:
{transcript}
"""


class InvalidVideoURLError(Exception):
    """Raised when the given URL is not a valid, downloadable YouTube video."""


def _build_ydl_options(output_template: str) -> dict:
    """Builds the yt-dlp options dict for audio-only extraction."""
    return {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }


def download_audio(youtube_url: str) -> str:
    """Downloads audio from a YouTube URL and returns the path to the mp3 file."""
    filename = str(uuid.uuid4())
    output_template = f"media/{filename}.%(ext)s"
    ydl_opts = _build_ydl_options(output_template)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except DownloadError as exc:
        raise InvalidVideoURLError(f"Could not download video: {youtube_url}") from exc

    return f"media/{filename}.mp3"


def transcribe_audio(audio_path: str) -> str:
    """Transcribes an audio file to text using Whisper AI (base model)."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


def cleanup_audio_file(audio_path: str) -> None:
    """Deletes a temporary audio file if it exists."""
    if os.path.exists(audio_path):
        os.remove(audio_path)


def build_quiz_prompt(transcript: str) -> str:
    """Builds the prompt sent to Gemini to generate a quiz from a transcript."""
    return QUIZ_PROMPT_TEMPLATE.format(transcript=transcript)


def _call_gemini(prompt: str) -> str:
    """Sends a prompt to Gemini Flash and returns the raw text response."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


def _strip_markdown_fences(text: str) -> str:
    """Removes markdown code fences that Gemini sometimes wraps JSON in."""
    return text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()


def generate_quiz_with_gemini(transcript: str) -> dict:
    """Sends the transcript to Gemini Flash and returns the parsed quiz data."""
    prompt = build_quiz_prompt(transcript)
    raw_text = _call_gemini(prompt)
    clean_text = _strip_markdown_fences(raw_text)
    return json.loads(clean_text)


def create_quiz_from_url(owner, youtube_url: str) -> Quiz:
    """Runs the full pipeline: download, transcribe, generate, and save."""
    audio_path = download_audio(youtube_url)
    transcript = transcribe_audio(audio_path)
    cleanup_audio_file(audio_path)
    quiz_data = generate_quiz_with_gemini(transcript)
    return save_quiz(owner, youtube_url, quiz_data)


def save_quiz(owner, youtube_url: str, quiz_data: dict) -> Quiz:
    """Saves generated quiz data as Quiz and Question model instances."""
    quiz = Quiz.objects.create(
        owner=owner,
        title=quiz_data["title"],
        description=quiz_data["description"],
        video_url=youtube_url,
    )
    _save_questions(quiz, quiz_data["questions"])
    return quiz


def _save_questions(quiz: Quiz, questions_data: list) -> None:
    """Creates Question instances linked to the given quiz."""
    for q in questions_data:
        Question.objects.create(
            quiz=quiz,
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"],
        )
