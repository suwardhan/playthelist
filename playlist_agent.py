# playlist_agent.py

import os
import re
import logging
from urllib.parse import urlparse, parse_qs
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
import openai
from dotenv import load_dotenv

# ---------- LOAD ENV ----------
load_dotenv()

# Import configuration
from config import config

# Load environment variables with multiple fallbacks
try:
    import streamlit as st
    # Try Streamlit secrets first (for Streamlit Cloud)
    SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID") or config.SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET = st.secrets.get("SPOTIFY_CLIENT_SECRET") or config.SPOTIFY_CLIENT_SECRET
    SPOTIFY_REDIRECT_URI = st.secrets.get("SPOTIFY_REDIRECT_URI") or config.SPOTIFY_REDIRECT_URI
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or config.OPENAI_API_KEY
except:
    # Fallback to config (for Railway, Vercel, etc.)
    SPOTIFY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET
    SPOTIFY_REDIRECT_URI = config.SPOTIFY_REDIRECT_URI
    OPENAI_API_KEY = config.OPENAI_API_KEY

SPOTIFY_SCOPE = config.SPOTIFY_SCOPE

# Validate required environment variables
required_vars = {
    "SPOTIFY_CLIENT_ID": SPOTIFY_CLIENT_ID,
    "SPOTIFY_CLIENT_SECRET": SPOTIFY_CLIENT_SECRET,
    "SPOTIFY_REDIRECT_URI": SPOTIFY_REDIRECT_URI,
    "OPENAI_API_KEY": OPENAI_API_KEY
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

openai.api_key = OPENAI_API_KEY

# ---------- INIT ----------
ytmusic = YTMusic()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE
))

# ---------- HELPERS ----------
def clean_title(title):
    """Remove parentheses/brackets and unnecessary words but keep essential punctuation."""
    title = re.sub(r"[\(\[].*?[\)\]]", "", title)
    title = re.sub(r"(official video|music video|lyrics|audio)", "", title, flags=re.I)
    title = re.sub(r"\s+", " ", title)
    return title.strip()

def detect_platform(url):
    if "music.youtube.com" in url or "youtu.be" in url or "youtube.com" in url:
        return "youtube"
    elif "spotify.com" in url:
        return "spotify"
    else:
        return None

def ai_best_match(query, candidates):
    """Use AI to pick the best candidate."""
    try:
        prompt = f"""
        You are helping match songs across platforms.
        Original: "{query}"
        Candidates: {candidates}
        Pick the best candidate that matches title and artist. If none fit, return "NONE".
        """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"AI matching failed: {str(e)}")
        return "NONE"

def fallback_match(query, candidates):
    match = get_close_matches(query, candidates, n=1, cutoff=0.7)
    return match[0] if match else None

# ---------- YOUTUBE ----------
def get_youtube_tracks(playlist_id):
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=500)
        tracks = []
        for track in playlist['tracks']:
            title = clean_title(track['title'])
            artist = track['artists'][0]['name'] if track['artists'] else ""
            tracks.append((title, artist))
        playlist_title = playlist.get('title', 'Imported Playlist')
        return tracks, playlist_title
    except Exception as e:
        logging.error(f"Failed to get YouTube tracks: {str(e)}")
        raise ValueError(f"Could not access YouTube playlist: {str(e)}")

def search_ytmusic(title, artist):
    query = f"{title} {artist}"
    results = ytmusic.search(query, filter="songs")
    candidates = [f"{r['title']} {r['artists'][0]['name']}" for r in results[:5]]
    best = ai_best_match(query, candidates)
    if best == "NONE":
        best = fallback_match(query, candidates)
    if best:
        for r in results:
            candidate = f"{r['title']} {r['artists'][0]['name']}"
            if candidate == best:
                return r['videoId']
    return None

def create_youtube_playlist(name, description, video_ids):
    raise NotImplementedError("YTMusic playlist creation requires YouTube Data API.")

# ---------- SPOTIFY ----------
def get_spotify_tracks(playlist_id):
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = []
        for item in results['items']:
            track = item['track']
            title = clean_title(track['name'])
            artist = track['artists'][0]['name'] if track['artists'] else ""
            tracks.append((title, artist))
        playlist_title = sp.playlist(playlist_id)['name']
        return tracks, playlist_title
    except Exception as e:
        logging.error(f"Failed to get Spotify tracks: {str(e)}")
        raise ValueError(f"Could not access Spotify playlist: {str(e)}")

def search_spotify(title, artist):
    """Robust Spotify search with fallbacks."""
    try:
        query = f"track:{title} artist:{artist}"
        results = sp.search(q=query, type="track", limit=5)
        if results['tracks']['items']:
            return results['tracks']['items'][0]['uri']

        results = sp.search(q=f"track:{title}", type="track", limit=5)
        if results['tracks']['items']:
            return results['tracks']['items'][0]['uri']

        candidates = [f"{r['name']} {r['artists'][0]['name']}" for r in results['tracks']['items']]
        best = ai_best_match(f"{title} {artist}", candidates)
        if best == "NONE":
            best = fallback_match(f"{title} {artist}", candidates)
        if best:
            for r in results['tracks']['items']:
                candidate = f"{r['name']} {r['artists'][0]['name']}"
                if candidate == best:
                    return r['uri']

        logging.warning(f"Could not find: {title} - {artist}")
        return None
    except Exception as e:
        logging.error(f"Spotify search failed for {title} - {artist}: {str(e)}")
        return None

def create_spotify_playlist(user_id, name):
    try:
        return sp.user_playlist_create(user=user_id, name=name, public=True)
    except Exception as e:
        logging.error(f"Failed to create Spotify playlist: {str(e)}")
        raise ValueError(f"Could not create Spotify playlist: {str(e)}")

# ---------- URL PARSING ----------
def extract_youtube_playlist_id(url):
    query = parse_qs(urlparse(url).query)
    return query.get("list", [None])[0]

def extract_spotify_playlist_id(url):
    path = urlparse(url).path
    return path.split("playlist/")[1] if "playlist/" in path else None

# ---------- AGENT ----------
def transfer_playlist(url, target="spotify"):
    platform = detect_platform(url)
    if not platform:
        raise ValueError("Unsupported playlist URL")
    print(f"Detected source: {platform}, target: {target}")

    if platform == "youtube":
        playlist_id = extract_youtube_playlist_id(url)
        tracks, playlist_title = get_youtube_tracks(playlist_id)
    elif platform == "spotify":
        playlist_id = extract_spotify_playlist_id(url)
        tracks, playlist_title = get_spotify_tracks(playlist_id)

    if target == "spotify":
        user_id = sp.me()['id']
        new_playlist = create_spotify_playlist(user_id, playlist_title)
        uris, missing = [], []
        for title, artist in tracks:
            uri = search_spotify(title, artist)
            if uri:
                uris.append(uri)
            else:
                missing.append(f"{title} - {artist}")
        if uris:
            sp.playlist_add_items(new_playlist['id'], uris)
        return {"playlist_url": new_playlist['external_urls']['spotify'], "missing": missing}

    elif target == "youtube":
        video_ids, missing = [], []
        for title, artist in tracks:
            vid = search_ytmusic(title, artist)
            if vid:
                video_ids.append(vid)
            else:
                missing.append(f"{title} - {artist}")
        new_playlist_id = create_youtube_playlist(playlist_title, "Created by AI Agent", video_ids)
        return {"playlist_url": f"https://music.youtube.com/playlist?list={new_playlist_id}", "missing": missing}

# ---------- MAIN ----------
if __name__ == "__main__":
    url = "https://www.youtube.com/playlist?list=PLppQ61iuprWia7W0IQQeI5rhYYG8gW67q"
    result = transfer_playlist(url, target="spotify")
    print("✅ New Playlist:", result["playlist_url"])
    print("⚠️ Missing tracks:", result["missing"])
