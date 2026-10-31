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

3. **🎬 Kho Phim Bom Tấn (Trích Xuất Từ Phim4K APK):**
   * 🎬 Phim Lẻ Chiếu Rạp Full HD 1080p
   * 🎬 Phim Bộ Mới Nhất (Tập cập nhật liên tục)
   * 🎬 Hoạt Hình - Anime Vietsub

---

## ⚙️ Cơ Chế Tự Động Hóa 24/7 (GitHub Actions)

* **Tần suất quét:** Tự động chạy **30 phút / lần** thông qua GitHub Actions Cron (`*/30 * * * *`).
* **Cơ chế chống tắt:** Sử dụng `keepalive-workflow` ngăn GitHub tự động vô hiệu hóa sau 60 ngày.
* **Tự xử lý xung đột:** Tự động rebase và push commit với cờ `[skip ci]`.
* **Kích hoạt thủ công:** Bạn có thể vào tab **Actions** trên GitHub và bấm **Run workflow** bất cứ lúc nào muốn cập nhật ngay tức thì.
