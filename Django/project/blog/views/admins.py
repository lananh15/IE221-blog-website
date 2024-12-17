from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from ..models import Admin, User, Post, Like, Comment
from ..models.posts_forms import PostForm  
from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews
from django.views import View

import os

class AdminViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.admin_id = request.session.get('admin_id', None)
        self.user_id = request.session.get('user_id', None)
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)

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
    
    def get_posts(self, status=None):
        """Lấy tất cả các bài viết của admin theo trạng thái nếu có"""
        if status:  # Nếu có status, lọc theo trạng thái
            select_posts = Post.objects.filter(admin_id=self.admin_id, status=status)
        else:  # Nếu không có status, lấy tất cả bài viết của admin
            select_posts = Post.objects.filter(admin_id=self.admin_id)
        self.initialize_handlers()
        post_data = list(map(lambda post: {
            'post': post,
            'total_post_comments': self.comment_handler.get_post_total_comments(post),
            'total_post_likes': self.like_handler.get_post_total_likes(post),
        }, select_posts))

        return post_data
    
    def delete_post(self, request, **kwargs):
        """Cho phép admin xóa bài viết"""
        message = ''
        status = kwargs.get('status', None)
        if 'delete' in request.POST:
            p_id = request.POST.get('post_id', '').strip()
            post = Post.objects.get(id=p_id)

            if post.image != '':
                image_path = post.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)

            post.delete()
            Comment.objects.filter(post_id=p_id).delete()
            message = 'Bài viết đã được xóa thành công!'
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(status=status),
            'message': message,
        }
        return render(request, 'admin/view_posts.html', context)
    
class AdminLoginView(AdminViews):
    def get(self, request):
        """Hiển thị trang login phía admin"""
        if request.session.get('admin_id'):
            return redirect('dashboard')
        return render(request, 'admin/admin_login.html')

    def post(self, request):
        """Xử lý form đăng nhập vào admin"""
        name = request.POST.get('name')
        password = request.POST.get('pass')

        try:
            admin = Admin.objects.get(name=name)
            if check_password(password, admin.password):
                request.session['admin_id'] = admin.id
                return redirect('dashboard')
            else:
                message = 'Tên đăng nhập hoặc mật khẩu không đúng'
        except Admin.DoesNotExist:
            message = 'Tên đăng nhập hoặc mật khẩu không đúng!'

        return render(request, 'admin/admin_login.html', {'message': message})

class AdminDashboardView(AdminViews, View):
    def get(self, request):
        """Hiển thị trang Dashboard phía admin"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        numbers_of_posts = Post.objects.filter(admin_id=self.admin_id).count()
        numbers_of_active_posts = Post.objects.filter(admin_id=self.admin_id, status='Đang hoạt động').count()
        numbers_of_deactive_posts = Post.objects.filter(admin_id=self.admin_id, status='Ngừng hoạt động').count()
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
        """Xử lý logout cho admin"""
        logout(request)
        return redirect('admin_login')

class AdminUpdateProfileView(AdminViews):
    def get(self, request, **kwargs):
        """Hiển thị trang update profile cho admin"""
        admin_name = kwargs.get('admin_name')
        return render(request, 'admin/update_profile.html', {'admin_name': admin_name, 'admin_id': self.admin_id})

    def update_password(self, old_pass, new_pass, confirm_pass):
        if not check_password(old_pass, self.admin.password):
            return 'Mật khẩu hiện tại không đúng!'
        elif new_pass != confirm_pass:
            return 'Mật khẩu nhập lại không chính xác!'
        elif not new_pass:
            return 'Vui lòng nhập mật khẩu mới!'
        else:
            self.admin.password = make_password(new_pass)
            self.admin.save()
            return 'Mật khẩu được cập nhật thành công!'
        
    def post(self, request, **kwargs):
        """Xử lý form update profile cho admin"""
        message = []

        if request.method == 'POST' and 'submit' in request.POST:
            name = request.POST.get('name').strip()
            if name:
                if Admin.objects.filter(name=name).exists():
                    message.append('Tên đăng nhập này đã được dùng!')
                else:
                    self.admin.name = name
                    self.admin.save()

            old_pass = request.POST.get('old_pass', '').strip()
            new_pass = request.POST.get('new_pass', '').strip()
            confirm_pass = request.POST.get('confirm_pass', '').strip()

            if old_pass:
                message = self.update_password(old_pass, new_pass, confirm_pass)

        context = {
            'admin_name': self.admin.name,
            'admin_id': self.admin_id,
            'message': message,
        }

        return render(request, 'admin/update_profile.html', context)

class AdminViewPostView(AdminViews):
    def get(self, request):
        """Xem tất cả các bài viết đã đăng của admin hiện tại đã login"""
        if self.admin_id is None:
            return redirect('admin_login')
        
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """Cho phép admin xóa bài viết của mình"""
        return self.delete_post(request)

class AdminViewActivePostView(AdminViews):    
    def get(self, request):
        """Xem tất cả các bài viết đang hoạt động có trên website"""
        if self.admin_id is None:
            return redirect('admin_login')
        
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(status='Đang hoạt động'),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """Cho phép admin xóa bài viết đang hoạt động"""
        return self.delete_post(request, status="Đang hoạt động")

class AdminViewDeactivePostView(AdminViews):
    def get(self, request):
        """Xem tất cả các bài viết đang hoạt động"""
        if self.admin_id is None:
            return redirect('admin_login')

        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(status='Ngừng hoạt động'),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """Cho phép admin xóa bài viết ngừng hoạt động"""
        return self.delete_post(request, status="Ngừng hoạt động")

# Hiển thị chi tiết các bài đăng của admin khi bấm vào những bài đăng, lấy id đối chiếuchiếu
#tại view_post.html
class AdminReadPostView(AdminViews):
    def get(self, request, post_id):
        """Xem chi tiết bài viết và các bình luận liên quan"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        try:
            post = Post.objects.get(id=post_id, admin_id=self.admin_id)
        except Post.DoesNotExist:
            return redirect('admin_posts')  # Quay lại danh sách bài viết nếu bài viết không tồn tại

        comments = Comment.objects.filter(post_id=post.id).order_by('-date')

        # Hiện tổng lượt like và comment
        post.total_likes = self.like_handler.get_post_total_likes(post)
        post.total_comments = self.comment_handler.get_post_total_comments(post)

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'post': post,
            'comments': comments,
        }
        return render(request, 'admin/read_post.html', context)
    
    def post(self, request, post_id):
        """Cho phép xóa cmt tại chỗ xem chi tiết bài viết"""
        if 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id', '')
            try:
                comment = Comment.objects.get(id=comment_id, post_id=post_id, admin_id=self.admin_id)
                comment.delete()
            except Comment.DoesNotExist:
                pass 

        return redirect('admin_read_post', post_id=post_id)

    def post(self, request):
        if 'post_id' in request.POST:
            post_id = request.POST.get('post_id')
            try:
                # Tìm và xóa bài viết
                post = Post.objects.get(id=post_id, admin_id=self.admin_id)
                post.delete()
            except Post.DoesNotExist:
                pass  # Nếu bài viết không tồn tại, bỏ qua
            
        return redirect('admin_view_post')  # Quay lại danh sách bài viết sau khi xóa
    

class AdminEditPostView(AdminViews):
    def get(self, request, post_id):
        """Hiển thị trang chỉnh sửa bài viết"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        try:
            post = Post.objects.get(id=post_id, admin_id=self.admin_id)
        except Post.DoesNotExist:
            return redirect('admin_posts')

        form = PostForm(instance=post)
        context = {
            'admin_name': admin_name,
            'post': post,
            'form': form,
        }
        return render(request, 'admin/edit_post.html', context)

    def post(self, request, post_id):
        """Xử lý form chỉnh sửa bài viết"""
        try:
            post = Post.objects.get(id=post_id, admin_id=self.admin_id)
        except Post.DoesNotExist:
            return redirect('admin_posts')

        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # Xử lý trạng thái
            post.status = request.POST.get('status', post.status)
            post.save()
            return redirect('admin_read_post', post_id=post_id)

        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'admin/edit_post.html', context)

class AdminGetUsersView(AdminViews):
    def get(self, request):
        """Hiển thị thông tin tất cả user đang có trên web"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        users = User.objects.all()

        user_data = list(map(lambda user: {
            'user': user,
            'total_user_comments': Comment.objects.filter(user_id=user.id).count(),
            'total_user_likes': Like.objects.filter(user_id=user.id).count(),
        }, users))

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'users': user_data,
        }
        return render(request, 'admin/users_accounts.html', context)

class AdminGetAdminsView(AdminViews):
    def get(self, request):
        """Hiển thị thông tin tất cả các admin hiện tại có trên web"""
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
        admin_data = list(map(lambda admin: {
            'admin': admin,
            'total_admin_posts': Post.objects.filter(admin_id=admin.id).count(),
        }, admins))

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'admins': admin_data,
        }
        return render(request, 'admin/admin_accounts.html', context)

class AdminGetCommentsView(AdminViews):
    def get(self, request):
        """Xem tất cả comment của admin đã login nhận được"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

        message = ''
        comments = Comment.objects.filter(admin_id=self.admin_id)
        comment_data = list(map(lambda comment: {
            'comment': comment,
            'post': Post.objects.get(id=comment.post_id.id),
        }, comments))

        context = {
            'admin_name': admin_name,
            'admin_id': self.admin_id,
            'comments': comment_data,
            'message': message,
        }
        return render(request, 'admin/comments.html', context)

    def post(self, request):
        """Cho phép xóa bình luận admin nhận được"""
        message = ''
        if 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id', '')
            if self.comment_handler.delete_comment(comment_id=comment_id, admin_id=self.admin_id):
                message = "Bình luận được xóa thành công!"

        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'message': message,
        }

        return render(request, 'admin/comments.html', context)
    
class AdminAddPostView(AdminViews):
    def get(self, request):
        """Hiển thị trang chỉnh sửa bài viết"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')
        
        form = PostForm()
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'form': form
        }
        return render(request, 'admin/add_post.html', context)
    
    def post(self, request):
        """Xử lý form chỉnh sửa bài viết"""
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')
        
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.admin = self.admin
            post.status = 'Đang hoạt động' if 'publish' in request.POST else 'Ngừng hoạt động'
            post.content = form.cleaned_data['content'] 
            post.save()
            messages.success(request, 'Bài viết đã được xuất bản!' if post.status == 'Đang hoạt động' else 'Bản nháp đã được lưu!')
            return redirect('add_post')
        else:
            messages.error(request, 'Vui lòng sửa lỗi bên dưới.')
            print(form.errors)
        
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'form': form,
        }
        return render(request, 'admin/add_post.html', context)