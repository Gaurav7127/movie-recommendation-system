import streamlit as st
import pandas as pd
import requests
import pickle
import base64
import os

# Load the data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

API_KEY = "8d45dcb1eefec0761446c65d574e58a6"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_movie_details(movie_id):
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
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        recommended_movie_indices = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

        recommendations = []
        for i in recommended_movie_indices:
            movie_id = movies.iloc[i[0]].movie_id
            details = fetch_movie_details(movie_id)
            recommendations.append(details)

        return recommendations
    except Exception as e:
        return [{"title": "Error fetching recommendations", "poster": "", "rating": "", "release_date": "", "plot": "", "director": "", "cast": []}]

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
            background-position: center;
            background-repeat: no-repeat;
        }}
        .title {{
            font-size: 55px; 
            color: #FFFFFF;  
            text-align: center;
            font-family: 'Arial', sans-serif;  
            padding: 10px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }}
        .movie-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            padding: 20px;
        }}
        .movie-card {{
            background: rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            color: white;
            width: 250px;
        }}
        .movie-poster {{
            width: 100%;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown('<h1 class="title">MovieMatch</h1>', unsafe_allow_html=True)
selected_movie = st.selectbox("🎬 Choose a movie:", movies["title"].values)

if st.button("🍿 Show Recommendations"):
    recommendations = recommend(selected_movie)
    
    st.markdown("<div class='movie-container'>", unsafe_allow_html=True)
    for movie in recommendations:
        st.markdown(
            f"""
            <div class='movie-card'>
                <img src="{movie['poster']}" class='movie-poster'/>
                <h3>{movie['title']}</h3>
                <p>⭐ {movie['rating']} | 📅 {movie['release_date']}</p>
                <p><b>Director:</b> {movie['director']}</p>
                <p><b>Cast:</b> {', '.join(movie['cast'])}</p>
                <p>{movie['plot']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
