from playwright.sync_api import sync_playwright

def auto_san_toan_bo_giai_dau():
    url_co_dinh = "https://bit.ly/socolive"
    print("🚀 KHỞI ĐỘNG BOT VỚI CHẾ ĐỘ NGỤY TRANG (STEALTH MODE)...")
    
    with sync_playwright() as p:
        # 1. Thêm vũ khí chống phát hiện tự động hóa
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        # 2. Giả mạo danh tính: Đóng giả máy tính Windows 10 dùng Chrome thật
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        # 3. Xóa sổ chữ "webdriver" (Dấu vết Bot) trong hệ thống lõi
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # ==========================================
        # GIAI ĐOẠN 1: QUÉT PHÒNG (Đã được bảo vệ)
        # ==========================================
        print(f"📥 Đang truy cập biển chỉ đường: {url_co_dinh}")
        page.goto(url_co_dinh, timeout=30000)
        
        # Chờ lâu hơn một chút (10s) để lách qua vòng xoay Cloudflare nếu có
        page.wait_for_timeout(10000) 
        
        ten_mien_that = page.url 
        print(f"🎯 Đã hạ cánh an toàn tại: {ten_mien_that}")
        
        cac_link_phong = page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="/room/"]')).map(a => a.href)
        """)
        cac_link_phong = list(set(cac_link_phong))
        print(f"🎯 Đã lọt qua cửa! Phát hiện {len(cac_link_phong)} trận đấu.\n")
        
        if not cac_link_phong:
            print("❌ Vẫn bị tường lửa chặn hoặc web không có trận nào.")
            browser.close()
            return

        # ==========================================
        # GIAI ĐOẠN 2: ĐỘT NHẬP & BẮT LINK
        # ==========================================
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")

            for stt, link_phong in enumerate(cac_link_phong, 1):
                # Để test nhanh, thầy giới hạn Bot chỉ cào 5 trận đầu tiên rồi nghỉ
                # Tránh mở quá nhiều phòng một lúc làm Cloudflare nghi ngờ khóa IP
                if stt > 5:
                    print("🛑 Đã cào đủ 5 trận an toàn. Tạm dừng để tránh bị khóa IP.")
                    break
                    
                print(f"🔄 [{stt}/5] Đang ngụy trang đột nhập: {link_phong}")
                stream_link = None
                
                def bat_goi_tin(request):
                    nonlocal stream_link
                    if ".flv" in request.url or ".m3u8" in request.url:
                        stream_link = request.url
                
                page.on("request", bat_goi_tin)
                
                try:
                    page.goto(link_phong, timeout=20000)
                    page.wait_for_timeout(10000) # Đợi 10s cho video xuyên tường lửa
                except Exception:
                    print("   ⚠️ Lỗi mạng, bỏ qua.")
                
                page.remove_listener("request", bat_goi_tin)
                
                if stream_link:
                    print(f"   ✅ Bắt sống luồng video: {stream_link[:60]}...")
                    file.write(f"#EXTINF:-1, ⚽ Kênh Tự Động {stt}\n")
                    file.write(f"{stream_link}\n")
                else:
                    print("   ❌ Không thấy video (Trận chưa đá hoặc dính CAPTCHA).")
                    
        browser.close()
        print("\n🎉 HOÀN TẤT CHIẾN DỊCH VƯỢT RÀO!")

if __name__ == "__main__":
    auto_san_toan_bo_giai_dau()
