## 📒 NOTE
Trong thư mục **Django/project** sẽ có các thư mục *blog, cert, project*; trong đó thư mục **Django/project/project** là chạy lệnh **django-admin startproject project** mà có (project là tên dự án), thư mục **Django/project/blog** là chạy lệnh **python manage.py startapp blog** mà có (blog là tên app của mình), còn thư mục **Django/project/cert** là chỗ chứa chứng chỉ SSL của bên hosting database của mình thôi nên ko cần quan tâm và cũng đừng đụng tới (xóa hay gì là mất kết nối database á).  

Tuyệt đối ko chỉnh sửa hay đụng tới thư mục *models, static, cert*, và các file như *Django/project/blog/middleware.py, Django/project/blog/views/base.py*

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

### ⚠️ Lưu ý sơ bộ
Backend python làm thường gặp mấy lỗi kiểu gọi thuộc tính của instance gì đó từ database thì mn có thể đọc lỗi python nó báo rồi hỏi chatgpt nó fix được, khum thì tham khảo code của t cũng được.  

Lúc code nếu mà máy của mọi người nó báo lỗi liên quan mấy cái module của Django giống giống dưới đây (mặc dù đã pip install django rồi) thì cứ kệ nha, runserver vẫn chạy được web á:  
![Screenshot 2024-11-17 194606](https://github.com/user-attachments/assets/98db5c1d-b5f9-4ff5-861c-a66672a8b055)  

Lưu ý nhỏ là thường trong lúc code python mà muốn lấy user hiện tại đang dùng web thì chỉ cho gọi theo kiểu:
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

Tuy nhiên, base.py này chứa class mấy class khác trong thư mục **Django/project/blog/views** kế thừa (do nó chứa thông tin của user hiện tại duyệt web hoặc thông tin của admin hiện tại và bất kì trang nào ở phía user cũng liên quan đến user nên cần lấy id, name của user để hiện lên header... tương tự như các trang bên phía admin thì cũng cần các thông tin của admin hiện tại) => Nhờ cái này mà mấy class kế thừa sau nếu muốn lấy id của user thì chỉ cần gọi:
```bash
self.user_id
# Hoặc gọi admin_id thì dùng self.admin_id
# Tương tự, gọi được self.user, self.user_name, self.user_email, self.admin, self.admin_name
```

## ⚠️ Lưu ý các file trong thư mục Django/project/blog/models
Hiện tại database t đã tích hợp vào rồi, mọi người cứ làm thôi ko cần chạy lệnh makemigrate hay gì đâu, cứ runserver là được.  
Cấu trúc file của thư mục models:  
![Screenshot 2024-11-17 155144](https://github.com/user-attachments/assets/fdb1edba-8d3c-4b5e-98cc-f46a19154868)  
5 file *admins.py, comments.py, likes.py, posts.py, users.py* tương ứng là 5 table trong database của mình.
Trong quá trình làm thì ko sửa mấy file trong thư mục models giùm t vì trong đó là thiết lập các table của database, mọi người xem tên thuộc tính đồ thôi ha. Ví dụ như file **Django/project/blog/models/posts.py** sẽ chứa các thuộc tính của bảng post trong database và tên thuộc tính cũng giống với cái tên thuộc tính hiển thị trên phpMyAdmin luôn để dễ làm việc:
```python
from django.db import models
from .admin import Admin

class Post(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)  # Foreign key relationship
    name = models.CharField(max_length=100)  # Corresponds to the 'name' field in your database
    title = models.CharField(max_length=100)  # Corresponds to the 'title' field
    content = models.TextField()  # Use TextField for larger text content
    category = models.CharField(max_length=50)  # Corresponds to the 'category' field
    image = models.ImageField(upload_to='', null=True, blank=True)  # Assuming images are stored in 'uploaded_img/'
    date = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    status = models.CharField(max_length=10)  # Corresponds to the 'status' field

    class Meta:
        db_table = 'posts'  # This should match your database table name
        managed = False
```

## ⚠️ Lưu ý để code MVC (thực chất với Django là MVT), tổ chức OOP
Trong **Django/project/blog/views** có cấu trúc như hình dưới đây:  
![Screenshot 2024-11-16 143317](https://github.com/user-attachments/assets/babbf8a8-35f4-4f47-b722-cbb8bcfeb859)  
Nhìn tên file là biết rồi ha, tương ứng với mỗi file thì nội dung bên trong file sẽ là các code chứa logic liên quan đến tên file. Ví dụ trong users.py sẽ có code logic để hiển thị trang login, register, load trang home... phía user.

Để thuận tiện cho việc MVT, tổ chức code theo OOP để dễ quản lý thì Django có hỗ trợ **class-based view** mọi người có thể tìm đọc thêm, ở đây nói sơ sơ thôi nha.

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
**UserCommentsView.as_view()** có format *[tên lớp].as_view()* là do class-based view của Django hỗ trợ, tức là cứ ghi theo format này thì nó sẽ tự chạy logic các hàm tương ứng bên trong lớp UserCommentsView, còn nó sẽ chạy hàm thế nào thì đọc tiếp ở dưới he.  
Trong **Django/project/blog/views/users.py** sẽ có 1 lớp chính là *UserViews* để các lớp liên quan user kế thừa:
```python
# đoạn code thuộc file Django/project/blog/views/users.py
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
# đoạn code thuộc file Django/project/blog/views/users.py
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
Tức là khi người dùng truy cập vào url chứa /user-comments là GET á thì nó sẽ chạy hàm get của lớp UserCommentsView; nếu người dùng nhấn button gì đó của form như là nhấn Delete comment tức là phương thức POST thì nó sẽ chạy hàm post của lớp UserCommentsView. (trong class-based view này chỉ chạy 2 phương thức là GET và POST thôi, và đó là lý do tại sao các class trong users.py của t chỉ có 1 hoặc cả 2 hàm get và post tùy theo trang đó có form để dùng POST hay không nếu chỉ là trang hiển thị bình thường không có có form xóa sửa gì thì chỉ cần hàm get là đủ).  

Trong hàm get của t có return ra như dưới đây:
```python
# đoạn code thuộc file Django/project/blog/views/users.py

# format render của Django là render(request, 'template_name.html', context)
# trong đó {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email} chính là context
return render(request, 'user_comments.html', {'user_name': self.user_name, 'user_id': self.user_id, 'user_email': self.user_email})
```
Hoặc trong hàm post của t có return ra như dưới đây:
```python
# đoạn code thuộc file Django/project/blog/views/users.py

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

Tương ứng với định dạng url trong file **Django/project/blog/urls.py** (t đã ví dụ ở trên) thì khi user truy cập url chứa /user-comments nó sẽ hiển thị user-comments.html dưới đây (do hàm get trong lớp *UserCommentsView* render ra *user_comments.html*):
```html
<!-- đoạn template thuộc file Django/project/blog/template/user_comments.html -->

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

## ⚠️ Lưu ý với các file comments.py và likes.py trong thư mục Django/project/blog/views
Với các hàm xử lý logic lặp đi lặp lại nhiều lần (ví dụ như liên quan Comment là Lấy số lượt bình luận của một bài viết, hoặc liên quan Like là Lấy tất cả lượt like của người dùng đã like,...) thì sẽ tổ chức thành các lớp CommentViews và LikeViews tương ứng trong thư mục **Django/project/blog/views**, gom nhóm tất cả các hàm (method) liên quan, giúp code dễ bảo trì hơn và có thể tái sử dụng nhiều lần ở nhiều file code khác nhau mà không cần lặp lại logic code đó. 
- Lớp **CommentViews** trong file *comments.py* chỉ tập trung xử lý các công việc liên quan đến bình luận.
- Lớp **LikeViews** trong file *likes.py* chỉ tập trung xử lý các công việc liên quan đến lượt thích.
Nên khi mn code có gì liên quan đến comment và like thì nên code vào class của 2 file comments.py và likes.py này nha để tiện gọi và quản lý code.

## ⚠️ Lưu ý với các file template_name.html
### Load các file tĩnh như css, js hoặc image (image tĩnh là image dạng không thay đổi được trên web sẽ khác với image các bài blog là thêm, xóa, sửa được)
Với đoạn mã HTML ở trên (user_comments.html) thì mọi người sẽ thấy ngay dòng đầu tiên là:
```html
{% load static %}
```
Tại sao ghi như vậy là vì các file .js và .css nó nằm trong thư mục **Django/project/blog/static** (tức là các file tĩnh sẽ nằm trong static này á), khi muốn load được css hoặc js trong .html thì phải ghi thêm dòng đó vào rồi load .css và .js bằng cách:
```html
<head>
    <!-- thẻ head còn nhiều dòng nhưng lấy dòng vidu cho static này thôi -->
   <link rel="icon" type="image/x-icon" href="{% static 'image/doraemon.webp' %}">

   <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<!-- load js -->
<script src="{% static 'js/script.js' %}"></script>
```

### Load header và footer cho trang web
Import header và footer cho trang web chỉ với 2 dòng dưới đây:
```html
<!-- Ghi ở dòng đầu tiên của thẻ <body> ghi như này là import được header -->
{% include 'user_header.html' %}
<!-- Nếu muốn lấy header của trang admin thì cũng ghi ở dòng đầu tiên của thẻ <body> bên các trang của admin -->
{% include 'admin/admin_header.html' %}

<!-- Ghi ở dòng cuối cùng của thẻ <body> ghi như dưới là import được footer -->
{% include 'footer.html' %}
```

### Load các url cần thiết cho href của thẻ <a> hoặc các button nhấn vào để chuyển hướng đến trang khác
Trong *user_comments.html* có chứa các dòng url sau (lấy ví dụ):
```html
<div class="inline-option-btn" onclick="window.location.href = '{% url 'user_comments' %}';">Cancel Edit</div>

<a href="{% url 'view_post' comment.post_id.id %}">View Post</a>
```
Tương ứng có các url pattern đã cài trong **Django/project/blog/urls.py**:
```python
urlpatterns = [
    # còn nhiều path nữa, lấy ví dụ cái này thôi
    path('user-comments', UserCommentsView.as_view(), name='user_comments'),

    path('post/<int:post_id>/', PostViewPost.as_view(), name='view_post'),
]
```
Format của path: *path(route, view, kwargs=None, name=None)*, trong đó:
- route: Chuỗi định nghĩa URL mà bạn muốn ánh xạ (ví dụ: 'post/<int:post_id>/').
- view: View xử lý khi người dùng truy cập URL này (có thể là class-based view).
- kwargs (tùy chọn): Dictionary các tham số bổ sung bạn muốn truyền đến view.
- name: Tên của route, cho phép bạn tham chiếu URL này ở các nơi khác (như trong file template_name.html) bằng tên thay vì viết lại toàn bộ đường dẫn.  

Dòng **{% url 'user_comments' %}** format là *{% url 'name_of_path_tương_ứng' %}*  
Dòng **{% url 'view_post' comment.post_id.id %}** format là *{% url 'name_of_path_tương_ứng' biến_truyền_thêm_vào %}*  

Khi nào cần truyền thêm biến vào url? Ví dụ như view_post sẽ truyền thêm biến id của bài post vì khi người dùng click vào Read More của bài viết bất kì, sẽ phải lấy id của bài viết đó truyền cho url và hàm views tương ứng để xử lý hiển thị cho nó, như code dưới đây nhận thêm biến post_id để xử lý hiển thị đúng bài post (tùy trường hợp code mà sẽ cần truyền biến, không thì thôi):
```python
# đoạn code trong file Django/project/blog/views/posts.py
class PostViewPost(PostsViews):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id, status='active')
        all_comments = self.comment_handler.get_all_comments(post_id)
        user_comments = self.comment_handler.get_user_comments_of_post(post_id)

        total_post_comments = self.comment_handler.get_post_total_comments(post)
        total_post_likes = self.like_handler.get_post_total_likes(post)
        user_liked = False

        if self.user_id:
            user_liked = self.like_handler.user_liked_post(post.id)

        context = {
            'post': post,
            'all_comments': all_comments,
            'user_name': self.user_name,
            'user_id': self.user_id,
            'user_comments': user_comments,
            'total_post_comments': total_post_comments,
            'total_post_likes': total_post_likes,
            'user_liked': user_liked,
        }
        return render(request, 'view_post.html', context)
```

### Django Template Language (DTL)
Có thể đọc ở https://viblo.asia/p/django-template-language-6J3ZgyRP5mB (quan trọng là mục Tags) để hiểu thêm.  
#### Gọi biến trong context ra sử dụng:  
Như đã nói trong urls.py:
```python
path('user-comments', UserCommentsView.as_view(), name='user_comments'),
``` 
Và ví dụ context của lớp UserCommentsView trong **Django/project/blog/views/users.py**:
```python
# đoạn code thuộc file Django/project/blog/views/users.py

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
Giả sử trong *user_comments.html* khi render ra mà muốn lấy giá trị message trong context thì chỉ cần ghi:
```html
{{ message }}
```
Là khi render ra *user_comments.html* nó sẽ lấy *message* trong context để in ra trên *user_comments.html*. Trong trường hợp này thì *message* là những thông báo alert của javascript, và t cài script này ở file header chung là *user_header.html* và *admin_header.html* (do phía user thì trang nào cũng có header nên cài chung thông báo alert nhận message cho tiện, giống như header được import vào file *user_comments.html* nên khi render ra *user_comments.html* thì header cũng sẽ nhận được biến message này, tương tự như admin thì trang nào cũng có admin_header ha):
```html
<!-- đoạn mã trong file Django/project/blog/template/user_header.html -->
{% if message %}
   <script>
      alert("{{ message }}");
   </script>
{% endif %}
```
Nên là nếu mọi người muốn alert thông báo message trên trang (A) mà trang (A) có import *user_header.html* hoặc import *admin_header.html* thì chỉ cần thêm message vào context của views xử lý render của trang (A) là được.  

#### Về vòng lặp for của DTL trong file .html
Ví dụ 1 đoạn mã trong *user_comments.html*:
```html
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
```
Và comments trong context của file **Django/project/blog/views/users.py**:
```python
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
Và hàm *get_all_comments* trong file **Django/project/blog/views/comments.py**:
```python
def get_user_comments(self):
    """Lấy tất cả các bình luận của người dùng đã bình luận"""
    return Comment.objects.filter(user_id=self.user_id)
```
- comments này là 1 list các comments mà người dùng hiện tại đã bình luận. 1 comment sẽ chứa các thuộc tính là *id, post_id, admin_id, user_id, user_name, comment, date* nên trong html, **{% for comment in comments %}** là duyệt qua từng comment trong list comments này, lấy nội dung comment của từng comment sẽ truy cập thuộc tính comment theo kiểu **{{ comment.comment }}** (Nếu vòng lặp for ghi là **{% for item in comments %}** thì lấy nội dung comment của từng comment sẽ truy cập thuộc tính comment theo kiểu **{{ item.comment }}**)
- Trong vòng lặp for **{% for comment in comments %}**, có chứa **{{ comment.post_id.title }}** lấy title của bài viết, kiểu post_id là khóa ngoại nối giữa 2 bảng là **post** và **comment**, trong bảng post có title nên khi lấy title bài viết tương ứng với comment đó thì phải thông qua khóa ngoại post_id á, nên phải ghi **{{ comment.post_id.title }}**. Ngoài ra lúc code nếu muốn lấy kiểu gì thì mn cứ hỏi chatgpt hoặc xem lỗi nó báo như thế nào rồi fix theo miễn ra đúng là được ^^
**Lưu ý:** trong DTL thì if phải có endif, for phải có endfor nha.

### ⚠️ Chú ý các form trong html
Để submit được form thì phải thêm dòng dưới đây vào dòng đầu tiên của thẻ form:
```html
{% csrf_token %}
```
Giống như hình:  
![Screenshot 2024-11-18 122820](https://github.com/user-attachments/assets/a6522ab7-a14f-436a-9b85-01f4f7160ac6)  

## 😊 Cảm ơn mn! Có gì ko hiểu thì hỏi t nhaaa