from rest_framework import permissions

class IsApprovedVendor(permissions.BasePermission):
    def has_permission(self, request, view, ):
        return(
            request.user.is_authenticated and 
            request.user.role == 'vendor' and
            request.user.is_approved
        )