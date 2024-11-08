from django.db import models
from .users import User
from .posts import Post
from .admin import Admin

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')  # Specify exact column name
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')  # Specify exact column name
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id')  # Specify exact column name

    class Meta:
        db_table = 'likes'  # Ensure this matches your existing table name
        managed = False  
