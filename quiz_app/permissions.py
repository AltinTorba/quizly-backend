"""Custom permissions for the quiz_app."""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allows access only to the owner of the quiz object."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    