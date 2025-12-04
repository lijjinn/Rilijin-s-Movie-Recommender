# main_app.py
import streamlit as st
import requests
import time

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_movie_details(title):
    """Fetch movie overview and poster using TMDB API."""
    if not TMDB_API_KEY:
        return {"overview": "No API key found.", "poster": None}

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]
            return {
                "overview": movie.get("overview", "No description available."),
                "poster": f"https://image.tmdb.org/t/p/w200{movie.get('poster_path')}" if movie.get("poster_path") else None
            }
    return {"overview": "No details found.", "poster": None}


st.markdown("""
    <style>
        /* Style Streamlit progress bar to match dark theme */
        div[data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, #8A2BE2, #20B2AA);
        }
        /* Optional: Customize success message color */
        .stAlert {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)


try:
    from recommender import get_recommendations
    from mood_detection import analyze_mood
except ImportError:
    get_recommendations = None
    analyze_mood = None


# Streamlit Page Setup

st.set_page_config(page_title="🎬 Rilijin’s Movie Recommender", page_icon="🎥", layout="wide")

st.title("🎬 Rilijin’s Movie Recommender")
st.write("Get movie suggestions based on your mood, favorite films, and genres!")


# User Input Fields

user_mood = st.text_input("Enter your current mood (e.g., happy, sad, adventurous):")
selected_genre = st.selectbox(
    "Choose a genre:",
    ["Action", "Comedy", "Drama", "Romance", "Horror", "Thriller", "Sci-Fi", "Animation"]
)
favorite_movies = st.text_area("List a few movies you’ve liked (comma separated):")


# Fetch Recommendations
recommended_movies = []

if st.button("Get Recommendations 🎬"):
    with st.spinner("Fetching personalized recommendations..."):

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)
        progress.empty()
        time.sleep(1.5)

        if get_recommendations and analyze_mood:
            try:
                mood_score = analyze_mood(user_mood)
                recommended_movies = get_recommendations(mood_score, selected_genre, favorite_movies)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                recommended_movies = []
        else:
            recommended_movies = [
                {"title": "Inception", "poster": "https://image.tmdb.org/t/p/w200/qmDpIHrmpJINaRKAfWQfftjCdyi.jpg"},
                {"title": "Interstellar", "poster": "https://image.tmdb.org/t/p/w200/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg"},
                {"title": "The Dark Knight", "poster": "https://image.tmdb.org/t/p/w200/qJ2tW6WMUDux911r6m7haRef0WH.jpg"},
                {"title": "Tenet", "poster": "https://image.tmdb.org/t/p/w200/aCIFMriQh8rvhxpN1IWGgvH0Tlg.jpg"}
            ]

    # Create placeholder for messages
    status_placeholder = st.empty()

    # --- Display Recommendations (now inside button logic) ---
    if recommended_movies:
        st.subheader("🎥 Personalized Movie Recommendations")

        cols = st.columns(3)
        for idx, movie in enumerate(recommended_movies):
            with cols[idx % 3]:
                details = get_movie_details(movie["title"])
                poster = details["poster"] or "https://via.placeholder.com/200x300?text=No+Image"
                st.image(poster, width=200)
                st.markdown(f"**{movie['title']}**")
                st.caption(details["overview"][:200] + "...")

                time.sleep(0.1)

        success_box = status_placeholder.success("Recommendations generated successfully!")
        time.sleep(3)
        success_box.empty()
    else:
        warning_box = status_placeholder.warning("No recommendations available yet. Try again later!")
        time.sleep(3)
        warning_box.empty()