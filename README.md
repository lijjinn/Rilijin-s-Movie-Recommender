# Rilijin's Movie Recommender

 A Streamlit-based movie recommendation engine that uses mood detection, genre preferences, and favorite movies to suggest films tailored to your interests.

 ## Features

 **Personalized Recommendations** based on:
 - **Mood**: Analyzes your mood input to prioritize movies matching emotional themes
 - **Favorite Movies**: Finds similar films based on movies you've enjoyed
 - **Genre Selection**: Filters recommendations by your preferred genre
 - **Smart Scoring**: Multi-factor algorithm combining ratings, popularity, mood keywords, and genre matches

 ## How It Works

 ### Recommendation Engine (`recommender.py`)

 The improved recommendation system uses a **hybrid scoring algorithm** that considers:

 1. **Mood Keyword Matching** (strongest influence)
    - Extracts keywords from TMDB movie database
    - Matches multiple mood-related keywords in movie title, overview, and keywords
    - Higher score for more matches (not just binary yes/no)

 2. **Genre Matching**
    - Strong bonus for genre match when specified
    - Falls back to genre-filtered TMDB Discover when no favorites provided

 3. **Quality Metrics**
    - Vote average (TMDB rating out of 10)
    - Popularity score

 4. **Fallback Strategy**
    - **With Favorites**: Gathers similar movies from TMDB's `/similar` endpoint
    - **Without Favorites**: Uses TMDB Discover filtered by selected genre (much better than raw popular movies)

 ### Mood Detection (`mood_detection.py`)

 Uses VADER sentiment analysis + keyword matching to classify mood:
 - Supports: happy, sad, angry, relaxed, bored, romantic, scared, adventurous, neutral

 ## Setup

 ### Prerequisites
 - Python 3.10+
 - TMDB API Key (get one free at https://www.themoviedb.org/settings/api)

 ### Installation

 1. Clone the repository:
    ```bash
    git clone https://github.com/lijjinn/Rilijin-s-Movie-Recommender.git
    cd Rilijin-s-Movie-Recommender
    ```

 2. Create a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # or
    source .venv/bin/activate  # macOS/Linux
    ```

 3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

 4. Create a `.env` file with your TMDB API key:
    ```
    TMDB_API_KEY=your_api_key_here
    ```

 ### Running the App

 ```bash
 streamlit run main_app.py
 ```

 Then open your browser to `http://localhost:8501`

 ## Tuning the Recommendation Algorithm

 The scoring weights in `recommender.py` can be adjusted to prioritize different factors:

 ```python
 # In compute_score() function:
 WEIGHT_RATING = 2.0               # Influence of movie rating (0-10)
 WEIGHT_POPULARITY = 0.03          # Influence of popularity score
 WEIGHT_MOOD_PER_MATCH = 6.0       # Boost per mood keyword match
 WEIGHT_GENRE_MATCH = 12.0         # Boost for genre match
 MAX_CANDIDATES = 60               # Max movies to fetch details for
 ```

 ### Tuning Guide

 | Goal | Adjustment |
 |------|------------|
 | Prioritize mood over genre | Increase `WEIGHT_MOOD_PER_MATCH` |
 | Make genre selection more important | Increase `WEIGHT_GENRE_MATCH` |
 | Favor highly-rated films | Increase `WEIGHT_RATING` |
 | Reduce popularity bias | Decrease `WEIGHT_POPULARITY` |
 | Consider more movies before filtering | Increase `MAX_CANDIDATES` (slower) |


 ## Dependencies

 - `streamlit` - Web UI framework
 - `requests` - HTTP requests to TMDB API
 - `python-dotenv` - Environment variable management
 - `nltk` - VADER sentiment analysis for mood detection

 See `requirements.txt` for full dependency list.


 ## License

 MIT

 ## Credits

 Created by Rilijin, Alejandro, and Anthony for CPSC 481 AI Course