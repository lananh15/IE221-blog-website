from django.utils import timezone
from ..models import Comment

class CommentViews:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id', None)
        self.admin_id = kwargs.get('admin_id', None)

    def get_current_comment(self, comment_id):
        """Lấy comment với id=comment_id"""
        return Comment.objects.get(id=comment_id)
    
    def get_user_comments(self):
        """Lấy tất cả thông tin liên quan đến các bình luận của người dùng đã bình luận"""
        return Comment.objects.filter(user_id=self.user_id)
    
    def get_current_comments(self, comment_id):
        """Lấy bình luận hiện tại của người dùng"""
        return Comment.objects.filter(id=comment_id, user_id=self.user_id).first()

    def get_user_comments_of_post(self, post_id):
        """Lấy tất cả các thông tin liên quan đến bình luận của người dùng trong một bài viết"""
        return Comment.objects.filter(post_id=post_id, user_id=self.user_id)

    def get_all_comments(self, post_id):
        """Lấy tất cả các bình luận của một bài viết"""
        return Comment.objects.filter(post_id=post_id)
    
    def get_post_total_comments(self, post):
        """Lấy số lượt bình luận của một bài viết"""
        total_comments = Comment.objects.filter(post_id=post.id).count()
        return total_comments

    def get_admin_comments(self, **kwargs):
        """Lấy tất cả thông tin liên quan đến các bình luận mà admin nhận được"""
        admin_id = kwargs.get('admin_id')
        return Comment.objects.filter(admin_id=admin_id)
    
    def add_comment(self, **kwargs):
        """Thêm một bình luận mới"""
        post = kwargs.get('post')
        comment_text = kwargs.get('comment_text')
        user = kwargs.get('user')
        comment = Comment.objects.create(
            post_id=post,
            admin_id=post.admin,
            user_id=user,
            user_name=user.name,
            comment=comment_text,
            date=timezone.now(),
        )
        return comment
    
    def edit_comment(self, **kwargs):
        """Chỉnh sửa một bình luận"""
        comment_id = kwargs.get('comment_id')
        comment_text = kwargs.get('comment_text')
        comment_to_edit = Comment.objects.filter(id=comment_id, user_id=self.user_id).first()
        if comment_to_edit:
            comment_to_edit.comment = comment_text
            comment_to_edit.save()
            return comment_to_edit
        return None
    
    def delete_comment(self, **kwargs):
        """Xóa một bình luận"""
        comment_id = kwargs.get('comment_id')
        user_id = kwargs.get('user_id', None)
        admin_id = kwargs.get('admin_id', None)
        comment = (
            Comment.objects.filter(id=comment_id, user_id=user_id).first()
            if user_id
            else Comment.objects.filter(id=comment_id).first())
        
        if comment:
            comment.delete()
            return True
        return False
    
    def comment_exists(self, comment_text, comment_id):
        """Kiểm tra xem bình luận vừa chỉnh sửa có cùng nội dung đã tồn tại trước khi chỉnh sửa hay không"""
        return Comment.objects.filter(comment=comment_text, id=comment_id).exists()
    
    def update_comment(self, comment_id, new_text):
        """Cập nhật comment nếu comment thuộc về người dùng hiện tại"""
        return Comment.objects.filter(id=comment_id, user_id=self.user_id).update(comment=new_text)