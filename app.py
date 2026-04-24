import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

API_READ_ACCESS_TOKEN = os.getenv('API_Read_Access_Token')
if not API_READ_ACCESS_TOKEN:
    # In production, this should probably be a logged error or a fallback
    print("Warning: API_Read_Access_Token not found in environment.")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
ACCESSIBILITY_KEYWORDS = (
    'sign language', 'signed version', 'asl', 'bsl', 'deaf',
    'audio description', 'audio described', 'open caption',
    'closed caption', 'subtitled', 'sdh',
)

app = Flask(__name__)

def tmdb_request(endpoint, params=None):
    """Generic helper for TMDB API requests with error handling."""
    if not API_READ_ACCESS_TOKEN:
        return None
    
    url = f"{TMDB_BASE_URL}/{endpoint}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_READ_ACCESS_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB Request Error: {e}")
    return None

def is_accessibility_version(video):
    name = video.get('name', '').lower()
    return any(kw in name for kw in ACCESSIBILITY_KEYWORDS)

def pick_english_trailer(results):
    yt_en = [
        v for v in results
        if v.get('site') == 'YouTube'
        and v.get('iso_639_1') == 'en'
        and not is_accessibility_version(v)
    ]
    for preferred_type in ('Trailer', 'Teaser', 'Clip', 'Featurette'):
        match = next((v for v in yt_en if v.get('type') == preferred_type), None)
        if match:
            return match
    return yt_en[0] if yt_en else None

@app.route('/')
def index():
    data = tmdb_request("trending/movie/day", {"language": "en-US"})
    movies = data.get('results', []) if data else []
    return render_template('home.html', movies=movies)

@app.route('/series')
def series():
    data = tmdb_request("trending/tv/day", {"language": "en-US"})
    series_list = data.get('results', []) if data else []
    return render_template('series.html', series=series_list)

@app.route('/all_movies')
def all_movies():
    page = min(request.args.get('page', 1, type=int), 500)
    data = tmdb_request("discover/movie", {"language": "en-US", "page": page})
    
    movies = []
    current_page = page
    total_pages = 0
    
    if data:
        movies = data.get('results', [])
        current_page = data.get('page', page)
        total_pages = min(data.get('total_pages', 1), 500)
        
    return render_template('all_movies.html', movies=movies, page=current_page, total_pages=total_pages)

@app.route('/all_series')
def all_series():
    page = min(request.args.get('page', 1, type=int), 500)
    data = tmdb_request("discover/tv", {"language": "en-US", "page": page})
    
    series_list = []
    current_page = page
    total_pages = 0
    
    if data:
        series_list = data.get('results', [])
        current_page = data.get('page', page)
        total_pages = min(data.get('total_pages', 1), 500)
        
    return render_template('all_series.html', series=series_list, page=current_page, total_pages=total_pages)

@app.route('/trailer/<media_type>/<int:media_id>')
def get_trailer(media_type, media_id):
    if media_type not in ('movie', 'tv'):
        return {'key': None}, 400

    data = tmdb_request(f"{media_type}/{media_id}/videos", {"language": "en-US"})
    if data:
        results = data.get('results', [])
        trailer = pick_english_trailer(results)
        if trailer:
            return {'key': trailer['key']}
        
        # Fallback to all languages
        fallback_data = tmdb_request(f"{media_type}/{media_id}/videos")
        if fallback_data:
            all_results = fallback_data.get('results', [])
            trailer = pick_english_trailer(all_results)
            if trailer:
                return {'key': trailer['key']}
                
    return {'key': None}

if __name__ == '__main__':
    # Use environment variable for port if available (standard practice)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)