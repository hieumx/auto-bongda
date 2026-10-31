import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests
import json
import time
import re
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

STATIC_PROXY = {
    "server": "http://14.241.72.139:10906",
    "username": "hieumx",
    "password": "hieu123"
}

# ==========================================
# 1. BỘ THU HOẠCH TỐC ĐỘ CAO (DIRECT APIS TỪ GETOUT APK)
# ==========================================

_DOMAIN_CACHE = {}

def lay_domain_dong(provider_name, default_url):
    """Lấy domain cập nhật tự động từ kho dữ liệu GetOut nếu có"""
    if provider_name in _DOMAIN_CACHE:
        return _DOMAIN_CACHE[provider_name]
    try:
        url = f"https://raw.githubusercontent.com/leeshin5757/getout/main/txt/{provider_name}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.text.strip():
            link = r.text.strip().split('|')[0].strip()
            if link.startswith('http'):
                _DOMAIN_CACHE[provider_name] = link
                return link
    except Exception:
        pass
    _DOMAIN_CACHE[provider_name] = default_url
    return default_url

def thu_hoach_socolive_api():
    """Thu hoạch Socolive qua JSON API trực tiếp (siêu tốc, không kẹt Cloudflare)"""
    streams = []
    print("\n⚡ [Socolive API] Đang kết nối trực tiếp json.vnres.co...", flush=True)
    try:
        url = f"https://json.vnres.co/all_live_rooms.json?v={int(time.time())}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        text = r.text.strip()
        if '(' in text and ')' in text:
            text = text[text.find('(')+1 : text.rfind(')')]
        data = json.loads(text)
        rooms_dict = data.get('data', {})
        
        all_rooms = []
        if isinstance(rooms_dict, dict):
            for k, room_list in rooms_dict.items():
                if isinstance(room_list, list):
                    all_rooms.extend(room_list)
        elif isinstance(rooms_dict, list):
            all_rooms = rooms_dict
            
        print(f"   🎯 Phát hiện {len(all_rooms)} phòng đang phát sóng!", flush=True)
        
        def fetch_detail(room):
            room_num = room.get('roomNum') or room.get('id')
            title = room.get('title') or 'Socolive Match'
            anchor = room.get('anchor', {})
            blv_name = anchor.get('nickName', '')
            thumb = anchor.get('cutOutIcon') or anchor.get('icon') or "https://img.icons8.com/color/512/football2.png"
            try:
                d_url = f"https://json.vnres.co/room/{room_num}/detail.json?v={int(time.time())}"
                dr = requests.get(d_url, headers=HEADERS, timeout=5)
                d_text = dr.text.strip()
                if '(' in d_text and ')' in d_text:
                    d_text = d_text[d_text.find('(')+1 : d_text.rfind(')')]
                d_json = json.loads(d_text)
                st = d_json.get('data', {}).get('stream', {})
                stream_url = st.get('hdM3u8') or st.get('m3u8') or st.get('hdFlv') or st.get('flv')
                if stream_url:
                    name_full = f"{title} (BLV {blv_name})" if blv_name else title
                    return {
                        'nhom': 'Socolive - Trực tiếp',
                        'ten': name_full,
                        'link': stream_url,
                        'thumb': thumb
                    }
            except Exception:
                pass
            return None

        # Tải đa luồng song song 15 luồng cùng lúc
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = executor.map(fetch_detail, all_rooms)
            for res in results:
                if res:
                    streams.append(res)
                    
        print(f"✅ Socolive API: Thu hoạch thành công {len(streams)} luồng stream!", flush=True)
    except Exception as e:
        print(f"⚠️ Socolive API gặp lỗi: {e}", flush=True)
    return streams

def thu_hoach_gavang_api():
    """Thu hoạch Gà Vàng / Giờ Vàng qua API thể thao trực tiếp"""
    streams = []
    print("\n⚡ [Gà Vàng API] Đang kết nối trực tiếp live-api...", flush=True)
    try:
        url = f"https://live-api.keonhacaitp.one/storage/livestream/live.json?t={int(time.time())}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        matches = data.get('response', [])
        print(f"   🎯 Phát hiện {len(matches)} trận đấu đang live!", flush=True)
        
        def fetch_match(m):
            res_list = []
            match_id = m.get('id')
            teams = m.get('teams', {})
            home = teams.get('home', {}).get('name', 'Đội nhà')
            away = teams.get('away', {}).get('name', 'Đội khách')
            league = m.get('league', {}).get('name', '')
            sport = m.get('type') or 'football'
            thumb = teams.get('home', {}).get('logo') or "https://img.icons8.com/color/512/football2.png"
            try:
                f_url = f"https://live-api.keonhacaitp.one/api/fixtures/{match_id}"
                fr = requests.get(f_url, headers=HEADERS, timeout=5)
                fd = fr.json()
                f_resp = fd.get('response', {})
                blv_list = f_resp.get('blv', [])
                for b in blv_list:
                    stream_url = b.get('linkStreamHd') or b.get('pc_stream_url') or b.get('mobile_stream_url') or b.get('linkStreamSd')
                    blv_name = b.get('name') or b.get('blvName') or ''
                    if stream_url:
                        name_full = f"[{league}] {home} vs {away}" + (f" (BLV {blv_name})" if blv_name else "")
                        group_name = f"GaVang - {'Bóng đá' if sport == 'football' else sport.capitalize()}"
                        res_list.append({
                            'nhom': group_name,
                            'ten': name_full,
                            'link': stream_url,
                            'thumb': thumb
                        })
            except Exception:
                pass
            return res_list

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_match, matches)
            for r_list in results:
                streams.extend(r_list)
                
        print(f"✅ Gà Vàng API: Thu hoạch thành công {len(streams)} luồng stream!", flush=True)
    except Exception as e:
        print(f"⚠️ Gà Vàng API gặp lỗi: {e}", flush=True)
    return streams

def thu_hoach_kenh_truyen_hinh():
    """Tải các kênh truyền hình Thể thao, World Cup, VTV từ kho dữ liệu APK"""
    streams = []
    m3u_file = "kenh_truyen_hinh.m3u"
    if not os.path.exists(m3u_file):
        return streams
    try:
        with open(m3u_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        cur_info = None
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF"):
                grp_match = re.search(r'group-title="([^"]+)"', line)
                grp = grp_match.group(1) if grp_match else "Truyền hình"
                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                logo = logo_match.group(1) if logo_match else ""
                name = line.split(",")[-1].strip()
                cur_info = {'nhom': f"TV - {grp}", 'ten': name, 'thumb': logo}
            elif line.startswith("http") and cur_info:
                cur_info['link'] = line
                streams.append(cur_info)
                cur_info = None
        print(f"📺 [Truyền Hình 24/7] Đã nạp {len(streams)} kênh TV & Thể thao từ kho dữ liệu!", flush=True)
    except Exception as e:
        print(f"⚠️ Không nạp được kênh truyền hình: {e}", flush=True)
    return streams


# ==========================================
# 2. BỘ ĐIỀU KHIỂN TRÌNH DUYỆT (PLAYWRIGHT CHO CÁC SERVER CÒN LẠI)
# ==========================================

def san_browser_servers(danh_sach_phat, server_da_thanh_cong):
    """Chạy Playwright với tối ưu domcontentloaded cho Thapcam, Thiendinh, Xoilac, Quechoa"""
    tat_ca_server = [
        ("Xoilac", lay_domain_dong("xoilactv", "https://xoilacz.vip"), "/truc-tiep/", "xoilac"),
        ("Quechoa", lay_domain_dong("quechatv", "https://quechoa5.live"), "/truc-tiep/", "chuan"),
        ("ThienDinh", "https://sv2.thiendinh3.live/trang-chu", "", "thiendinh"),
        ("Hoiquan", "https://sv2.hoiquan6.live/trang-chu", "", "thiendinh"),
        ("Thapcam", "https://thapcamtivi.app", "/truc-tiep", "thapcam"),
        ("BiaOm", lay_domain_dong("biaomtv", "https://biaomtv.in/live"), "/live/", "chuan"),
        ("ChuoiChien", lay_domain_dong("chuoichien", "https://live03.chuoichientv.me"), "/live", "chuan"),
        ("BongLau", lay_domain_dong("bonglau", "https://lau03.bonglautv1.org"), "/live", "chuan"),
        ("CoLa", lay_domain_dong("colatv", "https://colatv.live"), "", "chuan"),
        ("SaoKe", lay_domain_dong("saoke", "https://vip3.saoketv40.xyz"), "", "chuan"),
        ("RungTv", lay_domain_dong("rungtv", "https://live1.rung90tv1.xyz"), "", "chuan"),
        ("S8", lay_domain_dong("s8", "https://s8tv011.com"), "", "chuan"),
        ("BTV", lay_domain_dong("btv", "https://bongplus.vip"), "", "chuan"),
        ("KhanDai", lay_domain_dong("khandai", "https://khandaia.pro"), "", "chuan"),
    ]

    server_can_quet = [s for s in tat_ca_server if s[0] not in server_da_thanh_cong]
    if not server_can_quet:
        return

    print(f"\n🌐 [Trình duyệt Web] Quét bổ sung các server: {', '.join(s[0] for s in server_can_quet)}", flush=True)

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
        "billiards": "Billiards",
    }

    def _loc_trung(danh_sach_raw, url_goc):
        result = {}
        for item in danh_sach_raw:
            url = item.get('url', '')
            ten = item.get('ten', '').strip()
            if not url or url == url_goc or url == url_goc + "/":
                continue
            if url not in result or len(ten) > len(result.get(url, {}).get('ten', '')):
                result[url] = {
                    'ten': ten if ten else "Trận đấu đang chờ cập nhật",
                    'thumb': item.get('thumb', 'https://img.icons8.com/color/512/football2.png'),
                    'sport': item.get('sport', '')
                }
        return result

    def lay_phong_xoilac(page, url_goc, keyword_link):
        raw = page.evaluate(f"""
            (() => {{
                const results = [];
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
                document.querySelectorAll('.match-horizontals-item[href*="{keyword_link}"]').forEach(a => {{
                    const url = a.href;
                    if (results.some(r => r.url === url)) return;
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
        return _loc_trung(raw, url_goc)

    def lay_phong_thapcam(page, url_goc):
        raw = page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="/truc-tiep"]')).map(a => {
                let img = a.querySelector('img');
                let parent = a.closest('.match-card') || a.closest('li') || a.closest('.item') || a.parentElement.parentElement;
                let rawText = parent ? parent.innerText : a.innerText;
                let cleanText = rawText.trim().split('\\n').join(' - ').replace(/  +/g, ' ').replace(/XEM LIVE/g, '').replace(/ - - /g, ' - ').trim();
                if (cleanText.startsWith('- ')) cleanText = cleanText.substring(2);
                if (cleanText.endsWith(' -')) cleanText = cleanText.substring(0, cleanText.length - 2);
                
                let sport = 'football';
                if (a.href.includes('bong-ro') || a.href.includes('basketball')) sport = 'basketball';
                else if (a.href.includes('tennis')) sport = 'tennis';
                else if (a.href.includes('bong-chuyen')) sport = 'volleyball';
                else if (a.href.includes('esport')) sport = 'esports';

                return {
                    url: a.href,
                    ten: cleanText || 'Trận đấu',
                    thumb: img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '',
                    sport: sport
                }
            }).filter(r => r.ten.length > 3)
        """)
        return _loc_trung(raw, url_goc)

    def lay_phong_thiendinh(page, url_goc):
        all_rooms = {}
        mon_sidebar = [
            ("Bóng đá", "Bóng đá"),
            ("Bóng chuyền", "Bóng chuyền"),
            ("Tennis", "Tennis"),
            ("Billiards", "Billiards"),
            ("Esports", "Esports"),
            ("Cầu lông", "Cầu lông"),
        ]

        def _get_thiendinh_rooms():
            return page.evaluate("""
                (() => {
                    const results = [];
                    const seen = new Set();
                    const navTexts = ['Trực tuyến','Bóng đá','Bóng chuyền','Billiards','Esports','Cầu lông','Tennis','Trang chủ','Lịch thi đấu','Kết quả','Xem lại'];
                    const mainEl = document.querySelector('main, [class*="content"], [class*="match"], [class*="list"]') || document.body;
                    mainEl.querySelectorAll('a[href]').forEach(a => {
                        const href = a.getAttribute('href') || '';
                        if (!href || href === '/' || href === '/trang-chu' || href === '#') return;
                        if (href.startsWith('javascript:')) return;
                        if (href.startsWith('http') && !href.includes(location.hostname)) return;
                        if (seen.has(href)) return;
                        const text = (a.textContent || '').trim();
                        if (navTexts.includes(text)) return;
                        if (!text || text.length < 2) return;
                        seen.add(href);
                        const img = a.querySelector('img');
                        const cleanText = text.split('\\n').join(' - ').replace(/  +/g, ' ').trim();
                        results.push({
                            url: a.href,
                            ten: cleanText || 'Trận đấu',
                            thumb: img ? (img.src || img.getAttribute('data-src') || '') : ''
                        });
                    });
                    return results;
                })()
            """)

        for ten_mon, sport_key in mon_sidebar:
            try:
                page.locator(f"aside >> text={ten_mon}").first.click(timeout=3000)
                page.wait_for_timeout(1500)
                rooms = _get_thiendinh_rooms()
                for r in rooms:
                    r['sport'] = sport_key
                all_rooms.update(_loc_trung(rooms, url_goc))
            except Exception:
                pass

        if not all_rooms:
            rooms = _get_thiendinh_rooms()
            all_rooms = _loc_trung(rooms, url_goc)

        return all_rooms

    def lay_phong_chuan(page, url_goc, keyword_link):
        raw = page.evaluate(f"""
            (() => {{
                const kw = "{keyword_link}";
                const results = [];
                const seen = new Set();
                document.querySelectorAll('a').forEach(a => {{
                    const href = a.href || '';
                    if (!href || href === location.href || href === location.origin + '/' || href.startsWith('javascript:')) return;
                    if (kw) {{
                        if (!href.includes(kw)) return;
                    }} else {{
                        const isMatchLink = ['/truc-tiep', '/live', '/match', '/room', '/watch'].some(k => href.includes(k));
                        if (!isMatchLink) return;
                    }}
                    if (seen.has(href)) return;
                    seen.add(href);
                    let rawText = (a.innerText || '').trim().split('\\n').join(' - ').replace(/  +/g, ' ');
                    let text = rawText.replace(/XEM LIVE/g, '').replace(/SẮP DIỄN RA/g, '').replace(/ - - /g, ' - ').trim();
                    if (text.startsWith('- ')) text = text.substring(2).trim();
                    if (text.endsWith(' -')) text = text.substring(0, text.length - 2).trim();
                    if (text.length < 3) return;
                    const img = a.querySelector('img');
                    results.push({{
                        url: href,
                        ten: text,
                        thumb: img ? (img.src || img.getAttribute('data-src') || '') : 'https://img.icons8.com/color/512/football2.png',
                        sport: ''
                    }});
                }});
                return results;
            }})()
        """)
        return _loc_trung(raw, url_goc)

    # Thử chạy: ưu tiên Direct Connection nếu không cấu hình PROXY_REQUIRED
    # để tránh proxy chết kéo theo cả hệ thống
    configs_to_try = [None, STATIC_PROXY]

    for cfg_proxy in configs_to_try:
        proxy_label = "Proxy" if cfg_proxy else "Kết nối trực tiếp"
        servers_success_count = 0
        try:
            with sync_playwright() as p:
                launch_kwargs = {
                    "headless": True,
                    "args": ["--disable-blink-features=AutomationControlled"]
                }
                if cfg_proxy:
                    launch_kwargs["proxy"] = cfg_proxy

                browser = p.chromium.launch(**launch_kwargs)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )

                def chan_tai_nguyen(route):
                    if route.request.resource_type in ["image", "media"]:
                        route.abort()
                    else:
                        route.continue_()
                context.route("**/*", chan_tai_nguyen)

                for ten_nhom, url_trang_chu, keyword_link, kieu_quet in server_can_quet:
                    if ten_nhom in server_da_thanh_cong:
                        continue

                    print(f"\n📥 ĐANG QUÉT SERVER: {ten_nhom.upper()} ({proxy_label})", flush=True)
                    page = context.new_page()
                    try:
                        page.goto(url_trang_chu, timeout=8000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2000)

                        if kieu_quet == "xoilac":
                            danh_sach_phong = lay_phong_xoilac(page, url_trang_chu, keyword_link)
                        elif kieu_quet == "thapcam":
                            danh_sach_phong = lay_phong_thapcam(page, url_trang_chu)
                        elif kieu_quet == "thiendinh":
                            danh_sach_phong = lay_phong_thiendinh(page, url_trang_chu)
                        else:
                            danh_sach_phong = lay_phong_chuan(page, url_trang_chu, keyword_link)

                        print(f"🎯 Phát hiện {len(danh_sach_phong)} phòng chiếu tại {ten_nhom}!", flush=True)

                        thu_duoc = 0
                        for link_phong, info in list(danh_sach_phong.items())[:6]:
                            stream_link_found = None
                            def bat_goi_tin(request):
                                nonlocal stream_link_found
                                if any(ext in request.url for ext in [".m3u8", ".flv"]) and "thumb" not in request.url and not stream_link_found:
                                    stream_link_found = request.url

                            page.on("request", bat_goi_tin)
                            try:
                                # Đối với Xoilac, luôn vào sublink /link/0 để player kích hoạt luồng phát
                                link_dich = link_phong
                                if "xoilac" in link_phong and "/link/" not in link_phong:
                                    link_dich = link_phong.rstrip("/") + "/link/0"

                                page.goto(link_dich, timeout=8000, wait_until="domcontentloaded")
                                page.wait_for_timeout(1800)
                                if stream_link_found:
                                    sport_text = SPORT_MAP.get(info.get('sport', ''), info.get('sport', ''))
                                    nhom_full = f"{ten_nhom} - {sport_text}" if sport_text else f"{ten_nhom} - Trực tiếp"
                                    danh_sach_phat.append({
                                        'nhom': nhom_full,
                                        'ten': info['ten'],
                                        'link': stream_link_found,
                                        'thumb': info['thumb']
                                    })
                                    thu_duoc += 1
                            except Exception:
                                pass
                            finally:
                                page.remove_listener("request", bat_goi_tin)

                        print(f"✅ {ten_nhom}: Thu hoạch {thu_duoc} luồng stream!", flush=True)
                        if thu_duoc > 0:
                            server_da_thanh_cong.add(ten_nhom)
                            servers_success_count += 1
                    except Exception as e:
                        print(f"⚠️ {ten_nhom} tạm thời chưa kết nối được: {e}", flush=True)
                    finally:
                        page.close()

                browser.close()
                if servers_success_count > 0:
                    break
        except Exception as e:
            print(f"⚠️ Chạy browser qua {proxy_label} lỗi ({e}), chuyển sang chế độ tiếp theo...", flush=True)


# ==========================================
# 3. CHƯƠNG TRÌNH ĐIỀU PHỐI CHÍNH
# ==========================================

def san_full_server_sieu_toc():
    t_start = time.time()
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH LINK THỂ THAO & IPTV (HYBRID ENGINE)...", flush=True)
    print("==========================================================================", flush=True)

    danh_sach_phat = []
    server_da_thanh_cong = set()

    # --- BƯỚC 1: QUÉT SIÊU TỐC QUA DIRECT API (SOCOLIVE, GAVANG) ---
    soco_streams = thu_hoach_socolive_api()
    if soco_streams:
        danh_sach_phat.extend(soco_streams)
        server_da_thanh_cong.add("Socolive")

    gavang_streams = thu_hoach_gavang_api()
    if gavang_streams:
        danh_sach_phat.extend(gavang_streams)
        server_da_thanh_cong.add("Gavang")

    # --- BƯỚC 2: QUÉT BỔ SUNG CÁC TRANG CÒN LẠI BẰNG BROWSER ---
    san_browser_servers(danh_sach_phat, server_da_thanh_cong)

    # --- BƯỚC 3: NẠP KÊNH TRUYỀN HÌNH WORLD CUP, VTV, THỂ THAO TỪ APK ---
    tv_streams = thu_hoach_kenh_truyen_hinh()
    if tv_streams:
        danh_sach_phat.extend(tv_streams)

    # --- BƯỚC 4: LỌC TRÙNG & XUẤT FILE M3U CHUẨN ---
    seen_links = set()
    danh_sach_sach = []
    for luong in danh_sach_phat:
        link = luong.get('link', '').strip()
        if link and link not in seen_links:
            seen_links.add(link)
            danh_sach_sach.append(luong)

    print("\n==========================================================================", flush=True)
    print("📦 ĐANG ĐÓNG GÓI M3U VÀ PHÂN LOẠI DANH MỤC...", flush=True)
    with open("tong_hop_bong_da.m3u", "w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        for luong in danh_sach_sach:
            logo = luong.get("thumb", "")
            ten = luong.get("ten", "Trực tiếp")
            nhom = luong.get("nhom", "Thể thao")
            file.write(f'#EXTINF:-1 group-title="{nhom}" tvg-logo="{logo}", ⚽ {ten}\n')
            file.write(f'{luong["link"]}\n')

    duration = time.time() - t_start
    print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_sach)} KÊNH & TRẬN ĐẤU TRONG {duration:.2f}s!", flush=True)
    nhom_count = {}
    for l in danh_sach_sach:
        nhom = l.get('nhom', 'Khác')
        nhom_count[nhom] = nhom_count.get(nhom, 0) + 1
    print(f"📊 Chi tiết danh mục: {', '.join(f'{k}: {v}' for k, v in list(nhom_count.items())[:10])}...", flush=True)

if __name__ == "__main__":
    san_full_server_sieu_toc()
