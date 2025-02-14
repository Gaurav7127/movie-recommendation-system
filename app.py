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
    """ Get recommended movies. """
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
            font-size: 60px; 
            color: #FFD700;  /* Gold color for better contrast */
            text-align: center;
            font-family: 'Arial Black', sans-serif;  
            padding: 10px 0;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
        }}
        .subtitle {{
            font-size: 24px; 
            color: #FFFFFF;  /* White color for clarity */
            text-align: center;
            font-family: 'Arial', sans-serif;  
            margin-top: -10px;  
            padding-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);  
        }}
        .selectbox-label {{
            font-size: 20px;
            font-weight: bold;
            text-align: left;
            color: #00FF7F; /* Spring Green for unique contrast */
            margin-bottom: 10px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        .movie-info {{
            font-size: 18px;
            color: #FFFFFF; /* White for readability */
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
        }}
        .streamlit-expanderHeader {{
            font-size: 18px !important;
            font-weight: bold !important;
            color: #FFD700 !important; /* Gold color */
            background-color: rgba(255, 255, 255, 0.1) !important;
            padding: 10px !important;
            border-radius: 10px !important;
        }}
        /* Responsiveness for tablets */
        @media (max-width: 1024px) {{
            .title {{
                font-size: 40px;
            }}
            .subtitle {{
                font-size: 18px;
            }}
            .movie-poster {{
                height: 220px;
                width: 150px;
            }}
        }}
        /* Responsiveness for mobile devices */
        @media (max-width: 768px) {{
            .title {{
                font-size: 30px;
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
st.markdown("""
    <style>
    /* Change the color of the expander title */
    .streamlit-expanderHeader {
        color: #FFD700 !important;  /* Gold color */
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Get recommended movies
recommendations = recommend(selected_movie)

# Display recommended movies
for movie in recommendations:
    with st.expander(f"📽️ <span style='color: #FFD700;'>{movie['title']} (More Info)</span>", expanded=False):
        st.image(movie['poster'], width=300)
        st.markdown(f"<div class='movie-info'>⭐ <b>Rating:</b> {movie['rating']}/10</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-info'>📅 <b>Release Date:</b> {movie['release_date']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-info'>📖 <b>Plot:</b> {movie['plot']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-info'>🎬 <b>Director:</b> {movie['director']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-info'>🎭 <b>Cast:</b> {', '.join(movie['cast'])}</div>", unsafe_allow_html=True)
