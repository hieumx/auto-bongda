import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def san_full_server_qua_proxy():
    url_co_dinh = "https://bit.ly/socolive"
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH SERVER VỚI PROXY ẨN DANH...")
    
    # 1. HÚT CHÌA KHÓA TỪ KÉT SẮT GITHUB
    proxy_ip = os.getenv("PROXY_IP")
    proxy_port = os.getenv("PROXY_PORT")
    proxy_user = os.getenv("PROXY_USER")
    proxy_pass = os.getenv("PROXY_PASS")
    
    # 2. LẮP RÁP CẤU HÌNH MẠNG
    cau_hinh_proxy = None
    if proxy_ip and proxy_port:
        print(f"🌐 Đã kết nối ống ngầm Proxy: {proxy_ip}")
        cau_hinh_proxy = {
            "server": f"http://{proxy_ip}:{proxy_port}",
            "username": proxy_user,
            "password": proxy_pass
        }
    else:
        print("⚠️ Cảnh báo: Không tìm thấy Proxy! Bot sẽ chạy bằng IP máy chủ.")

    with sync_playwright() as p:
        # 3. KÍCH HOẠT TRÌNH DUYỆT TÀNG HÌNH
        browser = p.chromium.launch(
            headless=True,
            proxy=cau_hinh_proxy,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page) 
        
        # ==========================================
        # GIAI ĐOẠN 1: VƯỢT TƯỜNG LỬA & QUÉT LINK
        # ==========================================
        print(f"📥 Đang truy cập trạm trung chuyển: {url_co_dinh}")
        try:
            page.goto(url_co_dinh, timeout=60000)
            print("⏳ Đang rình Cloudflare mở cửa và chờ dữ liệu tải về...")
            
            # Cơ chế rình mồi: Đợi tối đa 40s cho đến khi thấy link phòng chiếu
            page.wait_for_selector('a[href*="/room/"]', timeout=40000)
            page.wait_for_timeout(5000) # Đợi thêm 5s cho load hẳn
        except Exception as e:
            print(f"⚠️ Hết thời gian chờ hoặc kẹt tường lửa: {e}")

        # Quét tên trận và link
        danh_sach_raw = page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="/room/"]')).map(a => {
                return {
                    url: a.href,
                    ten: a.innerText.trim().replace(/\\n/g, ' - ')
                }
            })
        """)
        
        danh_sach_phong = {}
        for item in danh_sach_raw:
            url = item['url']
            ten = item['ten']
            if url not in danh_sach_phong or len(ten) > len(danh_sach_phong.get(url, "")):
                danh_sach_phong[url] = ten if ten else "Trận đấu đang chờ cập nhật"

        tong_so_tran = len(danh_sach_phong)
        print(f"🎯 ĐÃ QUA CỬA! Phát hiện tổng cộng {tong_so_tran} trận đấu!\n")

        if tong_so_tran == 0:
            print("❌ Không tìm thấy phòng nào. Web chưa lên lịch. Tắt Bot.")
            browser.close()
            return

        # ==========================================
        # GIAI ĐOẠN 2: CÀO DATA TOÀN BỘ VÀ LƯU FILE
        # ==========================================
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")

            for stt, (link_phong, ten_tran) in enumerate(danh_sach_phong.items(), 1):
                print(f"🔄 [{stt}/{tong_so_tran}] Đang lấy link: {ten_tran}")
                stream_link = None
                
                def bat_goi_tin(request):
                    nonlocal stream_link
                    if ".flv" in request.url or ".m3u8" in request.url:
                        stream_link = request.url
                
                page.on("request", bat_goi_tin)
                
                try:
                    page.goto(link_phong, timeout=30000)
                    page.wait_for_timeout(8000) # Chờ video bung luồng
                except Exception:
                    print("   ⚠️ Lỗi mạng phòng chiếu, bỏ qua.")
                
                page.remove_listener("request", bat_goi_tin)
                
                if stream_link:
                    print("   ✅ Thành công!")
                    file.write(f"#EXTINF:-1, ⚽ {ten_tran}\n")
                    file.write(f"{stream_link}\n")
                else:
                    print("   ❌ Trận này chưa phát sóng.")
                    
        browser.close()
        print("\n🎉 ĐÃ VÉT SẠCH SERVER! Hoàn tất đóng gói m3u.")

if __name__ == "__main__":
    san_full_server_qua_proxy()
