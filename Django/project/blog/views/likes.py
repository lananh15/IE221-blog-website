from django.utils import timezone
from ..models import Like, Comment

class LikeViews:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_post_total_likes(self, post):
        """Lấy số lượt thích của một bài viết"""
        total_likes = Like.objects.filter(post_id=post.id).count()
        return total_likes

    def get_user_likes(self):
        """Lấy tất cả lượt like của người dùng đã like"""
        return Like.objects.filter(user_id=self.user_id)
    
    def user_liked_post(self, post_id):
        """Kiểm tra xem người dùng đã thích bài viết này chưa"""
        return Like.objects.filter(user_id=self.user_id, post_id=post_id).exists()
    
    def like_post(self, user, admin, post):
        return Like.objects.create(user_id=user, admin_id=admin, post_id=post)