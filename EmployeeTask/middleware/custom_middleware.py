# your_app/middleware.py
import datetime
class CheckUserMiddleware:
    def __init__(self, get_response):
        print("CheckUserMiddleware initialized")
        print("response",get_response)
        self.get_response = get_response

    def __call__(self, request):
        # Log the request info
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'Anonymous'
        path = request.path
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # print user's status
        print(f"[{timestamp}] User: {username} | Path: {path}")
      

        # Check if user is staff or manager
        if not user.is_staff and not user.groups.filter(name='manager').exists():
            print("Access denied: Staff or manager only.")

        # Allow request to proceed
        response = self.get_response(request)
        return response
  