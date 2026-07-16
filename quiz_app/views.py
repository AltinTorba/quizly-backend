"""Views for quiz CRUD operations."""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .functions import create_quiz_from_url, InvalidVideoURLError
from .models import Quiz
from .permissions import IsOwner
from .serializers import QuizSerializer, QuizCreateSerializer


class QuizListCreateView(APIView):
    """Lists the user's quizzes (GET) or creates a new one from a URL (POST)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.filter(owner=request.user)
        return Response(QuizSerializer(quizzes, many=True).data)

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = _try_create_quiz(request.user, serializer.validated_data["url"])
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, partially updates, or deletes a single quiz."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Quiz.objects.all()


def _try_create_quiz(user, url):
    """Creates a quiz from a URL; converts an invalid-URL error into a 400."""
    try:
        return create_quiz_from_url(user, url)
    except InvalidVideoURLError as exc:
        raise ValidationError("Invalid URL or unable to process this video.") from exc
