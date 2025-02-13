import streamlit as st
import pandas as pd
import requests
import time
import base64
import os
import gdown

movies_url = 'https://drive.google.com/uc?id=1CUX_tGSQAiesw6lq1vEOzSMSHJMFo0xl'
similarity_url = 'https://drive.google.com/uc?id=1cau-WUZR1F1TszqManqqkpigga43nC_g'

movies_file = 'movies_dict.pkl'
similarity_file = 'similarity.pkl'

if not os.path.exists(movies_file):
    gdown.download(movies_url, movies_file, quiet=False)

if not os.path.exists(similarity_file):
    gdown.download(similarity_url, similarity_file, quiet=False)

def fetch_movie_details(movie_id, retries=3, delay=5):
    api_key = '8d45dcb1eefec0761446c65d574e58a6'
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US'
    image_base_url = 'https://image.tmdb.org/t/p/w500'

    for attempt in range(retries):
        try:
            movie_response = requests.get(movie_url)
            movie_response.raise_for_status()
            movie_data = movie_response.json()

            credits_response = requests.get(credits_url)
            credits_response.raise_for_status()
            credits_data = credits_response.json()

            poster_path = movie_data.get('poster_path')
            poster_url = f'{image_base_url}/{poster_path}' if poster_path else None
            title = movie_data.get('title')
            rating = movie_data.get('vote_average')
            release_date = movie_data.get('release_date')
            plot = movie_data.get('overview')

            director_data = next((member for member in credits_data['crew'] if member['job'] == 'Director'), None)
            director_name = director_data['name'] if director_data else 'Unknown'
            director_image_path = director_data['profile_path'] if director_data and director_data.get('profile_path') else None
            director_image_url = f'{image_base_url}/{director_image_path}' if director_image_path else None

            cast_members = []
            for cast_member in credits_data['cast'][:3]:
                cast_name = cast_member['name']
                cast_image_path = cast_member['profile_path']
                cast_image_url = f'{image_base_url}/{cast_image_path}' if cast_image_path else None
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

        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return None

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies = [movies.iloc[i[0]] for i in movie_list]
        return recommended_movies
    except IndexError:
        return []

movies_dict = pd.read_pickle(movies_file)
movies = pd.DataFrame(movies_dict)
similarity = pd.read_pickle(similarity_file)

st.markdown('<h1 class="title">MovieMatch</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Right Film,Every Time</div>', unsafe_allow_html=True)


st.markdown('<div class="selectbox-container"><div class="selectbox-label">🎬 Find your next watch 🍿</div></div>',
            unsafe_allow_html=True)

selected_movie_name = st.selectbox('Pick a movie:', movies['title'].values)

if st.button('Lets Goo 🚀🎥'):
    recommended_movies = recommend(selected_movie_name)
    for movie in recommended_movies:
        movie_id = movie.movie_id
        movie_details = fetch_movie_details(movie_id)
        if movie_details:
            if st.button(movie_details['title']):
                st.image(movie_details['poster_url'], width=300)
                st.write(f"**Rating:** {movie_details['rating']}/10")
                st.write(f"**Release Date:** {movie_details['release_date']}")
                st.write(f"**Plot:** {movie_details['plot']}")
                st.write(f"**Director:** {movie_details['director_name']}")
                if movie_details['director_image_url']:
                    st.image(movie_details['director_image_url'], width=150, caption=f"Director: {movie_details['director_name']}")
                st.write("**Cast:**")
                for cast_member in movie_details['cast_members']:
                    st.image(cast_member['image_url'], width=100, caption=cast_member['name'])
