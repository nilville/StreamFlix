from flask import Flask, render_template, request, redirect, url_for, session
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_key')
API_Read_Access_Token = os.getenv('API_Read_Access_Token')

def tmdb():
    url = f'https://api.themoviedb.org/3/trending/movie/day?language=en-US'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_Read_Access_Token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['results']

def tmdb_series():
    url = f'https://api.themoviedb.org/3/trending/tv/day?language=en-US'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_Read_Access_Token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['results']

def fetch_all_movies(page=1):
    url = f'https://api.themoviedb.org/3/discover/movie?language=en-US&page={page}'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_Read_Access_Token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        current_page = data.get('page', page)
        # TMDB caps discover pagination at 500 pages
        total_pages = min(data.get('total_pages', 1), 500)
        return results, current_page, total_pages

def fetch_all_series(page=1):
    url = f'https://api.themoviedb.org/3/discover/tv?language=en-US&page={page}'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_Read_Access_Token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        current_page = data.get('page', page)
        total_pages = min(data.get('total_pages', 1), 500)
        return results, current_page, total_pages

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    trending_movies = tmdb()
    return render_template('home.html', movies=trending_movies)

@app.route('/series', methods=['GET', 'POST'])
def series():
    trending_series = tmdb_series()
    return render_template('series.html', series=trending_series)

@app.route('/all_movies', methods=['GET', 'POST'])
def all_movies():
    page = request.args.get('page', 1, type=int)
    movies, current_page, total_pages = fetch_all_movies(page)
    return render_template('all_movies.html', movies=movies, page=current_page, total_pages=total_pages)

@app.route('/all_series', methods=['GET', 'POST'])
def all_series():
    page = request.args.get('page', 1, type=int)
    series, current_page, total_pages = fetch_all_series(page)
    return render_template('all_series.html', series=series, page=current_page, total_pages=total_pages)

ACCESSIBILITY_KEYWORDS = (
    'sign language', 'signed version', 'asl', 'bsl', 'deaf',
    'audio description', 'audio described', 'open caption',
    'closed caption', 'subtitled', 'sdh',
)

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

@app.route('/trailer/<media_type>/<int:media_id>')
def get_trailer(media_type, media_id):
    if media_type not in ('movie', 'tv'):
        return {'key': None}, 400
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_Read_Access_Token
    }
    response = requests.get(
        f'https://api.themoviedb.org/3/{media_type}/{media_id}/videos?language=en-US',
        headers=headers
    )
    if response.status_code == 200:
        results = response.json().get('results', [])
        trailer = pick_english_trailer(results)
        if trailer:
            return {'key': trailer['key']}
        fallback = requests.get(
            f'https://api.themoviedb.org/3/{media_type}/{media_id}/videos',
            headers=headers
        )
        if fallback.status_code == 200:
            all_results = fallback.json().get('results', [])
            trailer = pick_english_trailer(all_results)
            if trailer:
                return {'key': trailer['key']}
    return {'key': None}

if __name__ == '__main__':
    app.run()