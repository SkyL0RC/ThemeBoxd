import pandas as pd
import numpy as np

df = pd.read_json("themes_embedded.json")
df['embedding'] = df['embedding'].apply(np.array)

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# kullanıcıdan alınan filmin temalarını letterboxd'dan çekiyorum.
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

# önceden embed edilmiş df ile kullanıcıdan alınan filmin temalarını benzerlik karşılaştırması yapıyorum.
def recommend(themes,df,top_n=6):
  from sklearn.metrics.pairwise import cosine_similarity

  # tahmin edilmesi istenen temaları vektöre çevirdim.
  theme_vec=model.encode(themes)

  # vektörü 2 boyutlu matris haline getirdim. 
  theme_vec_mean=np.mean(theme_vec,axis=0).reshape(1,-1)

  #temaları tek bir matris haline getirdim.
  vecs=np.vstack(df["embedding"].values)

  sim=cosine_similarity(theme_vec_mean,vecs)[0]

  #tahminleri sıralayıp ters çevirdim.
  predict=sim.argsort()[::-1][:top_n]

  return df.iloc[predict][["name","theme"]]

if __name__ == "__main__":
    movie_name=input("Film ismi giriniz: ")

    movie_themes=get_themes(movie_name)

    predictions=recommend(movie_themes,df)

    print("En benzer temalarda olan filmler: ")
    print(predictions)



