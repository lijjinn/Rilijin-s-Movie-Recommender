# main_app.py
import streamlit as st
import requests
import time
from dotenv import load_dotenv
import os

# --- Load API key ---
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- Function to get movie details from TMDB ---
def get_movie_details(title):
    """Fetch movie overview, poster, release date, and rating using TMDB API."""
    if not TMDB_API_KEY:
        return {"overview": "No API key found.", "poster": None, "release_date": None, "rating": None}

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]
            return {
                "overview": movie.get("overview", "No description available."),
                "poster": f"https://image.tmdb.org/t/p/w200{movie.get('poster_path')}" if movie.get("poster_path") else None,
                "release_date": movie.get("release_date", "Unknown"),
                "rating": movie.get("vote_average", "N/A"),
            }

    return {"overview": "No details found.", "poster": None, "release_date": None, "rating": None}


# --- Page Setup ---
st.set_page_config(page_title="🎬 Rilijin’s Movie Recommender", page_icon="🎥", layout="wide")

st.markdown("""
    <style>
        /* --- App Background and Text --- */
        .stApp {
            background: linear-gradient(180deg, #0f0f0f, #1a1a1a);
            color: #f5f5f5;
        }
        div[data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, #8A2BE2, #20B2AA);
            height: 10px;
            border-radius: 10px;
        }
        button[kind="secondary"] {
            border-radius: 12px !important;
        }
        .stAlert {
            border-radius: 10px;
            background-color: #222222;
            color: #f5f5f5;
        }
        .stMarkdown p {
            text-align: center;
            font-weight: bold;
            color: #e0e0e0;
        }
        .stCaption {
            text-align: center;
            color: #cccccc;
            font-size: 0.9rem;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Try to import teammate modules ---
try:
    from recommender import get_recommendations
    from mood_detection import analyze_mood
except ImportError:
    get_recommendations = None
    analyze_mood = None

# --- UI ---
st.title("🎬 Rilijin’s Movie Recommender")
st.write("Get movie suggestions based on your mood, favorite films, and genres!")

user_mood = st.text_input("Enter your current mood (e.g., happy, sad, adventurous):")
selected_genre = st.selectbox(
    "Choose a genre:",
    ["Action", "Comedy", "Drama", "Romance", "Horror", "Thriller", "Sci-Fi", "Animation"],
)
favorite_movies = st.text_area("List a few movies you’ve liked (comma separated):")

# --- Session State setup ---
if "recommended_movies" not in st.session_state:
    st.session_state.recommended_movies = []

status_placeholder = st.empty()

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    get_clicked = st.button("Get Recommendations 🎬")
with col2:
    clear_clicked = st.button("Clear Results")

# --- Get Recommendations Logic ---
if get_clicked:
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
                st.session_state.recommended_movies = get_recommendations(
                    mood_score, selected_genre, favorite_movies
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.session_state.recommended_movies = []
        else:
            st.session_state.recommended_movies = [
                {"title": "Inception"},
                {"title": "Interstellar"},
                {"title": "The Dark Knight"},
                {"title": "Tenet"},
            ]

# --- Clear Results ---
if clear_clicked:
    st.session_state.recommended_movies = []
    st.rerun()

# --- Display Recommendations ---
if st.session_state.get("recommended_movies"):
    st.subheader("🎥 Personalized Movie Recommendations")

    cols = st.columns(3)
    for idx, movie in enumerate(st.session_state.recommended_movies):
        with cols[idx % 3]:
            details = get_movie_details(movie["title"])
            poster = details["poster"] or "https://via.placeholder.com/200x300?text=No+Image"
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <img src='{poster}' width='200' style='border-radius:10px; margin-bottom:10px;'>
                    <p style='font-weight:bold; color:#f0f0f0;'>{movie['title']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"More Info about {movie['title']}"):
                st.write(f"**Release Date:** {details['release_date']}")
                st.write(f"**Rating:** {details['rating']}/10 ⭐")
                st.write(details["overview"] or "No additional details available.")

            time.sleep(0.1)

    success_box = status_placeholder.success("Recommendations generated successfully!")
    time.sleep(3)
    success_box.empty()

elif "recommended_movies" in st.session_state and not st.session_state.recommended_movies:
    warning_box = status_placeholder.warning("No recommendations available yet. Try again later!")
    time.sleep(3)
    warning_box.empty()

