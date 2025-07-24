import pandas as pd

df=pd.read_json("themes.json")

df=df[df["theme"]!="NaN"]

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_film_embedding(theme_list):
    embeddings = model.encode(theme_list)
    return np.mean(embeddings, axis=0)

# theme sütunundaki her bir elemanı fonksiyona gönderiyorum.
df['embedding'] = df['theme'].apply(get_film_embedding)

df["embedding"]=df["embedding"].apply(lambda x: x.tolist())

df.to_json("themes_embedded.json", orient="records", indent=2)