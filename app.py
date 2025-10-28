from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# =====================
# Load and prepare data
# =====================

movies = pd.read_csv('archive (1)/tmdb_5000_movies.csv')
credits = pd.read_csv('archive (1)/tmdb_5000_credits.csv')

movies = movies.merge(credits, on='title')
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

def convert(text):
    return [i['name'] for i in ast.literal_eval(text)]

def convert_cast(text):
    return [i['name'] for i in ast.literal_eval(text)[:3]]

def fetch_director(text):
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            return [i['name']]
    return []

def remove_space(words):
    return [i.replace(" ", "") for i in words]

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert_cast)
movies['crew'] = movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())

for col in ['cast', 'crew', 'genres', 'keywords']:
    movies[col] = movies[col].apply(remove_space)

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_df = movies[['movie_id', 'title', 'tags']].copy()
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

# =====================
# Recommender Function
# =====================

def recommend_movies_based_on_movie(movie):
    movie = movie.lower()
    if movie not in new_df['title'].str.lower().values:
        return []
    index = new_df[new_df['title'].str.lower() == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    return [new_df.iloc[i[0]].title for i in movie_list]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    age = int(data.get('age', 18))
    interests = [i.strip().lower() for i in data.get('interests', '').split(',')]
    fav_movie = data.get('fav_movie', '').strip()
    
    similar_movies = recommend_movies_based_on_movie(fav_movie)
    genre_bias = []
    for genre in interests:
        if genre:
            for i, row in new_df.iterrows():
                if genre in row['tags']:
                    genre_bias.append(row['title'])
    
    combined = list(set(similar_movies + genre_bias))
    if age < 18:
        combined = [m for m in combined if "horror" not in m.lower() and "thriller" not in m.lower()]
    if len(combined) > 5:
        combined = combined[:5]
    
    return jsonify({'recommendations': combined})

if __name__ == '__main__':
    app.run(debug=True)
