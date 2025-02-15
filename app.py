import streamlit as st
import pandas as pd
import requests
import pickle
import base64

# Load data
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

# Initialize session state to track which movie is expanded
if "expanded_movie" not in st.session_state:
    st.session_state.expanded_movie = None

# Convert background image to Base64
bg_base64 = base64.b64encode(bg_image).decode()

# Inject Custom CSS with your background image
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .title {{
        font-size: 60px; 
        color: #FFD700;  
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        padding: 10px 0;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
    }}

    .subtitle {{
        font-size: 24px;
        color: #FFFFFF;
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
        color: #00FF7F;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
    }}

    .movie-info {{
        font-size: 18px;
        color: #FFFFFF;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
    }}

    details summary {{
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s ease-in-out;
        padding: 10px;
        border-radius: 8px;
    }}

    details summary:hover {{
        color: #FFD700 !important;
        text-shadow: 0px 0px 8px rgba(255, 215, 0, 0.9);
        transform: scale(1.05);
    }}

    details {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border-radius: 8px;
        padding: 5px;
    }}

    button {{
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease-in-out;
    }}

    button:hover {{
        background-color: #FFA500 !important;
        transform: scale(1.05);
    }}

    @media (max-width: 1024px) {{
        .title {{ font-size: 40px; }}
        .subtitle {{ font-size: 18px; }}
    }}

    @media (max-width: 768px) {{
        .title {{ font-size: 30px; }}
        .subtitle {{ font-size: 16px; }}
    }}
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

    for index, movie in enumerate(recommendations):
        expander_key = f"expander_{index}"
        
        # Check if this movie should be expanded
        expanded = st.session_state.expanded_movie == expander_key

        # Define expander
        with st.expander(f"📽️ {movie['title']} (More Info)", expanded=expanded):
            st.image(movie['poster'], width=300)
            st.markdown(f"**⭐ Rating:** {movie['rating']}/10")
            st.markdown(f"**📅 Release Date:** {movie['release_date']}")
            st.markdown(f"**📖 Plot:** {movie['plot']}")
            st.markdown(f"**🎬 Director:** {movie['director']}")
            st.markdown(f"**🎭 Cast:** {', '.join(movie['cast'])}")

            # Set session state to track the last opened movie
            if expanded:
                st.session_state.expanded_movie = expander_key

