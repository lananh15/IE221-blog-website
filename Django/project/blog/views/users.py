from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews

import hashlib
import random
import string

from django.core.mail import send_mail
from django.conf import settings

class UserViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.session.get('user_id', None)
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)
        return response
    
    def initialize_handlers(self):
        """Khởi tạo comment_handler và like_handler"""
        self.comment_handler = CommentViews(user_id=self.user_id)
        self.like_handler = LikeViews(user_id=self.user_id)
    
    @staticmethod
    def generate_otp(length=6):
        """Tạo mã OTP ngẫu nhiên"""
        otp = ''.join(random.choices(string.digits, k=length))
        return otp
    
    @staticmethod
    def send_otp_email(request, email, otp_code):
        """Gửi email chứa mã xác thực với subject và nội dung"""
        subject = '[PyBlog] Verification Code'
        message = f"""<h3 style='display:block;text-align:center;font-size:18px;'> Verify </h3>
                        <p>Your verification code is:
                            <strong style='display:block;text-align:center;font-size:25px;'>{otp_code}</strong>
                        </p>
                        <p>This verification code is only valid for 3 minutes. Please use this code to complete the process.</p>
                        <p>Regards,<br>PyBlog.</p>"""
        send_mail(subject, '', settings.EMAIL_HOST_USER, [email], html_message=message)
        request.session['otp_sent_time'] = timezone.now().isoformat()
    
class UserVerification(UserViews):
    """Gửi mail chứa OTP xác thực"""
    def get(self, request):
        email = request.session.get('email')
        otp = self.generate_otp()
        request.session['otp'] = otp
        self.send_otp_email(request, email, otp)
        return render(request, 'verification.html', self.context)
    
    def post(self, request):
        name, email, password, npass = (
            request.session.get('name'),
            request.session.get('email'),
            request.session.get('password'),
            request.session.get('npass'),
        )

        if request.method == "POST" and request.POST.get('otp') and request.session.get('otp_sent_time'):
            otp_code_input = request.POST.get('otp')
            otp_sent_time = timezone.datetime.fromisoformat(request.session.get('otp_sent_time'))
            if otp_sent_time:
                time_diff = timezone.now() - otp_sent_time
                if time_diff > timedelta(minutes=3):
                    del request.session['otp']
                    del request.session['otp_sent_time']
                    return render(request, 'verification.html', {'message': 'The verification code has expired. Please click "Resend" below.'})
                
                if otp_code_input != request.session.get('otp'):
                    return render(request, 'verification.html', {'message': 'The verification code is invalid.'})
                else:
                    if email and password:
                        User.objects.create(name=name, email=email, password=password)
                        del request.session['name']
                        del request.session['email']
                        del request.session['password']

                    elif email and npass:
                        user = User.objects.filter(email=email).first()
                        if user:
                            user.password = npass
                            user.save()
                            del request.session['email']
                            del request.session['npass']
                        else:
                            return render(request, 'verification.html', {'message': 'User not found.'})
                    return redirect('login')
            
        else:
            return render(request, 'verification.html', {'message': 'Please click "Resend" below.'})

        return render(request, 'verification.html', {'message': 'Session data not found. Please try again.'})

class UserResendOTP(UserViews):
    """Gửi lại mã xác thực cho người dùng"""
    def get(self, request):
        email = request.session.get('email')
        if not email:
            return redirect('register')

        request.session.pop('otp', None)
        request.session.pop('otp_sent_time', None)

        otp = self.generate_otp()
        request.session['otp'] = otp
        self.send_otp_email(request, email, otp)

        return redirect('verification')
    
class UserForgetPassword(UserViews):
    """Người dùng quên mật khẩu, cài lại mật khẩu mới"""
    def get(self, request):
        return render(request, 'forgetpassword.html', self.context)
    
    def post(self, request):
        message = ''
        if request.method == "POST":
            fp_email, npass, cpass = (
                request.POST.get('email', '').strip(),
                request.POST.get('npass', ''),
                request.POST.get('cpass', ''),
            )

            if npass != cpass:
                message = 'Confirm password not matched!'
            
            else:
                hashed_password = make_password(npass)
                request.session['email'] = fp_email
                request.session['npass'] = hashed_password
                return redirect('verification')
        return render(request, 'forgetpassword.html', {'message': message if 'message' in locals() else ''})

class UserHeaderView(UserViews):
    """Load header đối với user"""
    def get(self, request):
        return render(request, 'user_header.html', self.context)

class UserContactView(UserViews):
    """Load trang Contact"""
    def get(self, request):
        return render(request, 'contact.html', self.context)

class UserAboutView(UserViews):
    """Load trang About"""
    def get(self, request):
        return render(request, 'about.html', self.context)

class UserLogoutView(UserViews):
    """Đăng xuất"""
    def get(self, request):
        logout(request)
        return redirect('home')

class UserLoginView(UserViews):
    """Đăng nhập"""
    def get(self, request):
        if request.session.get('user_id'):
            return redirect('home')
        return render(request, 'login.html')
     
    def post(self, request):
        message = ''
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('pass')
    
            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    print(self.user_id)
                    return redirect('home')
                else:
                    message = 'Incorrect username or password!'
            except User.DoesNotExist:
                message = 'Incorrect username or password!'

        return render(request, 'login.html', {'message': message if 'message' in locals() else ''})

class UserRegisterView(UserViews):
    """Đăng ký""" 
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        message = ''
        if request.method == 'POST':
            name, email, password, confirm_password = (
                request.POST.get('name'),
                request.POST.get('email'),
                request.POST.get('pass'),
                request.POST.get('cpass'),
            )
            
            if User.objects.filter(email=email).exists():
                message = 'Email already exists!'
            else:
                if password != confirm_password:
                    message = 'Confirm password not matched!'
                else:
                    hashed_password = make_password(password)
                    request.session['name'] = name
                    request.session['email'] = email
                    request.session['password'] = hashed_password

                    return redirect('verification')

        return render(request, 'register.html', {'message': message if 'message' in locals() else ''})

class UserUpdateProfileView(UserViews):
    """Chỉnh sửa thông tin cá nhân"""
    def get(self, request):
        return render(request, 'update.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email})

    def update_password(self, old_pass, new_pass, confirm_pass):
        if not check_password(old_pass, self.user.password):
            return 'Old password not matched!'
        elif new_pass != confirm_pass:
            return 'Confirm password not matched!'
        elif not new_pass:
            return 'Please enter a new password!'
        else:
            self.user.password = make_password(new_pass)
            self.user.save()
            return 'Password updated successfully!'

    def post(self, request):
        message = ''
        if request.method == 'POST' and 'submit' in request.POST:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()

            self.user.name = name if name else self.user.name
            self.user.save()

            if email and User.objects.filter(email=email).exclude(id=self.user_id).exists():
                    message = 'Email already taken!'
            else:
                self.user.email = email
                self.user.save()

            old_pass = request.POST.get('old_pass', '')
            new_pass = request.POST.get('new_pass', '')
            confirm_pass = request.POST.get('confirm_pass', '')
            
            if old_pass:
                message = self.update_password(old_pass, new_pass, confirm_pass)

        context = {
            'user_name': self.user.name,
            'user_email': self.user.email,
            'message': message,
            'user_id': self.user_id,
        }
        return render(request, 'update.html', context)

class UserLikesView(UserViews):
    """Hiển thị tất cả các bài viết mà user đã Like"""
    def get(self, request):
        post_data = []

        if self.user_id:
            likes = self.like_handler.get_user_likes()
            if likes.exists():
                post_ids = likes.values_list('post_id', flat=True)
                posts = Post.objects.filter(id__in=post_ids, status='active').annotate(
                    total_likes=Count('like'),
                    total_comments=Count('comment')
                )
                list(map(lambda post: post_data.append({
                        'post': post,
                        'total_post_likes': post.total_likes,
                        'total_post_comments': post.total_comments,
                    }), posts))
        
        context = {
            'posts': post_data,
            'user_id': self.user_id,
        }

        return render(request, 'user_likes.html', context)

class UserHomeView(UserViews):
    """Load trang Home"""
    def get(self, request):
        posts = Post.objects.filter(status='active')[:4]

        post_data = list(map(lambda post: {
            'post': post,
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked_by_user': self.like_handler.user_liked_post(post.id),
            'author': (Admin.objects.filter(id=post.admin_id).first() or {}).name,
            'author_id': (Admin.objects.filter(id=post.admin_id).first() or {}).id,
        }, posts))
        print(self.user_id)
        context = {
            'user_name': self.user_name,
            'user_comments': self.comment_handler.get_user_comments().count(),
            'user_likes': self.like_handler.get_user_likes().count(),
            'posts': post_data,
            'authors': Admin.objects.all(),
            'user_id': self.user_id,
        }

        return render(request, 'home.html', context)

class UserCommentsView(UserViews):
    """Hiển thị tất cả comment mà user đã comment"""
    def get(self, request):
        if self.user_id:
            comments = self.comment_handler.get_user_comments()
        
        context = {
            'comments': comments,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

        return render(request, 'user_comments.html', context)

    def post(self, request):
        comment_id = None
        edit_comment = None
        message = ''
        if request.method == "POST":
            if 'edit_comment' in request.POST:
                edit_comment_id = request.POST.get('edit_comment_id')
                comment_edit_box = request.POST.get('comment_edit_box')

                if self.comment_handler.comment_exists(comment_edit_box, edit_comment_id):
                    message = "Comment already added!"
                else:
                    self.comment_handler.update_comment(edit_comment_id, comment_edit_box)
                    message = "Your comment edited successfully!"

            elif 'delete_comment' in request.POST:
                delete_comment_id = request.POST.get('comment_id')
                if self.comment_handler.delete_comment(comment_id=delete_comment_id, user_id=self.user_id):
                    message = "Comment deleted successfully!"

            elif 'open_edit_box' in request.POST:
                comment_id = request.POST.get('comment_id')
                edit_comment = self.comment_handler.get_current_comments(comment_id)

        context = {
            'comments': self.comment_handler.get_user_comments(),
            'edit_comment': edit_comment,
            'comment_id': comment_id,
            'message': message,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

        return render(request, 'user_comments.html', context)

class UserLikedPost(UserViews):
    """Like hoặc Unlike bài post"""
    def post(self, request, **kwargs):
        post_id = kwargs.get('post_id')
        like = Like.objects.filter(user_id=self.user_id, post_id=post_id).first()
        post = Post.objects.get(id=post_id)
        admin = Admin.objects.get(id=post.admin_id)

        if like:
            like.delete()
        else:
            self.like_handler.like_post(self.user, admin, post)

        return redirect(request.META.get('HTTP_REFERER'))

class UserLoadAuthorPosts(UserViews):
    """Hiển thị các bài post của tác giả tương ứng"""
    def get(self, request, **kwargs):
        author = kwargs.get('author')
        posts = Post.objects.filter(name=author, status='active')

        post_data = list(map(lambda post: {
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked': self.like_handler.user_liked_post(post.id),
            'post': post
        }, posts))

        context = {
            'posts': post_data,
            'author': author,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }  

        return render(request, 'author_posts.html', context)
    

class UserLoadAuthors(UserViews):
    """Hiển thị các tác giả (là admin)"""
    def get(self, request):
        authors = Admin.objects.all()

        author_stats = list(map(lambda author: {
            'name': author.name,
            'total_posts': Post.objects.filter(admin_id=author.id, status='active').count(),
            'total_likes': self.like_handler.get_admin_likes(admin_id=author.id).count(),
            'total_comments': self.comment_handler.get_admin_comments(admin_id=author.id).count(),
        }, authors))

        context = {
            'author_stats': author_stats,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        
        return render(request, 'authors.html', context)