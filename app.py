from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_key')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)