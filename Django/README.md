## Vui lòng không chỉnh sửa hay đụng gì tới mấy cái code t sửa trong thư mục Django này rồi nha 😞. Chỉ được thêm code mới vào hoặc xem thôi

### ⚠️ Chú ý
Thư mục Django này là chỗ chính thức để tụi mình code đồ án (tức là chuyển mấy code php kia sang python thì sẽ làm trong thư mục này khi nào xong hết đồ án thì tụi mình xóa mấy file php bên ngoài thư mục Django này).  
Nhưng mà hiện tại t mới fix bên phía người dùng thôi, còn admin thì chưa; còn về MVC với OOP thì t đang làm giữa chừng chưa xong mà nếu muốn coi web ở mức độ người dùng thì cx coi được rồi á (ngoại trừ trang posts.html với thanh tìm kiếm chưa xong).  

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

**Lưu ý:** Hiện tại database t cũng tích hợp vào luôn rồi, mọi người cứ làm thôi ko cần chạy lệnh makemigrate hay gì đâu, cứ runserver là được. Trong quá trình làm thì ko sửa mấy file trong thư mục models giùm t nha. Backend python làm thường gặp mấy lỗi kiểu gọi thuộc tính của instance gì đó từ database thì mn có thể đọc lỗi python nó báo rồi hỏi chatgpt nó fix được, khum thì tham khảo code của t cũng được.  

Trong thư mục Django/project sẽ có thư mục blog, cert, project; trong đó thư mục Django/project/project là chạy lệnh **django-admin startproject project** mà có (project là tên dự án), thư mục Django/project/blog là chạy lệnh **python manage.py startapp blog** mà có (blog là tên app của mình), còn thư mục Django/project/cert là chỗ chứa chứng chỉ SSL của bên hosting database của mình thôi nên ko cần quan tâm và cũng đừng đụng tới (xóa hay gì là mất kết nối database với python á).  

Lưu ý nhỏ nữa là thường trong lúc code python mà muốn lấy user hiện tại đang dùng web thì chỉ cho gọi theo kiểu:
```bash
user = request.user
```
Nhưng mà trong file Django/project/blog/middleware.py thì t có để code sẵn sẽ cho gọi lấy thẳng id của user hiện tại từ các file code khác bằng cách gọi:
```bash
user_id = request.user_id
```
Giống trong file Django/project/blog/views/base.py (dòng thứ 6):
```python
from django.contrib.auth.models import User

class BaseView:
    def __init__(self, request):
        self.request = request
        self.user_id = request.user.id if request.user.is_authenticated else None
        self.user = User.objects.filter(id=self.user_id).first() if self.user_id else None
        self.user_name = self.user.name if self.user else None
        self.user_email = self.user.email if self.user else None

        self.context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
        }
```

Nên là khi mọi người copy dính dòng code gọi này của t khi hỏi chatgpt thì nó sẽ kêu lỗi nhưng thật ra là ko có lỗi đâu vì đã được code sẵn bên Django/project/blog/middleware.py để gọi rồi á

Tuy nhiên, base.py này chứa class t tính để cho mấy class khác kế thừa (do nó chứa thông tin của user hiện tại duyệt web và bất kì trang nào cũng liên quan đến user nên cần lấy id, name của user để hiện lên header...) => Nhờ cái này mà mấy class kế thừa sau nếu muốn lấy id của user thì chỉ cần gọi:
```bash
self.user_id
```

### 😊 Cảm ơn mn! Có gì ko hiểu thì hỏi t nhaaa