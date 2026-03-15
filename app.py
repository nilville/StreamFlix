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

if __name__ == '__main__':
    app.run()