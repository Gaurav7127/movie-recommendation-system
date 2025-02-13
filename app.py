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
            color: #FFD700;  
            text-align: center;
            font-family: 'Arial Black', sans-serif;  
            padding: 20px 0;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
        }}
        .subtitle {{
            font-size: 22px; 
            color: #FFFFFF;  
            text-align: center;
            font-family: 'Arial', sans-serif;  
            margin-top: -15px;  
            padding-bottom: 25px;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.7);  
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown('<h1 class="title">MovieMatch</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subtitle">The Right Film, Every Time</h3>', unsafe_allow_html=True)

st.markdown('<div class="selectbox-container"><div class="selectbox-label">🎬 Find your next watch 🍿</div></div>',
            unsafe_allow_html=True)

selected_movie_name = st.selectbox('', movies['title'].values, key='movie_selectbox')

if st.button('Lets Goo 🚀'):
    names, posters = recommend(selected_movie_name)

    for idx, movie in enumerate(recommendations):
        with st.expander(f"📽️ {movie['title']} (More Info)"):
            st.image(movie['poster'], width=300)
            st.write(f"⭐ **Rating:** {movie['rating']}/10")
            st.write(f"📅 **Release Date:** {movie['release_date']}")
            st.write(f"📖 **Plot:** {movie['plot']}")
            st.write(f"🎬 **Director:** {movie['director']}")
            st.write(f"🎭 **Cast:** {', '.join(movie['cast'])}")
