import streamlit as st
import pandas as pd
import requests
import time
import base64
import os
import gdown

# Download required files
movies_url = 'https://drive.google.com/uc?id=1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl'
similarity_url = 'https://drive.google.com/uc?id=1cau-WUZR1F1TszqManqqkpigga43nC_g'

movies_file = 'movies_dict.pkl'
similarity_file = 'similarity.pkl'

if not os.path.exists(movies_file):
    gdown.download(movies_url, movies_file, quiet=False)

if not os.path.exists(similarity_file):
    gdown.download(similarity_url, similarity_file, quiet=False)

# Load movie data
movies_dict = pd.read_pickle(movies_file)
movies = pd.DataFrame(movies_dict)
similarity = pd.read_pickle(similarity_file)

# Fetch movie details
API_KEY = '8d45dcb1eefec0761446c65d574e58a6'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

def fetch_movie_details(movie_id):
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US'
    
    try:
        movie_response = requests.get(movie_url)
        movie_response.raise_for_status()
        movie_data = movie_response.json()
        
        credits_response = requests.get(credits_url)
        credits_response.raise_for_status()
        credits_data = credits_response.json()
        
        poster_url = IMAGE_BASE_URL + movie_data.get('poster_path', '') if movie_data.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
        director = next((crew['name'] for crew in credits_data['crew'] if crew['job'] == 'Director'), 'Unknown')
        cast = [cast['name'] for cast in credits_data['cast'][:3]]
        
        return {
            'title': movie_data['title'],
            'poster_url': poster_url,
            'rating': movie_data['vote_average'],
            'release_date': movie_data['release_date'],
            'plot': movie_data['overview'],
            'director': director,
            'cast': cast
        }
    except requests.exceptions.RequestException:
        return None

# Recommendation function
def recommend(movie):
    if movie not in movies['title'].values:
        return []
    
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommendations = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        if movie_details:
            recommendations.append(movie_details)
    
    return recommendations

# Streamlit UI
st.title('🎬 MovieMatch - Find Your Next Watch 🍿')
selected_movie = st.selectbox('Pick a movie:', movies['title'].values)

if st.button('🎥 Get Recommendations!'):
    recommended_movies = recommend(selected_movie)
    
    if recommended_movies:
        for movie in recommended_movies:
            if st.button(f"🎭 {movie['title']}"):
                st.image(movie['poster_url'], width=300)
                st.write(f"⭐ Rating: {movie['rating']}/10")
                st.write(f"📅 Release Date: {movie['release_date']}")
                st.write(f"🎬 Director: {movie['director']}")
                st.write(f"🎭 Cast: {', '.join(movie['cast'])}")
                st.write(f"📖 Plot: {movie['plot']}")
    else:
        st.write("No recommendations found. Try another movie!")
