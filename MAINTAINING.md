# Cập nhật website portfolio

Hướng dẫn giữ cho https://phuongvhapple.github.io luôn cập nhật được, kể cả khi bắt đầu một phiên Claude mới.
Mở thư mục này trong Claude Code và nói việc cần làm. Claude đọc `CLAUDE.md` (chỉ có trên máy) và file này.

## Nguyên tắc

- Sửa nội dung trong `portfolio.src.html`, **không sửa `index.html`** (file này được tạo lại mỗi lần build).
- Giữ nguyên giao diện, nội dung và hiệu ứng hiện có, trừ khi chủ trang yêu cầu đổi.
- Ảnh và video gốc nằm trong `Images/` (không đưa lên GitHub). Hãy sao lưu thư mục này (iCloud/Google Drive): mất nó thì vẫn còn website, nhưng không tạo lại được ảnh từ bản gốc.
- Không để trùng ảnh hay video. Trước khi đưa lên, kiểm tra không còn chữ mẫu (Lorem ipsum, XX/XX/XXXX).

## Chuẩn bị (một lần cho mỗi máy)

Cần: Python 3, Node, ffmpeg, GitHub CLI (`gh`, đã đăng nhập tài khoản phuongvhapple).

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Quy trình chung

```bash
.venv/bin/python optimize_images.py   # khi thêm/bớt ảnh, slide, PDF
python3 build.py                      # luôn chạy sau mọi thay đổi
git add -A && git commit -m "..." && git push
```

Khoảng 1 phút sau trang tự cập nhật (mở `?v=<số mới>` để tránh bản cũ trong bộ nhớ đệm).
Nếu sau khi đẩy file lớn mà trang không cập nhật: `gh api -X POST repos/phuongvhapple/phuongvhapple.github.io/pages/builds`.
Nếu bước triển khai bị quá thời gian: tạo một commit trống (`git commit --allow-empty -m "Redeploy"`) rồi đẩy lại.

## Thêm hoặc bớt ảnh trong một dự án

| Dự án | Thư mục |
|---|---|
| Dai-ichi Life | `Images/DAI-ICHI LIFE/` |
| Sunrise Events | `Images/SUNRISE EVENT/` |
| CEN Group | `Images/CEN GROUP/` |
| Laguna Lăng Cô | `Images/LAGUNA LANG CO/` |
| Nam Long | `Images/NAM LONG/` |
| Thien Minh (Victoria) | `Images/VICTORIA/` |
| Freelance | `Images/FREELANCE/` (mỗi brand một thư mục con `1 Dong Nguyen` … `7 Felix Office`) |

Thứ tự trong gallery: ảnh bìa, thư mục `New/`, ảnh ở thư mục chính, rồi các thư mục con đánh số theo thứ tự tên.
Thư mục bắt đầu bằng `_` bị bỏ qua: chuyển ảnh vào `_removed/` để gỡ khỏi trang mà không xoá.
Ảnh bìa của mỗi dự án đặt ở `COVERS` trong `optimize_images.py`.

## Thêm video

Video gốc để trong `Images/<DỰ ÁN>/_videos/`, rồi:

```bash
tools/add_video.sh "Images/DAI-ICHI LIFE/_videos/ten-goc.mp4" dlvn-ten-ngan 10 28
```

(10 = giây lấy ảnh poster; 27 cho video UI ngắn, 28 cho video sự kiện dài.)
Sau đó thêm vào mục `videos:` của dự án trong `portfolio.src.html`:

```js
["Tên tiếng Anh", "assets/video/dlvn-ten-ngan.mp4", "assets/video/dlvn-ten-ngan.webp"]
```

Thêm `true` làm phần tử thứ 4 nếu file trên 15 MB (bản Artifact sẽ mở video trên website).
Video YouTube: `["Tên", "<mã YouTube 11 ký tự>"]`. Mỗi file dưới 100 MB (giới hạn của GitHub).

## Thêm slide hoặc brochure lật trang

Đặt thư mục ảnh slide hoặc file PDF trong `Images/`, khai báo trong `DECKS` của `optimize_images.py`:
`"slides"` = slide 16:9 lật từng trang; `"book"` = brochure in, tách trang đôi, mở 2 trang có bìa.
Rồi thêm vào mục `decks:` của dự án: `["<id>", "Tên brand", "Loại tài liệu"]`.

## Mockup standee

```bash
.venv/bin/python tools/standee_mockup.py "artwork.jpg" "Images/FREELANCE/4 Keppel Land/ten_Mockup.jpg"
```

## Nội dung chữ

Trong `portfolio.src.html`: phần đầu trang và Professional Summary (`class="hero"`), mô tả dự án (`var PROJECTS`),
kinh nghiệm (`var JOBS`), About, Characteristics, Education, Contact.
Màu ở `:root` (đầu file), font ở `--headline`, `--sub`, `--body`; font Google ở `GOOGLE_FONTS` trong `build.py`.

## Những gì build tự làm

`build.py` tạo `index.html` cùng `llms.txt`, `robots.txt`, `sitemap.xml` và phần chữ cho AI/Google đọc
(nội dung Work và Experience được ghi sẵn vào HTML). Không cần sửa các file này bằng tay.

Bản chia sẻ trên claude.ai (Artifact): `python3 build.py --artifact <file.html>` rồi nhờ Claude đăng lên
https://claude.ai/artifact/19D7Y9dtCUfNh2Ng7proPr (chỉ chứa file dưới 15 MB).
