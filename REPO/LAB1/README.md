# 🛡️ Lab 01 – SecureValidator & Kỹ thuật Khai thác Bypass Bộ Lọc

**Thông tin sinh viên:**
- **Họ và tên:** Lê Thị Hồng Thắm
- **MSSV:** 2387700062
- **Lớp:** 23DATA1
- **Buổi:** 1
- **Bài 1:** Cơ sở lập trình bảo mật, kiểm tra đầu vào

---

## 🎯 1. Mục tiêu

- Cài đặt môi trường lập trình Python kết hợp Flask để xây dựng ứng dụng web kiểm thử trực quan.
- Xây dựng thư viện `SecureValidator` nhằm kiểm tra/làm sạch dữ liệu đầu vào: email, URL (chống SSRF), tên file (chống Path Traversal), chuỗi SQL (chống SQL Injection), chuỗi HTML (chống XSS).
- Viết Unit Test cho toàn bộ thư viện bằng module `unittest`.
- **Trọng tâm nâng cao:** Đánh giá rủi ro bảo mật của cơ chế phòng thủ dựa trên danh sách đen (Blacklist) và Biểu thức chính quy (Regex). Thực nghiệm 6 ca kiểm thử (bao gồm 1 ca hợp lệ và 5 phương pháp tấn công bypass) để chứng minh mã độc vẫn có thể lọt qua hệ thống.

---

## 📁 2. Cấu trúc thư mục

```text
TH-LTANTT-2387700062/
└── REPO/
    └── LAB1/
        ├── README.md                   # File báo cáo thực hành bài Lab 1
        └── secure-validator-lab/
            ├── securevalidator/
            │   ├── __init__.py
            │   └── core.py                 # Logic validate/sanitize dữ liệu
            ├── templates/
            │   └── index.html              # Giao diện web
            ├── tests/
            │   ├── __init__.py
            │   └── test_validators.py      # Unit test (unittest)
            ├── app.py                      # Ứng dụng Flask
            └── requirements.txt            # Các thư viện phụ thuộc
```
*(Cấu trúc trên đã ẩn các thư mục `__pycache__` sinh ra tự động trong quá trình biên dịch để hiển thị rõ ràng các thành phần chính của dự án).*

---

## 🛠️ 3. Thư viện `securevalidator/core.py`

| Hàm | Chức năng | Kỹ thuật phòng chống |
| :--- | :--- | :--- |
| `validate_email(email)` | Kiểm tra định dạng email bằng regex `^[\w\.-]+@[\w\.-]+\.\w+$` | Input validation |
| `validate_url(url)` | Parse URL bằng `urllib.parse`, chỉ chấp nhận scheme `http/https` và bắt buộc có `netloc` | Chống SSRF cơ bản |
| `validate_filename(filename)` | Từ chối filename chứa `..`, `/`, `\`; so sánh với `os.path.basename` | Chống Path Traversal |
| `sanitize_sql_input(input_str)` | Loại bỏ ký tự đặc biệt (`-- ; ' " #`) và các từ khoá SQL (`OR, AND, SELECT, INSERT, DELETE, UPDATE, DROP, UNION, WHERE`) | Chống SQL Injection |
| `sanitize_html_input(html_str)` | Escape ký tự HTML bằng `html.escape()` | Chống XSS |

---

## 🚀 4. Cài đặt & Chạy ứng dụng

Di chuyển vào thư mục chứa mã nguồn ứng dụng và cài đặt các thư viện cần thiết:

```bash
cd secure-validator-lab
pip install -r requirements.txt
python app.py
```

Sau đó mở trình duyệt tại `http://127.0.0.1:5000/`, nhập dữ liệu vào các trường Email, URL, Filename, SQL Input, HTML Input và bấm **Xác thực ngay**.

---

## 🧪 5. Unit Test

Chạy bộ kiểm thử tự động để xác nhận các hàm hoạt động đúng theo logic cơ sở:

```bash
cd secure-validator-lab
python -m unittest discover tests
```

Bộ test bao phủ các trường hợp hợp lệ và không hợp lệ cơ bản. 
> **Kết quả mong đợi:** `Ran 10 tests ... OK`

---

## ⚠️ 6. Thực nghiệm 6 Ca Kiểm Thử & Kỹ Thuật Bypass (Báo Cáo Lỗ Hổng)

Mặc dù ứng dụng vượt qua toàn bộ Unit Test ban đầu, việc sử dụng Regex và Blacklist để làm sạch dữ liệu bộc lộ nhiều điểm yếu. Dưới đây là 6 ca thực nghiệm được thực hiện trực tiếp trên giao diện web nhằm đánh giá và vượt mặt (bypass) hoàn toàn các bộ lọc này.

| STT | Kịch bản / Kỹ thuật Bypass | Dữ liệu đầu vào (Payload) | Kết quả nhận được (Hệ thống bị qua mặt) | Giải thích nguyên lý |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Dữ liệu chuẩn hợp lệ**<br>*(Baseline Test)* | - **URL:** `https://hutech.edu.vn`<br>- **File:** `report.pdf`<br>- **SQL:** `' OR 1=1 --`<br>- **HTML:** `<script>alert('XSS')</script>` | - **URL / File:** `True`<br>- **SQL:** `1=1`<br>- **HTML:** `&lt;script&gt;...` | Cấu hình lọc cơ bản hoạt động đúng với dữ liệu sạch và các mẫu tấn công phổ thông được khai báo sẵn trong Regex. |
| **2** | **Lồng từ khóa SQL & XSS Schema** | - **File:** `app.py`<br>- **SQL:** `' OORR 1=1 --`<br>- **HTML:** `javascript:alert(1)` | - **File:** `True`<br>- **SQL:** `OR 1=1`<br>- **HTML:** `javascript:alert(1)` | Hệ thống không lọc SQL đệ quy, `OORR` bị xóa chữ `OR` ở giữa sẽ tái tạo lại thành `OR`. Hàm `html.escape` vô dụng với URI `javascript:` vì không chứa dấu `< >`. Đọc file mã nguồn không bị chặn vì không chứa ký tự `/`. |
| **3** | **SSRF Decimal & Toán tử SQL thay thế** | - **URL:** `http://2130706433`<br>- **File:** `.env`<br>- **SQL:** `1 \|\| 1=1 /*`<br>- **HTML:** `onmouseover=alert(1)` | - **URL:** `True`<br>- **SQL:** `1 \|\| 1=1 /*`<br>- **HTML:** `onmouseover=alert(1)` | Lách kiểm tra SSRF bằng cách chuyển IP `127.0.0.1` sang định dạng số thập phân. Dùng toán tử Boolean `\|\|` thay cho `OR` và `/*` thay cho `--` để chọc thủng Blacklist SQL. |
| **4** | **NTFS ADS & XSS Data URI Base64** | - **URL:** `http://localhost:22`<br>- **File:** `secret.txt:$DATA`<br>- **SQL:** `1 LIKE 1`<br>- **HTML:** `data:text/html;base64,PHNjc...` | - **File:** `True`<br>- **SQL:** `1 LIKE 1`<br>- **HTML:** `data:text/html;base64,...` | Kỹ thuật Data Stream `$DATA` của NTFS trên Windows cho phép truy xuất file ẩn mà không cần dùng ký tự cấm. Base64 giấu toàn bộ mã XSS độc hại khỏi quá trình quét ký tự của hàm `html.escape`. |
| **5** | **IPv6 SSRF & Tên thiết bị Windows** | - **URL:** `http://[::1]:8080`<br>- **File:** `CON`<br>- **SQL:** `1 ORDER BY 5 /*`<br>- **HTML:** `&#x6A;&#x61;...alert(1)` | - **URL / File:** `True`<br>- **SQL:** `1 ORDER BY 5 /*`<br>- **HTML:** `&#x6A;...` | IPv6 giúp vượt qua các bộ lọc chỉ chặn IPv4 cục bộ. `CON` là tên thiết bị ảo trên Windows, gọi vào có thể gây DoS. Lệnh `ORDER BY` bị bỏ sót giúp hacker thực thi Error-based SQL. |
| **6** | **SQL Toán học & CSS Injection** | - **URL:** `http://admin:123@127.0.0.1`<br>- **File:** `boot.ini`<br>- **SQL:** `1 / 0 /*`<br>- **HTML:** `style=background-image:url(...)` | - **URL:** `True`<br>- **SQL:** `1 / 0 /*`<br>- **HTML:** `style=...` | Ép DB thực thi phép chia cho 0 để gây từ chối dịch vụ. Nhúng mã độc XSS qua thuộc tính CSS không dùng dấu nháy HTML nên lọt qua hàm mã hóa hoàn toàn. |

---

## 📝 7. Kết luận

Bài thực hành hoàn thiện việc xây dựng một thư viện kiểm tra đầu vào cơ bản và tích hợp thành công trên nền tảng web Flask. Tuy nhiên, qua 6 thực nghiệm bypass, có thể kết luận rằng phương pháp tiếp cận theo hướng "Blacklist" (Danh sách đen) và Regex thô sơ là không đủ độ tin cậy để bảo vệ ứng dụng thực tế. Kẻ tấn công luôn tìm ra những cú pháp thay thế hoặc tận dụng đặc tả của hệ điều hành và giao thức mạng để qua mặt bộ lọc.

> **💡 Khuyến nghị:** Trong các dự án bảo mật tiếp theo, cần chuyển đổi sang nguyên tắc **Whitelist** (danh sách trắng), sử dụng Parameterized Queries/Prepared Statements để ngừa SQL Injection triệt để, và ứng dụng các bộ thư viện sanitizer chuyên nghiệp (như Bleach) để làm sạch HTML DOM.
