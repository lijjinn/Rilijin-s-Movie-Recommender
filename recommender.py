import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# -----------------------------------------------------------
# Streamlit Catching for API Requests
# -----------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=3600)
def tmdb_request(url):
    """Cached TMDB GET request."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

# -----------------------------------------------------------
# Search Movie -> TMBD ID
# -----------------------------------------------------------
def search_movie_id(title):
    url = f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
    data = tmdb_request(url)
    if data.get("results"):
        return data["results"][0]["id"]
    return None

# -----------------------------------------------------------
# Get Similar Movies
# -----------------------------------------------------------
def get_tmdb_similar(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar?api_key={TMDB_API_KEY}"
    data = tmdb_request(url)
    return data.get("results", [])

# -----------------------------------------------------------
# Get Movie Details
# -----------------------------------------------------------
def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=keywords"
    return tmdb_request(url)

# -----------------------------------------------------------
# Mood Keyword Map
# -----------------------------------------------------------
MOOD_KEYWORD_MAP = {
    "happy": ["feel good", "comedy", "fun", "inspiration"],
    "sad": ["sad", "loss", "tragedy", "drama"],
    "angry": ["revenge", "crime", "violence"],
    "relaxed": ["calm", "romance", "easy"],
    "bored": ["action", "fast", "thriller"],
    "romantic": ["love", "romance"],
    "scared": ["horror", "fear", "supernatural"],
    "adventurous": ["adventure", "journey", "explore"],
    "neutral": ["drama", "mystery", "fantasy"]
}

# -----------------------------------------------------------
# Hybrid Scoring System
# -----------------------------------------------------------
def compute_score(movie, mood_keywords, genre_id):
    score = 0

    # Rating weight
    score += movie.get("vote_average", 0) * 1.5

    # Popularity weight
    score += movie.get("popularity", 0) * 0.05

    # Mood keyword match
    overview = movie.get("overview", "").lower()
    if any(kw in overview for kw in mood_keywords):
        score += 14

    # Genre match
    if genre_id in movie.get("genre_ids", []):
        score += 10

    return score

# -----------------------------------------------------------
# Main Recommendation Function
# -----------------------------------------------------------
def get_recommendations(mood_data, genre, favorite_text):
    mood = mood_data.get("mood", "neutral")
    mood_keywords = MOOD_KEYWORD_MAP.get(mood, MOOD_KEYWORD_MAP["neutral"])

    # Genre -> TMDB Genre ID Mapping
    GENRE_MAP = {
        "Action": 28,
        "Comedy": 35,
        "Drama": 18,
        "Romance": 10749,
        "Horror": 27,
        "Thriller": 53,
        "Sci-Fi": 878,
        "Animation": 16,
    }
    genre_id = GENRE_MAP.get(genre)

    favorites = [m.strip() for m in favorite_text.split(",") if m.strip()]
    similar_pool = []

    # -----------------------------------------------------------
    # For each favorite movie, add similar movies
    # -----------------------------------------------------------
    for fav in favorites:
        movie_id = search_movie_id(fav)
        if movie_id:
            similar_pool.extend(get_tmdb_similar(movie_id))

    
    # if user has no favorites, fallback to popular movies
    if not similar_pool:
        url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}"
        similar_pool = tmdb_request(url).get("results", [])

    # -----------------------------------------------------------
    # Score all candidate movies
    # -----------------------------------------------------------
    scored = []
    for movie in similar_pool:
        score = compute_score(movie, mood_keywords, genre_id)
        scored.append((movie, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # -----------------------------------------------------------
    # Return top 15 results as Streamlit-compatible dicts
    # -----------------------------------------------------------
    return [{"title": m["title"]} for m, s in scored[:15]]
