from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone

from .posts import PostsViews
from .user import UserViews
from .posts import PostsViews
from .admins import AdminsViews

def user_header(request):
    return UserViews(request).user_header()

def load_home(request):
    return UserViews(request).load_home()

def like_post(request, post_id):
    return UserViews(request).like_post(post_id)


def search(request):
    user_id = request.user_id
    posts = []

    if 'search_box' in request.POST or 'search_btn' in request.POST:
        search_box = request.POST.get('search_box', '')
        posts = Post.objects.filter(
            Q(title__icontains=search_box) | Q(category__icontains=search_box),
            status='active'
        )

    context = {
        'posts': posts,
        'user_id': user_id,
    }
    
    return render(request, 'search.html', context)

def load_posts(request):
    return PostsViews(request).load_posts()

def load_authors(request):
    return AdminsViews(request).load_authors()

def login(request):
    return UserViews(request).login()

def admin_login(request):
    return AdminsViews(request).admin_login()

def admin_logout(request):
    return AdminsViews(request).admin_logout()

def dashboard(request):
    return AdminsViews(request).dashboard()

def admin_update_profile(request, admin_name):
    return AdminsViews(request).admin_update_profile(admin_name)

def admin_view_post(request):
    return AdminsViews(request).admin_view_post()

def get_users_accounts(request):
    return AdminsViews(request).get_users_accounts()

def get_admin_accounts(request):
    return AdminsViews(request).get_admin_accounts()

def get_comments(request):
    return AdminsViews(request).get_comments()


def register(request):
    return UserViews(request).register()


def load_contact(request):
    return UserViews(request).load_contact()

def load_about(request):
    return UserViews(request).load_about()

def load_author_posts(request, author):
    return AdminsViews(request).load_author_posts(author)

def user_logout(request):
    return UserViews(request).user_logout()

def update_profile(request):
    return UserViews(request).update_profile()

def view_post(request, post_id):
    return PostsViews(request).view_post(post_id)


def user_likes(request):
    return UserViews(request).user_likes()

def user_comments(request):
    return UserViews(request).user_comments()
