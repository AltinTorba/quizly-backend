"""URL routes for the quiz_app."""
from django.urls import path
from .views import QuizListCreateView, QuizDetailView

urlpatterns = [
    path("quizzes/", QuizListCreateView.as_view(), name="quiz-list-create"),
    path("quizzes/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
]
