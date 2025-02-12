import streamlit as st
import pandas as pd
import requests
import time
import base64
import gdown
import os

# Function to download files from Google Drive
def download_file_from_gdrive(url, output_path):
    file_id = url.split('/d/')[1].split('/')[0]
    download_url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(download_url, output_path, quiet=False)

# Download the files if not already present
if not os.path.exists('movies_dict.pkl'):
    download_file_from_gdrive('https://drive.google.com/file/d/1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl/view?usp=drive_link', 'movies_dict.pkl')

if not os.path.exists('similarity.pkl'):
    download_file_from_gdrive('https://drive.google.com/file/d/1cau-WUZR1F1TszqManqqkpigga43nC_g/view?usp=drive_link', 'similarity.pkl')

# Function to fetch movie poster
def fetch_poster(movie_id, retries=2, delay=3):
    api_key = '8d45dcb1eefec0761446c65d574e58a6'  # Replace with your actual API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            return f'https://image.tmdb.org/t/p/w500/{poster_path}' if poster_path else "Poster not available."
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return "Error fetching poster"

# Function to recommend movies
def recommend(movie):
    if movie not in movies['title'].values:
        return ["Movie not found"], [""]

    movie_index = movies[movies['title'] == movie].index[0]

    if movie_index >= len(similarity):
        return ["Similarity index out of range"], [""]

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movies_posters = []

    for i in movie_list:
        if i[0] < len(movies):
            movie_id = movies.iloc[i[0]].movie_id
            recommend_movies.append(movies.iloc[i[0]].title)
            recommend_movies_posters.append(fetch_poster(movie_id))
        else:
            recommend_movies.append("Movie ID not found")
            recommend_movies_posters.append("")

    return recommend_movies, recommend_movies_posters

# Load movie data
movies_dict = pd.read_pickle('movies_dict.pkl')
movies = pd.DataFrame(movies_dict)
similarity = pd.read_pickle('similarity.pkl')

# Load background image
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

bg_image = get_base64_image('234234-1140x641.jpg')

# Streamlit UI Styling
if bg_image:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .title {{
            font-size: 50px; 
            color: #FFFFFF;  
            text-align: center;
            font-family: 'Arial', sans-serif;  
            padding: 20px 0;  
        }}
        .selectbox-container {{
            text-align: left;
            margin: 5px 0; 
        }}
        .selectbox-label {{
            font-size: 16px; 
            color: #FFFFFF;  
            font-family: 'Arial', sans-serif; 
            margin-bottom: 10px;  
        }}
        .custom-selectbox select {{
            font-size: 18px;  
            color: #4682B4; 
            padding: 10px;  
            border-radius: 5px;  
            border: 2px solid #4B0082; 
            background-color: #f0f8ff; 
        }}
        .movie-title {{
            font-size: 20px; 
            color: #FFFFFF;  
            margin-bottom: 10px; 
        }}
        .movie-poster {{
            height: 200px;  
            width: 400px;   
            border-radius: 10px;  
            border: 2px solid #FFFFFF;  
        }}
        .poster-container {{
            text-align: center;
            padding: 10px; 
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit UI Components
st.markdown('<h1 class="title">Movie Recommender System</h1>', unsafe_allow_html=True)

st.markdown('<div class="selectbox-container"><div class="selectbox-label">Find your next watch</div></div>',
            unsafe_allow_html=True)

selected_movie_name = st.selectbox('', movies['title'].values, key='movie_selectbox')

if st.button('Lets Goo 🚀'):
    names, posters = recommend(selected_movie_name)

    # Dynamically adjust columns based on recommendations
    cols = st.columns(min(5, len(names)))

    for col, name, poster in zip(cols, names, posters):
        col.markdown(
            f'''
            <div class="poster-container" style="text-align:center;">
                <p class="movie-title">{name}</p>
                <img src="{poster}" class="movie-poster"/>
            </div>
            ''',
            unsafe_allow_html=True
        )
