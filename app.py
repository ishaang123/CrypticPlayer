import concurrent.futures
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Configured backends
YOUTUBE_PROXY_API = "https://yt.chocolatemoo53.com"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrypticPlayer // Ultra Premium Hybrid Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #020204;
            --bg-surface: rgba(15, 15, 27, 0.7);
            --bg-element: rgba(30, 30, 54, 0.4);
            --border-glow: rgba(255, 255, 255, 0.04);
            --accent: #eab308;
            --accent-glow: rgba(234, 179, 8, 0.25);
            --text-primary: #f8fafc;
            --text-secondary: #64748b;
            --yt-color: #ef4444;
            --dm-color: #2563eb;
            --dz-color: #ec4899;
            --transition: cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 75% 15%, rgba(37, 99, 235, 0.07) 0%, transparent 45%),
                radial-gradient(circle at 25% 85%, rgba(236, 72, 153, 0.05) 0%, transparent 40%);
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 24px 48px;
            background: rgba(2, 2, 4, 0.8);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(24px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .logo {
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.8px;
            cursor: pointer;
            user-select: none;
        }

        .logo span {
            color: var(--accent);
            text-shadow: 0 0 30px var(--accent-glow);
        }

        .search-wrapper {
            display: flex;
            background: var(--bg-surface);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 6px 6px 6px 20px;
            width: 100%;
            max-width: 620px;
            backdrop-filter: blur(12px);
            transition: all 0.4s var(--transition);
        }

        .search-wrapper:focus-within {
            border-color: rgba(234, 179, 8, 0.4);
            box-shadow: 0 0 40px rgba(234, 179, 8, 0.12);
            background: rgba(18, 18, 32, 0.9);
        }

        .search-wrapper input {
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 500;
            width: 100%;
            outline: none;
        }

        .search-wrapper input::placeholder {
            color: var(--text-secondary);
        }

        .search-wrapper button {
            background: var(--accent);
            color: #020204;
            border: none;
            padding: 12px 28px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s var(--transition);
        }

        .search-wrapper button:hover {
            opacity: 0.95;
            transform: translateY(-1px);
            box-shadow: 0 4px 15px var(--accent-glow);
        }

        main {
            flex: 1;
            padding: 48px;
            max-width: 1600px;
            width: 100%;
            margin: 0 auto;
        }

        .theater-stage {
            display: none;
            margin-bottom: 48px;
            animation: slideUp 0.6s var(--transition) forwards;
        }

        .aspect-ratio-box {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: #000;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 35px 70px rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .aspect-ratio-box iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }

        .shelf-header {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.4px;
        }

        .shelf-header::before {
            content: '';
            width: 4px;
            height: 18px;
            background: var(--accent);
            border-radius: 4px;
        }

        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
            gap: 28px;
        }

        .video-card {
            background: var(--bg-surface);
            border-radius: 20px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.4s var(--transition);
            border: 1px solid rgba(255, 255, 255, 0.01);
            backdrop-filter: blur(12px);
            position: relative;
        }

        .video-card:hover {
            transform: translateY(-6px);
            border-color: rgba(255, 255, 255, 0.07);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }

        .thumb-wrap {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: var(--bg-element);
            overflow: hidden;
        }

        .thumb-wrap img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s var(--transition);
        }

        .video-card:hover .thumb-wrap img {
            transform: scale(1.05);
        }

        .platform-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #fff;
            z-index: 2;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        .platform-badge.youtube { background: var(--yt-color); }
        .platform-badge.dailymotion { background: var(--dm-color); }
        .platform-badge.deezer-match { background: linear-gradient(135deg, var(--dz-color), #7c3aed); }

        .card-details {
            padding: 20px;
        }

        .card-title {
            font-size: 14px;
            font-weight: 600;
            line-height: 1.5;
            color: var(--text-primary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-subtitle {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .skeleton {
            background: linear-gradient(90deg, rgba(255,255,255,0.01) 25%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.01) 75%);
            background-size: 200% 100%;
            animation: pulse 1.5s infinite linear;
        }

        @keyframes pulse {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 900px) {
            header { padding: 20px; flex-direction: column; gap: 20px; }
            .search-wrapper { max-width: 100%; }
            main { padding: 24px; }
        }
    </style>
</head>
<body>

    <header>
        <div class="logo" onclick="routeToHome()">Cryptic<span>Player</span></div>
        <div class="search-wrapper">
            <input type="text" id="query-input" placeholder="Search track titles, global artists, or playlists...">
            <button onclick="commitSearch()">Search</button>
        </div>
    </header>

    <main>
        <div class="theater-stage" id="theater-stage">
            <div class="aspect-ratio-box">
                <iframe id="video-embed" src="" allowfullscreen></iframe>
            </div>
        </div>

        <h2 class="shelf-header" id="shelf-title">Featured Content Feed</h2>
        <div class="video-grid" id="video-grid"></div>
    </main>

    <script>
        window.addEventListener('DOMContentLoaded', () => parseState(window.location.search));
        window.addEventListener('popstate', () => parseState(window.location.search));

        function parseState(searchQuery) {
            const params = new URLSearchParams(searchQuery);
            const v = params.get('v');
            const q = params.get('q');

            if (v) {
                renderPlayer(v);
            } else if (q) {
                document.getElementById('query-input').value = q;
                fetchUnifiedFeed(`/api/search?q=${encodeURIComponent(q)}`, false);
            } else {
                hidePlayerStage();
                document.getElementById('shelf-title').innerText = "Featured Content Feed";
                fetchUnifiedFeed('/api/trending', false);
            }
        }

        function routeToHome() {
            document.getElementById('query-input').value = '';
            history.pushState({}, '', window.location.pathname);
            hidePlayerStage();
            document.getElementById('shelf-title').innerText = "Featured Content Feed";
            fetchUnifiedFeed('/api/trending', false);
        }

        function commitSearch() {
            const query = document.getElementById('query-input').value.trim();
            if (!query) return;
            history.pushState({}, '', `?q=${encodeURIComponent(query)}`);
            document.getElementById('shelf-title').innerText = `Search results for "${query}"`;
            fetchUnifiedFeed(`/api/search?q=${encodeURIComponent(query)}`, true);
        }

        function fetchUnifiedFeed(endpoint, resetPlayer) {
            if (resetPlayer) hidePlayerStage();
            const grid = document.getElementById('video-grid');
            grid.innerHTML = '';
            
            for (let i = 0; i < 8; i++) {
                grid.innerHTML += `
                    <div class="video-card">
                        <div class="thumb-wrap skeleton"></div>
                        <div class="card-details">
                            <div class="skeleton" style="height:14px; width:92%; border-radius:4px; margin-bottom:8px;"></div>
                            <div class="skeleton" style="height:12px; width:45%; border-radius:4px;"></div>
                        </div>
                    </div>`;
            }

            fetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    grid.innerHTML = '';
                    if (!data || data.length === 0) {
                        grid.innerHTML = '<p style="color: var(--text-secondary)">No index matches found across search clusters.</p>';
                        return;
                    }
                    data.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'video-card';
                        card.onclick = () => selectVideo(item.id);
                        
                        let subtitle = item.source.toUpperCase();
                        if (item.deezer_meta) {
                            subtitle = `🎵 ${item.deezer_meta.artist} • Track Match`;
                        }

                        card.innerHTML = `
                            <span class="platform-badge ${item.deezer_meta ? 'deezer-match' : item.source}">${item.deezer_meta ? 'Music Match' : item.source}</span>
                            <div class="thumb-wrap">
                                <img src="${item.thumbnail}" alt="${item.title}" loading="lazy">
                            </div>
                            <div class="card-details">
                                <p class="card-title" title="${item.title}">${item.title}</p>
                                <p class="card-subtitle">${subtitle}</p>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                })
                .catch(() => {
                    grid.innerHTML = '<p style="color: var(--yt-color)">Search cluster aggregation failure.</p>';
                });
        }

        function selectVideo(id) {
            const params = new URLSearchParams(window.location.search);
            const q = params.get('q');
            let newPath = `?v=${id}`;
            if (q) newPath = `?q=${encodeURIComponent(q)}&v=${id}`;
            
            history.pushState({}, '', newPath);
            renderPlayer(id);
        }

        function renderPlayer(id) {
            const stage = document.getElementById('theater-stage');
            document.getElementById('video-embed').src = `https://ishaan2-nebulaviwstreaming.hf.space/download?id_or_url=${id}&minimal=true`;
            stage.style.display = 'block';
            stage.scrollIntoView({ behavior: 'smooth' });
        }

        function hidePlayerStage() {
            document.getElementById('theater-stage').style.display = 'none';
            document.getElementById('video-embed').src = '';
        }

        document.getElementById('query-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') commitSearch();
        });
    </script>
</body>
</html>
"""

def get_youtube_data(endpoint):
    try:
        r = requests.get(f"{YOUTUBE_PROXY_API}/api/v1/{endpoint}", timeout=4)
        if r.status_code == 200:
            raw_data = r.json()
            items = raw_data.get("textualResults", raw_data) if isinstance(raw_data, dict) else raw_data
            
            parsed_videos = []
            for item in items:
                if item.get("type") == "video":
                    v_id = item.get("videoId")
                    if not v_id:
                        continue
                        
                    thumbnails = item.get("videoThumbnails", [])
                    thumb_url = ""
                    if thumbnails:
                        thumb_url = next((t["url"] for t in thumbnails if t.get("quality") == "medium"), thumbnails[0]["url"])
                    
                    # Fix broken asset paths returned by parsing engines
                    if not thumb_url or thumb_url.startswith("/vi/") or not thumb_url.startswith("http"):
                        thumb_url = f"https://img.youtube.com/vi/{v_id}/0.jpg"
                        
                    parsed_videos.append({
                        "id": v_id,
                        "title": item.get("title"),
                        "thumbnail": thumb_url,
                        "source": "youtube",
                        "deezer_meta": None
                    })
            return parsed_videos[:8]
    except Exception:
        pass
    return []

def get_dailymotion_data(url):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return [{
                "id": v["id"], 
                "title": v["title"], 
                "thumbnail": v["thumbnail_360_url"], 
                "source": "dailymotion",
                "deezer_meta": None
            } for v in r.json().get("list", [])]
    except Exception:
        pass
    return []

def check_deezer_music(query):
    try:
        r = requests.get(f"https://api.deezer.com/search?q={query}&limit=3", timeout=3)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return {
                    "track": data[0].get("title"),
                    "artist": data[0].get("artist", {}).get("name"),
                    "album_art": data[0].get("album", {}).get("cover_medium")
                }
    except Exception:
        pass
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/trending')
def trending():
    dm_url = "https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&flags=featured&limit=8"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yt = executor.submit(get_youtube_data, "trending?region=US")
        future_dm = executor.submit(get_dailymotion_data, dm_url)
        
        yt_results = future_yt.result()
        dm_results = future_dm.result()
        
    combined = [val for pair in zip(yt_results, dm_results) for val in pair]
    remaining = yt_results[len(dm_results):] + dm_results[len(yt_results):]
    return jsonify(combined + remaining)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    # Step 1: Pre-search Deezer to find exact track names and artist strings
    music_match = check_deezer_music(query)
    
    # Step 2: Set enhanced search query parameter if match occurs
    if music_match:
        enhanced_query = f"{music_match['track']} {music_match['artist']}"
    else:
        enhanced_query = query

    dm_url = f"https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&search={enhanced_query}&limit=8"
    
    # Step 3: Run queries concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yt = executor.submit(get_youtube_data, f"search?q={enhanced_query}&filter=videos")
        future_dm = executor.submit(get_dailymotion_data, dm_url)
        
        yt_results = future_yt.result()
        dm_results = future_dm.result()

    # Step 4: Interlace meta properties for matching titles
    if music_match:
        track_token = music_match["track"].lower()
        artist_token = music_match["artist"].lower()
        
        for item in (yt_results + dm_results):
            title_lower = item["title"].lower()
            if track_token in title_lower or artist_token in title_lower:
                item["deezer_meta"] = music_match
                if not item["thumbnail"]:
                    item["thumbnail"] = music_match["album_art"]

    # Step 5: Sort verified music items directly to the top positions
    all_videos = yt_results + dm_results
    sorted_videos = sorted(all_videos, key=lambda x: 0 if x.get("deezer_meta") else 1)

    return jsonify(sorted_videos[:16])

if __name__ == '__main__':
    app.run(debug=True)
