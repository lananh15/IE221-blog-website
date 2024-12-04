from django.urls import path, include
from .views.admins import AdminLoginView, AdminDashboardView, AdminUpdateProfileView, AdminViewPostView, AdminGetUsersView, AdminGetCommentsView, AdminGetAdminsView, AdminLogoutView, AdminAddPostView, AdminRegisterView
from .views.users import UserHeaderView, UserContactView, UserAboutView, UserLogoutView, UserLoginView, UserRegisterView, UserHomeView, UserUpdateProfileView, UserLikesView, UserCommentsView, UserLoadAuthors, UserLoadAuthorPosts, UserLikedPost, UserVerification, UserResendOTP, UserForgetPassword
from .views.posts import PostAllCategory, PostOfCategory, PostLoadAllPost, PostViewPost
from .views.search import SearchPostView

urlpatterns = [
    # User
    # path('search/', views.search, name='search'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('user_header/', UserHeaderView.as_view(), name='user_header'),
    path('', UserHomeView.as_view(), name='home'),
    path('contact/', UserContactView.as_view(), name='contact'),
    path('about/', UserAboutView.as_view(), name='about'),
    path('authors/', UserLoadAuthors.as_view(), name='authors'),
    path('author/<str:author>/', UserLoadAuthorPosts.as_view(), name='author_posts'),
    path('update-profile', UserUpdateProfileView.as_view(), name='update_profile'),
    path('user-likes', UserLikesView.as_view(), name='user_likes'),
    path('user-comments', UserCommentsView.as_view(), name='user_comments'),
    path('like-post/<int:post_id>', UserLikedPost.as_view(), name='like_post'),
    path('verification/', UserVerification.as_view(), name='verification'),
    path('resend-otp/', UserResendOTP.as_view(), name='resend_otp'),
    path('forget-password/', UserForgetPassword.as_view(), name='forget_password'),

    # Post
    path('all-category/', PostAllCategory.as_view(), name='all_category'),
    path('category/<str:category_name>/', PostOfCategory.as_view(), name='category'),
    path('post/<int:post_id>/', PostViewPost.as_view(), name='view_post'),
    path('posts/', PostLoadAllPost.as_view(), name='posts'),

    # Admin
    path('admin-register/', AdminRegisterView.as_view(), name='admin_register'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('update-profile/<str:admin_name>/', AdminUpdateProfileView.as_view(), name='admin_update_profile'),
    path('view-post/', AdminViewPostView.as_view(), name='admin_view_post'),
    path('add-post/', AdminAddPostView.as_view(), name='add_post'),
    path('tinymce/', include('tinymce.urls')),
    path('users-accounts', AdminGetUsersView.as_view(), name='users_accounts'),
    path('admin-accounts', AdminGetAdminsView.as_view(), name='admin_accounts'),
    path('comments', AdminGetCommentsView.as_view(), name='comments'),
    
    # Search 
    path('search/', SearchPostView.as_view(), name='search'),
]