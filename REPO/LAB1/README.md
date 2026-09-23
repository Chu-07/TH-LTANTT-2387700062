# Lab 01 – SecureValidator & Kỹ thuật Khai thác Bypass Bộ Lọc

**Sinh viên:** Lê Thị Hồng Thắm — **MSSV:** 2387700062  
**Trường:** Đại học Công Nghệ Tp.HCM - HUTECH — **Lớp:** 23DATA1  
**Buổi:** 1 — **Bài 1:** Cơ sở lập trình bảo mật, kiểm tra đầu vào  

---

## 1. Mục tiêu

* Cài đặt môi trường lập trình Python kết hợp Flask để xây dựng ứng dụng web kiểm thử trực quan.
* Xây dựng thư viện `SecureValidator` nhằm kiểm tra/làm sạch dữ liệu đầu vào: email, URL (chống SSRF), tên file (chống Path Traversal), chuỗi SQL (chống SQL Injection), chuỗi HTML (chống XSS).
* Viết Unit Test cho toàn bộ thư viện bằng module `unittest`.
* **Trọng tâm nâng cao:** Đánh giá rủi ro bảo mật của cơ chế phòng thủ dựa trên danh sách đen (Blacklist) và Biểu thức chính quy (Regex). Thực nghiệm 7 ca kiểm thử để chứng minh mã độc vẫn có thể lọt qua hệ thống.

---

## 2. Cấu trúc thư mục

```text
TH-LTANTT-2387700062/
└── REPO/
    └── LAB1/
        ├── image/                      # Thư mục chứa hình ảnh minh chứng kiểm thử
        │   ├── run.png
        │   ├── ca1-1.png, ca1-2.png
        │   ├── ca2-1.png, ca2-2.png
        │   ├── ca3-1.png, ca3-2.png
        │   ├── ca4-1.png, ca4-2.png
        │   ├── ca5-1.png, ca5-2.png
        │   ├── ca6-1.png, ca6-2.png
        │   └── ca7-1.png, ca7-2.png
        ├── README.md                   # Báo cáo thực hành Lab 1
        └── secure-validator-lab/
            ├── securevalidator/
            │   ├── __init__.py
            │   └── core.py                 
            ├── templates/
            │   └── index.html              
            ├── tests/
            │   ├── __init__.py
            │   └── test_validators.py      
            ├── app.py                      
            └── requirements.txt            
```

---

## 3. Thư viện `securevalidator/core.py`

| Hàm | Chức năng | Kỹ thuật phòng chống |
| :--- | :--- | :--- |
| `validate_email(email)` | Kiểm tra định dạng email bằng regex `^[\w\.-]+@[\w\.-]+\.\w+$` | Input validation |
| `validate_url(url)` | Parse URL bằng `urllib.parse`, chỉ chấp nhận `http`/`https` | Chống SSRF cơ bản |
| `validate_filename(filename)` | Từ chối filename chứa `..`, `/`, `\`; so sánh với basename | Chống Path Traversal |
| `sanitize_sql_input(input_str)` | Loại bỏ ký tự đặc biệt và các từ khoá SQL cơ bản | Chống SQL Injection |
| `sanitize_html_input(html_str)` | Escape ký tự HTML bằng `html.escape()` | Chống XSS |

---

## 4. Cài đặt & Chạy ứng dụng

Di chuyển vào thư mục dự án, cài đặt thư viện và khởi chạy Flask:

```bash
cd secure-validator-lab
pip install -r requirements.txt
python app.py
```

Ứng dụng sẽ chạy tại `http://127.0.0.1:5000` và liên tục ghi nhận các yêu cầu truy vấn (POST/GET) đẩy về máy chủ.

![Terminal Flask Server](image/run.png)  
*Hình: Giao diện Terminal hiển thị máy chủ Flask đang hoạt động và nhận các request kiểm thử.*

---

## 5. Thực nghiệm 7 Ca Kiểm Thử & Kỹ Thuật Bypass (Báo Cáo Lỗ Hổng)

### Ca 1: Dữ liệu chuẩn hợp lệ (Baseline Test)
* **Mục đích:** Chứng minh hệ thống chấp nhận dữ liệu sạch, các hàm lọc chuỗi SQL và mã hóa HTML hoạt động bình thường.
* **Payload:**
  * **Email:** `hongphuoc@gmail.com`
  * **URL:** `https://www.hutech.edu.vn`
  * **Filename:** `report.pdf`
  * **SQL Input:** `' OR 1=1 --`
  * **HTML Input:** `<script>alert('XSS')</script>`

![Ca 1 - Giao diện nhập liệu](image/ca1-1.png)  
*Hình: Dữ liệu đầu vào chuẩn xác.*

![Ca 1 - Kết quả](image/ca1-2.png)  
*Hình: Trả về True cho dữ liệu hợp lệ; SQL được cắt lọc còn 1=1 và HTML được escape thành &lt;script&gt; đúng theo quy tắc.*

---

### Ca 2: Lồng từ khóa SQL & XSS Schema URL
* **Mục đích:** Vượt qua Regex bằng cách lồng ghép từ khóa (`OORR`) và sử dụng giao thức không chứa dấu `< >`.
* **Payload:**
  * **Email:** `hongphuoc@gmail.com`
  * **URL:** `https://www.hutech.edu.vn`
  * **Filename:** `app.py`
  * **SQL Input:** `' OORR 1=1 --`
  * **HTML Input:** `javascript:alert(1)`

![Ca 2 - Giao diện nhập liệu](image/ca2-1.png)  
*Hình: Nhập mã độc lồng ghép.*

![Ca 2 - Kết quả](image/ca2-2.png)  
*Hình: Hệ thống bị bypass, giữ nguyên chuỗi OORR 1=1 và javascript:alert(1) mà không hề mã hóa hay lọc bỏ.*

---

### Ca 3: Bypass SSRF Decimal & Toán tử SQL thay thế
* **Mục đích:** Đánh lừa hàm kiểm tra URL bằng IP dạng thập phân và lách Blacklist SQL bằng toán tử logic khác.
* **Payload:**
  * **Email:** `tham@hutech.edu.vn`
  * **URL:** `http://2130706433` *(Đại diện cho 127.0.0.1 dạng số thập phân)*
  * **Filename:** `.env`
  * **SQL Input:** `1 || 1=1 /*`
  * **HTML Input:** `onmouseover=alert(1)`

![Ca 3 - Giao diện nhập liệu](image/ca3-1.png)  
*Hình: Cố tình sử dụng IP Decimal và toán tử thay thế (Lưu ý: Có dư dấu ] trong URL).*

![Ca 3 - Kết quả](image/ca3-2.png)  
*Hình: SQL và HTML hoàn toàn lách được bộ lọc; URL trả về False do dư ký tự ] trong lúc nhập liệu.*

---

### Ca 4: Khai thác luồng dữ liệu NTFS ADS & XSS Data URI Base64
* **Mục đích:** Đọc file ẩn trên Windows không cần ký tự gạch chéo và giấu mã độc XSS bằng chuẩn Base64.
* **Payload:**
  * **Email:** `hacker@gmail.com`
  * **URL:** `http://localhost:22`
  * **Filename:** `secret.txt:$DATA`
  * **SQL Input:** `1 LIKE 1`
  * **HTML Input:** `data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==`

![Ca 4 - Giao diện nhập liệu](image/ca4-1.png)  
*Hình: Giao diện nhập liệu khai thác NTFS ADS và XSS Data URI Base64.*

![Ca 4 - Kết quả](image/ca4-2.png)  
*Hình: Kết quả hệ thống chấp nhận filename chứa NTFS ADS và dữ liệu Base64 không bị lọc.*

---

### Ca 5: Bypass bằng IPv6 SSRF, Tên thiết bị Windows & SQL ORDER BY
* **Mục đích:** Lách bộ lọc IPv4 cục bộ, thử đọc tên phần cứng ảo trên Windows (có thể gây DoS) và dùng lệnh SQL bị bỏ sót.
* **Payload:**
  * **Email:** `root@localhost`
  * **URL:** `http://[::1]:8080`
  * **Filename:** `CON`
  * **SQL Input:** `1 ORDER BY 5 /*`
  * **HTML Input:** `&#x6A;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x3A;alert(1)` *(Mã hóa HTML Entities Hex)*

![Ca 5 - Giao diện nhập liệu](image/ca5-1.png)  
*Hình: Giao diện nhập liệu kiểm thử IPv6 SSRF, thiết bị đặc biệt CON và SQL ORDER BY.*

![Ca 5 - Kết quả](image/ca5-2.png)  
*Hình: Hệ thống không chặn thiết bị ảo CON và lệnh SQL ORDER BY lọt qua hoàn toàn.*

---

### Ca 6: Xác thực Basic Auth, DoS Toán học SQL & CSS Injection
* **Mục đích:** Gây lỗi cơ sở dữ liệu bằng phép tính chia cho 0 và nhúng mã độc qua thuộc tính CSS hoàn toàn không dùng nháy kép hay thẻ HTML.
* **Payload:**
  * **Email:** `admin@192.168.1.254`
  * **URL:** `http://admin:123456@127.0.0.1/admin-panel`
  * **Filename:** `boot.ini`
  * **SQL Input:** `1 / 0 /*`
  * **HTML Input:** `style=background-image:url(javascript:alert(1))`

![Ca 6 - Giao diện nhập liệu](image/ca6-1.png)  
*Hình: Giao diện nhập liệu kiểm thử Basic Auth URL, SQL chia cho 0 và CSS Injection.*

![Ca 6 - Kết quả](image/ca6-2.png)  
*Hình: Phép toán gây lỗi SQL và thuộc tính CSS chứa javascript hoàn toàn không bị mã hóa.*

---

### Ca 7: URL Authority Spoofing, Path Traversal (URL Encoding) & SQL Comment Obfuscation
* **Mục đích:** Lợi dụng việc hệ thống kiểm tra dữ liệu trước, nhưng lại giải mã (decode) sau. Đánh lừa trình phân tích URL bằng cú pháp xác thực và bẻ gãy từ khóa SQL bằng ký tự chú thích.
* **Payload:**
  * **Email:** `admin@hutech.edu.vn.evil.com`
  * **URL:** `https://hutech.edu.vn@evil.com`
  * **Filename:** `%2e%2e%2f%2e%2e%2fetc%2fpasswd`
  * **SQL Input:** `U/**/NION S/**/ELECT 1,2 /*`
  * **HTML Input:** `autofocus onfocus=alert(1)`

![Ca 7 - Giao diện nhập liệu](image/ca7-1.png)  
*Hình: Giao diện nhập liệu giả mạo URL authority, Path Traversal dạng URL Encoding và SQL comment obfuscation.*

![Ca 7 - Kết quả](image/ca7-2.png)  
*Hình: URL và Path Traversal encoded lách qua hàm kiểm tra thành công.*

---

## 6. Kết luận

Qua 7 thực nghiệm bypass, có thể kết luận rằng phương pháp tiếp cận theo hướng "Blacklist" (Danh sách đen) và Regex thô sơ là không đủ độ tin cậy. Kẻ tấn công luôn tìm ra những cú pháp thay thế hoặc tận dụng đặc tả của hệ điều hành, giao thức mạng, và cơ chế Encoding (Mã hóa URL/Base64/Hex) để qua mặt bộ lọc. Trong thực tế, cần áp dụng Whitelist, Prepared Statements, và các bộ thư viện Sanitizer chuyên sâu.
