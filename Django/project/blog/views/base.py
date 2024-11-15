from ..models import Admin, User
from django.views import View

class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.user_id = request.session.get('user_id', None)
        self.user = User.objects.filter(id=self.user_id).first() if self.user_id else None
        self.user_name = self.user.name if self.user else None
        self.user_email = self.user.email if self.user else None

        self.admin_id = request.session.get('admin_id', None)
        self.admin = Admin.objects.filter(id=self.admin_id).first() if self.admin_id else None
        self.admin_name = self.admin.name if self.admin else None

        self.context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'admin_id': self.admin_id,
            'admin_name': self.admin_name,
        }
        return super().dispatch(request, *args, **kwargs)