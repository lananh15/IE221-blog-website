from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews

class PostsViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.session.get('user_id', None)
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)

        return response
    
    def initialize_handlers(self):
        """Khởi tạo comment_handler và like_handler"""
        self.comment_handler = CommentViews(user_id=self.user_id)
        self.like_handler = LikeViews(user_id=self.user_id)

class PostAllCategory(PostsViews):
    def get(self, request):
        """Hiển thị tất cả category"""
        context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        return render(request, 'all_category.html', context)

class PostOfCategory(PostsViews):
    def get(self, request, **kwargs):
        """Hiển thị tất cả bài viết thuộc category""" 
        category_name = kwargs.get('category_name')
        posts = Post.objects.filter(category=category_name, status='Đang hoạt động')
        post_data = []
        if posts.exists():
            post_data = list(map(lambda post: {
                'post': post,
                'total_post_comments': self.comment_handler.get_post_total_comments(post),
                'total_post_likes': self.like_handler.get_post_total_likes(post),
                'is_liked_by_user': self.like_handler.user_liked_post(post_id=post.id),
            }, posts))

        context = {
            'posts': post_data,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        return render(request, 'category.html', context)

class PostLoadAllPost(PostsViews):    
    def get(self, request):
        """Hiển thị tất cả các bài viết"""
        posts = Post.objects.filter(status='Đang hoạt động')

        post_data = list(map(lambda post: {
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked_by_user': self.like_handler.user_liked_post(post.id),
            'post': post,
        }, posts))

        context = {
            'posts': post_data,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        
        return render(request, 'posts.html', context)

class PostViewPost(PostsViews):
    def get(self, request, **kwargs):
        """Hiển thị bài viết có id = post_id"""
        post_id = kwargs.get('post_id')
        post = Post.objects.get(id=post_id, status='Đang hoạt động')

        context = {
            'post': post,
            'all_comments': self.comment_handler.get_all_comments(post_id),
            'user_name': self.user_name,
            'user_id': self.user_id,
            'user_comments': self.comment_handler.get_user_comments_of_post(post_id),
            'total_post_comments': self.comment_handler.get_post_total_comments(post),
            'total_post_likes': self.like_handler.get_post_total_likes(post),
            'user_liked': self.like_handler.user_liked_post(post.id),
        }
        return render(request, 'view_post.html', context)

    
    def post(self, request, **kwargs):
        """User thêm, xóa, sửa comment"""
        post_id = kwargs.get('post_id')
        message = ''
        post = Post.objects.get(id=post_id, status='Đang hoạt động')
        edit_comment = None
        if request.method == 'POST' and self.user_id:
            if 'add_comment' in request.POST:
                comment = request.POST.get('comment')
                self.comment_handler.add_comment(post=post, comment_text=comment, user=self.user)
                
            elif 'edit_comment' in request.POST:
                edit_comment_id = request.POST.get('edit_comment_id')
                comment_edit_box = request.POST.get('comment_edit_box')
                self.comment_handler.edit_comment(comment_id=edit_comment_id, comment_text=comment_edit_box)
                return redirect('view_post', post_id=post_id)

            elif 'delete_comment' in request.POST:
                delete_comment_id = request.POST.get('comment_id')
                if self.comment_handler.delete_comment(comment_id=delete_comment_id, user_id=self.user_id):
                    message = "Comment deleted successfully!"

            elif 'open_edit_box' in request.POST:
                comment_id = request.POST.get('comment_id')
                comment_id = str(comment_id).strip()
                edit_comment = Comment.objects.filter(id=comment_id).first()

        context = {
            'post': post,
            'all_comments': self.comment_handler.get_all_comments(post_id),
            'user_name': self.user_name,
            'user_id': self.user_id,
            'user_comments': self.comment_handler.get_user_comments_of_post(post_id),
            'comment_id': comment_id if 'comment_id' in locals() else None,
            'edit_comment': edit_comment,
            'total_post_comments': self.comment_handler.get_post_total_comments(post),
            'total_post_likes': self.like_handler.get_post_total_likes(post),
            'user_liked': self.like_handler.user_liked_post(post.id),
            'message': message
        }
        return render(request, 'view_post.html', context)