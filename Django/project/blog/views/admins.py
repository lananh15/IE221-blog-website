from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone

from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews

import hashlib
import os

class AdminViews(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.comment_handler = CommentViews(self.user_id)
        self.like_handler = LikeViews(self.user_id)

        
    def admin_login(self):
        """Admin đăng nhập"""
        if self.request.method == 'POST':
            name = self.request.POST.get('name')
            password = self.request.POST.get('pass')

            try:
                admin = Admin.objects.get(name=name)
                hashed_password = hashlib.sha1(password.encode()).hexdigest()
                if hashed_password == admin.password:
                    self.request.session['admin_id'] = admin.id
                    return redirect('dashboard')
                else:
                    message = 'Incorrect username or password!'
            except User.DoesNotExist:
                message = 'Incorrect username or password!'

        return render(self.request, 'admin/admin_login.html', {'message': message if 'message' in locals() else ''})    

    def load_authors(self):
        """Hiển thị các tác giả (là admin)"""
        authors = Admin.objects.all()
        author_stats = []
        for author in authors:
            total_posts = Post.objects.filter(admin_id=author.id, status='active').count()

            total_likes = Like.objects.filter(admin_id=author.id).count()
            total_comments = Comment.objects.filter(admin_id=author.id).count()
            
            author_stats.append({
                'name': author.name,
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_comments': total_comments,
            })

        context = {
            'author_stats': author_stats,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        
        return render(self.request, 'authors.html', context)
    

    def admin_logout(self):
        """Admin đăng xuất"""
        logout(self.request)
        return redirect('admin_login')
    
    def dashboard(self):
        """Load trang Dashboard của Admin"""
        admin_name = None
        if self.admin_id:
            admin_name = self.admin_name
        else:
            return redirect('admin_login')
        
        numbers_of_posts = Post.objects.filter(admin_id=self.admin_id).count()
        numbers_of_active_posts = Post.objects.filter(admin_id=self.admin_id, status='active').count()
        numbers_of_deactive_posts = Post.objects.filter(admin_id=self.admin_id, status='deactive').count()
        numbers_of_users = User.objects.all().count()
        numbers_of_admins = Admin.objects.all().count()
        numbers_of_comments = Comment.objects.filter(admin_id=self.admin_id).count()
        numbers_of_likes = Like.objects.filter(admin_id=self.admin_id).count()

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'numbers_of_posts': numbers_of_posts,
            'numbers_of_active_posts': numbers_of_active_posts,
            'numbers_of_deactive_posts': numbers_of_deactive_posts,
            'numbers_of_users': numbers_of_users,
            'numbers_of_admins': numbers_of_admins,
            'numbers_of_comments': numbers_of_comments,
            'numbers_of_likes': numbers_of_likes,
        }

        return render(self.request, 'admin/dashboard.html', context)
    
    def admin_update_profile(self, admin_name):
        """Chỉnh sửa thông tin Admin"""
        message = []
        admin_id = self.admin_id if admin_name else None

        if self.request.method == "POST" and 'submit' in self.request.POST:
            name = self.request.POST.get('name').strip()
            if name:
                select_name = Admin.objects.get(name=name).count()
                if select_name > 0:
                    message.append('username already taken!')
                else:
                    Admin.objects.filter(id=admin_id).update(name=name)
        
            old_pass = self.request.POST.get('old_pass', '').strip()
            new_pass = self.request.POST.get('new_pass', '').strip()
            confirm_pass = self.request.POST.get('confirm_pass', '').strip()

            if old_pass:
                if hashlib.sha1(old_pass.encode()).hexdigest() != self.admin.password:
                    message = 'Old password not matched!'
                elif new_pass != confirm_pass:
                    message = 'Confirm password not matched!'
                else:
                    if new_pass:
                        self.admin.password = hashlib.sha1(new_pass.encode()).hexdigest()
                        self.admin.save()
                        message = 'Password updated successfully!'
                    else:
                        message = 'Please enter a new password!'

        context = {
            'admin_name': admin_name,
            'admin_id': admin_id,
            'message': message,
        }

        return render(self.request, 'admin/update_profile.html', context)
    
    def admin_view_post(self):
        """Xem tất cả bài blog của admin"""
        message = ''
        admin_id = self.admin_id
        admin_name = self.admin_name

        if self.request.method == "POST" and 'delete' in self.request.POST:
            p_id = self.request.POST.get('post_id', '').strip()
            delete_image = Post.objects.get(id=p_id)
            if delete_image.image != '':
                image_path = delete_image.image.path
                print(image_path)
                if os.path.isfile(image_path):
                    os.remove(image_path)

            delete_image.delete()

            Post.objects.get(id=p_id).delete()

            Comment.objects.get(post_id=p_id).delete()
            message = 'Post deleted successfully!';

        select_posts = Post.objects.filter(admin_id=admin_id)
        if select_posts.count() > 0:
            post_data = []

            for post in select_posts:
                total_post_comments = self.comment_handler.get_post_total_comments(post)
                total_post_likes = self.like_handler.get_post_total_likes(post)
                post_data.append({
                    'post': post,
                    'total_post_comments': total_post_comments,
                    'total_post_likes': total_post_likes,
                })
                print(post.content)

            
        context = {
            'admin_name': admin_name,
            'admin_id': admin_id,
            'message': message,
            'posts': post_data,
        }
        return render(self.request, 'admin/view_post.html', context)
    
    def get_users_accounts(self):
        """Lấy thông tin các User Account"""
        admin_id = self.admin_id
        admin_name = self.admin_name

        users = User.objects.all()
        if users.count() > 0:
            user_data = []
            for user in users:
                total_user_comments = Comment.objects.filter(user_id=user.id).count()
                total_user_likes = Like.objects.filter(user_id=user.id).count()
                user_data.append({
                    'user': user,
                    'total_user_comments': total_user_comments,
                    'total_user_likes': total_user_likes,
                })

        context = {
            'admin_name': admin_name,
            'admin_id': admin_id,
            'users': user_data,
        }
        return render(self.request, 'admin/users_accounts.html', context)
    
    def get_admin_accounts(self):
        """Lấy thông tin các Admin Account"""
        admin_id = self.admin_id
        admin_name = self.admin_name

        if self.request.method == "POST" and 'delete' in self.request.POST:
            delete_posts = Post.objects.filter(admin_id=admin_id)
            for post in delete_posts:
                image_path = post.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)
                post.delete()

            Post.objects.filter(admin_id=admin_id).delete()

            Like.objects.filter(admin_id=admin_id).delete()
            Comment.objects.filter(admin_id=admin_id).delete()

            Admin.objects.get(id=admin_id).delete()

            return redirect('admin_logout')

        admins = Admin.objects.all()
        if admins.exists():
            admin_data = []
            for admin in admins:
                total_admin_posts = Post.objects.filter(admin_id=admin.id).count()
                admin_data.append({
                    'admin': admin,
                    'total_admin_posts': total_admin_posts,
                })

        context = {
            'admin_name': admin_name,
            'admin_id': admin_id,
            'admins': admin_data,
        }
        return render(self.request, 'admin/admin_accounts.html', context)


    def get_comments(self):
        """Lấy thông tin các comment"""
        admin_id = self.admin_id
        admin_name = self.admin_name
        message = ''

        if self.request.method == "POST" and 'delete' in self.request.POST:
            comment_id = self.request.POST.get('comment_id', '').strip()
            Comment.objects.get(id=comment_id).delete()
            message = 'Comment delete!'

        comments = Comment.objects.filter(admin_id=admin_id)
        comment_data = []
        if comments.exists():
            for comment in comments:
                post = Post.objects.get(id=comment.post_id.id)
                print(comment.user_name)
                comment_data.append({
                    'comment': comment,
                    'post': post,
                })

        context = {
            'admin_name': admin_name,
            'admin_id': admin_id,
            'comments': comment_data,
            'message': message,
        }
        return render(self.request, 'admin/comments.html', context)
