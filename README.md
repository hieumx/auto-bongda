# ⚽ Siêu Bot Săn Link Thể Thao & IPTV Tự Động (Auto Bóng Đá)

[![Tự Động Săn Link Bóng Đá Hằng Ngày](https://github.com/hieumx/auto-bongda/actions/workflows/chay_bot.yml/badge.svg)](https://github.com/hieumx/auto-bongda/actions/workflows/chay_bot.yml)

Hệ thống tự động cào và cập nhật luồng phát trực tiếp thể thao, truyền hình 24/7 và kho phim Full HD qua GitHub Actions **mỗi 30 phút một lần**.

---

## 📺 Link Xem Trực Tiếp (Dùng Cho Mọi Ứng Dụng IPTV)

Dán một trong hai đường dẫn sau vào trình phát IPTV của bạn (TiviMate, Kodi, VLC, OTT Navigator, IPTV Smarters Pro,...):

* **🔗 Link Rút Gọn Siêu Tốc:**  
  ```text
  https://tinyurl.com/hieubongda
  ```

* **🔗 Link Dự Phòng Trực Tiếp Từ GitHub:**  
  ```text
  https://raw.githubusercontent.com/hieumx/auto-bongda/refs/heads/main/tong_hop_bong_da.m3u
  ```

---

## 🚀 Danh Mục Phát Sóng Tích Hợp

1. **⚽ Trực Tiếp Thể Thao (Đa Server Siêu Tốc):**
   * **Socolive** (Kết nối trực tiếp JSON API)
   * **Gà Vàng / Giờ Vàng** (API fixtures đa luồng)
   * **Bia Ôm, BTV, Xôi Lạc, Quê Choa, Thập Cẩm, Thiên Đỉnh, Hội Quán, Chuối Chiên, Cà Khịa, CoLa, S8...**
   * Đầy đủ các môn: *Bóng đá, Bóng chuyền, Bóng rổ, Tennis, Cầu lông, Billiards, Esports, Đua xe...*

2. **📺 Kênh Truyền Hình 24/7 (380+ Kênh):**
   * FIFA World Cup 2026, VTV, VTVCab, K+, SCTV, HTV, Thể thao quốc tế (Sky Sports, TNT Sports, Canal+ Live 1-12,...).

3. **🎬 Trọn Bộ Hoạt Hình 3D Full Series (YanHH3D Engine):**
   * **Kho Hoạt hình 3D đồ sộ với hơn 12.300+ tập phim trọn bộ từ YanHH3D (Nghịch Thiên Chí Tôn 559 tập, Vạn Giới Độc Tôn 495 tập, Luyện Khí Mười Vạn Năm 392 tập, Thế Giới Hoàn Mỹ 288 tập, Đấu La Đại Lục 266 tập, Tiên Nghịch 165 tập, Phàm Nhân Tu Tiên 198 tập, Đấu Phá Thương Khung 219 tập...)**
   * **Thế Giới Hoàn Mỹ (288 tập), Già Thiên (188 tập), Thôn Phệ Tinh Không (248 tập)**
   * **Mục Thần Ký (107 tập), Quang Âm Chi Ngoại (47 tập), Đấu La Đại Lục 2 (178 tập)...**

4. **🎬 Kho Phim Chiếu Rạp 1080p (Phim4K APK):**
   * 🎬 Phim Lẻ Chiếu Rạp Full HD 1080p
   * 🎬 Phim Bộ Mới Nhất (Tập cập nhật liên tục)
   * 🎬 Hoạt Hình - Anime Vietsub

---

## ⚙️ Cơ Chế Tự Động Hóa 24/7 (GitHub Actions)

* **Tần suất quét:** Tự động chạy **30 phút / lần** thông qua GitHub Actions Cron (`7,37 * * * *`).
* **Cơ chế chống tắt:** Sử dụng trực tiếp GitHub CLI native ngăn GitHub vô hiệu hóa sau 60 ngày.
* **Vận hành bởi Đội ngũ 5 AI Agents chuyên trách:** Chi tiết xem tại [AI_AGENTS_TEAM.md](AI_AGENTS_TEAM.md).
* **Tự xử lý xung đột:** Tự động rebase và push commit với cờ `[skip ci]`.
* **Kích hoạt thủ công:** Bạn có thể vào tab **Actions** trên GitHub và bấm **Run workflow** bất cứ lúc nào muốn cập nhật ngay tức thì.
