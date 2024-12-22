from django.shortcuts import render, redirect
from ..models import Admin, User, Post, Like
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from .base import BaseView

import random
import string

from django.core.mail import send_mail
from django.conf import settings

import requests
from bs4 import BeautifulSoup

class UserViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.session.get('user_id', None)
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)
        return response
    
    def initialize_handlers(self):
        from .comments import CommentViews
        from .likes import LikeViews
        """Khởi tạo comment_handler và like_handler"""
        self.comment_handler = CommentViews(user_id=self.user_id)
        self.like_handler = LikeViews(user_id=self.user_id)
    
    @staticmethod
    def generate_otp(length=6):
        """
        Tạo mã OTP ngẫu nhiên chỉ bao gồm 6 chữ số
        Input:
            length (int, optional): Độ dài mã OTP cần tạo, mặc định là 6
        Output:
            str: Mã OTP ngẫu nhiên bao gồm các chữ số có độ dài tương ứng với tham số đầu vào
        """
        otp = ''.join(random.choices(string.digits, k=length))
        return otp
    
    @staticmethod
    def send_otp_email(request, email, otp_code):
        """
        Gửi email chứa mã OTP xác thực với tiêu đề và nội dung được định dạng HTML
        Input:
            request (HttpRequest): Đối tượng request hiện tại để lưu thời gian gửi OTP
            email (str): Địa chỉ email của người nhận mã OTP
            otp_code (str): Mã OTP cần gửi
        Output:
            None
        """
        subject = '[PyBlog] Mã Xác Thực'
        message = f"""<h3 style='display:block;text-align:center;font-size:18px;'> Xác thực </h3>
                        <p>Mã xác thực của bạn là:
                            <strong style='display:block;text-align:center;font-size:25px;'>{otp_code}</strong>
                        </p>
                        <p>Mã xác thực này chỉ có hiệu lực trong vòng 3 phút. Vui lòng nhập mã xác thực này để hoàn thành quy trình.</p>
                        <p>Thân mến,<br>PyBlog.</p>"""
        send_mail(subject, '', settings.EMAIL_HOST_USER, [email], html_message=message)
        request.session['otp_sent_time'] = timezone.now().isoformat()

    @staticmethod
    def check_uit_email(email):
        """
        Kiểm tra xem email có kết thúc bằng "gm.uit.edu.vn" hay không
        Input:
            email (str): Địa chỉ email cần kiểm tra
        Output:
            bool: 
                - True nếu email kết thúc bằng "gm.uit.edu.vn"
                - False nếu không
        """
        return email.endswith("gm.uit.edu.vn")


def google_login_callback(request):
    """
    Xử lý callback sau khi người dùng đăng nhập thành công qua Google (popup)
    Input:
        request (HttpRequest): Yêu cầu HTTP chứa thông tin về phản hồi từ Google 
                                sau khi người dùng đăng nhập thành công
    Output:
        HttpResponse: Trả về mã HTML chứa script JavaScript để đóng cửa sổ đăng nhập 
                      và chuyển hướng trang chính của ứng dụng
    """
    html_content = """
    <script>
        if (window.opener) {
            window.opener.location.href = '/';
        }
        window.close();
    </script>
    """
    return HttpResponse(html_content)
    
class UserVerification(UserViews):
    def get(self, request):
        """
        Lấy OTP mới và gửi qua email để xác thực
        Input:
            request: Đối tượng HttpRequest chứa thông tin phiên của người dùng
        Output:
            Render trang 'verification.html' để người dùng nhập mã
            Lưu trữ OTP vào session và gửi email chứa mã xác thực
        """
        email = request.session.get('email')
        otp = self.generate_otp()
        request.session['otp'] = otp
        self.send_otp_email(request, email, otp)
        return render(request, 'verification.html', self.context)
    
    def post(self, request):
        """
        Xử lý việc xác thực OTP khi người dùng nhập hoặc chọn gửi lại mã
        Input:
            request: Đối tượng HttpRequest chứa mã OTP từ người dùng và các thông tin liên quan đến việc xác thực
        Output:
            Render trang 'verification.html' với thông báo lỗi nếu OTP không hợp lệ, hoặc chuyển hướng đến trang login nếu thành công
            kiểm tra tính hợp lệ của OTP và thời gian hết hạn, sau đó thực hiện tạo tài khoản hoặc thay đổi mật khẩu cho người dùng
        """
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
                    return render(request, 'verification.html', {'message': 'Mã xác thực đã hết hiệu lực. Vui lòng nhấn "Gửi lại" bên dưới.'})
                
                if otp_code_input != request.session.get('otp'):
                    return render(request, 'verification.html', {'message': 'Mã xác thực không hợp lệ.'})
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
                            return render(request, 'verification.html', {'message': 'Không tìm thấy người dùng.'})
                    return redirect('login')
            
        else:
            return render(request, 'verification.html', {'message': 'Vui lòng nhấn "Gửi lại" bên dưới.'})

        return render(request, 'verification.html', {'message': 'Không tìm thấy dữ liệu phiên. Vui lòng thử lại.'})

class UserResendOTP(UserViews):
    def get(self, request):
        """
        Gửi lại mã OTP xác thực qua email cho người dùng
        Input:
            request: Đối tượng HttpRequest chứa thông tin phiên của người dùng
        Output:
            Chuyển hướng đến trang xác thực hoặc trang đăng ký tùy thuộc vào sự tồn tại của email trong session
        """
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
    def get(self, request):
        """
        Hiển thị trang yêu cầu người dùng nhập email và mật khẩu mới
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            Trả về trang 'forgetpassword.html' cho người dùng
        """
        return render(request, 'forgetpassword.html', self.context)
    
    def post(self, request):
        """
        Xử lý yêu cầu cài lại mật khẩu mới cho người dùng
        Input:
            request: Đối tượng HttpRequest chứa thông tin email và mật khẩu mới
        Output:
            Chuyển hướng đến trang xác thực OTP nếu mật khẩu hợp lệ, hoặc hiển thị thông báo lỗi nếu mật khẩu nhập lại không khớp
        """
        message = ''
        if request.method == "POST":
            fp_email, npass, cpass = (
                request.POST.get('email', '').strip(),
                request.POST.get('npass', ''),
                request.POST.get('cpass', ''),
            )

            if npass != cpass:
                message = 'Mật khẩu nhập lại không khớp!'
            
            else:
                hashed_password = make_password(npass)
                request.session['email'] = fp_email
                request.session['npass'] = hashed_password
                return redirect('verification')
        return render(request, 'forgetpassword.html', {'message': message if 'message' in locals() else ''})

class UserHeaderView(UserViews):
    def get(self, request):
        """
        Hiển thị header người dùng
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            Trả về trang 'user_header.html' với dữ liệu context
        """
        return render(request, 'user_header.html', self.context)

class UserHomeView(UserViews):
    def get(self, request):
        """
        Hiển thị trang chủ với các bài viết mới nhất, thông tin về lượt thích và bình luận,
        cũng như thông tin của tác giả
        Input:
            request (HttpRequest): Yêu cầu GET từ người dùng
        Output:
            HttpResponse: Trả về trang 'home.html' với các bài viết, thông tin về lượt thích và bình luận của người dùng,
                          và danh sách các tác giả.
        """
        posts = Post.objects.filter(status='Đang hoạt động').order_by('-date')[:4]
          
        post_data = list(map(lambda post: {
            'post': post,
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked_by_user': self.like_handler.user_liked_post(post.id),
            'author': (Admin.objects.filter(id=post.admin_id).first() or {}).name,
            'author_id': (Admin.objects.filter(id=post.admin_id).first() or {}).id,
        }, posts))
        
        context = {
            'user_name': self.user_name,
            'user_comments': self.comment_handler.get_user_comments().count(),
            'user_likes': self.like_handler.get_user_likes().count(),
            'posts': post_data,
            'authors': Admin.objects.all(),
            'user_id': self.user_id,
        }

        return render(request, 'home.html', context)

class UserContactView(UserViews):
    def get(self, request):
        """
        Hiển thị trang Liên hệ
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            Trả về trang 'contact.html' với dữ liệu context
        """
        return render(request, 'contact.html', self.context)

class UserAboutView(UserViews):
    def get(self, request):
        """
        Hiển thị trang Giới thiệu
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            Trả về trang 'about.html' với dữ liệu context
        """
        return render(request, 'about.html', self.context)

class UserLogoutView(UserViews):
    def get(self, request):
        """
        Đăng xuất người dùng và chuyển hướng về trang chủ
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            Chuyển hướng về trang 'home' sau khi đăng xuất
        """
        logout(request)
        return redirect('home')

class UserLoginView(UserViews):
    def get(self, request):
        """
        Hiển thị trang đăng nhập cho user
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ user
        Output:
            HttpResponse: 
                - Nếu user đã đăng nhập (session có 'user_id'): Chuyển hướng đến trang 'home'
                - Nếu chưa đăng nhập: Hiển thị trang 'login.html'
        """
        if request.session.get('user_id'):
            return redirect('home')
        return render(request, 'login.html')
     
    def post(self, request):
        """
        Xử lý form đăng nhập cho user
        Input:
            request (HttpRequest): Yêu cầu HTTP POST chứa thông tin đăng nhập:
                - email: Tên đăng nhập của user
                - pass: Mật khẩu của user
        Output:
            HttpResponse:
                - Nếu đăng nhập thành công: Chuyển hướng đến trang 'home'
                - Nếu đăng nhập thất bại: Hiển thị lại trang 'login.html' cùng thông báo lỗi
        """
        message = ''
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('pass')
    
            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    return redirect('home')
                else:
                    message = 'Tên đăng nhập hoặc mật khẩu không đúng!'
            except User.DoesNotExist:
                message = 'Tên đăng nhập hoặc mật khẩu không đúng!'

        return render(request, 'login.html', {'message': message if 'message' in locals() else ''})

class UserLoginWithUITView(UserViews):
    login_url = "https://chungthuc.uit.edu.vn/Login.aspx"
    def get(self, request):
        """
        Hiển thị trang đăng nhập với UIT cho user
        Input:
            request (HttpRequest): Yêu cầu HTTP GET từ user
        Output:
            HttpResponse: 
                - Nếu user đã đăng nhập (session có 'user_id'): Chuyển hướng đến trang 'home'
                - Nếu chưa đăng nhập: Hiển thị trang 'login_with_uit.html'
        """
        if request.session.get('user_id'):
            return redirect('home')
        return render(request, 'login_with_uit.html')
    
    def initialize_session_uit (self):
        """
        Khởi tạo session và lấy các giá trị cần thiết cho việc đăng nhập vào hệ thống UIT
        Output:
            tuple: 
                - viewstate (str): Giá trị của __VIEWSTATE
                - eventvalidation (str): Giá trị của __EVENTVALIDATION
                - session (requests.Session): Đối tượng session cho các yêu cầu tiếp theo
        """
        with requests.Session() as session:
            response = session.get(self.login_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                viewstate = soup.find(id="__VIEWSTATE")["value"]
                eventvalidation = soup.find(id="__EVENTVALIDATION")["value"]
            else:
                viewstate = None
                eventvalidation = None
        return viewstate, eventvalidation, session
    
    def get_info_account_uit (self, **kwargs):
        """
        Lấy thông tin tài khoản từ hệ thống UIT sau khi đăng nhập thành công
        Input:
            kwargs (dict): 
                - viewstate (str): Giá trị __VIEWSTATE
                - eventvalidation (str): Giá trị __EVENTVALIDATION
                - username (str): Tên đăng nhập của người dùng
                - password (str): Mật khẩu của người dùng
                - session (requests.Session): Session đang sử dụng
        Output:
            tuple:
                - email (str): Email của người dùng
                - full_name (str): Tên đầy đủ của người dùng
        """
        viewstate = kwargs.get('viewstate', None)
        eventvalidation = kwargs.get('eventvalidation', None)
        username = kwargs.get('username','')
        password = kwargs.get('password', '')
        session = kwargs.get('session', None)
        payload = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": eventvalidation,
            "UcLogin1:tbUsername": str(username),  
            "UcLogin1:tbPassword": str(password),
            "UcLogin1:btLogin": "Đăng nhập"
        }

        login_response = session.post(self.login_url, data=payload)
        login_soup = BeautifulSoup(login_response.text, "html.parser")

        full_name = login_soup.find(id="UcUserProfile1_tbFN")["value"].split(" -")[0]
        email = login_soup.find(id="UcUserProfile1_tbEmail")["value"]

        return email, full_name
    
    def post(self, request):
        """
        Xử lý đăng nhập cho user thông qua thông tin từ hệ thống UIT
        Input:
            request (HttpRequest): Yêu cầu HTTP POST từ user với thông tin đăng nhập
        Output:
            HttpResponse:
                - Nếu đăng nhập thành công (đã có tài khoản trong CSDL): Lưu lại password của mail trường và 
                    chuyển hướng đến trang 'home'
                - Nếu chưa có tài khoản: Tạo tài khoản mới và chuyển hướng đến 'home'
                - Nếu có thông báo lỗi: Hiển thị lại trang đăng nhập với thông báo lỗi
        """
        message = ''
        if request.method == 'POST':
            username = request.POST.get('mssv')
            password = request.POST.get('pass')

            viewstate, eventvalidation, session = self.initialize_session_uit()
            email, full_name = self.get_info_account_uit(viewstate=viewstate, eventvalidation=eventvalidation, 
                                                         username=username, password=password, session=session)
            try:
                user = User.objects.get(email=email)
                if user:
                    request.session['user_id'] = user.id
                    return redirect('home')
            except User.DoesNotExist:
                User.objects.create(name=full_name, email=email, password=make_password(password))
                message = 'Tạo tài khoản mới thành công!'
                user = User.objects.get(email=email)
                request.session['user_id'] = user.id
                return redirect('home')

        return render(request, 'login_with_uit.html', {'message': message if 'message' in locals() else ''})

class UserRegisterView(UserViews):
    def get(self, request):
        """
        Hiển thị trang đăng ký tài khoản mới
        Input:
            request: Đối tượng HttpRequest chứa thông tin yêu cầu
        Output:
            HttpResponse:
                - Trả về trang đăng ký 'register.html' để người dùng nhập thông tin
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        Xử lý thông tin đăng ký người dùng và lưu trữ dữ liệu vào session
        Input:
            request (HttpRequest): Yêu cầu HTTP POST chứa thông tin đăng ký:
                - name: Tên người dùng
                - email: Địa chỉ email của người dùng
                - pass: Mật khẩu của người dùng
                - cpass: Mật khẩu nhập lại để xác nhận
        Output:
            HttpResponse:
                - Nếu email đã được đăng ký: Hiển thị lại trang 'register.html' với thông báo lỗi
                - Nếu mật khẩu và mật khẩu nhập lại không khớp: Hiển thị lại trang 'register.html' với thông báo lỗi
                - Nếu đăng ký thành công: Chuyển hướng đến trang 'verification' để xác thực OTP người dùng
        """
        message = ''
        if request.method == 'POST':
            name, email, password, confirm_password = (
                request.POST.get('name'),
                request.POST.get('email'),
                request.POST.get('pass'),
                request.POST.get('cpass'),
            )
            
            if User.objects.filter(email=email).exists():
                message = 'Email đã được đăng ký cho tài khoản khác!'
            else:
                if password != confirm_password:
                    message = 'Mật khẩu nhập lại không chính xác!'
                else:
                    hashed_password = make_password(password)
                    request.session['name'] = name
                    request.session['email'] = email
                    request.session['password'] = hashed_password

                    return redirect('verification')

        return render(request, 'register.html', {'message': message if 'message' in locals() else ''})

class UserUpdateProfileView(UserViews):
    def get(self, request):
        """
        Hiển thị trang chỉnh sửa thông tin cá nhân của người dùng
        Input:
            request (HttpRequest): Yêu cầu GET từ người dùng
        Output:
            HttpResponse: Trả về trang 'update.html' với thông tin người dùng hiện tại
        """
        if self.check_uit_email(self.user.email):
            message = "Các tài khoản có đuôi email là gm.uit.edu.vn sẽ không được cập nhật bất kì thông tin gì."

        return render(request, 'update.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email, 'message': message})

    def update_password(self, old_pass, new_pass, confirm_pass):
        """
        Cập nhật mật khẩu người dùng sau khi xác thực mật khẩu hiện tại và các điều kiện mật khẩu mới
        Input:
            old_pass (str): Mật khẩu hiện tại của người dùng
            new_pass (str): Mật khẩu mới muốn thay đổi
            confirm_pass (str): Xác nhận mật khẩu mới
        Output:
            str: Thông báo về kết quả cập nhật mật khẩu (thành công hoặc lỗi)
        """
        if not check_password(old_pass, self.user.password):
            return 'Mật khẩu hiện tại không đúng!'
        elif new_pass != confirm_pass:
            return 'Mật khẩu nhập lại không chính xác!'
        elif not new_pass:
            return 'Vui lòng nhập mật khẩu mới!'
        else:
            self.user.password = make_password(new_pass)
            self.user.save()
            return 'Mật khẩu được cập nhật thành công!'

    def post(self, request):
        """
        Xử lý yêu cầu cập nhật thông tin cá nhân của người dùng, bao gồm tên, email và mật khẩu
        Input:
            request (HttpRequest): Yêu cầu POST từ người dùng, chứa thông tin cập nhật:
                - name: Tên người dùng mới
                - email: Địa chỉ email mới
                - old_pass: Mật khẩu cũ (nếu thay đổi mật khẩu)
                - new_pass: Mật khẩu mới (nếu thay đổi mật khẩu)
                - confirm_pass: Xác nhận mật khẩu mới
        Output:
            HttpResponse: Trả về trang 'update.html' với thông báo kết quả cập nhật thông tin cá nhân
        """
        message = ''
        if request.method == 'POST' and 'submit' in request.POST:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            
            if self.user.email.endswith("gm.uit.edu.vn"):
                message = "Các tài khoản có đuôi email là gm.uit.edu.vn sẽ không được cập nhật bất kì thông tin gì."

            else:
                self.user.name = name if name else self.user.name
                self.user.save()

                if email and User.objects.filter(email=email).exclude(id=self.user_id).exists():
                        message = 'Email đã được đăng ký!'
                elif email:
                    self.user.email = email
                    self.user.save()

                old_pass = request.POST.get('old_pass', '').strip()
                new_pass = request.POST.get('new_pass', '').strip()
                confirm_pass = request.POST.get('confirm_pass', '').strip()
                
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
    def get(self, request):
        """
        Hiển thị tất cả các bài viết mà người dùng đã thích
        Input:
            request (HttpRequest): Yêu cầu GET từ người dùng
        Output:
            HttpResponse: Trả về trang 'user_likes.html' với danh sách các bài viết mà người dùng đã Like,
                          bao gồm số lượng like và comment của mỗi bài viết
        """
        post_data = []
        if self.user_id:
            likes = self.like_handler.get_user_likes()
            if likes.exists():
                post_ids = likes.values_list('post_id', flat=True)
                posts = Post.objects.filter(id__in=post_ids, status='Đang hoạt động').annotate(
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

class UserLoadAuthors(UserViews):
    def get(self, request):
        """
        Hiển thị thông tin các tác giả (admin) cho người dùng, bao gồm số lượng bài viết,
        số lượt like và số lượt comment của mỗi tác giả
        Input:
            request (HttpRequest): Yêu cầu GET từ người dùng
        Output:
            HttpResponse: Trả về trang 'authors.html' với danh sách các tác giả và thông tin thống kê liên quan
                          đến các bài viết, like và comment của họ
        """
        authors = Admin.objects.all()

        author_stats = list(map(lambda author: {
            'name': author.name,
            'total_posts': Post.objects.filter(admin_id=author.id, status='Đang hoạt động').count(),
            'total_likes': self.like_handler.get_admin_likes(admin_id=author.id).count(),
            'total_comments': self.comment_handler.get_admin_comments(admin_id=author.id).count(),
        }, authors))

        context = {
            'author_stats': author_stats,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        
        return render(request, 'authors.html', context)

class UserCommentsView(UserViews):
    def get(self, request):
        """
        Hiển thị tất cả các bình luận mà người dùng đã thực hiện
        Input:
            request (HttpRequest): Yêu cầu HTTP GET để tải trang bình luận của người dùng
        Output:
            HttpResponse: Trả về trang HTML 'user_comments.html' với danh sách bình luận của người dùng
        """
        if self.user_id:
            comments = self.comment_handler.get_user_comments()
        
        context = {
            'comments': comments,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

        return render(request, 'user_comments.html', context)

    def post(self, request):
        """
        Xử lý các hành động cho bình luận của người dùng: chỉnh sửa, xóa và mở hộp chỉnh sửa
        Input:
            request (HttpRequest): Yêu cầu HTTP POST chứa các thao tác với bình luận của người dùng
        Output:
            HttpResponse: Trả về trang HTML 'user_comments.html' với các thông báo và trạng thái hiện tại của bình luận.
                - Nếu chỉnh sửa bình luận thành công: Thông báo "Chỉnh sửa bình luận thành công!"
                - Nếu bình luận đã tồn tại: Thông báo "Bình luận đã tồn tại!"
                - Nếu xóa bình luận thành công: Thông báo "Bình luận được xóa thành công!"
        """
        comment_id = None
        edit_comment = None
        message = ''
        if request.method == "POST":
            if 'edit_comment' in request.POST:
                edit_comment_id = request.POST.get('edit_comment_id')
                comment_edit_box = request.POST.get('comment_edit_box')

                if self.comment_handler.comment_exists(comment_edit_box, edit_comment_id):
                    message = "Bình luận đã tồn tại!"
                else:
                    self.comment_handler.update_comment(edit_comment_id, comment_edit_box)
                    message = "Chỉnh sửa bình luận thành công!"

            elif 'delete_comment' in request.POST:
                delete_comment_id = request.POST.get('comment_id')
                if self.comment_handler.delete_comment(comment_id=delete_comment_id, user_id=self.user_id):
                    message = "Bình luận được xóa thành công!"

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
    def post(self, request, **kwargs):
        """
        Xử lý người dùng thực hiện hành động Like hoặc Unlike đối với bài viết
        Input:
            request (HttpRequest): Yêu cầu POST từ người dùng, chứa thông tin bài viết cần Like hoặc Unlike
            kwargs (dict): Chứa tham số `post_id` để xác định bài viết người dùng muốn Like hoặc Unlike
        Output:
            HttpResponse: Chuyển hướng về trang trước đó (HTTP_REFERER), cập nhật trạng thái Like của bài viết
        """
        if not self.user_id:
            return redirect('login')
        post_id = kwargs.get('post_id')
        like = Like.objects.filter(user_id=self.user_id, post_id=post_id).first()
        post = Post.objects.get(id=post_id)
        admin = Admin.objects.get(id=post.admin_id)

        if like:
            like.delete()
        else:
            self.like_handler.like_post(self.user, admin, post)

        return redirect(request.META.get('HTTP_REFERER'))