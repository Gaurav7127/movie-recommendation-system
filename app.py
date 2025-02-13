import streamlit as st
import pandas as pd
import requests
import time
import pickle
import base64
import os
import gdown

# Google Drive URLs for movie data
movies_url = 'https://drive.google.com/uc?id=1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl'
similarity_url = 'https://drive.google.com/uc?id=1cau-WUZR1F1TszqManqqkpigga43nC_g'

movies_file = 'movies_dict.pkl'
similarity_file = 'similarity.pkl'

if not os.path.exists(movies_file):
    gdown.download(movies_url, movies_file, quiet=False)
if not os.path.exists(similarity_file):
    gdown.download(similarity_url, similarity_file, quiet=False)

movies_dict = pd.read_pickle(movies_file)
movies = pd.DataFrame(movies_dict)
similarity = pd.read_pickle(similarity_file)

API_KEY = '8d45dcb1eefec0761446c65d574e58a6'  # Replace with your actual API key
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Fetch movie details including poster, rating, release date, plot, cast, and director
def fetch_movie_details(movie_id, retries=3, delay=5):
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US'

    for attempt in range(retries):
        try:
            movie_data = requests.get(movie_url).json()
            credits_data = requests.get(credits_url).json()

            poster_path = movie_data.get('poster_path')
            poster_url = f'{IMAGE_BASE_URL}/{poster_path}' if poster_path else "https://via.placeholder.com/500x750?text=Poster+Not+Found"
            
            director_data = next((member for member in credits_data['crew'] if member['job'] == 'Director'), None)
            director_name = director_data['name'] if director_data else 'Unknown'
            director_image_url = f'{IMAGE_BASE_URL}/{director_data["profile_path"]}' if director_data and director_data.get('profile_path') else "https://via.placeholder.com/500x500?text=No+Image"
            
            cast_members = [{
                'name': cast['name'],
                'image_url': f'{IMAGE_BASE_URL}/{cast["profile_path"]}' if cast.get('profile_path') else "https://via.placeholder.com/500x500?text=No+Image"
            } for cast in credits_data['cast'][:3]]

            return {
                'poster_url': poster_url,
                'title': movie_data.get('title', 'Unknown'),
                'rating': movie_data.get('vote_average', 'N/A'),
                'release_date': movie_data.get('release_date', 'Unknown'),
                'plot': movie_data.get('overview', 'No description available'),
                'director_name': director_name,
                'director_image_url': director_image_url,
                'cast_members': cast_members
            }
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return {"error": "Failed to fetch movie details."}

# Movie recommendation function
def recommend(movie):
    if movie not in movies['title'].values:
        return [{"title": "Movie not found", "poster_url": "", "rating": "", "release_date": "", "plot": "", "director_name": "", "director_image_url": "", "cast_members": []}]
    
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    return [fetch_movie_details(movies.iloc[i[0]].movie_id) for i in movie_list]

# Background Styling
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

bg_image = get_base64_image('234234-1140x641.jpg')
if bg_image:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_image}");
            background-size: cover;
        }}
        .title {{ font-size: 55px; color: #FFF; text-align: center; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); }}
        .subtitle {{ font-size: 20px; color: #FFD700; text-align: center; }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown('<h1 class="title">MovieMatch 🎬</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Right Film, Every Time 🍿</div>', unsafe_allow_html=True)

selected_movie_name = st.selectbox('Find your next watch:', movies['title'].values, key='movie_selectbox')

if st.button('Lets Goo 🚀'):
    recommended_movies = recommend(selected_movie_name)
    st.write("---")
    for movie in recommended_movies:
        st.header(movie['title'])
        st.image(movie['poster_url'], width=300)
        st.write(f"⭐ *Rating:* {movie['rating']}/10")
        st.write(f"📅 *Release Date:* {movie['release_date']}")
        st.write(f"📖 *Plot:* {movie['plot']}")
        
        st.write(f"🎬 *Director:* {movie['director_name']}")
        st.image(movie['director_image_url'], width=150, caption=f"Director: {movie['director_name']}")
        
        st.write("👥 *Cast:* ")
        cols = st.columns(3)
        for idx, cast in enumerate(movie['cast_members']):
            with cols[idx]:
                st.image(cast['image_url'], width=150)
                st.caption(cast['name'])
