import os
from playwright.sync_api import sync_playwright

def san_full_server_qua_proxy():
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH 2 SERVER (SOCOLIVE & XOILAC)...")
    
    # 1. KHAI BÁO CỨNG PROXY
    proxy_ip = "171.236.188.19"
    proxy_port = "41570"
    proxy_user = "hieumx"
    proxy_pass = "hieu123"
    
    cau_hinh_proxy = {
        "server": f"http://{proxy_ip}:{proxy_port}",
        "username": proxy_user,
        "password": proxy_pass
    }

    # Cặp biến để hứng toàn bộ data từ các nguồn
    danh_sach_phat = [] 

    with sync_playwright() as p:
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

        # ==========================================
        # HÀM LÕI: QUÉT TỪNG SERVER ĐỘC LẬP
        # ==========================================
        def quet_trang(ten_nhom, url_trang_chu, keyword_link):
            print(f"\n==========================================")
            print(f"📥 ĐANG QUÉT SERVER: {ten_nhom.upper()} ({url_trang_chu})")
            print(f"==========================================")
            try:
                page.goto(url_trang_chu, timeout=60000)
                print("⏳ Đang rình Cloudflare mở cửa...")
                page.wait_for_selector(f'a[href*="{keyword_link}"]', timeout=40000)
                page.wait_for_timeout(5000)
            except Exception as e:
                print(f"⚠️ Kẹt tường lửa hoặc web đang sập: {e}")
                return

            # Quét tên trận và link
            danh_sach_raw = page.evaluate(f"""
                Array.from(document.querySelectorAll('a[href*="{keyword_link}"]')).map(a => {{
                    return {{
                        url: a.href,
                        ten: a.innerText.trim().replace(/\\n/g, ' - ')
                    }}
                }})
            """)
            
            # ĐÃ SỬA LỖI Ở ĐÂY: Chỉ dùng 1 cặp ngoặc nhọn {} cho Python
            danh_sach_phong = {}
            
            for item in danh_sach_raw:
                url = item['url']
                ten = item['ten']
                # Lọc bỏ những link bị trùng với chính trang chủ
                if url == url_trang_chu or url == url_trang_chu + "/": continue
                
                if url not in danh_sach_phong or len(ten) > len(danh_sach_phong.get(url, "")):
                    danh_sach_phong[url] = ten if ten else "Trận đấu đang chờ cập nhật"

            tong_so_tran = len(danh_sach_phong)
            print(f"🎯 Phát hiện {tong_so_tran} phòng chiếu tại {ten_nhom}!")

            for stt, (link_phong, ten_tran) in enumerate(danh_sach_phong.items(), 1):
                print(f"🔄 [{ten_nhom}] [{stt}/{tong_so_tran}] Đang lấy luồng: {ten_tran}")
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
                    # Lưu kèm tên nhóm để lát nữa chia folder
                    danh_sach_phat.append({
                        'nhom': ten_nhom,
                        'ten': ten_tran,
                        'link': stream_link
                    })
                else:
                    print("   ❌ Trận này chưa phát sóng.")

        # ==========================================
        # GIAI ĐOẠN 1: THỰC THI QUÉT CÁC TRẠM
        # ==========================================
        quet_trang("Socolive", "https://bit.ly/socolive", "/room/")
        quet_trang("Xoilac", "https://xoilaczty.tv/truc-tiep", "/truc-tiep/")

        browser.close()

        # ==========================================
        # GIAI ĐOẠN 2: LƯU FILE CÓ CHIA THƯ MỤC
        # ==========================================
        print("\n📦 ĐANG ĐÓNG GÓI M3U VÀ CHIA THƯ MỤC...")
        
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            
            if not danh_sach_phat:
                print("❌ Không thu hoạch được link nào. Server chưa lên lịch.")
            else:
                for luong in danh_sach_phat:
                    file.write(f'#EXTINF:-1 group-title="{luong["nhom"]}", ⚽ {luong["ten"]}\n')
                    file.write(f'{luong["link"]}\n')
                    
        print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_phat)} TRẬN!")

if __name__ == "__main__":
    san_full_server_qua_proxy()
