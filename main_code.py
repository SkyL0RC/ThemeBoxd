import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
import requests
import re

TMDB_API_KEY = "4c4ca6bb233ef9ca3b5172891aacb992"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
df = pd.read_json("themes_embedded.json")
df['embedding'] = df['embedding'].apply(np.array)
model = SentenceTransformer('all-MiniLM-L6-v2')

def slugify(name):
    return re.sub(r'(^-|-$)', '', re.sub(r'[^a-z0-9]+', '-', name.lower()))

def get_themes(movie_name):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()  
    options.add_argument("user-agent")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    film_url = movie_name.strip().replace(" ", "-")
    url = f"https://letterboxd.com/film/{film_url}/genres/"

    driver.get(url)

    themes = []

    try:
        tab_genres = wait.until(EC.presence_of_element_located((By.ID, "tab-genres")))
        divs = tab_genres.find_elements(By.TAG_NAME, "div")
        a_list = divs[1].find_elements(By.TAG_NAME, "a")
        for a in a_list[:-1]:
            themes.append(a.text)
    except:
        themes = []

    driver.quit()
    return themes

def recommend(themes, df, movie_name=None, top_n=6):
    from sklearn.metrics.pairwise import cosine_similarity
    theme_vec = model.encode(themes)
    theme_vec_mean = np.mean(theme_vec, axis=0).reshape(1, -1)
    vecs = np.vstack(df["embedding"].values)
    sim = cosine_similarity(theme_vec_mean, vecs)[0]
    predict = sim.argsort()[::-1]
    results = df.iloc[predict][["name", "theme"]]
    if movie_name:
        # Girilen film adını önerilerden çıkar (küçük harfe çevirerek karşılaştır)
        results = results[results["name"].str.lower() != movie_name.strip().lower()]
    return results.head(top_n)

def get_tmdb_poster_url(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        print(f"TMDB API request: {url}")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        print(f"TMDB API response for '{movie_name}': {data}")
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                print(f"Poster for {movie_name}: {poster_url}")
                return poster_url
        # Fallback: Letterboxd poster URL (çalışmazsa placeholder)
        slug = slugify(movie_name)
        fallback_url = f"https://letterboxd.com/film/{slug}/poster/"
        print(f"No TMDB poster for {movie_name}, fallback: {fallback_url}")
        return fallback_url
    except Exception as e:
        print(f"TMDB poster error: {e}")
        slug = slugify(movie_name)
        return f"https://letterboxd.com/film/{slug}/poster/"

@app.route('/api/oner', methods=['POST'])
def api_oner():
    try:
        data = request.get_json()
        movie_name = data.get('filmAdi')
        print(f"Kullanıcıdan gelen film adı: {movie_name}")
        if not movie_name:
            return jsonify({'error': 'filmAdi alanı zorunlu!'}), 400
        movie_themes = get_themes(movie_name)
        print(f"Çekilen temalar: {movie_themes}")
        if not movie_themes:
            return jsonify({'error': 'Film teması bulunamadı!'}), 404
        predictions = recommend(movie_themes, df, movie_name=movie_name)
        result = predictions.to_dict(orient='records')
        user_film_poster = get_tmdb_poster_url(movie_name)
        print(f"User film poster: {user_film_poster}")
        for film in result:
            film['poster_url'] = get_tmdb_poster_url(film['name'])
            print(f"Poster for {film['name']}: {film['poster_url']}")
        return jsonify({'oneriler': result, 'user_film_theme': movie_themes, 'user_film_poster': user_film_poster})
    except Exception as e:
        print(f"API ERROR: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)



