# mood_detection.py
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure VADER lexicon is available
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

MOOD_KEYWORDS = {
    "happy": ["happy", "joyful", "excited", "energetic", "upbeat", "ecstatic"],
    "sad": ["sad", "down", "depressed", "heartbroken", "upset"],
    "angry": ["angry", "furious", "mad", "annoyed", "irritated"],
    "relaxed": ["calm", "chill", "relaxed", "peaceful", "serene"],
    "bored": ["bored", "tired", "uninterested", "dull"],
    "romantic": ["romantic", "love", "affectionate", "loving"],
    "scared": ["scared", "afraid", "anxious", "nervous"],
    "adventurous": ["adventurous", "excited", "bold", "daring"],
}

def classify_keywords(text):
    """Return a mood category based on keyword matching."""
    text = text.lower()
    for mood, words in MOOD_KEYWORDS.items():
        if any(w in text for w in words):
            return mood
        return None # no keyword match found
    
def analyze_mood(user_input: str) -> dict:
    """
    Expanded mood detection using:
    - VADAR sentiment
    - Mood keywords
    Returns
        { mood: str, score: float, raw: dict }
    """
    if not user_input or user_input.strip() == "":
        return {"score": 0.0, "mood": "neutral"}
    
    text = user_input.lower()

    # 1. Try keyword classification first (stronger signal)
    keyword_mood = classify_keywords(text)

    # 2. VADER sentiment
    sentiment = sia.polarity_scores(text)
    compound = sentiment["compound"]

    # Map VADER polarity to general emotion if keywords fail
    if keyword_mood:
        mood = keyword_mood
    else:
        if compound >= 0.4:
            mood = "happy"
        elif compound <= -0.4:
            mood = "sad"
        else:
            mood = "neutral"
    
    return {
        "score": compound,
        "mood": mood,
        "raw": sentiment,
        "keyword_mood": keyword_mood is not None
    }
