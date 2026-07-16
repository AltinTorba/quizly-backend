"""Helper functions for downloading, transcribing, and generating quizzes."""
import json
import os
import uuid

import yt_dlp
import whisper
from google import genai


def build_quiz_prompt(transcript: str) -> str:
    """Builds the prompt sent to Gemini to generate a quiz from a transcript."""
    return f"""Based on the following video transcript, generate a quiz.
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


def generate_quiz_with_gemini(transcript: str) -> dict:
    """Sends the transcript to Gemini Flash and returns the parsed quiz data."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    prompt = build_quiz_prompt(transcript)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw_text)