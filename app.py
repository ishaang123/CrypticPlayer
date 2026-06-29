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
    <title>CrypticPlayer // Next-Gen Media Nexus</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #030307;
            --bg-surface: rgba(18, 18, 36, 0.6);
            --bg-element: rgba(255, 255, 255, 0.03);
            --border-glow: rgba(255, 255, 255, 0.05);
            --accent: #f59e0b;
            --accent-glow: rgba(245, 158, 11, 0.3);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --yt-color: #ef4444;
            --dm-color: #3b82f6;
            --dz-color: #ec4899;
            --panel-blur: blur(20px);
            --transition: cubic-bezier(0.2, 0.8, 0.2, 1);
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
                radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 20% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(245, 158, 11, 0.02) 0%, transparent 40%);
            background-attachment: fixed;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 48px;
            background: rgba(3, 3, 7, 0.75);
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: var(--panel-blur);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .logo {
            font-size: 24px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -1px;
            cursor: pointer;
            user-select: none;
            transition: transform 0.3s var(--transition);
        }

        .logo:hover {
            transform: scale(1.02);
        }

        .logo span {
            color: var(--accent);
            text-shadow: 0 0 25px var(--accent-glow);
        }

        .search-container {
            position: relative;
            width: 100%;
            max-width: 600px;
        }

        .search-wrapper {
            display: flex;
            background: var(--bg-surface);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 5px 5px 5px 20px;
            backdrop-filter: var(--panel-blur);
            transition: all 0.4s var(--transition);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }

        .search-wrapper:focus-within {
            border-color: rgba(245, 158, 11, 0.5);
            box-shadow: 0 0 40px rgba(245, 158, 11, 0.15), inset 0 0 10px rgba(245, 158, 11, 0.05);
            background: rgba(18, 18, 36, 0.85);
        }

        .search-wrapper input {
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 15px;
            font-weight: 500;
            width: 100%;
            outline: none;
        }

        .search-wrapper input::placeholder {
            color: #64748b;
        }

        .search-wrapper button {
            background: linear-gradient(135deg, #fbbf24, var(--accent));
            color: #030307;
            border: none;
            padding: 12px 26px;
            border-radius: 15px;
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
            transition: all 0.3s var(--transition);
        }

        .search-wrapper button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        }

        /* Suggestions Dropdown */
        .suggestions-box {
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            right: 0;
            background: rgba(15, 15, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            overflow: hidden;
            z-index: 1100;
            backdrop-filter: var(--panel-blur);
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            display: none;
            max-height: 350px;
            overflow-y: auto;
        }

        .suggestion-item {
            padding: 14px 20px;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s var(--transition);
        }

        .suggestion-item::before {
            content: "🔍";
            font-size: 12px;
            opacity: 0.5;
        }

        .suggestion-item:hover, .suggestion-item.active {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }

        main {
            flex: 1;
            padding: 40px 48px;
            max-width: 1700px;
            width: 100%;
            margin: 0 auto;
        }

        .theater-stage {
            display: none;
            margin-bottom: 48px;
            animation: slideUp 0.7s var(--transition) forwards;
        }

        .aspect-ratio-box {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: #000;
            border-radius: 28px;
            overflow: hidden;
            box-shadow: 0 40px 90px rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.05);
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
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.5px;
            text-transform: uppercase;
            color: #e2e8f0;
        }

        .shelf-header::before {
            content: '';
            width: 4px;
            height: 16px;
            background: var(--accent);
            border-radius: 4px;
            box-shadow: 0 0 10px var(--accent);
        }

        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 32px;
        }

        .video-card {
            background: var(--bg-surface);
            border-radius: 24px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.4s var(--transition);
            border: 1px solid var(--border-glow);
            position: relative;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }

        .video-card:hover {
            transform: translateY(-8px);
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
        }

        .thumb-wrap {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: rgba(255,255,255,0.01);
            overflow: hidden;
        }

        .thumb-wrap img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.8s var(--transition);
        }

        .video-card:hover .thumb-wrap img {
            transform: scale(1.04);
        }

        .platform-badge {
            position: absolute;
            top: 14px;
            left: 14px;
            padding: 5px 12px;
            border-radius: 10px;
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #fff;
            z-index: 2;
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
            backdrop-filter: blur(4px);
        }

        .platform-badge.youtube { background: rgba(239, 68, 68, 0.85); border: 1px solid rgba(239, 68, 68, 0.3); }
        .platform-badge.dailymotion { background: rgba(59, 130, 246, 0.85); border: 1px solid rgba(59, 130, 246, 0.3); }
        .platform-badge.deezer-match { background: linear-gradient(135deg, rgba(236, 72, 153, 0.9), rgba(124, 58, 237, 0.9)); border: 1px solid rgba(236, 72, 153, 0.4); }

        .card-details {
            padding: 22px;
        }

        .card-title {
            font-size: 15px;
            font-weight: 600;
            line-height: 1.5;
            color: var(--text-primary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-subtitle {
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 10px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .skeleton {
            background: linear-gradient(90deg, rgba(255,255,255,0.01) 25%, rgba(255,255,255,0.04) 50%, rgba(255,255,255,0.01) 75%);
            background-size: 200% 100%;
            animation: pulse 1.6s infinite linear;
        }

        @keyframes pulse {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 900px) {
            header { padding: 20px; flex-direction: column; gap: 16px; }
            .search-container { max-width: 100%; }
            main { padding: 24px; }
        }
    </style>
</head>
<body>

    <header>
        <div class="logo" onclick="routeToHome()">Cryptic<span>Player</span></div>
        <div class="search-container">
            <div class="search-wrapper">
                <input type="text" id="query-input" placeholder="Search platforms, music tags, or artists..." autocomplete="off">
                <button onclick="commitSearch()">Search</button>
            </div>
            <div class="suggestions-box" id="suggestions-box"></div>
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
        let currentFocus = -1;

        window.addEventListener('DOMContentLoaded', () => parseState(window.location.search));
        window.addEventListener('popstate', () => parseState(window.location.search));

        const inputEl = document.getElementById('query-input');
        const suggestBox = document.getElementById('suggestions-box');

        // Dynamic Suggestion Logic
        inputEl.addEventListener('input', () => {
            const val = inputEl.value.trim();
            if (!val) {
                hideSuggestions();
                return;
            }

            // JSONP binding to call YouTube suggestion clusters securely inside frontend execution context
            const script = document.createElement('script');
            script.src = `https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q=${encodeURIComponent(val)}&callback=handleSuggestions`;
            document.body.appendChild(script);
            document.body.removeChild(script);
        });

        function handleSuggestions(data) {
            const suggestions = data[1];
            suggestBox.innerHTML = '';
            currentFocus = -1;

            if (suggestions.length === 0) {
                hideSuggestions();
                return;
            }

            suggestions.forEach((text) => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.textContent = text[0];
                item.onclick = () => {
                    inputEl.value = text[0];
                    hideSuggestions();
                    commitSearch();
                };
                suggestBox.appendChild(item);
            });
            suggestBox.style.display = 'block';
        }

        // Handle Arrow key navigation inside suggestions box
        inputEl.addEventListener('keydown', (e) => {
            const items = suggestBox.getElementsByClassName('suggestion-item');
            if (e.key === 'ArrowDown') {
                currentFocus++;
                addActive(items);
            } else if (e.key === 'ArrowUp') {
                currentFocus--;
                addActive(items);
            } else if (e.key === 'Enter') {
                if (currentFocus > -1 && items[currentFocus]) {
                    e.preventDefault();
                    items[currentFocus].click();
                } else {
                    hideSuggestions();
                    commitSearch();
                }
            } else if (e.key === 'Escape') {
                hideSuggestions();
            }
        });

        function addActive(items) {
            if (!items || items.length === 0) return;
            removeActive(items);
            if (currentFocus >= items.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = items.length - 1;
            items[currentFocus].classList.add('active');
            items[currentFocus].scrollIntoView({ block: 'nearest' });
        }

        function removeActive(items) {
            for (let i = 0; i < items.length; i++) {
                items[i].classList.remove('active');
            }
        }

        function hideSuggestions() {
            suggestBox.style.display = 'none';
        }

        document.addEventListener('click', (e) => {
            if (e.target !== inputEl && e.target !== suggestBox) {
                hideSuggestions();
            }
        });

        function parseState(searchQuery) {
            const params = new URLSearchParams(searchQuery);
            const v = params.get('v');
            const q = params.get('q');

            if (v) {
                renderPlayer(v);
            } else if (q) {
                inputEl.value = q;
                fetchUnifiedFeed(`/api/search?q=${encodeURIComponent(q)}`, false);
            } else {
                hidePlayerStage();
                document.getElementById('shelf-title').innerText = "Featured Content Feed";
                fetchUnifiedFeed('/api/trending', false);
            }
        }

        function routeToHome() {
            inputEl.value = '';
            history.pushState({}, '', window.location.pathname);
            hidePlayerStage();
            document.getElementById('shelf-title').innerText = "Featured Content Feed";
            fetchUnifiedFeed('/api/trending', false);
        }

        function commitSearch() {
            const query = inputEl.value.trim();
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
                            <div class="skeleton" style="height:15px; width:90%; border-radius:4px; margin-bottom:8px;"></div>
                            <div class="skeleton" style="height:12px; width:40%; border-radius:4px;"></div>
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

    # Smart Check: Only query/enhance through Deezer if explicitly looking for audio content
    music_keywords = ["song", "music", "lyrics", "audio", "mv", "track", "remix"]
    is_music_intent = any(k in query.lower() for k in music_keywords)

    music_match = None
    if is_music_intent:
        music_match = check_deezer_music(query)
    
    # Rebuild query strings depending on intent context
    if music_match:
        enhanced_query = f"{music_match['track']} {music_match['artist']}"
    else:
        enhanced_query = query

    dm_url = f"https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&search={enhanced_query}&limit=8"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yt = executor.submit(get_youtube_data, f"search?q={enhanced_query}&filter=videos")
        future_dm = executor.submit(get_dailymotion_data, dm_url)
        
        yt_results = future_yt.result()
        dm_results = future_dm.result()

    # Apply strict validation mapping logic to prevent random cross-labeling
    if music_match:
        track_token = music_match["track"].lower()
        artist_token = music_match["artist"].lower()
        
        for item in (yt_results + dm_results):
            title_lower = item["title"].lower()
            # Must strictly contain both tracking strings to claim an index match badge
            if track_token in title_lower and artist_token in title_lower:
                item["deezer_meta"] = music_match
                if not item["thumbnail"]:
                    item["thumbnail"] = music_match["album_art"]

    # Interleave results dynamically, prioritizing strict verified matches if they exist
    all_videos = yt_results + dm_results
    sorted_videos = sorted(all_videos, key=lambda x: 0 if x.get("deezer_meta") else 1)

    return jsonify(sorted_videos[:16])

if __name__ == '__main__':
    app.run(debug=True)
