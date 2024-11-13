from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.views import View

from .posts import PostsViews
from .users import UserViews
from .posts import PostsViews
from .admins import AdminViews

# Các xử lý liên quan User
def login(request):
    """Đăng nhập"""
    return UserViews(request).login()

def register(request):
    """Đăng ký"""
    return UserViews(request).register()

def load_contact(request):
    """Load trang Contact"""
    return UserViews(request).load_contact()

def load_about(request):
    """Load trang About"""
    return UserViews(request).load_about()

def user_header(request):
    """Load phần Header đối với User"""
    return UserViews(request).user_header()

def load_home(request):
    """Load trang Home"""
    return UserViews(request).load_home()

def like_post(request, post_id):
    return UserViews(request).like_post(post_id)

def user_likes(request):
    """Hiển thị tất cả bài viết mà người dùng đã thích"""
    return UserViews(request).user_likes()

def user_comments(request):
    """Hiển thị thông tin các comment mà người dùng đã comment"""
    return UserViews(request).user_comments()

def user_logout(request):
    """Đăng xuất"""
    return UserViews(request).user_logout()

def update_profile(request):
    """Cập nhật thông tin cá nhân người dùng"""
    return UserViews(request).update_profile()

def load_author_posts(request, author):
    """Hiển thị tất cả bài viết của author tương ứng"""
    return UserViews(request).load_author_posts(author)



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


# Các xử lý liên quan Posts
def load_posts(request):
    """Hiển thị tất cả các bài viết có trên website"""
    return PostsViews(request).load_posts()

def load_authors(request):
    """Hiển thị tất cả các author trên website"""
    return AdminViews(request).load_authors()

def load_all_category(request):
    """Hiển thị tất cả category"""
    return PostsViews(request).load_all_category()

def load_category(request, category_name):
    """Hiển thị các bài post tương ứng với category được chọn"""
    return PostsViews(request).load_category(category_name)

def view_post(request, post_id):
    """Hiển thị bài viết được chọn"""
    return PostsViews(request).view_post(post_id)


# Các xử lý liên quan Admins
def admin_login(request):
    """Đăng nhập (Admin)"""
    return AdminViews(request).admin_login()

def admin_logout(request):
    """Đăng xuất (Admin)"""
    return AdminViews(request).admin_logout()

def dashboard(request):
    """Hiển thị trang Dashboard"""
    return AdminViews(request).dashboard()

def admin_update_profile(request, admin_name):
    """Cập nhật thông tin Admin"""
    return AdminViews(request).admin_update_profile(admin_name)

def admin_view_post(request):
    """Xem tất cả bài blog của admin"""
    return AdminViews(request).admin_view_post()

def get_users_accounts(request):
    """Lấy thông tin các User Account"""
    return AdminViews(request).get_users_accounts()

def get_admin_accounts(request):
    """Lấy thông tin các Admin Account"""
    return AdminViews(request).get_admin_accounts()

def get_comments(request):
    """Lấy thông tin các comment"""
    return AdminViews(request).get_comments()
