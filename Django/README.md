## Vui lòng không chỉnh sửa hay đụng gì tới mấy cái code t sửa trong thư mục Django này rồi nha 😞. Chỉ được thêm code mới vào hoặc xem thôi

### ⚠️ Chú ý
Thư mục Django này là chỗ chính thức để tụi mình code đồ án (tức là chuyển mấy code php kia sang python thì sẽ làm trong thư mục này khi nào xong hết đồ án thì tụi mình xóa mấy file php bên ngoài thư mục Django này).  
Nhưng mà hiện tại t mới fix bên phía người dùng thôi, còn admin thì chưa sửa hết.

### ✨ Xem web với code Python mới 
**Bước 1:** Clone repo về, bật terminal trong VSCode (hoặc Pycharm), chạy câu lệnh:
```bash
cd Django/project
```
Chạy xong thấy đuôi như này là oke:  
![Screenshot 2024-11-09 014555](https://github.com/user-attachments/assets/66e4caf3-cb5b-4ba4-98ae-4dcf9a96f67c)  

**Bước 2:** Sau đó chạy lệnh rồi truy cập vào link http://127.0.0.1:8000/ là coi được web mình nha:
```bash
python manage.py runserver
```

### Lưu ý sơ bộ
Hiện tại database t cũng tích hợp vào luôn rồi, mọi người cứ làm thôi ko cần chạy lệnh makemigrate hay gì đâu, cứ runserver là được. Trong quá trình làm thì ko sửa mấy file trong thư mục models giùm t nha. Backend python làm thường gặp mấy lỗi kiểu gọi thuộc tính của instance gì đó từ database thì mn có thể đọc lỗi python nó báo rồi hỏi chatgpt nó fix được, khum thì tham khảo code của t cũng được.  

Trong thư mục **Django/project** sẽ có các thư mục *blog, cert, project*; trong đó thư mục **Django/project/project** là chạy lệnh **django-admin startproject project** mà có (project là tên dự án), thư mục **Django/project/blog** là chạy lệnh **python manage.py startapp blog** mà có (blog là tên app của mình), còn thư mục Django/project/cert là chỗ chứa chứng chỉ SSL của bên hosting database của mình thôi nên ko cần quan tâm và cũng đừng đụng tới (xóa hay gì là mất kết nối database với python á).  

Lưu ý nhỏ nữa là thường trong lúc code python mà muốn lấy user hiện tại đang dùng web thì chỉ cho gọi theo kiểu:
```bash
user = request.user
```
Nhưng mà trong file Django/project/blog/middleware.py thì t có code để mình tiện gọi user_id với admin_id:
```python
# middleware.py
class UserIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_id = request.session.get('user_id', None)
        
        response = self.get_response(request)
        return response
    
class AdminIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.admin_id = request.session.get('admin_id', None)
        
        response = self.get_response(request)
        return response
```

Nhờ vậy mà sẽ cho gọi lấy thẳng id của user hiện tại từ các file code khác bằng cách gọi:
```bash
user_id = self.user_id
```
Giống trong file **Django/project/blog/views/base.py** (dòng thứ 7 chỗ self.user_id):
```python
from ..models import Admin, User
from django.views import View

class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.user_id = request.session.get('user_id', None)
        self.user = User.objects.filter(id=self.user_id).first() if self.user_id else None
        self.user_name = self.user.name if self.user else None
        self.user_email = self.user.email if self.user else None

        self.admin_id = request.session.get('admin_id', None)
        self.admin = Admin.objects.filter(id=self.admin_id).first() if self.admin_id else None
        self.admin_name = self.admin.name if self.admin else None

        self.context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'admin_id': self.admin_id,
            'admin_name': self.admin_name,
        }
        return super().dispatch(request, *args, **kwargs)
```

Nên là khi mọi người copy dính dòng code gọi này của t khi hỏi chatgpt thì nó sẽ kêu lỗi chỗ **self.user_id** nhưng thật ra là ko có lỗi đâu vì đã được code sẵn bên **Django/project/blog/middleware.py** để gọi rồi.  

Tuy nhiên, base.py này chứa class mấy class khác trong thư mục **Django/project/blog/views** kế thừa (do nó chứa thông tin của user hiện tại duyệt web và bất kì trang nào cũng liên quan đến user nên cần lấy id, name của user để hiện lên header...) => Nhờ cái này mà mấy class kế thừa sau nếu muốn lấy id của user thì chỉ cần gọi:
```bash
self.user_id
# Hoặc gọi admin_id thì dùng self.admin_id
```

## Lưu ý để code MVC (thực chất với Django là MVT), tổ chức OOP
Trong **Django/project/blog/views** có cấu trúc như hình dưới đây:  
![Screenshot 2024-11-16 143317](https://github.com/user-attachments/assets/babbf8a8-35f4-4f47-b722-cbb8bcfeb859)  
Nhìn tên file là biết rồi ha, tương ứng với mỗi file thì nội dung bên trong file sẽ là các code chứa logic liên quan đến tên file. Ví dụ trong users.py sẽ có code logic để hiển thị trang login, register phía user...

Để thuận tiện cho việc MVT, tổ chức code theo OOP để dễ quản lý thì Django có hỗ trợ **class base view** mọi người có thể tìm đọc thêm, ở đây nói sơ sơ thôi nha.

Trong **Django/project/blog/urls.py** sẽ chứa các pattern url để định dạng cái url mà mình mong muốn nó chạy logic gì giống thầy nói trên lớp (t lấy ví dụ phía user xem tất cả comment mà họ đã comment nha):
```python
# from này là để import các class trong Django/project/blog/views/users.py qua đây để dùng gọi hàm logic cho url
from .views.users import UserHeaderView, UserContactView, UserAboutView, UserLogoutView, UserLoginView, UserRegisterView, UserHomeView, UserUpdateProfileView, UserLikesView, UserCommentsView, UserLoadAuthors, UserLoadAuthorPosts, UserLikedPost
urlpatterns = [
    # còn nhiều path nữa, lấy ví dụ cái này thôi
    # import class như trên thì mới gọi được UserCommentsView
    path('user-comments', UserCommentsView.as_view(), name='user_comments'),
]
```
UserCommentsView.as_view() có format [tên lớp].as_view() là do class base view của Django hỗ trợ, tức là cứ ghi theo format này thì nó sẽ tự chạy logic các hàm tương ứng bên trong lớp UserCommentsView, còn nó sẽ chạy hàm thế nào thì đọc tiếp ở dưới he.
Trong **Django/project/blog/views/users.py** sẽ có 1 lớp chính là *UserViews* để các lớp liên quan user kế thừa:
```python
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

```
Lấy ví dụ lớp *UserCommentsView* (logic Hiển thị tất cả comment mà user đã comment) sẽ kế thừa lớp *UserViews* trên và bao gồm 2 hàm bên trong là **get** và **post** tương ứng là 2 phương thức GET và POST đã học trong mạng máy tính:
```python
class UserCommentsView(UserViews):
    """Hiển thị tất cả comment mà user đã comment"""
    def get(self, request):
        return render(request, 'user_comments.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email})

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
                if self.comment_handler.delete_comment(delete_comment_id):
                    message = "Comment deleted successfully!"

            elif 'open_edit_box' in request.POST:
                comment_id = request.POST.get('comment_id')
                edit_comment = self.comment_handler.get_current_comments(comment_id)

        comments = self.comment_handler.get_user_comments()

        context = {
            'comments': comments,
            'edit_comment': edit_comment,
            'comment_id': comment_id,
            'message': message,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

        return render(request, 'user_comments.html', context)
```
Tức là khi người dùng truy cập vào url chứa /user-comments là GET á thì nó sẽ chạy hàm get của lớp UserCommentsView; nếu người dùng nhấn button gì đó của form như là nhấn Delete comment tức là phương thức POST thì nó sẽ chạy hàm post của lớp UserCommentsView. (trong class base view này chỉ chạy 2 phương thức là GET và POST thôi, và đó là lý do tại sao các class trong users.py của t chỉ có 1 hoặc cả 2 hàm get và post tùy theo trang đó có form để dùng POST hay không nếu chỉ là trang hiển thị bình thường không có có form xóa sửa gì thì chỉ cần hàm get là đủ).  

Trong hàm get của t có return ra như dưới đây:
```python
# format render của Django là render(request, 'template_name.html', context)
# trong đó {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email} chính là context
return render(request, 'user_comments.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email})
```
Hoặc trong hàm post của t có return ra như dưới đây:
```python
context = {
    'comments': comments,
    'edit_comment': edit_comment,
    'comment_id': comment_id,
    'message': message,
    'user_id': self.user_id,
    'user_name': self.user_name,
}

return render(request, 'user_comments.html', context)
```
Cấu trúc của context là một dictionary với các cặp key-value, trong đó:
- Key: Tên của biến mà bạn muốn sử dụng trong template.
- Value: Giá trị của biến (có thể là chuỗi, số, danh sách, đối tượng, hoặc bất kỳ loại dữ liệu Python nào).  

Tương ứng với định dạng url trong file **Django/project/blog/urls.py** (t đã ví dụ ở trên) thì khi user truy cập url chứa /user-comments nó sẽ hiển thị user-comments.html dưới đây (do hàm get trong lớp *UserCommentsView* return render(request, 'user_comments.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email}) là render ra *user_comments.html*):
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>User Comments</title>
   
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
   <link rel="icon" type="image/x-icon" href="{% static 'image/doraemon.webp' %}">

   <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>

{% include 'user_header.html' %}

{% if edit_comment %}
   <section class="comment-edit-form">
      <p>Edit your comment</p>
      <form action="" method="POST">
         {% csrf_token %}
         <input type="hidden" name="edit_comment_id" value="{{ edit_comment.id }}">
         <textarea name="comment_edit_box" required cols="30" rows="10" placeholder="Please enter your comment">{{ edit_comment.comment }}</textarea>
         <button type="submit" class="inline-btn" name="edit_comment">Edit Comment</button>
         <div class="inline-option-btn" onclick="window.location.href = '{% url 'user_comments' %}';">Cancel Edit</div>
      </form>
   </section>
{% endif %}

<section class="comments-container">
   <h1 class="heading">Your Comments</h1>
   <p class="comment-title">Your comments on the posts</p>
   <div class="user-comments-container">
      {% if comments %}
         {% for comment in comments %}
            <div class="show-comments">
               <div class="post-title">From: 
                  <span>{{ comment.post_id.title }}</span> 
                  <a href="{% url 'view_post' comment.post_id.id %}">View Post</a>
               </div>
               <div class="comment-box">{{ comment.comment }}</div>
               <form action="" method="POST">
                  {% csrf_token %}
                  <input type="hidden" name="comment_id" value="{{ comment.id }}">
                  <button type="submit" class="inline-option-btn" name="open_edit_box">Edit Comment</button>
                  <button type="submit" class="inline-delete-btn" name="delete_comment" onclick="return confirm('Delete this comment?');">Delete Comment</button>
               </form>
            </div>
         {% endfor %}
      {% else %}
         <p class="empty">No comments added yet!</p>
      {% endif %}
   </div>
</section>

{% include 'footer.html' %}

<script src="{% static 'js/script.js' %}"></script>
</body>
</html>
```

### 😊 Cảm ơn mn! Có gì ko hiểu thì hỏi t nhaaa. Chỉ code thêm, và đặc biệt là không xóa sửa gì các file **Django/project/blog/middleware.py**, **Django/project/blog/views/base.py**