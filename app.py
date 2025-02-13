import streamlit as st
import pandas as pd
import requests
import pickle

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

API_KEY = "8d45dcb1eefec0761446c65d574e58a6"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Apply background image using CSS
BACKGROUND_IMAGE_URL = "https://wallpapercave.com/wp/wp4065228.jpg"
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url("{BACKGROUND_IMAGE_URL}");
            background-size: cover;
            background-position: center;
        }}
        .movie-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .movie-title {{
            font-size: 18px;
            font-weight: bold;
            color: white;
            text-align: center;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

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

# Streamlit App
st.title("🎬 MovieMatch - Find Your Next Watch!")

selected_movie = st.selectbox("Choose a movie:", movies["title"].values)

if st.button("🎥 Show Recommendations"):
    recommendations = recommend(selected_movie)

    for idx, movie in enumerate(recommendations):
        st.markdown(f"<div class='movie-container'>", unsafe_allow_html=True)
        st.image(movie['poster'], width=250)
        more_info_button = st.button(f"ℹ️ More Info - {movie['title']}", key=f"info_{idx}")

        if more_info_button:
            st.write(f"⭐ **Rating:** {movie['rating']}/10")
            st.write(f"📅 **Release Date:** {movie['release_date']}")
            st.write(f"📖 **Plot:** {movie['plot']}")
            st.write(f"🎬 **Director:** {movie['director']}")
            st.write(f"🎭 **Cast:** {', '.join(movie['cast'])}")

        st.markdown("</div>", unsafe_allow_html=True)
