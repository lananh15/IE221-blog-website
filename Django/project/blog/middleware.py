# middleware.py
class UserIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_id = request.session.get('user_id', None)
        
        response = self.get_response(request)
        return response
    
class AdminIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.admin_id = request.session.get('admin_id', None)
        
        response = self.get_response(request)
        return response