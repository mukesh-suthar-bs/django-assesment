from rest_framework import permissions


class ArticleOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-Level permission to allow only owner to edit or delete of an object
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # only when item is not in draft
        if request.method in permissions.SAFE_METHODS and obj.draft != 1:
            return True

        return obj.owner == request.user
