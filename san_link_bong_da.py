import os
import requests
import json
from playwright.sync_api import sync_playwright

# ==========================================
# HÀM API: LẤY IP TỪ PROXYXOAY.SHOP
# ==========================================
def lay_proxy_tu_api():
    print("🔄 Đang gọi API ProxyXoay xin IP mới...", flush=True)
    
    # Key mua hàng đã được tích hợp sẵn
    api_key = "HZjISqEzmNZkVapIOpceYm"
    
    url = f"https://proxyxoay.shop/api/get.php?key={api_key}&nhamang=Random&tinhthanh=0"
    
    try:
        response = requests.get(url, timeout=15).json()
        
        if response.get("status") == 100:
            proxy_raw = response.get("proxyhttp", "")
            ip_port = proxy_raw.rstrip(":") # Gọt bỏ dấu hai chấm thừa
            
            nha_mang = response.get("Nha Mang", "Unknown")
            vi_tri = response.get("Vi Tri", "Unknown")
            
            print(f"✅ Đã bốc được IP mới: {ip_port} (Mạng: {nha_mang} - Khu vực: {vi_tri})", flush=True)
            return ip_port
        else:
            loi_msg = response.get("message", "Lỗi không xác định")
            print(f"⚠️ API báo lỗi (Status {response.get('status')}): {loi_msg}", flush=True)
            return None
            
    except Exception as e:
        print(f"❌ Kẹt mạng lúc gọi API: {e}", flush=True)
        return None

# ==========================================
# HÀM LÕI: ĐIỀU KHIỂN TRÌNH DUYỆT ĐI SĂN
# ==========================================
def san_full_server_qua_proxy():
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH TRÊN GITHUB ACTIONS...", flush=True)
    
    proxy_moi = lay_proxy_tu_api()
    if not proxy_moi:
        print("🛑 Không có Proxy, dừng toàn bộ chiến dịch để tránh bị block!", flush=True)
        return

    cau_hinh_proxy = {
        "server": f"http://{proxy_moi}"
    }

    danh_sach_phat = [] 

    with sync_playwright() as p:
        # QUAN TRỌNG: headless=True để chạy ngầm trên máy chủ Linux của GitHub
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

        def quet_trang(ten_nhom, url_trang_chu, keyword_link):
            print(f"\n==========================================", flush=True)
            print(f"📥 ĐANG QUÉT SERVER: {ten_nhom.upper()} ({url_trang_chu})", flush=True)
            print(f"==========================================", flush=True)
            try:
                page.goto(url_trang_chu, timeout=60000)
                print("⏳ Đang rình Cloudflare mở cửa...", flush=True)
                page.wait_for_selector(f'a[href*="{keyword_link}"]', timeout=40000)
                page.wait_for_timeout(5000)
            except Exception as e:
                print(f"⚠️ Kẹt tường lửa hoặc web đang sập: {e}", flush=True)
                return

            danh_sach_raw = page.evaluate(f"""
                Array.from(document.querySelectorAll('a[href*="{keyword_link}"]')).map(a => {{
                    return {{
                        url: a.href,
                        ten: a.innerText.trim().replace(/\\n/g, ' - ')
                    }}
                }})
            """)
            
            danh_sach_phong = {}
            for item in danh_sach_raw:
                url = item['url']
                ten = item['ten']
                if url == url_trang_chu or url == url_trang_chu + "/": continue
                
                if url not in danh_sach_phong or len(ten) > len(danh_sach_phong.get(url, "")):
                    danh_sach_phong[url] = ten if ten else "Trận đấu đang chờ cập nhật"

            tong_so_tran = len(danh_sach_phong)
            print(f"🎯 Phát hiện {tong_so_tran} phòng chiếu tại {ten_nhom}!", flush=True)

            for stt, (link_phong, ten_tran) in enumerate(danh_sach_phong.items(), 1):
                print(f"🔄 [{ten_nhom}] [{stt}/{tong_so_tran}] Đang lấy luồng: {ten_tran}", flush=True)
                stream_link = None
                
                def bat_goi_tin(request):
                    nonlocal stream_link
                    if ".flv" in request.url or ".m3u8" in request.url:
                        stream_link = request.url
                
                page.on("request", bat_goi_tin)
                
                try:
                    page.goto(link_phong, timeout=30000)
                    page.wait_for_timeout(8000) 
                except Exception:
                    print("   ⚠️ Lỗi mạng phòng chiếu, bỏ qua.", flush=True)
                
                page.remove_listener("request", bat_goi_tin)
                
                if stream_link:
                    print("   ✅ Thành công!", flush=True)
                    danh_sach_phat.append({
                        'nhom': ten_nhom,
                        'ten': ten_tran,
                        'link': stream_link
                    })
                else:
                    print("   ❌ Trận này chưa phát sóng.", flush=True)

        quet_trang("Socolive", "https://bit.ly/socolive", "/room/")
        quet_trang("Xoilac", "https://xoilaczty.tv/truc-tiep", "/truc-tiep/")

        browser.close()

        print("\n📦 ĐANG ĐÓNG GÓI M3U VÀ CHIA THƯ MỤC...", flush=True)
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            if not danh_sach_phat:
                print("❌ Không thu hoạch được link nào. Server chưa lên lịch.", flush=True)
            else:
                for luong in danh_sach_phat:
                    file.write(f'#EXTINF:-1 group-title="{luong["nhom"]}", ⚽ {luong["ten"]}\n')
                    file.write(f'{luong["link"]}\n')
                    
        print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_phat)} TRẬN!", flush=True)

if __name__ == "__main__":
    san_full_server_qua_proxy()
