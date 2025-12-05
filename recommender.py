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
    # NOTE: movie here is expected to be the TMDB 'movie' dict returned
    # from the details endpoint (so it may include 'keywords' and 'genres').
    score = 0.0

    # WEIGHTS CAN BE TUNED HERE
    WEIGHT_RATING = 1.0
    WEIGHT_POPULARITY = 5.0
    WEIGHT_MOOD_PER_MATCH = 10.0
    WEIGHT_GENRE_MATCH = 8.0

    # Base: rating and popularity
    score += movie.get("vote_average", 0) * WEIGHT_RATING
    score += movie.get("popularity", 0) * WEIGHT_POPULARITY

    # Prepare a combined text/keyword bag to check mood keywords against
    text_fields = []
    if movie.get("title"):
        text_fields.append(movie.get("title", ""))
    if movie.get("overview"):
        text_fields.append(movie.get("overview", ""))
    # keywords come as movie.get('keywords', {}).get('keywords', []) when details fetched
    kw_objs = movie.get("keywords", {}).get("keywords", []) if isinstance(movie.get("keywords", {}), dict) else []
    kw_names = [k.get("name", "") for k in kw_objs]
    text_fields.extend(kw_names)
    combined = " ".join(text_fields).lower()

    # Mood matching: count matches (not just boolean) so stronger signals matter
    mood_matches = sum(1 for kw in mood_keywords if kw in combined)
    score += mood_matches * WEIGHT_MOOD_PER_MATCH

    # Genre matching: check genre ids and genre names if available
    genres = movie.get("genres") or []
    genre_ids = [g.get("id") for g in genres]
    genre_names = [g.get("name", "").lower() for g in genres]
    if genre_id and genre_id in genre_ids:
        score += WEIGHT_GENRE_MATCH

    # Return final score
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

    favorites = [m.strip() for m in favorite_text.split(",") if m.strip()] if favorite_text else []

    candidates = {}

    # Helper to add movies to candidates dict keyed by id
    def add_candidate(movie_obj):
        mid = movie_obj.get("id")
        if not mid:
            return
        if mid not in candidates:
            candidates[mid] = movie_obj

    # 1) If favorites given -> gather similar movies
    if favorites:
        for fav in favorites:
            movie_id = search_movie_id(fav)
            if movie_id:
                sims = get_tmdb_similar(movie_id)
                for m in sims:
                    add_candidate(m)

    # 2) If still empty, fallback to Discover 
    if not candidates:
        if genre_id:
            url = f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
        else:
            url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}"
        results = tmdb_request(url).get("results", [])
        for m in results:
            add_candidate(m)

    # Limit candidates to a reasonable number to avoid too many detail requests
    MAX_CANDIDATES = 150
    candidate_list = list(candidates.values())[:MAX_CANDIDATES]

    # Score candidates using details
    scored = []
    for movie in candidate_list:
        # Get details to access keywords and full genres
        details = get_movie_details(movie.get("id")) or {}
        # merge shallow fields from movie into details so compute_score sees rating/popularity/title/overview
        merged = {**movie, **details}
        score = compute_score(merged, mood_keywords, genre_id)
        scored.append((merged, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Return top 15 results as Streamlit-compatible dicts (title)
    top = [{"title": m.get("title")} for m, s in scored[:15]]
    return top
