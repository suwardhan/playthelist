from dotenv import load_dotenv
import os

load_dotenv()  # load variables from .env

from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import openai

# ---------- CONFIG ----------
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
SPOTIFY_SCOPE = "playlist-modify-public"

OPENAI_API_KEY = "YOUR_OPENAI_KEY"
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
    return re.sub(r"\s*\(.*?\)", "", title).strip()

def detect_platform(url):
    if "music.youtube.com" in url or "youtu.be" in url or "youtube.com" in url:
        return "youtube"
    elif "spotify.com" in url:
        return "spotify"
    else:
        return None

def ai_best_match(query, candidates):
    """Use AI to pick the best match from a list of candidate results."""
    prompt = f"""
    You are helping match songs across platforms.
    Original: "{query}"
    Candidates: {candidates}

    Pick the best candidate that matches title and artist.
    If none fit, return "NONE".
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message["content"].strip()

# ---------- YOUTUBE ----------
def get_youtube_tracks(playlist_id):
    playlist = ytmusic.get_playlist(playlist_id, limit=500)
    tracks = []
    for track in playlist['tracks']:
        title = clean_title(track['title'])
        artist = track['artists'][0]['name'] if track['artists'] else ""
        tracks.append(f"{title} {artist}")
    return tracks

def search_ytmusic(query):
    results = ytmusic.search(query, filter="songs")
    candidates = [f"{r['title']} {r['artists'][0]['name']}" for r in results[:5]]
    best = ai_best_match(query, candidates)
    if best != "NONE":
        for r in results:
            candidate = f"{r['title']} {r['artists'][0]['name']}"
            if candidate == best:
                return r['videoId']
    return None

def create_youtube_playlist(name, description, video_ids):
    return ytmusic.create_playlist(name, description, video_ids)

# ---------- SPOTIFY ----------
def get_spotify_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        title = clean_title(track['name'])
        artist = track['artists'][0]['name'] if track['artists'] else ""
        tracks.append(f"{title} {artist}")
    return tracks

def search_spotify(query):
    results = sp.search(q=query, type="track", limit=5)
    candidates = [f"{r['name']} {r['artists'][0]['name']}" for r in results['tracks']['items']]
    best = ai_best_match(query, candidates)
    if best != "NONE":
        for r in results['tracks']['items']:
            candidate = f"{r['name']} {r['artists'][0]['name']}"
            if candidate == best:
                return r['uri']
    return None

def create_spotify_playlist(user_id, name):
    return sp.user_playlist_create(user=user_id, name=name, public=True)

# ---------- AGENT ----------
def transfer_playlist(url, target="spotify"):
    platform = detect_platform(url)
    if not platform:
        raise ValueError("Unsupported playlist URL")

    print(f"Detected source: {platform}, target: {target}")

    if platform == "youtube":
        playlist_id = url.split("list=")[1].split("&")[0]
        tracks = get_youtube_tracks(playlist_id)
    elif platform == "spotify":
        playlist_id = url.split("playlist/")[1].split("?")[0]
        tracks = get_spotify_tracks(playlist_id)

    if target == "spotify":
        user_id = sp.me()['id']
        new_playlist = create_spotify_playlist(user_id, "Imported Playlist")
        uris, missing = [], []
        for track in tracks:
            uri = search_spotify(track)
            if uri:
                uris.append(uri)
            else:
                missing.append(track)
        if uris:
            sp.playlist_add_items(new_playlist['id'], uris)
        return {"playlist_url": new_playlist['external_urls']['spotify'], "missing": missing}

    elif target == "youtube":
        video_ids, missing = [], []
        for track in tracks:
            vid = search_ytmusic(track)
            if vid:
                video_ids.append(vid)
            else:
                missing.append(track)
        new_playlist_id = create_youtube_playlist("Imported Playlist", "Created by AI Agent", video_ids)
        return {"playlist_url": f"https://music.youtube.com/playlist?list={new_playlist_id}", "missing": missing}


if __name__ == "__main__":
    url = "https://www.youtube.com/playlist?list=PLppQ61iuprWiip1EbM0MwDcjj7nhUnK0B"
    result = transfer_playlist(url, target="spotify")
    print("✅ New Playlist:", result["playlist_url"])
    print("⚠️ Missing tracks:", result["missing"])