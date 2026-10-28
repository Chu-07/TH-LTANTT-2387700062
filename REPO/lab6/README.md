# LAB 06 – BẢO MẬT VỚI DEVSECOPS

> **Sinh viên:** Lê Thị Hồng Thắm<br>
> **MSSV:** 2387700062<br>
> **Trường:** Đại học Công nghệ TP.HCM (HUTECH)<br>
> **Khoa:** Công nghệ Thông tin<br>
> **Môn học:** Lập trình An ninh Thông tin

## Mục lục

- [1. Giới thiệu](#1-giới-thiệu)
- [2. Công nghệ và môi trường thực hiện](#2-công-nghệ-và-môi-trường-thực-hiện)
- [3. Cấu trúc thư mục](#3-cấu-trúc-thư-mục)
- [4. Bài 6.2.1 – Thiết kế và kiểm thử CI/CD pipeline](#4-bài-621--thiết-kế-và-kiểm-thử-cicd-pipeline)
- [5. Bài 6.2.2 – Docusaurus và tự động hóa triển khai](#5-bài-622--docusaurus-và-tự-động-hóa-triển-khai)
- [6. Kiểm tra artifacts và tính toàn vẹn](#6-kiểm-tra-artifacts-và-tính-toàn-vẹn)
- [7. Tổng hợp kết quả thực hành](#7-tổng-hợp-kết-quả-thực-hành)
- [8. Khó khăn và cách khắc phục](#8-khó-khăn-và-cách-khắc-phục)
- [9. Kết luận](#9-kết-luận)
- [10. Tài liệu tham khảo](#10-tài-liệu-tham-khảo)

## 1. Giới thiệu

Lab 06 trình bày cách tổ chức quy trình tích hợp và phân phối liên tục (CI/CD), từ pipeline gồm các bước Build, Test và Deploy đến quá trình build website tĩnh và chuyển artifact sang môi trường triển khai. Nội dung thực hành ban đầu được thiết kế cho GitLab CI/CD và GitLab Pages; do việc chạy CI trên GitLab gặp giới hạn xác minh tài khoản và runner, hai project được giữ nguyên cấu hình GitLab để đối chiếu, đồng thời bổ sung GitHub Actions và GitHub Pages.

DevSecOps đưa các hoạt động bảo mật vào xuyên suốt vòng đời phát triển phần mềm. Một pipeline an toàn cần kiểm soát quyền truy cập, bảo vệ secrets, ghi log, kiểm tra mã và dependencies, bảo vệ runner, đồng thời bảo đảm artifact được chuyển giao nguyên vẹn. CI/CD hỗ trợ mục tiêu này bằng cách biến Build, Test và Deploy thành các bước lặp lại được, có thứ tự, có log và dừng sớm khi xảy ra lỗi.

### Mục tiêu học tập

- Hiểu cấu trúc stage/job của một pipeline CI/CD.
- Thiết lập quan hệ phụ thuộc và chạy song song giữa các job.
- Tự động build website Docusaurus bằng Node.js và npm.
- Lưu, chuyển giao và triển khai static artifact.
- Cấu hình GitHub Actions và GitHub Pages bằng các action chính thức.
- Kiểm tra tính toàn vẹn giữa `build/` và `public/` bằng SHA-256.
- Phân biệt kết quả kiểm thử local với kết quả thực thi trên nền tảng CI/CD.

## 2. Công nghệ và môi trường thực hiện

| Công nghệ | Vai trò | Phiên bản xác minh từ project/máy thực hành |
|---|---|---|
| Git | Quản lý phiên bản và đồng bộ repository | 2.52.0.windows.1 |
| GitHub | Lưu trữ hai repository sau khi chuyển đổi | Repository `Chu-07/Lab06-621-LeThiHongTham` và `Chu-07/Lab06-622-LeThiHongTham` |
| GitHub Actions | Chạy workflow bằng GitHub-hosted Ubuntu runner | Workflow dùng `ubuntu-latest` |
| GitHub Pages | Đích triển khai website tĩnh | Cấu hình bằng Pages artifact và deployment environment |
| Node.js | Runtime của Docusaurus | Máy local: v24.21.0; workflow: Node.js 22 |
| npm | Cài dependencies và chạy scripts | Máy local: 11.19.0 |
| Docusaurus | Xây dựng website tĩnh React | 3.10.2 |
| Visual Studio Code | Soạn thảo mã và chạy terminal | 1.143.1 |
| PowerShell | Chạy lệnh kiểm thử trên Windows | Phiên bản không được ghi nhận trong minh chứng |
| GitLab CI/CD | Nền tảng pipeline ban đầu theo tài liệu lab | Cấu hình được giữ trong `.gitlab-ci.yml` |

## 3. Cấu trúc thư mục

Các thư mục sinh tự động như `node_modules/`, `build/`, `public/` và `.docusaurus/` được loại khỏi cây dưới đây.

```text
Lab06_LeThiHongTham_2387700062/
├── 6.2.1/
│   ├── .github/
│   │   └── workflows/
│   │       └── basic-pipeline.yml
│   └── .gitlab-ci.yml
├── 6.2.2/
│   ├── .github/
│   │   └── workflows/
│   │       └── deploy-pages.yml
│   ├── pipelines/
│   │   ├── 01-basic.yml
│   │   ├── 02-build.yml
│   │   └── 03-pages.yml
│   ├── src/
│   │   ├── css/
│   │   │   └── custom.css
│   │   └── pages/
│   │       ├── index.js
│   │       └── index.module.css
│   ├── static/
│   │   └── img/
│   │       └── favicon.svg
│   ├── .gitignore
│   ├── .gitlab-ci.yml
│   ├── docusaurus.config.js
│   ├── package.json
│   └── package-lock.json
├── image/
│   └── 24 ảnh chụp màn hình minh chứng
├── scripts/
│   └── check-readme-images.ps1
└── README.md
```

## 4. Bài 6.2.1 – Thiết kế và kiểm thử CI/CD pipeline

### 4.1. Mục tiêu

Bài 6.2.1 mô phỏng pipeline gồm ba giai đoạn `build`, `test`, `deploy` với bốn job: `build-job`, `test-job1`, `test-job2` và `deploy-prod`. Job kiểm thử thứ hai chờ 20 giây để minh họa tác vụ có thời gian xử lý dài hơn; job deploy chỉ in thông báo và không triển khai production thật.

### 4.2. Cấu hình GitLab CI/CD ban đầu

File `6.2.1/.gitlab-ci.yml` giữ đúng cấu trúc trong tài liệu: hai job test thuộc cùng stage nên có thể chạy song song, còn stage deploy chỉ bắt đầu khi stage test thành công.

```yaml
stages: [build, test, deploy]

test-job2:
  stage: test
  script:
    - echo "This job tests something, but takes more time than test-job1."
    - sleep 20

deploy-prod:
  stage: deploy
  script:
    - echo "This job deploys something from the $CI_COMMIT_BRANCH branch."
  environment: production
```

![Hình 6.1 - Nội dung pipeline GitLab của bài 6.2.1](<./image/Ảnh chụp màn hình 2026-10-28 132222.png>)

**Hình 6.1 – Cấu hình ba stage và bốn job trong `.gitlab-ci.yml`.**

Mã nguồn đã được khởi tạo Git và đẩy lên repository GitLab ban đầu. Ảnh dưới đây xác nhận file cấu hình đã xuất hiện trên nhánh `main`; biểu tượng trạng thái màu đỏ cho thấy pipeline GitLab không phải là bằng chứng chạy thành công.

![Hình 6.2 - Repository GitLab của bài 6.2.1](<./image/Ảnh chụp màn hình 2026-10-28 134040.png>)

**Hình 6.2 – Repository GitLab sau khi push cấu hình pipeline.**

### 4.3. Chuyển sang GitHub Actions

GitLab yêu cầu bổ sung bước xác minh tài khoản trước khi sử dụng đầy đủ CI jobs, trong khi project không có project runner sẵn sàng. Vì vậy, project được chuyển sang GitHub Actions để tiếp tục thực hành trên GitHub-hosted runner. Cấu hình GitLab vẫn được giữ lại để so sánh.

[Repository bài 6.2.1 trên GitHub](https://github.com/Chu-07/Lab06-621-LeThiHongTham)

Workflow `6.2.1/.github/workflows/basic-pipeline.yml` chạy khi push lên `main` hoặc khi người dùng chọn **Run workflow**. Quan hệ thực thi được biểu diễn bằng `needs`:

```yaml
test-job1:
  needs: build-job

test-job2:
  needs: build-job

deploy-prod:
  needs: [test-job1, test-job2]
```

Luồng phụ thuộc:

```text
build-job
   ├── test-job1 ──┐
   └── test-job2 ──┴── deploy-prod
```

| Job | Chức năng |
|---|---|
| `build-job` | Chạy trên Ubuntu runner và in tên người kích hoạt workflow qua `$GITHUB_ACTOR`. |
| `test-job1` | Chạy sau `build-job`, in thông báo kiểm thử. |
| `test-job2` | Chạy sau `build-job`, song song với `test-job1`, ghi log và `sleep 20`. |
| `deploy-prod` | Chỉ chạy khi cả hai test job thành công; in tên nhánh qua `$GITHUB_REF_NAME`, không deploy thật. |

### 4.4. Kiểm thử đã thực hiện

Các lệnh tương đương đã được chạy thủ công trong PowerShell để kiểm tra nội dung echo, biến mô phỏng, thời gian chờ và thứ tự Build → Test → Deploy. Đây là **kiểm thử local**, không thay thế cho kết quả GitHub Actions.

![Hình 6.3 - Mô phỏng local các bước build và test](<./image/Ảnh chụp màn hình 2026-10-28 141113.png>)

**Hình 6.3 – Log kiểm thử local cho stage Build, hai tác vụ Test và thời gian chờ 20 giây.**

![Hình 6.4 - Mô phỏng local bước deploy](<./image/Ảnh chụp màn hình 2026-10-28 141138.png>)

**Hình 6.4 – Log local của bước Deploy mô phỏng trên nhánh `main`.**

Git remote `github` đã trỏ đến repository nêu trên và commit `67cb509` trên `main` đã có trên remote. Tuy nhiên, bộ ảnh hiện có không chứa trang GitHub Actions hoặc log của bốn job. Repository cũng không truy cập được qua API công khai tại thời điểm kiểm tra, nên README **không khẳng định workflow GitHub Actions đã Success**.

Ảnh GitLab cho thấy project không có project runner được gán, phù hợp với việc pipeline GitLab không thể dùng làm minh chứng hoàn tất.

![Hình 6.5 - GitLab không có project runner](<./image/Ảnh chụp màn hình 2026-10-28 142738.png>)

**Hình 6.5 – Mục Runners của GitLab hiển thị “No project runners found”.**

### 4.5. Cách chạy workflow trên GitHub

1. Mở repository bài 6.2.1 và chọn tab **Actions**.
2. Chọn workflow **Basic CI/CD**.
3. Chọn **Run workflow**, nhánh `main`, rồi xác nhận chạy.
4. Kiểm tra `build-job` hoàn tất trước; `test-job1` và `test-job2` chạy sau build và có thể chạy đồng thời.
5. Xác nhận `deploy-prod` chỉ bắt đầu khi cả hai test job đều thành công.
6. Mở log từng job và chụp màn hình kết quả thực tế trước khi ghi nhận trạng thái Success trong báo cáo.

## 5. Bài 6.2.2 – Docusaurus và tự động hóa triển khai

### 5.1. Mục tiêu và cấu trúc project

Bài 6.2.2 xây dựng website Docusaurus, kiểm thử trên máy local, tạo production build, lưu artifact và triển khai website tĩnh. Project sử dụng Docusaurus 3.10.2, React 19 và Node.js từ phiên bản 20 trở lên. Mã giao diện nằm trong `src/`, tài nguyên tĩnh nằm trong `static/`, còn `package-lock.json` khóa phiên bản dependencies để `npm ci` tái tạo môi trường nhất quán.

Các script chính:

```powershell
npm ci
npm run start
npm run build
npm run serve
```

| Lệnh | Chức năng |
|---|---|
| `npm ci` | Cài đúng dependency tree trong `package-lock.json`, phù hợp cho CI. |
| `npm run start` | Chạy development server, hỗ trợ cập nhật nhanh khi sửa mã. |
| `npm run build` | Tạo production static files trong `build/`; lệnh trả lỗi sẽ dừng workflow. |
| `npm run serve` | Phục vụ nội dung đã build để kiểm tra gần với production. |

### 5.2. Kiểm thử website local

Development server đã biên dịch thành công và chạy tại `http://localhost:3000/`.

![Hình 6.6 - Development server Docusaurus](<./image/Ảnh chụp màn hình 2026-10-28 141644.png>)

**Hình 6.6 – `npm run start` khởi động Docusaurus và biên dịch client thành công.**

![Hình 6.7 - Website Docusaurus trên localhost 3000](<./image/Ảnh chụp màn hình 2026-10-28 141217.png>)

**Hình 6.7 – Giao diện Lab 06 hoạt động trên development server.**

Production build cũng được phục vụ tại `http://localhost:3001/` để kiểm tra HTML, CSS và JavaScript sau khi build.

![Hình 6.8 - Production website trên localhost 3001](<./image/Ảnh chụp màn hình 2026-10-28 141807.png>)

**Hình 6.8 – Giao diện website khi phục vụ bản production local.**

### 5.3. Build production

Lệnh `npm run build` đã biên dịch thành công cả Client và Server, sau đó tạo static files trong `build/`.

![Hình 6.9 - Kết quả npm run build](<./image/Ảnh chụp màn hình 2026-10-28 141531.png>)

**Hình 6.9 – Docusaurus báo tạo static files trong `build/` thành công.**

File `build/index.html` tồn tại cùng các thư mục assets, images, trang 404 và sitemap.

![Hình 6.10 - Nội dung thư mục build](<./image/Ảnh chụp màn hình 2026-10-28 141549.png>)

**Hình 6.10 – Kiểm tra cấu trúc `build/` và xác nhận `index.html` tồn tại.**

![Hình 6.11 - Số lượng file trong build](<./image/Ảnh chụp màn hình 2026-10-28 141616.png>)

**Hình 6.11 – Thư mục production build có 11 file tại thời điểm kiểm thử.**

### 5.4. Pipeline GitLab ban đầu

File `6.2.2/.gitlab-ci.yml` có hai stage. `build-job` chạy `npm ci`, `npm run build` và lưu `build/`; job `pages` nhận artifact, chuyển thành `public/` và khai báo GitLab Pages.

![Hình 6.12 - Pipeline GitLab build và pages](<./image/Ảnh chụp màn hình 2026-10-28 141952.png>)

**Hình 6.12 – Cấu hình GitLab CI/CD ban đầu cho build và deploy Pages.**

Ba phiên bản theo tiến trình của tài liệu được lưu tại `6.2.2/pipelines/`: job cơ bản, job build có artifact, và pipeline build + Pages.

### 5.5. Workflow GitHub Actions và GitHub Pages

[Repository bài 6.2.2 trên GitHub](https://github.com/Chu-07/Lab06-622-LeThiHongTham)

Workflow `6.2.2/.github/workflows/deploy-pages.yml` gồm hai job:

1. **`build`:** checkout mã nguồn, cài Node.js 22, chạy `npm ci`, build website, kiểm tra `build/index.html`, rồi upload Pages artifact.
2. **`deploy`:** phụ thuộc `build`, sử dụng `actions/deploy-pages@v4`, triển khai artifact vào environment `github-pages` và xuất URL qua `page_url`.

```yaml
permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
```

`docusaurus.config.js` đọc `GITHUB_REPOSITORY` khi biến `GITHUB_PAGES=true`, từ đó tạo:

```text
url:     https://chu-07.github.io
baseUrl: /Lab06-622-LeThiHongTham/
```

Cơ chế này giúp các đường dẫn CSS, JavaScript và static assets có tiền tố repository khi chạy trên project Pages, đồng thời vẫn dùng `baseUrl: /` khi chạy local.

Địa chỉ dự kiến: [https://chu-07.github.io/Lab06-622-LeThiHongTham/](https://chu-07.github.io/Lab06-622-LeThiHongTham/)

Tại thời điểm kiểm tra README, URL trên trả về HTTP 404 và không có ảnh GitHub Actions/GitHub Pages trong thư mục minh chứng. Do đó, trạng thái deploy trên GitHub Pages được ghi là **chưa xác minh thành công**.

### 5.6. Cách chạy và kiểm tra GitHub Pages

1. Vào **Settings → Pages** của repository bài 6.2.2 và chọn nguồn **GitHub Actions**.
2. Mở tab **Actions**, chọn workflow **Build & Deploy**, rồi chạy trên `main`.
3. Trong job `build`, kiểm tra các bước `npm ci`, `npm run build`, kiểm tra `build/index.html` và upload Pages artifact đều thành công.
4. Trong job `deploy`, kiểm tra environment `github-pages` và URL do `actions/deploy-pages` trả về.
5. Mở URL, hard refresh trình duyệt và kiểm tra trang chủ, CSS, JavaScript, favicon cùng các liên kết nội bộ.
6. Chụp workflow graph, log upload artifact, job deploy và website thực tế để bổ sung bằng chứng.

## 6. Kiểm tra artifacts và tính toàn vẹn

Trong kiểm thử local, nội dung `build/` được sao chép sang `public/`. File `public/index.html` được kiểm tra tồn tại trước khi so sánh.

![Hình 6.13 - Sao chép build sang public](<./image/Ảnh chụp màn hình 2026-10-28 142230.png>)

**Hình 6.13 – Tạo `public/` từ production build và xác nhận `public/index.html`.**

![Hình 6.14 - Nội dung thư mục public](<./image/Ảnh chụp màn hình 2026-10-28 142242.png>)

**Hình 6.14 – Cấu trúc `public/` sau khi sao chép từ `build/`.**

PowerShell duyệt từng file trong `build/`, tính SHA-256 cho file nguồn và file có cùng đường dẫn tương đối trong `public/`, sau đó ghi nhận thuộc tính `Match`.

![Hình 6.15 - Script so sánh SHA-256](<./image/Ảnh chụp màn hình 2026-10-28 142318.png>)

**Hình 6.15 – Quy trình tính và so sánh SHA-256 giữa hai thư mục.**

![Hình 6.16 - Kết quả kiểm tra SHA-256](<./image/Ảnh chụp màn hình 2026-10-28 142323.png>)

**Hình 6.16 – Kết quả 11/11 file có hash trùng khớp và `public/` không có file thừa.**

SHA-256 tạo dấu vân tay cố định cho nội dung file. Hai hash giống nhau cho thấy file được sao chép mà không thay đổi bit; một khác biệt nhỏ trong nội dung sẽ tạo hash khác. Việc xác minh này giúp phát hiện artifact bị hỏng hoặc bị thay đổi ngoài ý muốn trong quá trình chuyển giao, qua đó hỗ trợ tính toàn vẹn của chuỗi cung ứng phần mềm.

Kết quả trên chỉ áp dụng cho bản sao `build/` → `public/` trên máy local. Nó không chứng minh Pages artifact trên GitHub Actions giống hoàn toàn với local build, vì chưa có hash hoặc log artifact từ workflow GitHub để đối chiếu.

## 7. Tổng hợp kết quả thực hành

| Nội dung | Kết quả xác minh | Minh chứng |
|---|---|---|
| Cấu hình pipeline 6.2.1 | Đã tạo đủ 4 job và quan hệ phụ thuộc; local simulation chạy đúng trình tự | Hình 6.1, 6.3, 6.4 |
| GitLab pipeline 6.2.1 | Không xác minh Passed; không có project runner được gán | Hình 6.2, 6.5 |
| GitHub Actions 6.2.1 | Workflow và commit trên remote đã có; chưa có ảnh/log run để xác minh Success | Chưa có minh chứng hình ảnh |
| Development server Docusaurus | Thành công trên localhost:3000 | Hình 6.6, 6.7 |
| Production local | Website hiển thị trên localhost:3001 | Hình 6.8 |
| Build Docusaurus | Thành công, có `build/index.html` và 11 file | Hình 6.9–6.11 |
| GitLab pipeline 6.2.2 | Đã cấu hình; chưa có bằng chứng pipeline Passed | Hình 6.12 |
| SHA-256 local | 11/11 file khớp, không có file thừa trong `public/` | Hình 6.13–6.16 |
| GitHub Actions 6.2.2 | Workflow và commit trên remote đã có; chưa có ảnh/log run để xác minh Success | Chưa có minh chứng hình ảnh |
| GitHub Pages | URL dự kiến đã cấu hình nhưng trả HTTP 404 tại thời điểm kiểm tra | Chưa có minh chứng triển khai thành công |

## 8. Khó khăn và cách khắc phục

| Khó khăn có căn cứ | Cách xử lý |
|---|---|
| GitLab yêu cầu hoàn tất xác minh tài khoản trước khi dùng đầy đủ CI jobs; việc xác minh số điện thoại không hoàn tất. | Chuyển phần thực thi pipeline sang GitHub Actions, giữ cấu hình GitLab để đối chiếu với tài liệu gốc. |
| Project GitLab không có project runner được gán. | Đã khảo sát việc tạo Windows runner; sau đó sử dụng GitHub-hosted Ubuntu runner để giảm phụ thuộc hạ tầng local. |
| GitHub Pages triển khai project dưới subpath. | Cấu hình Docusaurus suy ra `url` và `baseUrl` từ `GITHUB_REPOSITORY` khi workflow đặt `GITHUB_PAGES=true`. |
| Artifact cần được kiểm tra sau khi sao chép. | So sánh SHA-256 từng file giữa `build/` và `public/`, đồng thời kiểm tra file thừa. |
| Kết quả local và CI dễ bị hiểu là tương đương. | Bảng kết quả tách rõ minh chứng local, cấu hình workflow và trạng thái triển khai chưa xác minh. |

## 9. Kết luận

Lab 06 đã xây dựng được hai project thể hiện các khái niệm cốt lõi của CI/CD: chia pipeline thành Build, Test, Deploy; thiết lập job chạy song song và phụ thuộc; tự động cài dependency; build website tĩnh; đóng gói artifact; và chuẩn bị triển khai Pages. Website Docusaurus đã chạy ở cả development và production mode trên máy local, production build có `index.html`, và 11 file sao chép sang `public/` đã được xác minh toàn vẹn bằng SHA-256.

Việc chuyển đổi sang GitHub Actions cho thấy cùng một mục tiêu pipeline có thể được ánh xạ giữa các nền tảng: GitLab dùng stage/job/artifacts, còn GitHub Actions dùng jobs/`needs`/Pages artifact/environment. Các quyền `contents: read`, `pages: write` và `id-token: write` giới hạn workflow theo đúng nhu cầu triển khai.

Giới hạn hiện tại là chưa có ảnh chụp hoặc log xác nhận hai workflow GitHub Actions đã chạy Success, và URL GitHub Pages chưa hoạt động tại thời điểm kiểm tra. Vì vậy, README chỉ kết luận các phần đã có bằng chứng: cấu hình mã nguồn, kiểm thử local, production build và kiểm tra SHA-256.

## 10. Tài liệu tham khảo

1. Tài liệu **Lab 06 – Bảo mật với DevSecOps**, do giảng viên cung cấp (`lab-06.pdf`).
2. [GitHub Actions Documentation](https://docs.github.com/en/actions)
3. [GitHub Pages Documentation](https://docs.github.com/en/pages)
4. [Docusaurus Documentation](https://docusaurus.io/docs)
5. [GitLab CI/CD Documentation](https://docs.gitlab.com/ci/)
