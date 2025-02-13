import streamlit as st
import pandas as pd
import requests
import pickle
import os
import gdown

# Load the movies data from Google Drive
movies_url = 'https://drive.google.com/uc?id=1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl'
similarity_url = 'https://drive.google.com/uc?id=1cau-WUZR1F1TszqManqqkpigga43nC_g'

movies_file = 'movies_dict.pkl'
similarity_file = 'similarity.pkl'

if not os.path.exists(movies_file):
    gdown.download(movies_url, movies_file, quiet=False)

if not os.path.exists(similarity_file):
    gdown.download(similarity_url, similarity_file, quiet=False)

# Load data
movies_dict = pickle.load(open(movies_file, 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open(similarity_file, 'rb'))

# API Key for fetching movie details
API_KEY = '8d45dcb1eefec0761446c65d574e58a6'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Function to fetch movie details
def fetch_movie_details(movie_id):
    try:
        movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US'

        movie_response = requests.get(movie_url).json()
        credits_response = requests.get(credits_url).json()

        poster_url = IMAGE_BASE_URL + movie_response.get('poster_path', '') if movie_response.get('poster_path') else "https://via.placeholder.com/500x750?text=Poster+Not+Found"
        title = movie_response.get('title', 'Unknown')
        rating = movie_response.get('vote_average', 'N/A')
        release_date = movie_response.get('release_date', 'Unknown')
        plot = movie_response.get('overview', 'No plot available.')

        # Get director info
        director_info = next((crew for crew in credits_response.get('crew', []) if crew['job'] == 'Director'), {})
        director_name = director_info.get('name', 'Unknown')
        director_image_url = IMAGE_BASE_URL + director_info.get('profile_path', '') if director_info.get('profile_path') else "https://via.placeholder.com/500x500?text=No+Image"

        # Get cast info (top 3)
        cast_members = []
        for cast_member in credits_response.get('cast', [])[:3]:  # Top 3 cast members
            cast_name = cast_member.get('name', 'Unknown')
            cast_image_url = IMAGE_BASE_URL + cast_member.get('profile_path', '') if cast_member.get('profile_path') else "https://via.placeholder.com/500x500?text=No+Image"
            cast_members.append({'name': cast_name, 'image_url': cast_image_url})

        return {
            'poster_url': poster_url,
            'title': title,
            'rating': rating,
            'release_date': release_date,
            'plot': plot,
            'director_name': director_name,
            'director_image_url': director_image_url,
            'cast_members': cast_members
        }
    except Exception as e:
        return {"error": str(e)}

# Function to get recommendations
def recommend(movie_name):
    try:
        if movie_name not in movies['title'].values:
            return []

        movie_index = movies[movies['title'] == movie_name].index[0]
        distances = similarity[movie_index]
        movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        for idx, _ in movie_indices:
            movie_id = movies.iloc[idx].movie_id
            movie_details = fetch_movie_details(movie_id)
            movie_details['id'] = movie_id  # Store ID for click functionality
            recommended_movies.append(movie_details)

        return recommended_movies
    except Exception as e:
        return []

# Initialize session state for selected movie
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# Title and subtitle
st.markdown("<h1 style='text-align: center;'>🎬 MovieMatch 🎬</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFD700;'>The Right Film, Every Time 🍿</h3>", unsafe_allow_html=True)

# Select movie dropdown
selected_movie_name = st.selectbox("Find your next watch:", movies['title'].values)

# Button to get recommendations
if st.button("Let's Go 🚀"):
    st.session_state.selected_movie = None  # Reset selected movie when getting new recommendations
    recommended_movies = recommend(selected_movie_name)

    if not recommended_movies:
        st.write("No recommendations found.")
    else:
        cols = st.columns(5)
        for idx, movie in enumerate(recommended_movies):
            with cols[idx]:
                if movie['poster_url']:
                    st.image(movie['poster_url'], width=150)
                st.markdown(f"**{movie['title']}**")

                # Create a button for each movie
                if st.button(f"More Info 🎥 {idx}", key=f"movie_{idx}"):
                    st.session_state.selected_movie = movie  # Store selected movie in session state

# Show detailed movie info when clicked
if st.session_state.selected_movie:
    movie = st.session_state.selected_movie

    st.write("---")  # Horizontal divider
    st.markdown(f"<h2 style='text-align: center;'>{movie['title']}</h2>", unsafe_allow_html=True)
    
    # Display movie details
    cols = st.columns([1, 2])
    with cols[0]:
        st.image(movie['poster_url'], width=250)
    
    with cols[1]:
        st.write(f"**⭐ Rating:** {movie['rating']}/10")
        st.write(f"**📅 Release Date:** {movie['release_date']}")
        st.write(f"**📖 Plot:** {movie['plot']}")

        # Director details
        st.write(f"**🎬 Director:** {movie['director_name']}")
        st.image(movie['director_image_url'], width=100, caption=f"{movie['director_name']}")

    # Cast section
    st.write("### 🎭 Top Cast:")
    cast_cols = st.columns(3)
    for idx, cast in enumerate(movie['cast_members']):
        with cast_cols[idx]:
            st.image(cast['image_url'], width=120)
            st.caption(cast['name'])
