from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings

def role_required(*allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # If not logged in → redirect to login page
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            # If logged in but role not allowed → 403 Forbidden
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("You don't have permission to access this resource.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
