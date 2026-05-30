from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def auto_san_toan_bo_giai_dau():
    url_co_dinh = "https://bit.ly/socolive"
    print("🚀 KÍCH HOẠT VŨ KHÍ TỐI THƯỢNG: PLAYWRIGHT STEALTH...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # 🪄 ĐÂY LÀ PHÉP THUẬT: Tráng một lớp tàng hình lên toàn bộ trình duyệt
        stealth_sync(page)
        
        # ==========================================
        # GIAI ĐOẠN 1: QUÉT PHÒNG
        # ==========================================
        print(f"📥 Đang truy cập: {url_co_dinh}")
        
        try:
            # Chờ đến khi web load trạng thái an toàn
            page.goto(url_co_dinh, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(15000) # Ép đợi 15s để Cloudflare tự quay xong vòng xác nhận
        except Exception as e:
            print(f"⚠️ Cảnh báo lúc load trang: {e}")
            
        print(f"🎯 Đã hạ cánh: {page.url}")
        
        cac_link_phong = page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="/room/"]')).map(a => a.href)
        """)
        cac_link_phong = list(set(cac_link_phong))
        print(f"🎯 Đã lọt qua cửa! Phát hiện {len(cac_link_phong)} trận đấu.\n")
        
        if not cac_link_phong:
            print("❌ Vẫn bị Cloudflare phát hiện IP Data Center. Bó tay ở mảng Cloud không dùng Proxy!")
            browser.close()
            return

        # ==========================================
        # GIAI ĐOẠN 2: BẮT LINK .FLV
        # ==========================================
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")

            for stt, link_phong in enumerate(cac_link_phong, 1):
                if stt > 5:
                    print("🛑 Đã cào 5 trận. Rút lui an toàn.")
                    break
                    
                print(f"🔄 [{stt}/5] Đang đột nhập: {link_phong}")
                stream_link = None
                
                def bat_goi_tin(request):
                    nonlocal stream_link
                    if ".flv" in request.url or ".m3u8" in request.url:
                        stream_link = request.url
                
                page.on("request", bat_goi_tin)
                
                try:
                    page.goto(link_phong, timeout=30000)
                    page.wait_for_timeout(12000) 
                except Exception:
                    print("   ⚠️ Lỗi load phòng.")
                
                page.remove_listener("request", bat_goi_tin)
                
                if stream_link:
                    print(f"   ✅ Có Link: {stream_link[:60]}...")
                    file.write(f"#EXTINF:-1, ⚽ Kênh Socolive {stt}\n")
                    file.write(f"{stream_link}\n")
                else:
                    print("   ❌ Không thấy video.")
                    
        browser.close()
        print("\n🎉 CHIẾN DỊCH HOÀN TẤT!")

if __name__ == "__main__":
    auto_san_toan_bo_giai_dau()
