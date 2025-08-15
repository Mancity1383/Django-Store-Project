from rest_framework import permissions

class CustomePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET','POST','DELETE','HEAD','OPTIONS'):
            return request.user.is_staff
        return False