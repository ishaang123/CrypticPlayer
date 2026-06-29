import concurrent.futures
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Fallback pool for public YouTube data scraping infrastructure
YOUTUBE_PROXY_API = "https://inv.nadeko.net/"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrypticPlayer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #06060a;
            --bg-surface: #0f0f18;
            --bg-element: #171726;
            --border-glow: #222235;
            --accent: #ca8a04;
            --accent-glow: rgba(202, 138, 4, 0.3);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --yt-color: #ef4444;
            --dm-color: #0066ff;
            --transition-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
            --transition-smooth: cubic-bezier(0.16, 1, 0.3, 1);
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
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 24px 48px;
            background: linear-gradient(to bottom, rgba(6,6,10,0.95) 70%, rgba(6,6,10,0));
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255,255,255,0.02);
        }

        .logo {
            font-family: 'Cabinet Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 800;
            color: var(--text-primary);
            text-decoration: none;
            letter-spacing: -1px;
            cursor: pointer;
        }

        .logo span {
            color: var(--accent);
            text-shadow: 0 0 20px var(--accent-glow);
        }

        .search-wrapper {
            display: flex;
            background: var(--bg-surface);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 6px 6px 6px 20px;
            width: 100%;
            max-width: 560px;
            transition: all 0.4s var(--transition-smooth);
        }

        .search-wrapper:focus-within {
            border-color: var(--accent);
            box-shadow: 0 0 25px var(--accent-glow);
            background: var(--bg-element);
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
            color: var(--text-secondary);
        }

        .search-wrapper button {
            background: var(--accent);
            color: #000;
            border: none;
            padding: 12px 28px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s var(--transition-smooth);
        }

        .search-wrapper button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px var(--accent-glow);
        }

        main {
            flex: 1;
            padding: 24px 48px 48px 48px;
            max-width: 1600px;
            width: 100%;
            margin: 0 auto;
        }

        /* Theater Area Layout */
        .theater-stage {
            display: none;
            margin-bottom: 48px;
            animation: slideUp 0.6s var(--transition-smooth) forwards;
        }

        .aspect-ratio-box {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: #000;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 40px 80px rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(255,255,255,0.04);
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
            font-family: 'Cabinet Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 28px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .shelf-header::before {
            content: '';
            display: inline-block;
            width: 4px;
            height: 20px;
            background: var(--accent);
            border-radius: 4px;
        }

        /* Multi-Platform Feed Network */
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 32px;
        }

        .video-card {
            background: var(--bg-surface);
            border-radius: 20px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.4s var(--transition-smooth);
            border: 1px solid rgba(255, 255, 255, 0.01);
            position: relative;
        }

        .video-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 30px rgba(0,0,0,0.5);
            border-color: var(--border-glow);
        }

        .thumb-wrap {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: var(--bg-element);
        }

        .thumb-wrap img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .platform-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            z-index: 2;
            color: #fff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }

        .platform-badge.youtube { background: var(--yt-color); }
        .platform-badge.dailymotion { background: var(--dm-color); }

        .card-details {
            padding: 20px;
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
            text-overflow: ellipsis;
        }

        /* Micro-Animations (Skeleton Structure) */
        .skeleton {
            background: linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-element) 50%, var(--bg-surface) 75%);
            background-size: 200% 100%;
            animation: loadingPulse 1.5s infinite var(--transition-smooth);
        }

        @keyframes loadingPulse {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 900px) {
            header { padding: 20px; flex-direction: column; gap: 20px; }
            .search-wrapper { max-width: 100%; }
            main { padding: 20px; }
        }
    </style>
</head>
<body>

    <header>
        <div class="logo" onclick="routeToHome()">Cryptic<span>Player</span></div>
        <div class="search-wrapper">
            <input type="text" id="query-input" placeholder="Search YouTube & Dailymotion simultaneously...">
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
        // Parse states on start or history popping events
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
            
            // UI Loading skeletons
            for (let i = 0; i < 8; i++) {
                grid.innerHTML += `
                    <div class="video-card">
                        <div class="thumb-wrap skeleton"></div>
                        <div class="card-details">
                            <div class="skeleton" style="height:16px; width:90%; border-radius:4px; margin-bottom:8px;"></div>
                            <div class="skeleton" style="height:16px; width:60%; border-radius:4px;"></div>
                        </div>
                    </div>`;
            }

            fetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    grid.innerHTML = '';
                    if (!data || data.length === 0) {
                        grid.innerHTML = '<p style="color: var(--text-secondary)">No videos located across search architectures.</p>';
                        return;
                    }
                    data.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'video-card';
                        card.onclick = () => selectVideo(item.id, item.source);
                        card.innerHTML = `
                            <span class="platform-badge ${item.source}">${item.source}</span>
                            <div class="thumb-wrap">
                                <img src="${item.thumbnail}" alt="${item.title}" loading="lazy">
                            </div>
                            <div class="card-details">
                                <p class="card-title" title="${item.title}">${item.title}</p>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                })
                .catch(() => {
                    grid.innerHTML = '<p style="color: #ef4444">Federated API index lookup failed.</p>';
                });
        }

        function selectVideo(id, source) {
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

# Helper function to query YouTube data safely
def get_youtube_data(endpoint):
    try:
        r = requests.get(f"{YOUTUBE_PROXY_API}/api/v1/{endpoint}", timeout=4)
        if r.status_code == 200:
            res = r.json()
            items = res.get("textualResults", res) if "search" in endpoint else res
            return [{"id": v["url"].split("=")[-1], "title": v["title"], "thumbnail": v["thumbnail"], "source": "youtube"} for v in items if "url" in v or "title" in v][:8]
    except Exception:
        pass
    return []

# Helper function to query Dailymotion safely
def get_dailymotion_data(url):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return [{"id": v["id"], "title": v["title"], "thumbnail": v["thumbnail_360_url"], "source": "dailymotion"} for v in r.json().get("list", [])]
    except Exception:
        pass
    return []

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/trending')
def trending():
    dm_url = "https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&flags=featured&limit=8"
    
    # Run requests concurrently to speed up response load time
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yt = executor.submit(get_youtube_data, "trending?region=US")
        future_dm = executor.submit(get_dailymotion_data, dm_url)
        
        yt_results = future_yt.result()
        dm_results = future_dm.result()
        
    # Interleave the results beautifully
    combined = [val for pair in zip(yt_results, dm_results) for val in pair]
    remaining = yt_results[len(dm_results):] + dm_results[len(yt_results):]
    return jsonify(combined + remaining)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    dm_url = f"https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&search={query}&limit=8"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yt = executor.submit(get_youtube_data, f"search?q={query}&filter=videos")
        future_dm = executor.submit(get_dailymotion_data, dm_url)
        
        yt_results = future_yt.result()
        dm_results = future_dm.result()

    combined = [val for pair in zip(yt_results, dm_results) for val in pair]
    remaining = yt_results[len(dm_results):] + dm_results[len(yt_results):]
    return jsonify(combined + remaining)

if __name__ == '__main__':
    app.run(debug=True)
