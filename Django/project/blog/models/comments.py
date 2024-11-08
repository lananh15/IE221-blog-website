from django.db import models
from .users import User
from .posts import Post
from .admin import Admin

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id')  # Khóa ngoại đến Post
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')  # Khóa ngoại đến Admin
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')  # Khóa ngoại đến User
    user_name = models.CharField(max_length=100)
    comment = models.TextField()
    date = models.DateTimeField()

    class Meta:
        db_table = 'comments'
        managed = False
