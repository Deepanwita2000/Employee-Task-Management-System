from rest_framework.permissions import BasePermission



class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'manager'


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsEmployeeOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['manager', 'employee']