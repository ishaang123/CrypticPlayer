import concurrent.futures
import random
import requests
from flask import Flask, jsonify, render_template, request

# Global initialization for Vercel
app = Flask(__name__)

# Configured backends
YOUTUBE_PROXY_API = "https://yt.chocolatemoo53.com"

# --- HELPER FUNCTIONS FOR SEARCH ROUTE ---

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

# --- APP ROUTES ---

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    music_keywords = ["song", "music", "lyrics", "audio", "mv", "track", "remix"]
    is_music_intent = any(k in query.lower() for k in music_keywords)

    music_match = None
    if is_music_intent:
        music_match = check_deezer_music(query)
    
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

    if music_match:
        track_token = music_match["track"].lower()
        artist_token = music_match["artist"].lower()
        
        for item in (yt_results + dm_results):
            title_lower = item["title"].lower()
            if track_token in title_lower and artist_token in title_lower:
                item["deezer_meta"] = music_match
                if not item["thumbnail"]:
                    item["thumbnail"] = music_match["album_art"]

    all_videos = yt_results + dm_results
    sorted_videos = sorted(all_videos, key=lambda x: 0 if x.get("deezer_meta") else 1)

    return jsonify(sorted_videos[:16])

@app.route('/api/trending')
def trending():
    # Since Invidious instances are globally rate-limited or breaking on trends,
    # we pull diverse, multi-category feeds from Dailymotion to build a robust, clean layout.
    dm_endpoints = [
        "https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&sort=trending&country=us&limit=15",
        "https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&channel=music&sort=visited&country=us&limit=10",
        "https://api.dailymotion.com/videos?fields=id,title,thumbnail_360_url&channel=tech&sort=visited&country=us&limit=10"
    ]
    
    all_dm_results = []
    
    # Inline parallel fetching across the working channels
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        def fetch_url(url):
            try:
                r = requests.get(url, timeout=3)
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

        futures = [executor.submit(fetch_url, url) for url in dm_endpoints]
        for future in concurrent.futures.as_completed(futures):
            all_dm_results.extend(future.result())
            
    # Relaxed spam filter targeting web-novel text scripts
    trash_keywords = {
        "stole my guy", "swapped to a beggar", "hidden king", 
        "regret came too late", "lace me up my queen", "little prince is hiding"
    }
    
    clean_videos = [
        v for v in all_dm_results 
        if not any(bad in v.get('title', '').lower() for bad in trash_keywords)
    ]
    
    # Shuffle slightly so it feels like a diverse, custom network feed every refresh
    random.shuffle(clean_videos)
    
    return jsonify(clean_videos[:16])

if __name__ == '__main__':
    app.run(debug=True)
