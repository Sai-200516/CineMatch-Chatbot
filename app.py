from flask import Flask, render_template, request, jsonify, session
import requests
import random
import json
import os
import re

app = Flask(__name__)
app.secret_key = "syncgaze_secret_key"  # For session management
GEMINI_API_KEY = "AIzaSyDU4iF3npHYfXnYzZjbZMAgsrGcq-Q8_HI"  # Replace with your Gemini API key
YOUTUBE_API_KEY = "AIzaSyAqG7dcjl3noYAgMR4n-GaVgWxXTMRIJcc"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

GENRES = ["action", "comedy", "drama", "sci-fi", "horror", "romance", "thriller", "animation", "fantasy"]
LANGUAGES = ["english", "hindi", "spanish", "french", "tamil", "telugu", "korean", "japanese"]
MOODS = {
    "adventurous": ["action", "sci-fi", "fantasy"],
    "relaxed": ["comedy", "romance", "animation"],
    "intense": ["thriller", "horror", "drama"]
}
TRAILER_STYLES = ["short", "epic", "teaser", "official"]

@app.route("/")
def home():
    session.clear()
    session["state"] = "name"
    session["user_name"] = ""
    session["favorite_genres"] = []
    session["preferred_languages"] = []
    session["favorite_heroes"] = []
    session["selected_genres"] = []
    session["selected_language"] = ""
    session["selected_hero"] = ""
    session["trailer_style"] = ""
    session["history"] = []
    session["temp_input"] = {}
    return render_template("index.html", genres=GENRES, languages=LANGUAGES)

@app.route("/get_recommendation", methods=["POST"])
def get_recommendation():
    user_input = request.form["msg"].lower().strip()
    current_state = session.get("state", "name")
    user_name = session.get("user_name", "")
    favorite_genres = session.get("favorite_genres", [])
    preferred_languages = session.get("preferred_languages", [])
    favorite_heroes = session.get("favorite_heroes", [])
    selected_genres = session.get("selected_genres", [])
    selected_language = session.get("selected_language", "")
    selected_hero = session.get("selected_hero", "")
    trailer_style = session.get("trailer_style", "")
    history = session.get("history", [])
    temp_input = session.get("temp_input", {})

    # Handle reset
    if user_input == "start over":
        old_name = user_name
        session.clear()
        session["state"] = "name"
        session["user_name"] = old_name
        session["favorite_genres"] = []
        session["preferred_languages"] = []
        session["favorite_heroes"] = []
        session["selected_genres"] = []
        session["selected_language"] = ""
        session["selected_hero"] = ""
        session["trailer_style"] = ""
        session["history"] = []
        session["temp_input"] = {}
        return jsonify({
            "reply": f"🎬 Fresh start, {old_name or 'friend'}! What's your name?",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": False
        })

    # Handle feedback (star ratings)
    if user_input.startswith("rate:"):
        try:
            rating = int(user_input.split(":")[1])
            history.append({"genres": selected_genres, "language": selected_language, "hero": selected_hero, "rating": rating})
            session["history"] = history
            reply = {
                5: f"🌟 5 stars, {user_name or 'friend'}? You're a movie buff!",
                4: f"🌟 4 stars, {user_name or 'friend'}! Great choice!",
                3: f"🌟 3 stars, {user_name or 'friend'}? Let's find something better!",
                2: f"🌟 2 stars, {user_name or 'friend'}? We'll do better!",
                1: f"🌟 1 star, {user_name or 'friend'}? Time for a new pick!"
            }.get(rating, f"🌟 Thanks for the feedback, {user_name or 'friend'}!")
            suggested_genre = recommend_genre(history, favorite_genres)
            session["state"] = "mood"
            session["selected_genres"] = []
            session["selected_language"] = ""
            session["selected_hero"] = ""
            session["trailer_style"] = ""
            return jsonify({
                "reply": f"{reply} How about a {suggested_genre.title()} movie next, {user_name or 'friend'}? Or tell me your mood: adventurous, relaxed, or intense?",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": True
            })
        except:
            return jsonify({
                "reply": f"🤔 Invalid rating, {user_name or 'friend'}. Try 1–5 stars or a new search!",
                "recommendation": None,
                "feedback": False
            })

    # Parse input for genres, languages, heroes
    search_genres = [g for g in GENRES if g in user_input]
    search_languages = [l for l in LANGUAGES if l in user_input]
    is_hero_input = user_input not in GENRES and user_input not in LANGUAGES and user_input not in ["start over", "search:"] and not user_input.startswith("rate:") and current_state in ["heroes", "mood", "style", "recommendation"]

    # Handle freeform search after name collection
    if (search_genres or search_languages or is_hero_input or user_input.startswith("search:")) and current_state not in ["name", "genres", "languages", "heroes"]:
        if user_input.startswith("search:"):
            user_input = user_input.replace("search:", "").strip()
        selected_genres = search_genres or favorite_genres[:1] or [random.choice(GENRES)]
        selected_language = search_languages[0] if search_languages else preferred_languages[0] if preferred_languages else ""
        selected_hero = user_input if is_hero_input else favorite_heroes[0] if favorite_heroes else ""
        session["selected_genres"] = selected_genres
        session["selected_language"] = selected_language
        session["selected_hero"] = selected_hero
        session["state"] = "recommendation"
        session["trailer_style"] = random.choice(TRAILER_STYLES)
        return fetch_recommendation(selected_genres, selected_language, selected_hero, session["trailer_style"], user_name or "friend", user_input)

    # State machine
    if current_state == "name":
        if search_genres or search_languages:
            temp_input["genres"] = search_genres
            temp_input["languages"] = search_languages
            session["temp_input"] = temp_input
            return jsonify({
                "reply": f"🎬 Looks like you typed genres or languages, like {', '.join(search_genres + search_languages).title()}! What's your name first?",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": False
            })
        if user_input and not user_input.isspace():
            session["user_name"] = user_input.capitalize()
            session["state"] = "genres"
            if temp_input.get("genres"):
                session["favorite_genres"] = temp_input["genres"]
                session["state"] = "languages"
                reply = f"🎥 Nice to meet you, {session['user_name']}! I’ve got {', '.join(temp_input['genres']).title()} as your genres. What languages do you enjoy for movies?"
                if temp_input.get("languages"):
                    session["preferred_languages"] = temp_input["languages"]
                    session["state"] = "heroes"
                    reply = f"🎥 Nice to meet you, {session['user_name']}! I’ve got {', '.join(temp_input['genres']).title()} and {', '.join(temp_input['languages']).title()} as your preferences. Who are your favorite actors?"
                session["temp_input"] = {}
                return jsonify({
                    "reply": reply,
                    "recommendation": None,
                    "feedback": False,
                    "show_mood_buttons": False
                })
            return jsonify({
                "reply": f"🎬 Nice to meet you, {session['user_name']}! What genres do you love? Try Action, Comedy, or Sci-Fi!",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": False
            })
        return jsonify({
            "reply": "🎬 What's your name? Let’s make this personal!",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": False
        })

    if current_state == "genres":
        if not search_genres:
            suggested = random.sample(GENRES, 2)
            return jsonify({
                "reply": f"🎬 No genres detected, {user_name}. Try {', '.join(suggested).title()} or your favorites!",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": False
            })
        session["favorite_genres"] = search_genres[:3]
        session["state"] = "languages"
        return jsonify({
            "reply": f"🎥 Great picks, {user_name}! What languages do you enjoy for movies? Like English, Hindi, or Telugu?",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": False
        })

    if current_state == "languages":
        if not search_languages:
            suggested = random.sample(LANGUAGES, 2)
            return jsonify({
                "reply": f"🎬 No languages detected, {user_name}. Try {', '.join(suggested).title()} or your favorites!",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": False
            })
        session["preferred_languages"] = search_languages[:2]
        session["state"] = "heroes"
        return jsonify({
            "reply": f"🎥 Awesome, {user_name}! Who are your favorite actors? Like Chris Hemsworth, Deepika Padukone, or Ryan Reynolds?",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": False
        })

    if current_state == "heroes":
        if user_input and not user_input in GENRES and not user_input in LANGUAGES:
            session["favorite_heroes"] = [user_input.lower()]
            session["state"] = "mood"
            return jsonify({
                "reply": f"🎥 Cool, {user_name}! What's your mood today: adventurous, relaxed, or intense?",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": True
            })
        suggested = ["Chris Hemsworth", "Deepika Padukone", "Ryan Reynolds"]
        return jsonify({
            "reply": f"🎬 Who are your favorite actors, {user_name}? Try {', '.join(suggested)} or someone you love!",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": False
        })

    if current_state == "mood":
        mood = next((m for m in MOODS if m in user_input), None)
        if mood:
            session["state"] = "style"
            session["selected_genres"] = favorite_genres[:1] or MOODS[mood][:1]
            session["selected_language"] = preferred_languages[0] if preferred_languages else "english"
            session["selected_hero"] = favorite_heroes[0] if favorite_heroes else ""
            return jsonify({
                "reply": f"🎥 Feeling {mood}, {user_name}! Want a short, epic, teaser, or official trailer vibe?",
                "recommendation": None,
                "feedback": False,
                "show_mood_buttons": False
            })
        return jsonify({
            "reply": f"🤔 Not sure what you mean, {user_name}. Try a mood like adventurous, relaxed, or intense, or a search like 'Telugu thriller Prabhas'!",
            "recommendation": None,
            "feedback": False,
            "show_mood_buttons": True
        })

    if current_state == "style":
        trailer_style = next((s for s in TRAILER_STYLES if s in user_input), random.choice(TRAILER_STYLES))
        session["trailer_style"] = trailer_style
        session["state"] = "recommendation"
        return fetch_recommendation(selected_genres, selected_language, selected_hero, trailer_style, user_name, "")

    if current_state == "recommendation":
        return fetch_recommendation(selected_genres, selected_language, selected_hero, trailer_style, user_name, "")

    return jsonify({
        "reply": f"🤔 Not sure what you mean, {user_name or 'friend'}. Try a genre, language, actor, or search like 'Telugu thriller Prabhas'!",
        "recommendation": None,
        "feedback": False,
        "show_mood_buttons": False
    })

def fetch_recommendation(genres, language, hero, style, user_name, search_query):
    prompt = f"""
Recommend a movie trailer based on the following preferences:
- Genres: {', '.join(genres)}
- Language: {language or 'any'}
- Actor: {hero or 'any'}
- Trailer style: {style}
- Search query (if any): {search_query}

Respond ONLY in the following JSON format:
{{
    "title": "Movie Title",
    "genres": ["genre1", "genre2"],
    "language": "Language",
    "actors": ["Actor1", "Actor2"],
    "trailer_url": "https://www.youtube.com/embed/VIDEO_ID",
    "description": "Brief movie description"
}}

⚠️ Important:
- Ensure the trailer is a real, **available**, **public** YouTube video.
- The `trailer_url` must be a **valid YouTube embed link** (e.g., https://www.youtube.com/embed/VIDEO_ID).
- Do NOT use watch?v= links or short URLs. Do not make up fake trailers.
"""

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
        recommendation = json.loads(content.strip("```json\n").strip("```"))

        url = recommendation.get("trailer_url", "")
        video_id = url.split("/")[-1] if "/embed/" in url else ""

        if is_valid_youtube_embed_url(url) and is_youtube_video_available(video_id):
            return jsonify({
                "reply": f"🎥 Here’s your {language.title() if language else ''} {', '.join(genres).title()} trailer{', featuring ' + hero.title() if hero else ''}, {user_name}! Rate it 1–5 stars!",
                "recommendation": recommendation,
                "feedback": True,
                "show_mood_buttons": False
            })

    except Exception as e:
        print(f"Error fetching recommendation: {e}")
        print("Gemini response:", response.text)

    # 🛠️ Fallback path (used whether error or just bad link)
    fallback = {
        "title": "Fallback Movie Trailer",
        "genres": genres,
        "language": language or "English",
        "actors": [hero] if hero else ["Unknown"],
        "trailer_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "description": "This is a fallback trailer in case we couldn't fetch a valid one."
    }
    print("Fallback triggered")
    session["state"] = "genres"
    return jsonify({
        "reply": f"😔 Couldn't fetch a valid trailer, {user_name}. Here's a fallback instead. Try another genre or say 'start over'!",
        "recommendation": fallback,
        "feedback": False,
        "show_mood_buttons": False
    })


    # 🛠️ Fallback path (used whether error or just bad link)
    fallback = {
        "title": "Fallback Movie Trailer",
        "genres": genres,
        "language": language or "English",
        "actors": [hero] if hero else ["Unknown"],
        "trailer_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "description": "This is a fallback trailer in case we couldn't fetch a valid one."
    }
    print("Fallback triggered")
    session["state"] = "genres"
    return jsonify({
        "reply": f"😔 Couldn't fetch a valid trailer, {user_name}. Here's a fallback instead. Try another genre or say 'start over'!",
        "recommendation": fallback,
        "feedback": False,
        "show_mood_buttons": False
    })

def recommend_genre(history, favorite_genres):
    high_rated = [h["genres"][0] for h in history if h["rating"] >= 4]
    available = [g for g in GENRES if g not in favorite_genres]
    return random.choice(high_rated + available) if high_rated else random.choice(available)
def is_valid_youtube_embed_url(url):
    return bool(re.match(r"^https:\/\/www\.youtube\.com\/embed\/[a-zA-Z0-9_-]{11}$", url))



def is_youtube_video_available(video_id):
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=status&id={video_id}&key={YOUTUBE_API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if not data["items"]:
            return False
        status = data["items"][0]["status"]
        return status.get("privacyStatus") == "public" and status.get("embeddable") is True
    except Exception as e:
        print(f"Error checking YouTube video: {e}")
        return False


if __name__ == "__main__":
    app.run(debug=True)