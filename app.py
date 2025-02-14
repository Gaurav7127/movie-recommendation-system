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
/* Set background image for the entire app */
.stApp {{
    background-image: url("data:image/jpeg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

/* Title Styling */
.title {{
    font-size: 60px; 
    color: #FFD700;  /* Gold color */
    text-align: center;
    font-family: 'Arial Black', sans-serif;
    padding: 10px 0;
    text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
}}

/* Subtitle Styling */
.subtitle {{
    font-size: 24px;
    color: #FFFFFF;
    text-align: center;
    font-family: 'Arial', sans-serif;
    margin-top: -10px;
    padding-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}}

/* Label for Selectbox */
.selectbox-label {{
    font-size: 20px;
    font-weight: bold;
    text-align: left;
    color: #00FF7F; /* Spring Green */
    margin-bottom: 10px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}}

/* Movie Information Text */
.movie-info {{
    font-size: 18px;
    color: #FFFFFF; /* White for readability */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
}

/* Customize Expander Button */
details summary {{
    color: rgba(255, 255, 255, 0.8) !important;  /* Soft white */
    font-weight: bold;
    font-size: 18px;
    transition: all 0.3s ease-in-out;
    padding: 10px;
    border-radius: 8px;
}}


/* Expander Hover Effect */
details summary:hover {{
    color: #FFD700 !important;  /* Gold hover */
    text-shadow: 0px 0px 8px rgba(255, 215, 0, 0.9);  /* Glow effect */
    transform: scale(1.05);
}}


/* Expander Background */
details {{
    background-color: rgba(0, 0, 0, 0.5) !important;  /* Dark semi-transparent */
    border-radius: 8px;
    padding: 5px;
}}


/* Customize the Let’s Go Button */
button {{
    background-color: #FFD700 !important;  /* Gold */
    color: #000000 !important;  /* Black text */
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 16px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease-in-out;
}}

/* Button Hover */
button:hover {{
    background-color: #FFA500 !important;  /* Orange */
    transform: scale(1.05);
}}

/* Responsiveness for Tablets */
@media (max-width: 1024px) {{
    .title {
        font-size: 40px;
    }
    .subtitle {
        font-size: 18px;
    }
    .movie-poster {
        height: 220px;
        width: 150px;
}}
    
}

/* Responsiveness for Mobile */
@media (max-width: 768px) {{
    .title {
        font-size: 30px;
    }
    .subtitle {
        font-size: 16px;
    }
    .movie-poster {
        height: 180px;
        width: 120px;
    }
    .selectbox-label {
        font-size: 14px;
    }]
}
</style>
 """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">🎬 MovieMatch</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Right Film, Every Time</div>', unsafe_allow_html=True)
st.markdown('<div class="selectbox-label">🎬 Find Your Next Watch 🍿</div>', unsafe_allow_html=True)

selected_movie = st.selectbox("", movies["title"].values, key='movie_selectbox')

if st.button("🚀 Let’s Go"):
    recommendations = recommend(selected_movie)

    for movie in recommendations:
        with st.expander(f"📽️ {movie['title']} (More Info)"):
            st.markdown(f"<span style='color: #FFD700; font-size:18px; font-weight:bold;'>{movie['title']}</span>", unsafe_allow_html=True)
            st.image(movie['poster'], width=300)
            st.markdown(f"<div class='movie-info'>⭐ <b>Rating:</b> {movie['rating']}/10</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'>📅 <b>Release Date:</b> {movie['release_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'>📖 <b>Plot:</b> {movie['plot']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'>🎬 <b>Director:</b> {movie['director']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'>🎭 <b>Cast:</b> {', '.join(movie['cast'])}</div>", unsafe_allow_html=True)
