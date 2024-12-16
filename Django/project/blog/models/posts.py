from django.db import models
from .admin import Admin

class Post(models.Model):
    # Định nghĩa danh sách các lựa chọn cho category
    CATEGORY_CHOICES = [
        ('c++', 'C++'),
        ('python', 'Python'),
        ('c#', 'C#'),
    ]

    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)  # Foreign key relationship
    name = models.CharField(max_length=100) # Tên của tác giả
    title = models.CharField(max_length=100)  # Tiêu đề bài viết
    content = models.TextField()  # Nội dung bài viết
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='python')  # Sử dụng choices cho category
    image = models.ImageField(upload_to='uploaded_img/', null=True, blank=True)  # Lưu ảnh vào thư mục 'uploaded_img'
    date = models.DateTimeField(auto_now_add=True)  # Thời gian tạo tự động
    status = models.CharField(max_length=50)  # Trạng thái bài viết (ví dụ: 'active' hoặc 'inactive')

    class Meta:
        db_table = 'posts'  # Tên bảng trong cơ sở dữ liệu
        managed = False  # Không để Django tự quản lý bảng này nếu bảng đã có sẵn
