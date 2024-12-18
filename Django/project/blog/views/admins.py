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
        """Khởi tạo comment_handler và like_handler nếu admin_id hợp lệ"""
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
        """
        Lấy danh sách tất cả các bài viết của admin theo trạng thái (nếu có)
        Input:
            status (str, optional): Trạng thái của bài viết (ví dụ: 'Đang hoạt động', 'Đã ẩn')
                                    Nếu không truyền giá trị, sẽ lấy tất cả bài viết của admin
        Output:
            list: Danh sách các bài viết kèm thông tin bổ sung gồm:
                - 'post': Đối tượng bài viết (Post instance)
                - 'total_post_comments': Tổng số bình luận cho bài viết
                - 'total_post_likes': Tổng số lượt thích cho bài viết
        """
        if status:
            select_posts = Post.objects.filter(admin_id=self.admin_id, status=status)
        else:
            select_posts = Post.objects.filter(admin_id=self.admin_id)
        self.initialize_handlers()
        post_data = list(map(lambda post: {
            'post': post,
            'total_post_comments': self.comment_handler.get_post_total_comments(post),
            'total_post_likes': self.like_handler.get_post_total_likes(post),
        }, select_posts))

        return post_data
    
    def delete_post(self, request, **kwargs):
        """
        Xóa một bài viết cụ thể của admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
            kwargs (dict): Tham số bổ sung, bao gồm 'status' nếu có
        Output:
            HttpResponse: Trả về trang 'view_posts.html' với danh sách bài viết cập nhật và thông báo kết quả
        """
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
        """
        Hiển thị trang đăng nhập cho admin
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: 
                - Nếu admin đã đăng nhập (session có 'admin_id'): Chuyển hướng đến trang 'dashboard'
                - Nếu chưa đăng nhập: Hiển thị trang 'admin/admin_login.html'
        """
        if request.session.get('admin_id'):
            return redirect('dashboard')
        return render(request, 'admin/admin_login.html')

    def post(self, request):
        """
        Xử lý form đăng nhập cho admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST chứa thông tin đăng nhập:
                - name (str): Tên đăng nhập của admin
                - pass (str): Mật khẩu của admin
        Output:
            HttpResponse:
                - Nếu đăng nhập thành công: Chuyển hướng đến trang 'dashboard'
                - Nếu đăng nhập thất bại: Hiển thị lại trang 'admin/admin_login.html' cùng thông báo lỗi
        """
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
        """
        Hiển thị trang Dashboard với các số liệu thống kê cho admin
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trang 'admin/dashboard.html' với các thống kê:
                - numbers_of_posts: Tổng số bài viết của admin
                - numbers_of_active_posts: Số bài viết của admin đang hoạt động
                - numbers_of_deactive_posts: Số bài viết của admin ngừng hoạt động
                - numbers_of_users: Tổng số người dùng
                - numbers_of_admins: Tổng số admin
                - numbers_of_comments: Tổng số bình luận admin nhận được
                - numbers_of_likes: Tổng số lượt thích bài viết admin nhận được
                - admin_name: Tên admin hiện tại
                - admin_id: ID của admin hiện tại
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Xử lý yêu cầu đăng xuất
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse:
                - Đăng xuất admin và chuyển hướng đến trang 'admin_login'
        """
        logout(request)
        return redirect('admin_login')

class AdminUpdateProfileView(AdminViews):
    def get(self, request, **kwargs):
        """
        Hiển thị trang cập nhật thông tin cá nhân cho admin
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
            kwargs (dict): Các tham số bổ sung bao gồm 'admin_name'
        Output:
            HttpResponse: Trả về trang 'update_profile.html' với thông tin admin
        """
        admin_name = kwargs.get('admin_name')
        return render(request, 'admin/update_profile.html', {'admin_name': admin_name, 'admin_id': self.admin_id})

    def update_password(self, old_pass, new_pass, confirm_pass):
        """
        Cập nhật mật khẩu cho admin
        Input:
            old_pass (str): Mật khẩu hiện tại của admin
            new_pass (str): Mật khẩu mới
            confirm_pass (str): Xác nhận mật khẩu mới
        Output:
            str: Thông báo về kết quả của quá trình cập nhật mật khẩu
        """
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
        """
        Xử lý yêu cầu cập nhật thông tin cá nhân từ admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
            kwargs (dict): Các tham số bổ sung nếu có
        Output:
            HttpResponse: Trả về trang 'update_profile.html' với thông báo kết quả
        """
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
        """
        Hiển thị tất cả các bài viết đã đăng của admin hiện tại
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trả về trang 'view_posts.html' với danh sách bài viết
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
        if self.admin_id is None:
            return redirect('admin_login')
        
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """
        Xử lý yêu cầu xóa bài viết của admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
        Output:
            HttpResponse: Trả về kết quả sau khi xóa bài viết
        """
        return self.delete_post(request)

class AdminViewActivePostView(AdminViews):    
    def get(self, request):
        """
        Hiển thị tất cả các bài viết đang hoạt động trên website của admin hiện tại
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trả về trang 'view_posts.html' với danh sách bài viết đang hoạt động
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
        if self.admin_id is None:
            return redirect('admin_login')
        
        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(status='Đang hoạt động'),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """
        Xử lý yêu cầu xóa bài viết đang hoạt động của admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
        Output:
            HttpResponse: Trả về kết quả sau khi xóa bài viết đang hoạt động
        """
        return self.delete_post(request, status="Đang hoạt động")

class AdminViewDeactivePostView(AdminViews):
    def get(self, request):
        """
        Hiển thị tất cả các bài viết ngừng hoạt động trên website của admin hiện tại
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trả về trang 'view_posts.html' với danh sách bài viết ngừng hoạt động
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
        if self.admin_id is None:
            return redirect('admin_login')

        context = {
            'admin_name': self.admin_name,
            'admin_id': self.admin_id,
            'posts': self.get_posts(status='Ngừng hoạt động'),
        }
        return render(request, 'admin/view_posts.html', context)

    def post(self, request):
        """
        Xử lý yêu cầu xóa bài viết ngừng hoạt động của admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
        Output:
            HttpResponse: Trả về kết quả sau khi xóa bài viết ngừng hoạt động
        """
        return self.delete_post(request, status="Ngừng hoạt động")

# Hiển thị chi tiết các bài đăng của admin khi bấm vào những bài đăng, lấy id đối chiếu tại view_post.html
class AdminReadPostView(AdminViews):
    def get(self, request, post_id):
        """
        Hiển thị chi tiết bài viết và danh sách bình luận
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
            post_id (int): ID của bài viết cần xem chi tiết
        Output:
            HttpResponse: Trả về trang 'read_post.html' với thông tin chi tiết bài viết và bình luận
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Xóa bình luận từ trang xem chi tiết bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
            post_id (int): ID của bài viết chứa bình luận cần xóa
        Output:
            HttpResponse: Quay lại trang chi tiết bài viết sau khi xóa bình luận
        """
        if 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id', '')
            try:
                comment = Comment.objects.get(id=comment_id, post_id=post_id, admin_id=self.admin_id)
                comment.delete()
            except Comment.DoesNotExist:
                pass 

        return redirect('admin_read_post', post_id=post_id)

    def post(self, request):
        """
        Xóa bài viết từ danh sách bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
        Output:
            HttpResponse: Quay lại danh sách bài viết sau khi xóa bài viết
        """
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
        """
        Hiển thị trang chỉnh sửa bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
            post_id (int): ID của bài viết cần chỉnh sửa
        Output:
            HttpResponse: Trả về trang 'edit_post.html' với thông tin bài viết và form chỉnh sửa
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Xử lý form chỉnh sửa bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ admin
            post_id (int): ID của bài viết cần chỉnh sửa
        Output:
            HttpResponse: Quay lại trang chi tiết bài viết nếu chỉnh sửa thành công
            HttpResponse: Trả về trang 'edit_post.html' với lỗi nếu form không hợp lệ
        """
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
        """
        Hiển thị danh sách tất cả user và tổng số bình luận, lượt thích của mỗi user đã thực hiện
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trang 'admin/users_accounts.html' chứa:
                - users: Danh sách user cùng thông tin:
                    - user: Thông tin user
                    - total_user_comments: Tổng số bình luận của user
                    - total_user_likes: Tổng số lượt thích của user
                - admin_name: Tên admin hiện tại
                - admin_id: ID của admin hiện tại
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Hiển thị danh sách tất cả admin và tổng số bài viết của mỗi người
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trang 'admin/admin_accounts.html' chứa:
                - admins: Danh sách admin và tổng số bài viết của họ
                - admin_name: Tên admin hiện tại
                - admin_id: ID của admin hiện tại
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
        admin_name = self.get_admin_context()
        if admin_name is None:
            return redirect('admin_login')

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
    
    def post(self, request):
        """
        Xóa tài khoản admin hiện tại và toàn bộ dữ liệu liên quan
        Input:
            request (HttpRequest): Yêu cầu HTTP POST với key 'delete'
        Output:
            HttpResponseRedirect: Chuyển hướng đến trang 'admin_logout' sau khi xóa:
                - Bài viết (Post) và hình ảnh liên quan
                - Lượt thích (Like) của admin
                - Bình luận (Comment) của admin
                - Tài khoản admin
        """

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

class AdminGetCommentsView(AdminViews):
    def get(self, request):
        """
        Hiển thị danh sách bình luận của admin
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trang 'admin/comments.html' chứa:
                - comments: Danh sách bình luận và bài viết liên quan
                - admin_name: Tên admin
                - admin_id: ID của admin
                - message: Thông báo (nếu có)
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Xóa bình luận dựa trên yêu cầu từ admin
        Input:
            request (HttpRequest): Yêu cầu HTTP POST với:
                - 'delete_comment': Key để xác định xóa bình luận
                - 'comment_id': ID của bình luận cần xóa
        Output:
            HttpResponse: Trang 'admin/comments.html' chứa:
                - message: Thông báo kết quả xóa bình luận
                - admin_name: Tên admin
                - admin_id: ID của admin
        """
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
        """
        Hiển thị trang thêm bài viết
        Inputs:
            request (HttpRequest): Yêu cầu HTTP GET từ admin
        Output:
            HttpResponse: Trang 'admin/add_post.html' với form thêm bài viết
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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
        """
        Xử lý form thêm bài viết
        Inputs:
            request (HttpRequest): Yêu cầu HTTP POST chứa dữ liệu form.
        Output:
            HttpResponse: 
                - Chuyển hướng đến 'add_post' nếu lưu thành công
                - Render lại trang với thông báo lỗi nếu form không hợp lệ
            Redirect: Chuyển đến 'admin_login' nếu chưa đăng nhập
        """
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