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

    # ==========================================
    # DANH SÁCH BỘ TỨ SIÊU ĐẲNG
    # ==========================================
    tat_ca_server = [
        ("Socolive", "https://bit.ly/socolive", "/room/", False),
        ("Xoilac", "https://xoilaccg.tv", "/truc-tiep/", True),   # Chia theo môn thể thao
        ("Gavang", "https://gavanglink.co", "/truc-tiep/", False),
        ("Quechoa", "https://quechoa11.live", "/truc-tiep/", False),
    ]

    # Bảng ánh xạ data-sport → tên tiếng Việt cho Xoilac
    SPORT_MAP = {
        "football": "Bóng đá",
        "basketball": "Bóng rổ",
        "tennis": "Tennis",
        "badminton": "Cầu lông",
        "volleyball": "Bóng chuyền",
        "esports": "Esports",
        "lol": "Esports",
        "dota2": "Esports",
        "csgo": "Esports",
        "baseball": "Bóng chày",
    }

    danh_sach_phat = []           # Tích lũy kết quả xuyên suốt các vòng, KHÔNG reset
    server_da_thanh_cong = set()  # Đánh dấu server đã quét OK, không quét lại

    for lan_thu in range(1, MAX_RETRIES + 1):
        print(f"\n==========================================", flush=True)
        print(f"🔄 BẮT ĐẦU VÒNG QUÉT LẦN {lan_thu}/{MAX_RETRIES}", flush=True)
        print(f"==========================================", flush=True)

        # Chỉ quét lại các server chưa thành công
        server_can_quet = [s for s in tat_ca_server if s[0] not in server_da_thanh_cong]
        if not server_can_quet:
            print("✅ Tất cả server đã quét thành công, không cần chạy thêm!", flush=True)
            break

        print(f"📋 Cần quét: {', '.join(s[0] for s in server_can_quet)}", flush=True)

        proxy_moi = lay_proxy_tu_api()
        if not proxy_moi:
            print("🛑 Không lấy được Proxy. Tạm dừng vòng này...", flush=True)
            if lan_thu < MAX_RETRIES:
                print("⏳ Đang ngủ 60 giây trước khi thử lại...", flush=True)
                time.sleep(60)
            continue

        cau_hinh_proxy = {"server": f"http://{proxy_moi}"}
        so_tram_loi_vong_nay = 0
        so_tram_ok_vong_nay = 0

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

                def quet_trang(ten_nhom, url_trang_chu, keyword_link, chia_mon=False):
                    nonlocal so_tram_loi_vong_nay, so_tram_ok_vong_nay
                    page = context.new_page() # Mở Tab riêng biệt cho từng trạm
                    print(f"\n📥 ĐANG QUÉT SERVER: {ten_nhom.upper()}", flush=True)
                    
                    ket_qua_tram = [] # Kết quả tạm của riêng trạm này
                    
                    try:
                        page.goto(url_trang_chu, timeout=60000)
                        print("⏳ Đang rình Cloudflare mở cửa...", flush=True)
                        
                        page.wait_for_function(f"document.querySelectorAll('a[href*=\"{keyword_link}\"]').length > 0", timeout=60000)
                        page.wait_for_timeout(5000)
                        
                        if chia_mon:
                            # === XOILAC: Quét kèm môn thể thao từ data-sport ===
                            danh_sach_raw = page.evaluate(f"""
                                (() => {{
                                    const results = [];
                                    // Lấy từ grid chính (có data-sport)
                                    document.querySelectorAll('.grid-matches__item').forEach(item => {{
                                        const sport = item.getAttribute('data-sport') || 'football';
                                        const linkEl = item.querySelector('a[href*="{keyword_link}"]');
                                        if (!linkEl) return;
                                        const img = item.querySelector('img');
                                        results.push({{
                                            url: linkEl.href,
                                            ten: linkEl.getAttribute('title') || linkEl.innerText.trim().replace(/\\n/g, ' - '),
                                            thumb: img ? img.src : "https://img.icons8.com/color/512/football2.png",
                                            sport: sport
                                        }});
                                    }});
                                    // Lấy thêm từ thanh ngang (match-horizontals) - mặc định là football
                                    document.querySelectorAll('.match-horizontals-item[href*="{keyword_link}"]').forEach(a => {{
                                        const url = a.href;
                                        if (results.some(r => r.url === url)) return; // Đã có rồi thì bỏ qua
                                        const img = a.querySelector('img');
                                        results.push({{
                                            url: url,
                                            ten: a.innerText.trim().replace(/\\n/g, ' - '),
                                            thumb: img ? img.src : "https://img.icons8.com/color/512/football2.png",
                                            sport: 'football'
                                        }});
                                    }});
                                    return results;
                                }})()
                            """)
                        else:
                            # === CÁC SERVER KHÁC: Quét bình thường ===
                            danh_sach_raw = page.evaluate(f"""
                                Array.from(document.querySelectorAll('a[href*="{keyword_link}"]')).map(a => {{
                                    let img = a.querySelector('img');
                                    return {{
                                        url: a.href,
                                        ten: a.innerText.trim().replace(/\\n/g, ' - '),
                                        thumb: img ? img.src : "https://img.icons8.com/color/512/football2.png",
                                        sport: ''
                                    }}
                                }})
                            """)
                        
                        danh_sach_phong = {}
                        for item in danh_sach_raw:
                            url = item['url']
                            ten = item['ten']
                            thumb = item['thumb']
                            sport = item.get('sport', '')
                            if url == url_trang_chu or url == url_trang_chu + "/": continue
                            
                            if url not in danh_sach_phong or len(ten) > len(danh_sach_phong.get(url, {}).get('ten', "")):
                                danh_sach_phong[url] = {
                                    'ten': ten if ten else "Trận đấu đang chờ cập nhật",
                                    'thumb': thumb,
                                    'sport': sport
                                }

                        tong_so_tran = len(danh_sach_phong)
                        print(f"🎯 Phát hiện {tong_so_tran} phòng chiếu tại {ten_nhom}!", flush=True)
                        
                        # In chi tiết theo môn nếu chia môn
                        if chia_mon:
                            mon_dem = {}
                            for d in danh_sach_phong.values():
                                mon_vn = SPORT_MAP.get(d['sport'], d['sport'])
                                mon_dem[mon_vn] = mon_dem.get(mon_vn, 0) + 1
                            print(f"   📋 Chia theo môn: {', '.join(f'{k}: {v}' for k, v in mon_dem.items())}", flush=True)

                        for stt, (link_phong, data_phong) in enumerate(danh_sach_phong.items(), 1):
                            ten_tran = data_phong['ten']
                            anh_thumb = data_phong['thumb']
                            sport_key = data_phong.get('sport', '')
                            
                            # Xác định tên nhóm trong M3U
                            if chia_mon and sport_key:
                                ten_mon_vn = SPORT_MAP.get(sport_key, sport_key.capitalize())
                                nhom_m3u = f"{ten_nhom} - {ten_mon_vn}"
                            else:
                                nhom_m3u = ten_nhom
                            
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
                            finally:
                                # Luôn dọn listener dù có lỗi hay không
                                page.remove_listener("request", bat_goi_tin)
                            
                            if stream_link:
                                ket_qua_tram.append({
                                    'nhom': nhom_m3u,
                                    'ten': ten_tran,
                                    'link': stream_link,
                                    'thumb': anh_thumb
                                })
                        
                        # Trạm này quét THÀNH CÔNG → ghi nhận & giữ kết quả
                        so_tram_ok_vong_nay += 1
                        server_da_thanh_cong.add(ten_nhom)
                        danh_sach_phat.extend(ket_qua_tram)
                        print(f"✅ {ten_nhom}: Thu hoạch {len(ket_qua_tram)} luồng stream!", flush=True)

                    except Exception as e:
                        print(f"⚠️ Kẹt tường lửa hoặc web sập: {e}", flush=True)
                        so_tram_loi_vong_nay += 1
                    finally:
                        page.close() # Dọn dẹp sạch sẽ Tab sau khi xong việc

                # Quét từng server chưa thành công
                for ten_nhom, url_tc, keyword, chia_mon in server_can_quet:
                    quet_trang(ten_nhom, url_tc, keyword, chia_mon)

                browser.close()
        except Exception as e:
            print(f"🔥 Lỗi hệ thống cốt lõi: {e}", flush=True)

        # ==========================================
        # ĐÁNH GIÁ CHẤT LƯỢNG VÒNG QUÉT
        # ==========================================
        print(f"\n📊 Kết quả vòng {lan_thu}: ✅ {so_tram_ok_vong_nay} OK, ❌ {so_tram_loi_vong_nay} fail", flush=True)
        print(f"📊 Tổng tích lũy: {len(danh_sach_phat)} luồng từ {len(server_da_thanh_cong)}/{len(tat_ca_server)} server", flush=True)

        # Proxy hoàn toàn xịt nếu KHÔNG quét được server nào trong vòng này
        if so_tram_ok_vong_nay == 0 and so_tram_loi_vong_nay > 0 and lan_thu < MAX_RETRIES:
            print("⚠️ Proxy hoàn toàn xịt vòng này. Ngủ 60s xin IP mới...", flush=True)
            time.sleep(60)
            continue

        # Vẫn còn server chưa quét được → thử tiếp vòng sau
        if len(server_da_thanh_cong) < len(tat_ca_server) and lan_thu < MAX_RETRIES:
            server_con_lai = [s[0] for s in tat_ca_server if s[0] not in server_da_thanh_cong]
            print(f"🔄 Còn {len(server_con_lai)} server chưa quét được: {', '.join(server_con_lai)}", flush=True)
            print("⏳ Ngủ 60 giây rồi xin IP mới để thử server còn lại...", flush=True)
            time.sleep(60)
            continue

        # Tất cả server đã OK
        print("🏆 Tất cả server đã quét xong!", flush=True)
        break

    # ==========================================
    # LỌC TRÙNG & ĐÓNG GÓI KẾT QUẢ CUỐI CÙNG
    # ==========================================
    seen_links = set()
    danh_sach_sach = []
    for luong in danh_sach_phat:
        if luong['link'] not in seen_links:
            seen_links.add(luong['link'])
            danh_sach_sach.append(luong)

    if danh_sach_sach:
        da_loc = len(danh_sach_phat) - len(danh_sach_sach)
        if da_loc > 0:
            print(f"🧹 Đã lọc {da_loc} link trùng lặp.", flush=True)

        print(f"\n📦 ĐANG ĐÓNG GÓI M3U VÀ CHIA THƯ MỤC...", flush=True)
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            for luong in danh_sach_sach:
                file.write(f'#EXTINF:-1 group-title="{luong["nhom"]}" tvg-logo="{luong["thumb"]}", ⚽ {luong["ten"]}\n')
                file.write(f'{luong["link"]}\n')
                
        print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_sach)} TRẬN!", flush=True)
        # In chi tiết theo từng nhóm
        nhom_count = {}
        for l in danh_sach_sach:
            nhom_count[l['nhom']] = nhom_count.get(l['nhom'], 0) + 1
        print(f"📊 Chi tiết: {', '.join(f'{k}: {v}' for k, v in nhom_count.items())}", flush=True)
    else:
        print(f"❌ ĐÃ THỬ HẾT {MAX_RETRIES} LẦN NHƯNG VẪN THẤT BẠI. HẸN CHU KỲ SAU!", flush=True)
        with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")

if __name__ == "__main__":
    san_full_server_qua_proxy()
