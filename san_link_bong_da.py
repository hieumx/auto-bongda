import os
import requests
import time
from playwright.sync_api import sync_playwright

# ==========================================
# HÀM API: LẤY IP TỪ PROXYXOAY.SHOP
# ==========================================
def lay_proxy_tu_api():
    print("🔄 Đang gọi API ProxyXoay xin IP mới...", flush=True)
    
    api_key = "HZjISqEzmNZkVapIOpceYm"
    url = f"https://proxyxoay.shop/api/get.php?key={api_key}&nhamang=Random&tinhthanh=0"
    
    try:
        response = requests.get(url, timeout=15).json()
        if response.get("status") == 100:
            ip_port = response.get("proxyhttp", "").rstrip(":") 
            nha_mang = response.get("Nha Mang", "Unknown")
            print(f"✅ Đã bốc được IP: {ip_port} (Mạng: {nha_mang})", flush=True)
            return ip_port
        else:
            print(f"⚠️ API báo lỗi: {response.get('message')}", flush=True)
            return None
    except Exception as e:
        print(f"❌ Kẹt mạng lúc gọi API: {e}", flush=True)
        return None

# ==========================================
# HÀM LÕI: ĐIỀU KHIỂN TRÌNH DUYỆT ĐI SĂN
# ==========================================
def san_full_server_qua_proxy():
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH 4 SERVER (CÁCH LY TAB & KIỂM ĐỊNH PROXY)...", flush=True)
    
    MAX_RETRIES = 3 

    for lan_thu in range(1, MAX_RETRIES + 1):
        print(f"\n==========================================", flush=True)
        print(f"🔄 BẮT ĐẦU VÒNG QUÉT LẦN {lan_thu}/{MAX_RETRIES}", flush=True)
        print(f"==========================================", flush=True)

        proxy_moi = lay_proxy_tu_api()
        if not proxy_moi:
            print("🛑 Không lấy được Proxy. Tạm dừng vòng này...", flush=True)
            danh_sach_phat = []
        else:
            cau_hinh_proxy = {"server": f"http://{proxy_moi}"}
            danh_sach_phat = [] 
            so_tram_loi = 0 # Biến theo dõi sức khỏe Proxy

            try:
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

                    def quet_trang(ten_nhom, url_trang_chu, keyword_link):
                        nonlocal so_tram_loi
                        page = context.new_page() # VŨ KHÍ MỚI: Mở Tab riêng biệt cho từng trạm
                        print(f"\n📥 ĐANG QUÉT SERVER: {ten_nhom.upper()}", flush=True)
                        
                        try:
                            page.goto(url_trang_chu, timeout=60000)
                            print("⏳ Đang rình Cloudflare mở cửa...", flush=True)
                            
                            page.wait_for_function(f"document.querySelectorAll('a[href*=\"{keyword_link}\"]').length > 0", timeout=40000)
                            page.wait_for_timeout(5000)
                            
                            danh_sach_raw = page.evaluate(f"""
                                Array.from(document.querySelectorAll('a[href*="{keyword_link}"]')).map(a => {{
                                    let img = a.querySelector('img');
                                    return {{
                                        url: a.href,
                                        ten: a.innerText.trim().replace(/\\n/g, ' - '),
                                        thumb: img ? img.src : "https://img.icons8.com/color/512/football2.png"
                                    }}
                                }})
                            """)
                            
                            danh_sach_phong = {}
                            for item in danh_sach_raw:
                                url = item['url']
                                ten = item['ten']
                                thumb = item['thumb']
                                if url == url_trang_chu or url == url_trang_chu + "/": continue
                                
                                if url not in danh_sach_phong or len(ten) > len(danh_sach_phong.get(url, {}).get('ten', "")):
                                    danh_sach_phong[url] = {
                                        'ten': ten if ten else "Trận đấu đang chờ cập nhật",
                                        'thumb': thumb
                                    }

                            tong_so_tran = len(danh_sach_phong)
                            print(f"🎯 Phát hiện {tong_so_tran} phòng chiếu tại {ten_nhom}!", flush=True)

                            for stt, (link_phong, data_phong) in enumerate(danh_sach_phong.items(), 1):
                                ten_tran = data_phong['ten']
                                anh_thumb = data_phong['thumb']
                                
                                stream_link = None
                                def bat_goi_tin(request):
                                    nonlocal stream_link
                                    url_lower = request.url.lower()
                                    if ".flv" in url_lower or ".m3u8" in url_lower:
                                        stream_link = request.url
                                
                                page.on("request", bat_goi_tin)
                                try:
                                    page.goto(link_phong, timeout=30000)
                                    page.wait_for_load_state("domcontentloaded")
                                    page.wait_for_timeout(3000) 
                                    
                                    page.mouse.click(960, 300) 
                                    page.wait_for_timeout(500)
                                    page.mouse.click(960, 540) 
                                    
                                    page.wait_for_timeout(8000) 
                                except Exception:
                                    pass 
                                page.remove_listener("request", bat_goi_tin)
                                
                                if stream_link:
                                    danh_sach_phat.append({
                                        'nhom': ten_nhom,
                                        'ten': ten_tran,
                                        'link': stream_link,
                                        'thumb': anh_thumb
                                    })
                        except Exception as e:
                            print(f"⚠️ Kẹt tường lửa hoặc web sập: {e}", flush=True)
                            so_tram_loi += 1 # Đánh dấu Proxy bị xịt ở trạm này
                        finally:
                            page.close() # Dọn dẹp sạch sẽ Tab sau khi xong việc

                    # ==========================================
                    # DANH SÁCH BỘ TỨ SIÊU ĐẲNG
                    # ==========================================
                    quet_trang("Socolive", "https://bit.ly/socolive", "/room/")
                    quet_trang("Xoilac", "https://xoilacztw.tv", "/truc-tiep/")
                    quet_trang("Gavang", "https://gavanglink.co", "/truc-tiep/")
                    quet_trang("Quechoa", "https://quechoa11.live", "/truc-tiep/")

                    browser.close()
            except Exception as e:
                print(f"🔥 Lỗi hệ thống cốt lõi: {e}", flush=True)

        # ==========================================
        # ĐÁNH GIÁ CHẤT LƯỢNG PROXY TRƯỚC KHI ĐÓNG GÓI
        # ==========================================
        if so_tram_loi >= 2 and lan_thu < MAX_RETRIES:
            print(f"\n⚠️ CẢNH BÁO: Phát hiện {so_tram_loi}/4 trạm bị sập mạng giữa chừng.")
            print("🔄 Proxy có dấu hiệu đứt kết nối. Tiến hành hủy kết quả, ngủ 60s và xin IP mới...")
            time.sleep(60)
            continue # Quay lại đầu vòng lặp xin IP mới

        if len(danh_sach_phat) > 0:
            print("\n📦 ĐANG ĐÓNG GÓI M3U VÀ CHIA THƯ MỤC...", flush=True)
            with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
                file.write("#EXTM3U\n")
                for luong in danh_sach_phat:
                    file.write(f'#EXTINF:-1 group-title="{luong["nhom"]}" tvg-logo="{luong["thumb"]}", ⚽ {luong["ten"]}\n')
                    file.write(f'{luong["link"]}\n')
                    
            print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_phat)} TRẬN!", flush=True)
            break 
        else:
            print(f"⚠️ Vòng {lan_thu} thu hoạch 0 trận.", flush=True)
            if lan_thu < MAX_RETRIES:
                print("⏳ Đang ngủ 60 giây để nhà mạng hạ nhiệt trước khi xin IP mới...", flush=True)
                time.sleep(60)
            else:
                print("❌ ĐÃ THỬ HẾT 3 LẦN NHƯNG VẪN THẤT BẠI. HẸN CHU KỲ SAU!", flush=True)
                with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
                    file.write("#EXTM3U\n")

if __name__ == "__main__":
    san_full_server_qua_proxy()
