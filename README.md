# 🛢 Database
Sử dụng database (đã có hosting) dùng chung cho nhóm.

## Tải XAMPP hoặc Laragon để sử dụng phpMyAdmin:
phpMyAdmin cung cấp một giao diện quản lý cơ sở dữ liệu đầy đủ, cho phép bạn quản lý bất kỳ bảng nào trong cơ sở dữ liệu, thực hiện truy vấn SQL, xem cấu trúc bảng, và có quyền truy cập hoàn toàn vào cơ sở dữ liệu
- Tải XAMPP tại: https://www.apachefriends.org/download.html
- Tải Laragon tại: https://laragon.org/download/  
Bạn dùng XAMPP vẫn được, nhưng nếu trong quá trình làm mà XAMPP gặp lỗi hay vấn đề gì khó giải quyết thì có thể cân nhắc dùng Laragon vì tính ổn định của Laragon nha.

## Thiết lập phpMyAdmin:
### Đối với XAMPP:
Đầu tiên vào folder xampp đã tải, tìm và mở folder phpMyAdmin, trong đó tìm tiếp file **config.inc.php** rồi mở file lên:  
![Screenshot 2024-11-03 211805](https://github.com/user-attachments/assets/abcb236c-a060-4255-b2ff-20f74c84e9b2)  
Sau đó, thêm đoạn mã dưới đây vào dưới cùng của file **config.inc.php**:
```php
/**
 * End of servers configuration
 */
$i++;
// nhom2 server connection
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['user'] = 'avnadmin';
$cfg['Servers'][$i]['password'] = 'AVNS_rJlKFXve7NFmsh7WIVB';
$cfg['Servers'][$i]['extension'] = 'mysqli';
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['Servers'][$i]['host'] = 'mysql-dev-blog-lananhngo685-dev-blog.h.aivencloud.com';
$cfg['Servers'][$i]['port'] = 14981;
$cfg['Lang'] = '';
```
Sau khi thêm thì lưu file lại, rồi lên Chrome gõ url: http://localhost/phpmyadmin  
  
Đăng nhập với các thông tin sau:
- **Username**: avnadmin
- **Password**: AVNS_rJlKFXve7NFmsh7WIVB
- **Chọn server**: mysql-dev-blog-lananhngo685-dev-blog.h.aivencloud.com như hình dưới:
![Screenshot 2024-11-03 164559](https://github.com/user-attachments/assets/a581acbe-4e9a-47d5-93aa-7b4bcd9d4438)  

Đăng nhập vào xong sẽ hiển thị hình dưới và có sẵn các table trong database (lưu ý chỉ chú ý 5 table là admin, comments, likes, posts, users):  
![Screenshot 2024-11-03 223421](https://github.com/user-attachments/assets/26811936-fa64-46f0-a3bc-0de9cfdac4e4)  

Khi làm thì ko cần tạo database nữa, nếu cần thiết thì chỉ tạo thêm table trong defaultdb là tiếp tục code được, tham khảo link https://hocwebchuan.com/tutorial/php/phpmyadmin_create_table.php#google_vignette để tạo table (defaultdb là tên database mà bên hosting free họ đặt).  

### Đối với Laragon:
Do Laragon không được cài đặt sẵn phpMyAdmin nên cần phải cài đặt thêm phpMyAdmin vào. Xem đường link sau để có thể thêm được phpMyAdmin vào Laragon:
https://tientv.com/web-design/huong-dan-them-phpmyadmin-vao-laragon.html

Sau khi thêm phpMyAdmin thành công thì tìm và mở folder phpMyAdmin, trong đó tìm tiếp file **config.inc.php** rồi mở file lên:
![Screenshot 2024-11-03 214637](https://github.com/user-attachments/assets/d4b5fec4-5846-4c3b-b419-21952f9b498c)  

Sau đó thiết lập giống như XAMPP phía trên là được.