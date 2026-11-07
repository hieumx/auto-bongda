# 🤖 Hệ Thống Đội Ngũ AI Agents Vận Hành Hệ Thống Auto Bóng Đá & Giải Trí 24/7

Để đảm bảo danh sách IPTV/M3U (`https://tinyurl.com/hieubongda`) luôn đạt độ mượt mà tối đa, link không bao giờ chết, giao diện phân loại đạt tiêu chuẩn **OCD hoàn mỹ** và không bao giờ gặp lỗi CI trên GitHub Actions, dự án được phân bổ chuyên môn hóa cho **5 AI Agents chuyên trách**:

---

```
                       ┌─────────────────────────┐
                       │   ORCHESTRATOR AGENT    │
                       │ (Điều Phối Viên Tổng)   │
                       └────────────┬────────────┘
                                    │
    ┌─────────────────┬─────────────┼─────────────┬─────────────────┐
    │                 │             │             │                 │
┌───▼───────────┐ ┌───▼───────────┐ │ ┌───────────▼─┐ ┌───────────▼─┐ ┌─▼─────────────┐
│ AGENT 1:      │ │ AGENT 2:      │ │ │ AGENT 3:    │ │ AGENT 4:    │ │ AGENT 5:        │
│ STREAM SCOUT  │ │ STREAM GUARD  │ │ │ OCD M3U     │ │ CI/CD SENTRY│ │ CONTENT CURATOR │
│ & HARVESTER   │ │ & VERIFIER    │ │ │ ARCHITECT   │ │ & INFRA     │ │ & EXPANDER      │
└───────────────┘ └───────────────┘ │ └─────────────┘ └─────────────┘ └─────────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │   KHO GIẢI TRÍ TUYỆT VỜI│
                       │   (M3U / IPTV 24/7)     │
                       └─────────────────────────┘
```

---

## 🕵️‍♂️ Agent 1: Stream Scout & Harvester (Thám tử Săn Luồng & Reverse-Engineering)
* **Vai trò:** Khám phá, bóc tách và thu thập luồng phát trực tiếp thể thao và truyền hình.
* **Nhiệm vụ cụ thể:**
  1. Giám sát các website phát sóng hàng đầu: Socolive, ColaTV, Gà Vàng (24h/333), Giờ Vàng TV, Sút Bóng TV, SaoKê, Xôi Lạc, Thập Cẩm, BTV...
  2. Bóc tách ngược (reverse-engineering) các endpoint JSON API gốc bí mật (ví dụ: `https://api.gvapi.cc/api/matches`, `https://api.cltvlv.com`) để lấy trực tiếp luồng `.m3u8` trong `< 0.5s` mà không tốn tài nguyên chạy trình duyệt giả lập.
  3. Cung cấp cơ chế dự phòng: Luôn có từ 2–3 gateway / mirrors đối với mỗi hệ thống kênh để nếu domain này bị chặn thì lập tức fallback sang domain khác.
* **Tiêu chí Zero-Error (SOP):**
  - Mọi request mạng phải có timeout (tối đa 8s).
  - Không bao giờ để script bị crash nếu một website bị sập hoặc trả về mã lỗi 4xx/5xx.

---

## 🛡️ Agent 2: Stream Quality Guard & Verifier (Chuyên Viên Kiểm Định Tín Hiệu & Chống Lag)
* **Vai trò:** Kiểm định chất lượng từng luồng phát, chống giật lag và loại bỏ link chết.
* **Nhiệm vụ cụ thể:**
  1. Thẩm định cú pháp luồng phát HLS (`.m3u8`), MP4 hoặc FLV.
  2. Kiểm tra độ phản hồi và trạng thái HTTP (chỉ duyệt các link trả về HTTP 200 kèm Content-Type chuẩn stream).
  3. Xếp hạng chất lượng luồng: Ưu tiên đưa các luồng Full HD 1080p / 60fps lên làm Server 1, luồng SD/HD làm Server 2 dự phòng.
  4. Sàng lọc link theo độ trễ (latency), loại bỏ luồng phát bị nghẽn băng thông hoặc bị gắn watermark quảng cáo cờ bạc quá mức.
* **Tiêu chí Zero-Error (SOP):**
  - Không đưa link chết vào danh sách M3U.
  - Tự động fallback sang luồng dự phòng nếu luồng chính bị gián đoạn.

---

## 📐 Agent 3: OCD Playlist Architect & EPG Master (Kiến Trúc Sư Playlist M3U Chuẩn OCD)
* **Vai trò:** Tổ chức, định dạng và làm đẹp cấu trúc file M3U đạt tiêu chuẩn tương thích 100% với mọi ứng dụng IPTV (TiviMate, Kodi, VLC, OTT Navigator, Smart IPTV...).
* **Nhiệm vụ cụ thể:**
  1. **Quy hoạch Icon & Phân nhóm rành mạch:**
     - `⚽` Dành riêng cho thể thao trực tiếp: `⚽ Ngoại Hạng Anh`, `⚽ Cúp C1`, `⚽ Bóng rổ`, `⚽ Tennis`...
     - `📺` Dành cho các kênh truyền hình 24/7: `📺 VTV`, `📺 K+ Sports`, `📺 HTV`, `📺 Thể Thao Quốc Tế`...
     - `🎬` Dành cho kho phim rạp: `🎬 Phim Chiếu Rạp 1080p`, `🎬 Phim Bộ Mới Nhất`, `🎬 Hoạt Hình - Anime`...
  2. **Tiêu chuẩn hóa Metadata:** Gán chính xác các thuộc tính `#EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="" group-title=""`.
  3. **Lọc rác văn bản:** Loại bỏ các ký tự điều khiển UTF-8 lỗi, dấu ngoặc rỗng `[]`, chuẩn hóa khoảng trắng thừa.
  4. **Fail-Safe Mechanism:** Nếu số lượng kênh cào được `< 5` (do sự cố mạng toàn cục), cấm tuyệt đối việc ghi đè file để bảo toàn playlist hiện tại cho người dùng.
* **Tiêu chí Zero-Error (SOP):**
  - File định dạng chuẩn UTF-8 (No BOM), kết thúc dòng chuẩn `\n` (LF).
  - Tên trận đấu thể hiện rõ giờ đá, tên đội bóng và tên Bình Luận Viên (BLV).

---

## ⚡ Agent 4: CI/CD & Infrastructure Sentry (Vệ Binh Hạ Tầng GitHub Actions 24/7)
* **Vai trò:** Đảm bảo hệ thống tự động hóa chạy trơn tru, không bao giờ gửi mail báo lỗi (fail) và không bị gián đoạn.
* **Nhiệm vụ cụ thể:**
  1. Cấu hình lịch chạy tối ưu: Lên lịch chạy vào các phút lẻ (`cron: '7,37 * * * *'`) để né giờ cao điểm của GitHub Actions, tránh bị xếp hàng chờ runner.
  2. Tăng tốc độ thực thi: Lưu cache thư viện Playwright (`~/.cache/ms-playwright`) giúp rút ngắn thời gian chạy từ 6 phút xuống chỉ còn dưới 2 phút.
  3. Chống xung đột Git: Sử dụng cơ chế kéo và giải quyết xung đột tự động (`git pull --rebase -X theirs`) trước mỗi lần đẩy code.
  4. Duy trì trạng thái sống vĩnh viễn (Keep-alive): Sử dụng trực tiếp GitHub CLI native (`gh api -X PUT .../enable`) để ngăn GitHub tạm ngưng workflow sau 60 ngày, không phụ thuộc vào action bên thứ ba có nguy cơ bị khóa tài khoản.
* **Tiêu chí Zero-Error (SOP):**
  - Toàn bộ workflow phải hoàn tất trong vòng `< 300 giây`.
  - Tỷ lệ thành công (Success Rate) trên GitHub Actions đạt **100%**.

---

## 🍿 Agent 5: Entertainment & Content Curator (Biên Tập Viên Kho Phim & Truyền Hình)
* **Vai trò:** Đảm bảo trải nghiệm giải trí đỉnh cao toàn diện ngoài thể thao: phim ảnh, hoạt hình và các sự kiện giải trí đặc sắc.
* **Nhiệm vụ cụ thể:**
  1. Trích xuất và cập nhật liên tục kho phim Full HD 1080p từ các nguồn APK chuyên dụng (như Phim4K APK).
  2. Tự động gom tập phim thành danh sách khoa học, gắn poster bìa phim sắc nét, link m3u8 có âm thanh vòm và phụ đề chuẩn.
  3. Bổ sung các kênh sự kiện thể thao lớn khi vào mùa (World Cup, Euro, Olympic, giải đấu võ thuật UFC/ONE Championship, giải đua xe F1...).
* **Tiêu chí Zero-Error (SOP):**
  - Link phim load nhanh, không bị xoay vòng buffering.
  - Phim bộ có đủ tập mới nhất theo ngày phát sóng.

---

## 📋 Bảng Phân Công Nhiệm Vụ & Trách Nhiệm (RACI Matrix)

| Tác Vụ Cốt Lõi | Agent 1 (Scout) | Agent 2 (Verifier) | Agent 3 (Architect) | Agent 4 (CI/CD) | Agent 5 (Curator) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Săn API & Bypass Cloudflare** | **[R]** Trực tiếp | [C] Phản hồi | [I] Nhận link | [I] Cung cấp tài nguyên | [C] Hỗ trợ nguồn |
| **Check Live & Chống Link Giật Lag** | [I] Bàn giao link | **[R]** Trực tiếp | [I] Nhận kết quả | [A] Giám sát timeout | [C] Test link phim |
| **Định dạng M3U Chuẩn OCD & Icon** | [I] Cung cấp raw | [C] Báo link sạch | **[R]** Trực tiếp | [I] Chạy script | [C] Duyệt danh mục |
| **Tự Động Hóa 24/7 & Chặn Mail Fail** | [I] Theo dõi log | [I] Theo dõi mạng | [I] Theo dõi file | **[R]** Trực tiếp | [I] Báo trạng thái |
| **Cập Nhật Phim 1080p & Kênh 24/7** | [C] Hỗ trợ API | [C] Check stream | [I] Xếp group | [I] Tự động push | **[R]** Trực tiếp |

*(Ghi chú: [R] = Chịu trách nhiệm thực hiện chính, [A] = Giám sát & phê duyệt, [C] = Tham vấn hỗ trợ, [I] = Nhận thông tin)*
