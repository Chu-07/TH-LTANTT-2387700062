# Lab 02 – Git Pre-commit Security Hook (GitSecure)

**Sinh viên:** Lê Thị Hồng Thắm — **MSSV:** 2387700062  
**Lớp:** 23DATA1 — **Buổi:** 1 — **Phạm vi:** Mục 1.4 & 1.5 (Xây dựng và Kiểm thử hệ thống GitSecure).

## 1. Mục tiêu
* Hiểu và áp dụng tự động hóa bảo mật (Shift-left security) trong quy trình quản lý mã nguồn.
* Xây dựng hệ thống `GitSecure` bằng Python (chạy dưới dạng pre-commit hook) để tự động quét mã nguồn trước khi `git commit`.
* Ngăn chặn rò rỉ thông tin nhạy cảm (mật khẩu, API key, token...) và cấu hình quyền file không an toàn lọt vào repository.
* Ứng dụng công cụ `bandit` để phân tích tĩnh (SAST) mã nguồn Python.

## 2. Cấu trúc thư mục
```text
TH-LTANTT-2387700062/
└── REPO/
    └── LAB2/
        ├── .githooks/
        │   └── pre-commit              # Script Python xử lý logic quét bảo mật
        ├── pre-commit-hook-test/
        │   └── bad.py                  # File chứa lỗi bảo mật để kiểm thử
        ├── requirements-dev.txt        # Chứa thư viện bandit
        └── README.md                   # Báo cáo thực hành Lab 2
```
*(Lưu ý: Các file `.gitignore` và `gitsecure.log` được quản lý ở thư mục gốc của dự án để áp dụng cho toàn bộ repository).*

## 3. Triển khai GitSecure (Mục 1.4)
Hệ thống hook `.githooks/pre-commit` được viết bằng Python với các tính năng:
- **Quét Regex**: Phát hiện API key, mật khẩu, token bị hardcode (VD: `password = "123456"`).
- **Quét SAST**: Gọi lệnh `bandit -r .` để phân tích các lỗ hổng bảo mật tiềm ẩn trong code.
- **Kiểm tra quyền**: Quét các file có quyền world-writable (được tuỳ chỉnh bỏ qua trên Windows để tránh false-positive).
- **Ghi Log & Chặn**: Nếu có lỗi, ghi thông tin vào `gitsecure.log`, in ra Terminal và chặn tiến trình bằng `sys.exit(1)`.

Cấu hình kích hoạt hook trên môi trường cục bộ:
```bash
git config core.hooksPath REPO/LAB2/.githooks
```

## 4. Kiểm thử và Vận hành (Mục 1.5)
**Kịch bản 1: Bị chặn do vi phạm rò rỉ thông tin (Hardcoded Credentials)**
* Tạo file `pre-commit-hook-test/bad.py` chứa biến thông tin nhạy cảm `password = "123456"`.
* Thực hiện lệnh `git add` và `git commit`.
* **Kết quả**: Tiến trình commit lập tức bị chặn. Terminal hiển thị cảnh báo:
```plaintext
COMMIT BLOCKED by GitSecure:
 - Sensitive info found in REPO/LAB2/pre-commit-hook-test/bad.py: pattern password\s*=\s*['\"][^'\"]{4,}['\"]
```
Toàn bộ lịch sử phát hiện lỗi được ghi vào file `gitsecure.log`. File log này sau đó được khai báo vào `.gitignore` để đảm bảo nhật ký bảo mật không bị đẩy ngược lên kho lưu trữ công khai.

**Kịch bản 2: Khắc phục vi phạm và Commit thành công**
* Tiến hành gỡ bỏ thông tin nhạy cảm trong `bad.py` (xóa biến password hoặc chuyển sang dùng biến môi trường).
* Thực hiện lại lệnh `git add` và `git commit`.
* **Kết quả**: Hệ thống vượt qua toàn bộ khâu kiểm duyệt, thông báo `GitSecure: All checks passed.` và ghi nhận commit hợp lệ vào lịch sử.

## 5. Kết luận
Thông qua Lab 02, em đã nắm vững quy trình triển khai một chốt chặn bảo mật tự động ngay tại máy cá nhân (local environment). Việc kết hợp Pre-commit hook cùng Regex và công cụ SAST (Bandit) giúp phát hiện sớm các rủi ro bảo mật ngay từ khi lập trình viên thao tác đẩy code. Đây là lớp phòng thủ "Shift-Left" hiệu quả, giúp giảm thiểu tối đa nguy cơ rò rỉ dữ liệu nhạy cảm hoặc mã nguồn kém an toàn lên các kho chứa tập trung như GitHub.
