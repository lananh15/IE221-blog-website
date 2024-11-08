from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone

from .base import BaseView

import hashlib

class AdminsViews(BaseView):
    def __init__(self, request):
        super().__init__(request)
        
    def admin_login(self):
        if self.request.method == 'POST':
            name = self.request.POST.get('name')
            password = self.request.POST.get('pass')

            try:
                admin = Admin.objects.get(name=name)
                hashed_password = hashlib.sha1(password.encode()).hexdigest()
                if hashed_password == admin.password:
                    self.request.user_id = admin.id
                    return redirect('home')
                else:
                    message = 'Incorrect username or password!'
            except User.DoesNotExist:
                message = 'Incorrect username or password!'

        return render(self.request, 'admin_login.html', {'message': message if 'message' in locals() else ''})


    def load_authors(self):
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
    
    def load_author_posts(self, author):
        posts = Post.objects.filter(name=author, status='active')

        post_data = []
        for post in posts:
            total_comments = Comment.objects.filter(post_id=post.id).count()
            total_likes = Like.objects.filter(post_id=post.id).count()
            if self.user_id:
                is_liked = Like.objects.filter(user_id=self.user_id, post_id=post.id).exists()
            else:
                is_liked = False

            post_data.append({
                'total_comments': total_comments,
                'total_likes': total_likes,
                'is_liked': is_liked,
                'post': post
            })
        context = {
            'posts': post_data,
            'author': author,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }  

        return render(self.request, 'author_posts.html', context)

