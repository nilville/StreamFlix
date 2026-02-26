from flask import Flask, render_template, request
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

app = Flask(__name__)

@app.route('/')
def index():
    trending_movies = tmdb()
    return render_template('home.html', movies=trending_movies)

@app.route('/series')
def series():
    trending_series = tmdb_series()
    return render_template('series.html', series=trending_series)

if __name__ == '__main__':
    app.run(debug=True)