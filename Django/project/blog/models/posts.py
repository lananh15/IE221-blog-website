from django.db import models
from .admin import Admin

class Post(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)  # Foreign key relationship
    name = models.CharField(max_length=100)  # Corresponds to the 'name' field in your database
    title = models.CharField(max_length=100)  # Corresponds to the 'title' field
    content = models.TextField()  # Use TextField for larger text content
    category = models.CharField(max_length=50)  # Corresponds to the 'category' field
    image = models.ImageField(upload_to='image/', null=True, blank=True)  # Assuming images are stored in 'uploaded_img/'
    date = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    status = models.CharField(max_length=10)  # Corresponds to the 'status' field

    class Meta:
        db_table = 'posts'  # This should match your database table name
        managed = False

