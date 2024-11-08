from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Đảm bảo email là duy nhất
    password = models.CharField(max_length=50)  # Có thể sử dụng hash cho mật khẩu

    class Meta:
        db_table = 'users'
        managed = False
