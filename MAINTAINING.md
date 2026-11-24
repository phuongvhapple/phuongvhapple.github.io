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
kinh nghiệm (`var JOBS`), About, Working style, Education, Contact.
Màu ở `:root` (đầu file), font ở `--headline`, `--sub`, `--body`; font Google ở `GOOGLE_FONTS` trong `build.py`.

## Phiên bản 2 (https://phuongvhapple.github.io/v2/)

Bản v2 có layout và hiệu ứng riêng (cuộn mượt, câu sáng dần theo từng chữ, tiêu đề ghim giữa màn hình, thẻ dự án đánh số, phần About trượt ngang).
Dự án, ảnh gallery, video, flip book, số liệu (10+ years, Up to 10), kỹ năng, email và số điện thoại lấy từ `portfolio.src.html`: thêm hoặc đổi những thứ này như bình thường, mỗi lần `python3 build.py` cả hai bản cùng được cập nhật.

**Chữ của v2 thì viết riêng** trong `v2-copy.json` (bản v1 không bị ảnh hưởng):
- `eyebrow` (dòng chữ vàng trên tên), `lead` (câu sáng dần theo từng chữ), `points` (4 ý: tiêu đề + nội dung), `work_lede` (câu giới thiệu Selected Work), `contact_text` (câu dưới Let’s talk).
- `projects`: mô tả từng dự án theo slug (`title`, `role`, `when`, `text`, `extra` là đoạn thứ hai; bỏ trống `extra` thì không hiện đoạn đó). Thêm dự án mới trong `portfolio.src.html` mà không có mục ở đây thì v2 dùng chữ của v1.
- `jobs`: toàn bộ phần Where I've worked, cùng thứ tự với JOBS trong `portfolio.src.html` (thời gian, chức danh, công ty, tóm tắt, danh sách Responsibilities).
- `about` (3 thẻ đầu của About: tiêu đề + nội dung) và `education`.

- Layout, màu và hiệu ứng riêng của v2 nằm trong `v2.src.html`. Không sửa `v2/index.html` bằng tay.
- Câu giới thiệu dưới tên ở đầu trang (`<p class="x-intro">`), chữ trên 2 nút và tiêu đề Let’s talk viết thẳng trong `v2.src.html`. Các từ được tô vàng trong câu sáng dần nằm ở dòng `structured|creative|workflows` trong `v2.src.html`.
- Đầu trang: thiên hà xoắn ốc 3D theo màu thương hiệu trong một không gian trừu tượng: lõi có tia sáng hình sao, vệt sáng toả ra, lưới chấm sáng cong, tinh vân xoáy và đốm màu (three.js r128 từ cdnjs, đoạn `hero: a spiral galaxy` trong `v2.src.html`; tham khảo video Daft Punk "Contact" 0:59–1:16). Không có hành tinh. Khi cuộn, camera bay vào lõi. Máy không hỗ trợ WebGL sẽ thấy khối màu CSS thay thế.
- Thư viện hiệu ứng: GSAP 3.12.5 + ScrollTrigger và three.js r128 (cdnjs), Lenis 1.1.13 (jsDelivr). Nếu không tải được, trang vẫn hiện đủ nội dung, chỉ không có hiệu ứng.

## Những gì build tự làm

`build.py` tạo `index.html` cùng `llms.txt`, `robots.txt`, `sitemap.xml` và phần chữ cho AI/Google đọc
(nội dung Work và Experience được ghi sẵn vào HTML). Không cần sửa các file này bằng tay.

Bản chia sẻ trên claude.ai (Artifact): `python3 build.py --artifact <file.html>` rồi nhờ Claude đăng lên
https://claude.ai/artifact/19D7Y9dtCUfNh2Ng7proPr (chỉ chứa file dưới 15 MB).
