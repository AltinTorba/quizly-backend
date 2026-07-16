"""Serializers for Quiz and Question models."""
from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializes a single quiz question."""

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer",
                  "created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """Serializes a quiz together with its nested questions."""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "video_url",
                  "created_at", "updated_at", "questions"]


class QuizCreateSerializer(serializers.Serializer):
    """Validates the incoming YouTube URL used to create a quiz."""
    url = serializers.URLField()
    