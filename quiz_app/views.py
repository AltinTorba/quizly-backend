"""Views for quiz CRUD operations."""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz
from .serializers import QuizSerializer, QuizCreateSerializer
from .permissions import IsOwner
from .functions import create_quiz_from_url


class QuizListCreateView(APIView):
    """Lists the user's quizzes (GET) or creates a new one from a URL (POST)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.filter(owner=request.user)
        return Response(QuizSerializer(quizzes, many=True).data)

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = create_quiz_from_url(request.user, serializer.validated_data["url"])
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, partially updates, or deletes a single quiz."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Quiz.objects.all()
    