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

def lay_domain_bitly(slug, default_url, suffix=""):
    """Lấy domain mới qua redirect bit.ly/<slug>; bỏ qua nếu redirect sang youtube/docs..."""
    key = f"bitly:{slug}"
    if key in _DOMAIN_CACHE:
        return _DOMAIN_CACHE[key]
    try:
        r = requests.head(f'https://bit.ly/{slug}', allow_redirects=False, timeout=3)
        loc = r.headers.get('Location') or ''
        if loc.startswith('http') and not any(x in loc for x in ('youtube.', 'google.', 'pastes.io')):
            target = loc.rstrip('/') + suffix
            _DOMAIN_CACHE[key] = target
            return target
    except Exception:
        pass
    _DOMAIN_CACHE[key] = default_url
    return default_url

def lay_domain_hoiquan():
    """Lấy domain cập nhật tự động của Hội Quán TV qua Bitly redirect hoặc fallback"""
    if "hoiquantv" in _DOMAIN_CACHE:
        return _DOMAIN_CACHE["hoiquantv"]
    try:
        r = requests.head('https://bit.ly/hoiquantv', allow_redirects=False, timeout=3)
        loc = r.headers.get('Location')
        if loc and loc.startswith('http'):
            target = loc.rstrip('/') + '/trang-chu'
            _DOMAIN_CACHE["hoiquantv"] = target
            return target
    except Exception:
        pass
    fallback = lay_domain_dong("hoiquantv", "https://hoiquan6.tv/trang-chu")
    _DOMAIN_CACHE["hoiquantv"] = fallback
    return fallback

def thu_hoach_phim_phim4k():
    """Thu hoạch kho phim lẻ, phim bộ và anime hot từ Phim4K APK (KKPhim direct API)"""
    streams = []
    print("\n🎬 [Phim4K Engine] Đang thu hoạch kho phim chiếu rạp, phim bộ & anime...", flush=True)
    t0 = time.time()
    sources = [
        ("🎬 Phim Lẻ Chiếu Rạp", "https://phimapi.com/v1/api/danh-sach/phim-le?page=1&limit=15"),
        ("🎬 Phim Bộ Mới Nhất", "https://phimapi.com/v1/api/danh-sach/phim-bo?page=1&limit=15"),
        ("🎬 Hoạt Hình - Anime", "https://phimapi.com/v1/api/danh-sach/hoat-hinh?page=1&limit=15"),
    ]
    movie_tasks = []
    for grp, list_url in sources:
        try:
            r = requests.get(list_url, headers=HEADERS, timeout=6)
            d = r.json()
            items = d.get("data", {}).get("items", []) if "data" in d else d.get("items", [])
            for item in items:
                slug = item.get("slug")
                if slug:
                    movie_tasks.append((slug, grp))
        except Exception:
            pass

    def fetch_movie_detail(task):
        slug, group_name = task
        try:
            url = f"https://phimapi.com/phim/{slug}"
            r = requests.get(url, headers=HEADERS, timeout=6)
            data = r.json()
            movie = data.get("movie", {})
            name = movie.get("name") or slug
            thumb = movie.get("thumb_url") or movie.get("poster_url") or ""
            episodes = data.get("episodes", [])
            if episodes:
                server_data = episodes[0].get("server_data", [])
                if server_data:
                    ep = server_data[-1] if len(server_data) > 1 else server_data[0]
                    ep_name = ep.get("name")
                    m3u8 = ep.get("link_m3u8")
                    if m3u8 and m3u8.startswith("http"):
                        display_name = f"{name} ({ep_name})" if len(server_data) > 1 else name
                        return {
                            'nhom': group_name,
                            'ten': display_name,
                            'link': m3u8,
                            'thumb': thumb
                        }
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(fetch_movie_detail, movie_tasks)
        for res in results:
            if res:
                streams.append(res)
    print(f"✅ Phim4K Engine: Thu hoạch thành công {len(streams)} phim 1080p trong {time.time()-t0:.2f}s!", flush=True)
    return streams

HH3D_SERIES = [
    {"slug": "tien-nghich", "title": "Tiên Nghịch"},
    {"slug": "pham-nhan-tu-tien", "title": "Phàm Nhân Tu Tiên"},
    {"slug": "dau-pha-thuong-khung-phan-5", "title": "Đấu Phá Thương Khung (P5)"},
    {"slug": "the-gioi-hoan-my", "title": "Thế Giới Hoàn Mỹ"},
    {"slug": "gia-thien", "title": "Già Thiên"},
    {"slug": "thon-phe-tinh-khong", "title": "Thôn Phệ Tinh Không"},
    {"slug": "muc-than-ky", "title": "Mục Thần Ký"},
    {"slug": "quang-am-chi-ngoai", "title": "Quang Âm Chi Ngoại"},
    {"slug": "kiem-lai-phan-2", "title": "Kiếm Lai (P2)"},
    {"slug": "dai-vuong-tha-mang-phan-3", "title": "Đại Vương Tha Mạng (P3)"},
    {"slug": "dau-la-dai-luc-2-tuyet-the-duong-mon", "title": "Đấu La Đại Lục 2"},
    {"slug": "nhat-niem-vinh-hang", "title": "Nhất Niệm Vĩnh Hằng"},
    {"slug": "dai-phung-da-canh-nhan", "title": "Đại Phụng Đả Canh Nhân"}
]

def thu_hoach_hoat_hinh_3d_full():
    """Thu hoạch trọn bộ Full Series Hoạt hình 3D (Donghua YanHH3D) với toàn bộ tập phát sóng"""
    print("\n🎬 [YanHH3D Engine] Đang thu hoạch trọn bộ Full Series Hoạt Hình 3D Trung Quốc...", flush=True)
    t0 = time.time()
    all_eps = []

    def fetch_series(item):
        slug = item["slug"]
        series_title = item["title"]
        url = f"https://phimapi.com/phim/{slug}"
        eps_list = []
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                d = r.json()
                movie = d.get('movie', {})
                poster = movie.get('poster_url') or movie.get('thumb_url') or ""
                episodes = d.get('episodes', [])
                if episodes:
                    server_data = episodes[0].get('server_data', [])
                    group_name = f"🎬 HH3D - {series_title}"
                    for ep in server_data:
                        ep_name = ep.get('name', '')
                        m3u8 = ep.get('link_m3u8', '')
                        if m3u8 and m3u8.startswith('http'):
                            eps_list.append({
                                'nhom': group_name,
                                'ten': f"{series_title} - {ep_name}",
                                'link': m3u8,
                                'thumb': poster
                            })
        except Exception:
            pass
        return eps_list

    with ThreadPoolExecutor(max_workers=13) as executor:
        results = executor.map(fetch_series, HH3D_SERIES)
        for res in results:
            all_eps.extend(res)

    print(f"✅ YanHH3D Engine: Thu hoạch thành công {len(all_eps)} tập phim full series trong {time.time()-t0:.2f}s!", flush=True)
    return all_eps


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

def thu_hoach_colatv_gavang24h_api():
    """Thu hoạch ColaTV, Gà Vàng 24h, Gà Vàng 333, Giờ Vàng qua Direct JSON API"""
    streams = []
    print("\n⚡ [ColaTV & Gà Vàng 24h API] Đang kết nối trực tiếp api.gvapi.cc...", flush=True)
    urls = [
        "https://api.gvapi.cc/api/matches",
        "https://api.cltvlv.com/api/matches"
    ]
    data = None
    for u in urls:
        try:
            r = requests.get(u, headers=HEADERS, timeout=6)
            if r.status_code == 200:
                data = r.json().get('data', {})
                break
        except Exception:
            pass

    if not data:
        print("   ⚠️ Không kết nối được API ColaTV / Gà Vàng 24h", flush=True)
        return streams

    for k, m in data.items():
        comp = m.get('competitionName') or ''
        home = m.get('homeTeamName') or 'Đội nhà'
        away = m.get('awayTeamName') or 'Đội khách'
        sport_id = m.get('sportId') or 1
        sport_name = "Bóng đá" if sport_id == 1 else ("Bóng rổ" if sport_id == 2 else "Thể thao")
        thumb = m.get('homeTeamLogo') or "https://img.icons8.com/color/512/football2.png"
        vurl = m.get('videoUrl') or m.get('video_url')

        if vurl and vurl.startswith('http'):
            streams.append({
                'nhom': f"ColaTV - {sport_name}",
                'ten': f"[{comp}] {home} vs {away}",
                'link': vurl,
                'thumb': thumb
            })

        for a in m.get('anchorAppointmentVoList') or []:
            blv_name = a.get('nickName') or a.get('anchorName') or ''
            st_url = a.get('playStreamAddress') or a.get('playStreamAddress2')
            if st_url and st_url.startswith('http'):
                m3u8_url = st_url.replace('.flv', '.m3u8')
                blv_thumb = a.get('userImage') or thumb
                streams.append({
                    'nhom': f"GaVang24h - {sport_name}",
                    'ten': f"[{comp}] {home} vs {away}" + (f" (BLV {blv_name})" if blv_name else ""),
                    'link': m3u8_url,
                    'thumb': blv_thumb
                })

    print(f"✅ ColaTV & Gà Vàng 24h API: Thu hoạch thành công {len(streams)} luồng stream!", flush=True)
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
    # Lưu ý (11/2026): repo leeshin5757/getout trả 404 cho mọi tên -> lay_domain_dong luôn dùng fallback.
    # Quechoa, ThienDinh, CoLa, KhanDai: DNS không phân giải (NXDOMAIN) - có thể đã chết, giữ lại để thử.
    tat_ca_server = [
        ("Xoilac", lay_domain_dong("xoilactv", "https://xoilaczaz.cc"), "/truc-tiep/", "xoilac"),
        ("Sutbong", lay_domain_dong("sutbong", "https://sutbongtv.my"), "/truc-tiep/", "chuan"),
        ("BiaOm", lay_domain_dong("biaomtv", lay_domain_bitly("biaomtv", "https://biaomtv.in")), "/live/", "chuan"),
        ("BTV", lay_domain_dong("btv", "https://bongtvrtm.com"), "", "chuan"),
        ("S8", lay_domain_dong("s8", "https://s8tv011.com"), "", "chuan"),
        ("GaVangWeb", "https://gavang12.live", "/truc-tiep/", "chuan"),
        ("SaoKe", lay_domain_dong("saoke", "https://saoke34.xyz"), "", "chuan"),
        ("CoLa", lay_domain_dong("colatv", "https://colatv11.live"), "", "chuan"),
        ("Thapcam", "https://thapcamtivi.app", "/truc-tiep", "thapcam"),
        ("Hoiquan", lay_domain_hoiquan(), "", "thiendinh"),
        ("ThienDinh", lay_domain_dong("thiendinh", "https://sv2.thiendinh3.live/trang-chu"), "", "thiendinh"),
        ("ChuoiChien", lay_domain_dong("chuoichien", "https://live03.chuoichientv.me"), "/live", "chuan"),
        ("BongLau", lay_domain_dong("bonglau", "https://lau03.bonglautv1.org"), "/live", "chuan"),
        ("RungTv", lay_domain_dong("rungtv", "https://live1.rung90tv1.xyz"), "", "chuan"),
        ("Quechoa", lay_domain_dong("quechatv", "https://quechoa5.live"), "/truc-tiep/", "chuan"),
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
        raw = page.evaluate("""
            (() => {
                const results = [];
                const seen = new Set();
                const navTexts = ['Trực tuyến','Bóng đá','Bóng chuyền','Billiards','Esports','Cầu lông','Tennis','Trang chủ','Lịch thi đấu','Kết quả','Xem lại','Đua xe','Boxing','Bóng bàn'];
                
                document.querySelectorAll('a[href]').forEach(a => {
                    const href = a.href || '';
                    if (!href || href === location.href || href.endsWith('/trang-chu') || href.endsWith('/') || href.startsWith('javascript:')) return;
                    if (!href.includes(location.hostname)) return;
                    if (seen.has(href)) return;
                    
                    const rawText = (a.innerText || '').trim();
                    if (navTexts.includes(rawText) || rawText.length < 3) return;
                    
                    seen.add(href);
                    const img = a.querySelector('img');
                    const cleanText = rawText.split('\n').join(' - ').replace(/  +/g, ' ').trim();
                    
                    let sport = 'Bóng đá';
                    let parent = a.closest('.sport-section, section, [class*="section"], [class*="group"], [class*="sport"], [class*="category"]');
                    let headerText = '';
                    if (parent) {
                        const h = parent.querySelector('h1, h2, h3, h4, h5, [class*="title"], [class*="header"]');
                        if (h) headerText = h.innerText.toUpperCase();
                    }
                    if (!headerText) {
                        let prev = a.parentElement;
                        let depth = 0;
                        while (prev && prev !== document.body && depth < 8) {
                            const heading = prev.querySelector('h1, h2, h3, h4, [class*="title"]');
                            if (heading) {
                                headerText = heading.innerText.toUpperCase();
                                break;
                            }
                            prev = prev.previousElementSibling || prev.parentElement;
                            depth++;
                        }
                    }
                    
                    if (headerText.includes('BÓNG CHUYỀN') || headerText.includes('VOLLEY')) sport = 'Bóng chuyền';
                    else if (headerText.includes('BÓNG RỔ') || headerText.includes('BASKET')) sport = 'Bóng rổ';
                    else if (headerText.includes('TENNIS') || headerText.includes('QUẦN VỢT')) sport = 'Tennis';
                    else if (headerText.includes('CẦU LÔNG') || headerText.includes('BADMINTON')) sport = 'Cầu lông';
                    else if (headerText.includes('BILLIARDS') || headerText.includes('BI-A')) sport = 'Billiards';
                    else if (headerText.includes('ESPORT') || headerText.includes('LIÊN MINH')) sport = 'Esports';
                    else if (headerText.includes('ĐUA XE') || headerText.includes('MOTO')) sport = 'Đua xe';
                    else if (headerText.includes('BÓNG BÀN') || headerText.includes('PINGPONG')) sport = 'Bóng bàn';
                    
                    results.push({
                        url: href,
                        ten: cleanText || 'Trận đấu',
                        thumb: img ? (img.src || img.getAttribute('data-src') || '') : 'https://img.icons8.com/color/512/football2.png',
                        sport: sport
                    });
                });
                return results;
            })()
        """)
        return _loc_trung(raw, url_goc)

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
                context.set_default_timeout(8000)
                deadline = time.time() + (8 * 60)

                def chan_tai_nguyen(route):
                    if route.request.resource_type in ["image", "media"]:
                        route.abort()
                    else:
                        route.continue_()
                context.route("**/*", chan_tai_nguyen)

                for ten_nhom, url_trang_chu, keyword_link, kieu_quet in server_can_quet:
                    if time.time() > deadline:
                        print("⏱ Đã đạt giới hạn thời gian (deadline), chuyển sang xuất file!", flush=True)
                        break
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

_MON_THE_THAO_VI = {
    "football": "Bóng đá", "soccer": "Bóng đá", "bongda": "Bóng đá",
    "basketball": "Bóng rổ", "bongro": "Bóng rổ",
    "volleyball": "Bóng chuyền", "bongchuyen": "Bóng chuyền",
    "tennis": "Quần vợt", "quanvot": "Quần vợt",
    "esport": "Thể thao điện tử", "esports": "Thể thao điện tử",
    "vothuat": "Võ thuật", "boxing": "Quyền anh", "mma": "Võ thuật", "ufc": "Võ thuật",
    "badminton": "Cầu lông", "caulong": "Cầu lông",
    "billiards": "Bi-a", "bida": "Bi-a", "snooker": "Bi-a",
    "baseball": "Bóng chày", "hockey": "Khúc côn cầu", "icehockey": "Khúc côn cầu",
    "racing": "Đua xe", "motorsport": "Đua xe", "f1": "Đua xe", "golf": "Golf",
    "cricket": "Cricket", "rugby": "Bóng bầu dục", "handball": "Bóng ném",
    "tabletennis": "Bóng bàn", "pingpong": "Bóng bàn", "other": "Khác", "khac": "Khác",
}
_ICON_LOAI = {0: "⚽", 1: "📺", 2: "🎬"}


def _lam_sach_text(s):
    """Bỏ xuống dòng, ngoặc kép, ký tự điều khiển, [] rỗng, khoảng trắng thừa để parser M3U không vỡ."""
    s = str(s or "")
    s = re.sub(r"[\r\n\t\x00-\x1f\x7f]+", " ", s)
    s = s.replace('"', "'").replace("\u201c", "'").replace("\u201d", "'")
    s = re.sub(r"\[\s*\]", "", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,|")
    return s


def _bo_emoji_dau(s):
    return re.sub(r"^[^\wÀ-ỹ\[\(]+", "", s).strip()


def _phan_loai_luong(nhom):
    """Trả về (loai, ten_nhom_chuan) với loai 0=thể thao, 1=TV, 2=phim."""
    raw = _lam_sach_text(nhom) or "Thể thao"
    low = raw.lower()
    if raw.startswith("🎬") or low.startswith("phim") or "movie" in low or "hh3d" in low or "hoạt hình" in low:
        return 2, f"🎬 {_bo_emoji_dau(raw)}"
    if re.match(r"^tv\s*[-|:]", low) or "truyền hình" in low:
        ten = re.sub(r"^tv\s*[-|:]\s*", "", raw, flags=re.I)
        ten = re.sub(r"\s*\|\s*", " ", _bo_emoji_dau(ten)).strip(" 🔴") or "Kênh truyền hình"
        ten = ten[:1].upper() + ten[1:].lower() if ten.isupper() and len(ten) > 4 else ten
        return 1, f"📺 {ten}"
    parts = [p.strip() for p in re.split(r"\s+-\s+", raw, maxsplit=1)]
    nguon, mon = (parts[0], parts[1]) if len(parts) == 2 else ("", parts[0])
    mon = _MON_THE_THAO_VI.get(re.sub(r"[^a-z0-9]", "", mon.lower()), mon)
    return 0, f"⚽ {mon} - {nguon}" if nguon else f"⚽ {mon}"


def ghi_file_m3u_chuan(danh_sach, duong_dan):
    """Ghi M3U sạch: icon theo loại, nhóm tiếng Việt chuẩn, thứ tự ổn định (thể thao → TV → phim)."""
    ban_ghi, seen = [], set()
    for idx, luong in enumerate(danh_sach):
        link = str(luong.get("link", "")).strip()
        if not link or re.search(r"\s", link):
            continue
        loai, nhom = _phan_loai_luong(luong.get("nhom", "Thể thao"))
        ten = _bo_emoji_dau(_lam_sach_text(luong.get("ten", ""))) or "Trực tiếp"
        ten = re.sub(r"\s+vs\s*$", "", ten, flags=re.I)
        if (nhom, ten, link) in seen:
            continue
        seen.add((nhom, ten, link))
        logo = _lam_sach_text(luong.get("thumb", "")).replace(" ", "%20")
        ua = _lam_sach_text(luong.get("user_agent") or luong.get("ua") or "")
        # thể thao giữ thứ tự gốc (theo giờ) trong nhóm; TV/phim sắp theo tên
        # The thao va phim/series giu thu tu goc (theo gio/theo tap) trong nhom; TV xep theo ten
        khoa = (loai, nhom.lower(), idx if loai in (0, 2) else 0, "" if loai in (0, 2) else ten.lower())
        ban_ghi.append((khoa, nhom, ten, logo, link, ua, loai))
    ban_ghi.sort(key=lambda b: b[0])
    with open(duong_dan, "w", encoding="utf-8", newline="\n") as f:
        f.write("#EXTM3U\n")
        for _, nhom, ten, logo, link, ua, loai in ban_ghi:
            logo_attr = f' tvg-logo="{logo}"' if logo else ""
            f.write(f'#EXTINF:-1 group-title="{nhom}"{logo_attr},{_ICON_LOAI[loai]} {ten}\n')
            if ua:
                f.write(f"#EXTVLCOPT:http-user-agent={ua}\n")
            f.write(f"{link}\n")
    return len(ban_ghi)


def san_full_server_sieu_toc():
    t_start = time.time()
    print("🚀 KHỞI ĐỘNG CHIẾN DỊCH VÉT SẠCH LINK THỂ THAO & IPTV (HYBRID ENGINE)...", flush=True)
    print("==========================================================================", flush=True)

    danh_sach_phat = []
    server_da_thanh_cong = set()

    # --- BƯỚC 1: QUÉT SIÊU TỐC QUA DIRECT APIS (SOCOLIVE, GÀ VÀNG, COLATV, GIỜ VÀNG) ---
    soco_streams = thu_hoach_socolive_api()
    if soco_streams:
        danh_sach_phat.extend(soco_streams)
        server_da_thanh_cong.add("Socolive")

    cola_gv_streams = thu_hoach_colatv_gavang24h_api()
    if cola_gv_streams:
        danh_sach_phat.extend(cola_gv_streams)
        server_da_thanh_cong.add("CoLa")
        server_da_thanh_cong.add("GaVang")

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

    # --- BƯỚC 4: THU HOẠCH KHO PHIM HOT TỪ PHIM4K APK ---
    phim_streams = thu_hoach_phim_phim4k()
    if phim_streams:
        danh_sach_phat.extend(phim_streams)

    # --- BƯỚC 4B: THU HOẠCH TRỌN BỘ HOẠT HÌNH 3D FULL SERIES (YANHH3D) ---
    hh3d_streams = thu_hoach_hoat_hinh_3d_full()
    if hh3d_streams:
        danh_sach_phat.extend(hh3d_streams)

    # --- BƯỚC 5: LỌC TRÙNG & XUẤT FILE M3U CHUẨN ---
    seen_links = set()
    danh_sach_sach = []
    for luong in danh_sach_phat:
        link = luong.get('link', '').strip()
        if link and link not in seen_links:
            seen_links.add(link)
            danh_sach_sach.append(luong)

    if len(danh_sach_sach) < 5:
        print("⚠️ Thu hoạch được quá ít luồng (< 5), giữ nguyên danh sách phát hiện tại để bảo vệ người xem!", flush=True)
        return

    print("\n==========================================================================", flush=True)
    print("📦 ĐANG ĐÓNG GÓI M3U VÀ PHÂN LOẠI DANH MỤC...", flush=True)
    ghi_file_m3u_chuan(danh_sach_sach, "tong_hop_bong_da.m3u")

    duration = time.time() - t_start
    print(f"🎉 ĐÃ VÉT SẠCH THÀNH CÔNG TỔNG CỘNG {len(danh_sach_sach)} KÊNH & TRẬN ĐẤU TRONG {duration:.2f}s!", flush=True)
    nhom_count = {}
    for l in danh_sach_sach:
        nhom = l.get('nhom', 'Khác')
        nhom_count[nhom] = nhom_count.get(nhom, 0) + 1
    print(f"📊 Chi tiết danh mục: {', '.join(f'{k}: {v}' for k, v in list(nhom_count.items())[:10])}...", flush=True)

if __name__ == "__main__":
    san_full_server_sieu_toc()
