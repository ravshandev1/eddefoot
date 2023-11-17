from rest_framework.permissions import BasePermission


class IsStudentUser(BasePermission):
    """
    Allows access only to parent users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_authenticated and (request.user.role == 0)))


class IsParentUser(BasePermission):
    """
    Allows access only to parent users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_authenticated and (request.user.role == 1)))


class IsCoachUser(BasePermission):
    """
    Allows access only to parent users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_authenticated and (request.user.role == 2)))


class IsPsychologicalUser(BasePermission):
    """
    Allows access only to parent users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_authenticated and (request.user.role == 3)))
