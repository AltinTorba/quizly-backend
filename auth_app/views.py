"""Views for authentication: register, login, logout, and token refresh."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import RegisterSerializer


class RegisterView(APIView):
    """Registers a new user."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    """Logs in a user and sets JWT tokens as HTTP-only cookies."""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response({
            "detail": "Login successfully!",
            "user": _serialize_user(serializer.user),
        })
        _set_auth_cookies(
            response,
            serializer.validated_data["access"],
            serializer.validated_data["refresh"],
        )
        return response


class LogoutView(APIView):
    """Logs out a user by blacklisting the refresh token and clearing cookies."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _blacklist_refresh_token(request.COOKIES.get("refresh_token"))
        response = Response({
            "detail": "Log-Out successfully! All Tokens will be deleted. "
            "Refresh token is now invalid."
        })
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refreshes the access token using the refresh token stored in cookies."""

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"detail": "Refresh token missing."}, status=401)

        validated_data = _validate_refresh_token(self, refresh_token)
        if validated_data is None:
            return Response({"detail": "Refresh token invalid or expired."}, status=401)

        response = Response({"detail": "Token refreshed"})
        _set_access_cookie(response, validated_data["access"])
        return response


def _serialize_user(user):
    """Returns a minimal user representation for login responses."""
    return {"id": user.id, "username": user.username, "email": user.email}


def _set_auth_cookies(response, access_token, refresh_token):
    """Sets access and refresh tokens as HTTP-only cookies on the response."""
    _set_access_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)


def _set_access_cookie(response, access_token):
    """Sets the access token as an HTTP-only cookie on the response."""
    response.set_cookie(
        key="access_token", value=str(access_token),
        httponly=True, secure=False, samesite="Lax",
    )


def _set_refresh_cookie(response, refresh_token):
    """Sets the refresh token as an HTTP-only cookie on the response."""
    response.set_cookie(
        key="refresh_token", value=str(refresh_token),
        httponly=True, secure=False, samesite="Lax",
    )


def _blacklist_refresh_token(refresh_token):
    """Blacklists the given refresh token, ignoring already-invalid tokens."""
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass


def _validate_refresh_token(view, refresh_token):
    """Validates a refresh token and returns validated data, or None if invalid."""
    serializer = view.get_serializer(data={"refresh": refresh_token})
    try:
        serializer.is_valid(raise_exception=True)
    except (InvalidToken, TokenError):
        return None
    return serializer.validated_data
