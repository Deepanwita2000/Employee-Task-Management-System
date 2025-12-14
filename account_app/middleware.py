# # your_app/middleware.py
# import datetime
# from django.http import HttpResponseForbidden

# class CheckUserMiddleware:
#     """
#     Custom middleware that:
#     - Logs username, request path, and timestamp
#     - Denies access if user is not staff or authenticated manager
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Log the request info
#         user = getattr(request, 'user', None)
#         username = user.username if user and user.is_authenticated else 'Anonymous'
#         path = request.path
#         timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         print(f"[{timestamp}] User: {username} | Path: {path}")

#         # Access control
#         if not user or not user.is_authenticated:
#             return HttpResponseForbidden("Access denied: User not authenticated.")

#         # Check if user is staff or manager
#         if not user.is_staff and not user.groups.filter(name='manager').exists():
#             return HttpResponseForbidden("Access denied: Staff or manager only.")

#         # Allow request to proceed
#         response = self.get_response(request)
#         return response
  