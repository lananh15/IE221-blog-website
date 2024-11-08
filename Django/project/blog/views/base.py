from django.contrib.auth.models import User

class BaseView:
    def __init__(self, request):
        self.request = request
        self.user_id = request.user.id if request.user.is_authenticated else None
        self.user = User.objects.filter(id=self.user_id).first() if self.user_id else None
        self.user_name = self.user.name if self.user else None
        self.user_email = self.user.email if self.user else None

        self.context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
        }