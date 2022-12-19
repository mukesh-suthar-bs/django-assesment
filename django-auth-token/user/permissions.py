from rest_framework import permissions
from rest_framework.permissions import IsAdminUser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to allow only the autheticated user to 
    permform action on it's user object
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user
