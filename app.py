import streamlit as st
import pandas as pd
import requests
import time
import base64
import os
import gdown

# Google Drive links to movie data
movies_url = 'https://drive.google.com/uc?id=1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl'
similarity_url = 'https://drive.google.com/uc?id=1cau-WUZR1F1TszqManqqkpigga43nC_g'

movies_file = 'movies_dict.pkl'
similarity_file = 'similarity.pkl'

# Download if files are missing
if not os.path.exists(movies_file):
    gdown.download(movies_url, movies_file, quiet=False)

if not os.path.exists(similarity_file):
    gdown.download(similarity_url, similarity_file, quiet=False)

# Load movie data
movies_dict = pd.read_pickle(movies_file)
movies = pd.DataFrame(movies_dict)
similarity = pd.read_pickle(similarity_file)

# API Key for TMDB
API_KEY = "8d45dcb1eefec0761446c65d574e58a6"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_movie_details(movie_id):
    """ Fetch movie details including poster, rating, release date, plot, and cast. """
    try:
        movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US'

        movie_response = requests.get(movie_url).json()
        credits_response = requests.get(credits_url).json()

        return {
            "title": movie_response.get("title", "Unknown"),
            "poster": IMAGE_BASE_URL + movie_response.get("poster_path", ""),
            "rating": movie_response.get("vote_average", "N/A"),
            "release_date": movie_response.get("release_date", "Unknown"),
            "plot": movie_response.get("overview", "No plot available."),
            "director": next((m['name'] for m in credits_response['crew'] if m['job'] == 'Director'), "Unknown"),
            "cast": [m['name'] for m in credits_response['cast'][:3]]
        }
    except Exception as e:
        return {"error": str(e)}

def recommend(movie):
    """ Get recommended movies and their details. """
    try:
        if movie not in movies['title'].values:
            return []

        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        recommended_movies = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

        movie_details = []
        for i in recommended_movies:
            movie_id = movies.iloc[i[0]].movie_id
            details = fetch_movie_details(movie_id)
            movie_details.append(details)

        return movie_details
    except Exception as e:
        return [{"title": "Error fetching recommendations", "poster": "", "rating": "", "release_date": "", "plot": "", "director": "", "cast": []}]

# Function to convert an image to base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Background image
bg_image = get_base64_image('234234-1140x641.jpg')

# Apply custom styles if background image exists
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
            font-size: 55px; 
            color: #FFFFFF;  
            text-align: center;
            font-family: 'Arial', sans-serif;  
            padding: 10px 0;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }}
        .subtitle {{
            font-size: 20px; 
            color: #FFD700;  
            text-align: center;
            font-family: 'Arial', sans-serif;  
            margin-top: -10px;  
            padding-bottom: 20px;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);  
        }}
        .selectbox-container {{
            text-align: center;
            margin: 5px 0; 
        }}
        .movie-container {{
            text-align: center;
            padding: 10px; 
        }}
        .movie-title {{
            font-size: 20px; 
            color: #FFFFFF;  
            margin-bottom: 10px; 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
        }}
        .movie-poster {{
            height: 250px;  
            width: 170px;   
            border-radius: 10px;  
            border: 2px solid #FFFFFF;  
        }}
        .more-info {{
            background-color: #FFD700;
            color: black;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 16px;
            cursor: pointer;
        }}
        @media (max-width: 1024px) {{
        .title {{
            font-size: 55px;
        }}
        .subtitle {{
            font-size: 18px;
        }}
        .movie-poster {{
            height: 220px;
            width: 150px;
        }}
    }}


    @media (max-width: 768px) {{
        .title {{
            font-size: 45px;
        }}
        .subtitle {{
            font-size: 16px;
        }}
        .movie-poster {{
            height: 180px;
            width: 120px;
        }}
        .selectbox-label {{
            font-size: 14px;
        }}
    }}
        </style>
        """,
        unsafe_allow_html=True
    )

# App Title
st.markdown('<h1 class="title">MovieMatch</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Right Film, Every Time</div>', unsafe_allow_html=True)

# Select movie dropdown
selected_movie = st.selectbox("🎬 Find your next watch 🍿", movies['title'].values)

# Show recommendations when button is clicked
if st.button('Let’s Go 🚀'):
    recommendations = recommend(selected_movie)
    
    num_cols = min(5, len(recommendations))
    cols = st.columns(num_cols)
    
    for idx, (col, movie) in enumerate(zip(cols, recommendations)):
        with col:
            st.markdown(f"""
                <div class="movie-container">
                    <p class="movie-title">{movie['title']}</p>
                    <img src="{movie['poster']}" class="movie-poster"/>
                </div>
            """, unsafe_allow_html=True)

for idx, movie in enumerate(recommendations):
        with st.expander(f"📽️ {movie['title']} (More Info)"):       
            st.write(f"⭐ **Rating:** {movie['rating']}/10")
            st.write(f"📅 **Release Date:** {movie['release_date']}")
            st.write(f"📖 **Plot:** {movie['plot']}")
            st.write(f"🎬 **Director:** {movie['director']}")
            st.write(f"🎭 **Cast:** {', '.join(movie['cast'])}")
