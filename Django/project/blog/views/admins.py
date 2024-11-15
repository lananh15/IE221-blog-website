from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone

from ..models import Admin, User, Post, Like, Comment
from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews
from django.views import View

import hashlib
import os

class AdminViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.admin_id = request.session.get('admin_id', None)

        response = super().dispatch(request, *args, **kwargs)
        self.initialize_handlers()

        return response
    
    def initialize_handlers(self):
        """Khởi tạo comment_handler và like_handler nếu admin_id hợp lệ."""
        if self.admin_id:
            self.comment_handler = CommentViews(admin_id=self.admin_id)
            self.like_handler = LikeViews(admin_id=self.admin_id)
        else:
            self.comment_handler = None
            self.like_handler = None
    
    def get_admin_context(self):
        """Phần chung để lấy thông tin admin"""
        admin_name = None
        if self.admin_id:
            admin_name = self.admin_name
        else:
            return None
        return admin_name
    

class AdminLoginView(AdminViews):
    def get(self, request):
        if request.session.get('admin_id'):
            return redirect('dashboard')  # Nếu đã đăng nhập, chuyển hướng đến dashboard
        return render(request, 'admin/admin_login.html')

    def post(self, request):
        name = request.POST.get('name')
        password = request.POST.get('pass')

        try:
            admin = Admin.objects.get(name=name)
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            if hashed_password == admin.password:
                request.session['admin_id'] = admin.id
                return redirect('dashboard')
            else:
                message = 'Incorrect username or password!'
        except Admin.DoesNotExist:
            message = 'Incorrect username or password!'

        return render(request, 'admin/admin_login.html', {'message': message})

class AdminDashboardView(AdminViews, View):
    def get(self, request):
        admin_name = self.get_admin_context()
        if admin_name is None:
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

        return render(request, 'admin/dashboard.html', context)

class AdminLogoutView(AdminViews):
    def get(self, request):
        logout(request)
        return redirect('admin_login')

class AdminUpdateProfileView(AdminViews):
    def get(self, request, admin_name):
        return render(request, 'admin/update_profile.html', {'admin_name': admin_name, 'admin_id': self.admin_id})

    def post(self, request, admin_name):
        message = []
        admin_id = self.admin_id if admin_name else None
        if 'submit' in request.POST:
            name = request.POST.get('name').strip()
            if name:
                if Admin.objects.filter(name=name).exists():
                    message.append('username already taken!')
                else:
                    Admin.objects.filter(id=admin_id).update(name=name)

            old_pass = request.POST.get('old_pass', '').strip()
            new_pass = request.POST.get('new_pass', '').strip()
            confirm_pass = request.POST.get('confirm_pass', '').strip()

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

        return render(request, 'admin/update_profile.html', context)

class AdminViewPostView(AdminViews):    
    def get(self, request):
        if self.admin_id is None:
            return redirect('admin_login')
        
        select_posts = Post.objects.filter(admin_id=self.admin_id)

        self.initialize_handlers()

        post_data = []
        for post in select_posts:
            total_post_comments = self.comment_handler.get_post_total_comments(post)
            total_post_likes = self.like_handler.get_post_total_likes(post)
            post_data.append({
                'post': post,
                'total_post_comments': total_post_comments,
                'total_post_likes': total_post_likes,
            })

        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': post_data,
        }
        return render(request, 'admin/view_post.html', context)

    def post(self, request):
        message = ''
        if 'delete' in request.POST:
            p_id = request.POST.get('post_id', '').strip()
            post = Post.objects.get(id=p_id)

            if post.image != '':
                image_path = post.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)

            post.delete()
            Comment.objects.filter(post_id=p_id).delete()
            message = 'Post deleted successfully!'

        return redirect('admin_view_post')

class AdminGetUsersView(AdminViews):
    def get(self, request):
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        users = User.objects.all()
        user_data = []

        self.initialize_handlers()

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
            'admin_id': self.admin_id,
            'users': user_data,
        }
        return render(request, 'admin/users_accounts.html', context)

class AdminGetAdminsView(AdminViews):
    def get(self, request):
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        if 'delete' in request.POST:
            delete_posts = Post.objects.filter(admin_id=self.admin_id)
            for post in delete_posts:
                image_path = post.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)
                post.delete()

            Post.objects.filter(admin_id=self.admin_id).delete()
            Like.objects.filter(admin_id=self.admin_id).delete()
            Comment.objects.filter(admin_id=self.admin_id).delete()
            Admin.objects.get(id=self.admin_id).delete()

            return redirect('admin_logout')

        admins = Admin.objects.all()
        admin_data = []
        for admin in admins:
            total_admin_posts = Post.objects.filter(admin_id=admin.id).count()
            admin_data.append({
                'admin': admin,
                'total_admin_posts': total_admin_posts,
            })

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'admins': admin_data,
        }
        return render(request, 'admin/admin_accounts.html', context)

class AdminGetCommentsView(AdminViews):
    def get(self, request):
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        message = ''
        self.initialize_handlers()
        comments = Comment.objects.filter(admin_id=self.admin_id)
        comment_data = []
        for comment in comments:
            post = Post.objects.get(id=comment.post_id.id)
            comment_data.append({
                'comment': comment,
                'post': post,
            })

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'comments': comment_data,
            'message': message,
        }
        return render(request, 'admin/comments.html', context)

    def post(self, request):
        message = ''
        if 'delete' in request.POST:
            comment_id = request.POST.get('comment_id', '').strip()
            Comment.objects.get(id=comment_id).delete()
            message = 'Comment deleted!'

        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'message': message,
        }

        return render(request, 'admin/comments.html', context)
