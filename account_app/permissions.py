from rest_framework.permissions import BasePermission


# Permission to allow only professors to manage courses
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'manager'

# Permission to allow only students to enroll
class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'

# User can be either a professor or a student
# This permission allows both professors and students to access the view
class IsEmployeeOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['manager', 'employee']