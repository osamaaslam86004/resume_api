from rest_framework.permissions import BasePermission


class HasCustomerProfilePermission(BasePermission):
    """
    Custom permission to check if the user has permission for customer profile actions.
    """

    def has_permission(self, request, view):
        # Check if the user has the required permissions
        return request.user.has_perms(view.permission_required)
