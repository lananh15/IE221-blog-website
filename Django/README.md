## Vui lòng không chỉnh sửa hay đụng gì tới mấy cái code t sửa trong đây rồi nha 😞. Chỉ được thêm code mới vào hoặc xem thôi

### ⚠️ Chú ý
Thư mục Django này là chỗ chính thức để tụi mình code đồ án (tức là chuyển mấy code php kia sang python thì sẽ làm trong thư mục này khi nào xong hết đồ án thì tụi mình xóa mấy file php bên ngoài thư mục Django này).  
Nhưng mà hiện tại t mới fix bên phía người dùng thôi, còn admin thì chưa; còn về MVC với OOP thì t đang làm giữa chừng chưa xong mà nếu muốn coi web ở mức độ người dùng thì cx coi được rồi á (ngoại trừ trang posts.html với thanh tìm kiếm chưa xong).  

### Xem web với code Python mới ✨
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

### 😊 Cảm ơn mn!