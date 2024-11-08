from django.urls import path
from .views import views

urlpatterns = [
    path('', views.load_home, name='home'),
    path('user_header/', views.user_header, name='user_header'),
    path('search/', views.search, name='search'),
    path('posts/', views.load_posts, name='posts'),
    path('authors/', views.load_authors, name='authors'),

    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.register, name='register'),
    
    path('contact/', views.load_contact, name='contact'),
    path('about/', views.load_about, name='about'),

    path('admin-login/', views.admin_login, name='admin_login'),
    path('author/<str:author>/', views.load_author_posts, name='author_posts'),
    path('update_profile', views.update_profile, name='update_profile'),
    
    path('user_likes', views.user_likes, name='user_likes'),
    path('user_comments', views.user_comments, name='user_comments'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('like-post/<int:post_id>', views.like_post, name='like_post'),
]