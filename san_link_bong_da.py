from playwright.sync_api import sync_playwright

def auto_san_toan_bo_giai_dau():
    # Sử dụng link rút gọn cố định để chống "chết" tên miền
    url_co_dinh = "https://bit.ly/socolive"
    
    print("🚀 BẮT ĐẦU KHỞI ĐỘNG SIÊU BOT SĂN LINK BÓNG ĐÁ...")
    
    with sync_playwright() as p:
        # Bật trình duyệt có giao diện để xem Bot hoạt động
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        # ==========================================
        # GIAI ĐOẠN 1: GIẢI MÃ TÊN MIỀN VÀ QUÉT PHÒNG
        # ==========================================
        print(f"📥 Đang truy cập biển chỉ đường: {url_co_dinh}")
        page.goto(url_co_dinh, timeout=30000)
        page.wait_for_timeout(5000) # Đợi web tải xong và tự động redirect
        
        # Lấy tên miền thực tế sau khi bị chuyển hướng
        ten_mien_that = page.url 
        print(f"🎯 Đã giải mã! Tên miền sống hôm nay là: {ten_mien_that}")
        
        # Cào tất cả các link có chữ "/room/"
        cac_link_phong = page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="/room/"]')).map(a => a.href)
        """)
        
        # Lọc trùng lặp
        cac_link_phong = list(set(cac_link_phong))
        print(f"🎯 Đã phát hiện {len(cac_link_phong)} phòng đang/sắp Live!\n")
        
        if not cac_link_phong:
            print("❌ Không tìm thấy phòng nào. Tắt Bot.")
            browser.close()
            return

        # ==========================================
        # GIAI ĐOẠN 2: CHUI VÀO TỪNG PHÒNG ĐỂ BẮT LINK GỐC
        # ==========================================
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")

            # Duyệt qua từng phòng đã quét được
            for stt, link_phong in enumerate(cac_link_phong, 1):
                print(f"🔄 [{stt}/{len(cac_link_phong)}] Đang đột nhập: {link_phong}")
                
                stream_link = None
                
                def bat_goi_tin(request):
                    nonlocal stream_link
                    # Tóm cả link .flv và .m3u8
                    if ".flv" in request.url or ".m3u8" in request.url:
                        stream_link = request.url
                
                # Bật máy nghe lén mạng
                page.on("request", bat_goi_tin)
                
                try:
                    # Mở phòng chiếu và đợi 8 giây cho luồng video kích hoạt
                    page.goto(link_phong, timeout=20000)
                    page.wait_for_timeout(8000) 
                except Exception:
                    print("   ⚠️ Web lag hoặc tải quá lâu, bỏ qua sang phòng khác.")
                
                # Tắt máy nghe lén trước khi sang phòng mới
                page.remove_listener("request", bat_goi_tin)
                
                # Ghi link vào file
                if stream_link:
                    print(f"   ✅ Tóm được link: {stream_link[:60]}...")
                    file.write(f"#EXTINF:-1, ⚽ Kênh Trực Tiếp {stt}\n")
                    file.write(f"{stream_link}\n")
                else:
                    print("   ❌ Chưa có luồng video phát sóng.")
                    
        browser.close()
        print("\n🎉 CHIẾN DỊCH HOÀN TẤT! File 'tong_hop_bong_da.m3u' đã sẵn sàng lên TV.")

# Chạy hệ thống
if __name__ == "__main__":
    auto_san_toan_bo_giai_dau()