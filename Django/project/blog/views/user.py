from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Count

from .base import BaseView

import hashlib

class UserViews(BaseView):
    def __init__(self, request):
        super().__init__(request)

    def user_logout(self):
        """Đăng xuất"""
        logout(self.request)
        return redirect('home')

    def login(self):
        """Đăng nhập"""
        message = ''
        if self.request.method == 'POST':
            email = self.request.POST.get('email')
            password = self.request.POST.get('pass')

            try:
                user = User.objects.get(email=email)
                hashed_password = hashlib.sha1(password.encode()).hexdigest()
                if hashed_password == user.password:
                    self.request.session['user_id'] = user.id
                    return redirect('home')
                else:
                    message = 'Incorrect username or password!'
            except User.DoesNotExist:
                message = 'Incorrect username or password!'

        return render(self.request, 'login.html', {'message': message if 'message' in locals() else ''})
    
    def register(self):
        """Đăng ký"""
        message = ''
        if self.request.method == 'POST':
            name, email, password, confirm_password = (
                self.request.POST.get('name'),
                self.request.POST.get('email'),
                self.request.POST.get('pass'),
                self.request.POST.get('cpass'),
            )
            
            if User.objects.filter(email=email).exists():
                message = 'Email already exists!'
            else:
                if password != confirm_password:
                    message = 'Confirm password not matched!'
                else:
                    hashed_password = hashlib.sha1(password.encode()).hexdigest()
                    user = User(name=name, email=email, password=hashed_password)
                    user.save()
                    
                    self.request.user_id = user.id
                    return redirect('home')

        return render(self.request, 'register.html', {'message': message if 'message' in locals() else ''})

    def user_header(self):
        """Load header đối với user"""
        print(self.user_id)       
        return render(self.request, 'user_header.html', self.context)

    def load_contact(self):
        """Load trang Contact"""
        return render(self.request, 'contact.html', self.context)

    def load_about(self):
        """Load trang About"""
        return render(self.request, 'about.html', self.context)
    
    def update_profile(self):
        """Chỉnh sửa thông tin cá nhân"""
        message = ''
        if self.request.method == 'POST' and 'submit' in self.request.POST:
            name = self.request.POST.get('name', '').strip()
            email = self.request.POST.get('email', '').strip()

            if name:
                self.user.name = name
                self.user.save()

            if email:
                if User.objects.filter(email=email).exclude(id=self.user_id).exists():
                    message = 'Email already taken!'
                else:
                    self.user.email = email
                    self.user.save()

            old_pass = self.request.POST.get('old_pass', '')
            new_pass = self.request.POST.get('new_pass', '')
            confirm_pass = self.request.POST.get('confirm_pass', '')

            if old_pass:
                if hashlib.sha1(old_pass.encode()).hexdigest() != self.user.password:
                    message = 'Old password not matched!'
                elif new_pass != confirm_pass:
                    message = 'Confirm password not matched!'
                else:
                    if new_pass:
                        self.user.password = hashlib.sha1(new_pass.encode()).hexdigest()  # Mã hóa và cập nhật mật khẩu mới
                        self.user.save()
                        message = 'Password updated successfully!'
                    else:
                        message = 'Please enter a new password!'
        context = {
            'user_name': self.user.name,
            'user_email': self.user.email,
            'message': message,
            'user_id': self.user_id,
        }
        return render(self.request, 'update.html', context)
    
    def user_likes(self):
        """Hiển thị tất cả các bài viết mà user đã Like"""
        post_data = []

        if self.user_id:
            likes = Like.objects.filter(user_id=self.user_id)

            if likes.exists():
                post_ids = likes.values_list('post_id', flat=True)
                posts = Post.objects.filter(id__in=post_ids, status='active').annotate(
                    total_likes=Count('like'),
                    total_comments=Count('comment')
                )

                for post in posts:
                    post_data.append({
                        'post': post,
                        'total_post_likes': post.total_likes,
                        'total_post_comments': post.total_comments,
                    })
        
        context = {
            'posts': post_data,
            'user_id': self.user_id,
        }

        return render(self.request, 'user_likes.html', context)

    def load_home(self):
        """Load trang Home"""
        context = {
            'user_name': None,
            'user_comments': 0,
            'user_likes': 0,
            'posts': [],
            'authors': [],
            'user_id': self.user_id,
        }

        if self.user_id:
            context['user_name'] = self.user.name
            context['user_comments'] = Comment.objects.filter(user_id=self.user_id).count()
            context['user_likes'] = Like.objects.filter(user_id=self.user_id).count()

        posts = Post.objects.filter(status='active')[:4]
        post_data = []

        for post in posts:
            total_comments = Comment.objects.filter(post_id=post.id).count()
            total_likes = Like.objects.filter(post_id=post.id).count()
            is_liked_by_user = Like.objects.filter(user_id=self.user_id, post_id=post.id).exists()
            author = Admin.objects.filter(id=post.admin_id).first()
            post_data.append({
                'post': post,
                'total_comments': total_comments,
                'total_likes': total_likes,
                'is_liked_by_user': is_liked_by_user,
                'author': author.name if author else None,
                'author_id': author.id if author else None,
            })
            
        authors = Admin.objects.all()
        
        context['posts'] = post_data
        context['authors'] = authors
        
        return render(self.request, 'home.html', context)

    def user_comments(self):
        """Hiển thị tất cả comment mà user đã comment"""
        comment_id = None
        edit_comment = None
        message = ''
        if self.request.method == "POST":
            if 'edit_comment' in self.request.POST:
                edit_comment_id = self.request.POST.get('edit_comment_id')
                comment_edit_box = self.request.POST.get('comment_edit_box')

                if Comment.objects.filter(comment=comment_edit_box, id=edit_comment_id).exists():
                    message = "Comment already added!"
                else:
                    Comment.objects.filter(id=edit_comment_id, user_id=self.user_id).update(comment=comment_edit_box)
                    message = "Your comment edited successfully!"

            elif 'delete_comment' in self.request.POST:
                delete_comment_id = self.request.POST.get('comment_id')
                Comment.objects.filter(id=delete_comment_id, user_id=self.user_id).delete()
                message = "Comment deleted successfully!"

            elif 'open_edit_box' in self.request.POST:
                comment_id = self.request.POST.get('comment_id')
                edit_comment = Comment.objects.filter(id=comment_id, user_id=self.user_id).first()

        comments = Comment.objects.filter(user_id=self.user_id)

        context = {
            'comments': comments,
            'edit_comment': edit_comment,
            'comment_id': comment_id,
            'message': message,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

        return render(self.request, 'user_comments.html', context)
    
    def like_post(self, post_id):
        """Like hoặc Unlike bài post"""
        like = Like.objects.filter(user_id=self.user_id, post_id=post_id).first()
        post = Post.objects.get(id=post_id)
        admin = Admin.objects.get(id=post.admin_id)

        if like:
            like.delete()
        else:
            Like.objects.create(user_id=self.user, admin_id=admin, post_id=post)

        return redirect(self.request.META.get('HTTP_REFERER'))


