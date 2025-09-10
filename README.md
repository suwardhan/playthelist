# 🎵 PlayTheList

**Cross-Platform Playlist Transfer Tool** - Transfer your playlists between YouTube Music and Spotify with AI-powered song matching.

## ✨ Features

- 🔄 **Cross-platform transfers**: YouTube Music ↔ Spotify
- 🤖 **AI-powered matching**: Uses OpenAI GPT-4o-mini for intelligent song matching
- 🎯 **Smart fallbacks**: Multiple search strategies to find the best matches
- 🌐 **Web interface**: Clean, modern UI built with Streamlit
- 📊 **Progress tracking**: Real-time transfer progress and results
- ⚠️ **Missing track reporting**: See which songs couldn't be found

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables
Create a `.env` file with your API credentials:
```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the Web App
```bash
python run_app.py
```
Or directly with Streamlit:
```bash
streamlit run app.py
```

### 4. Open Your Browser
Navigate to `http://localhost:8501` and start transferring playlists!

## 🎯 How It Works

1. **Paste a playlist URL** from YouTube Music or Spotify
2. **Choose your target platform** (Spotify or YouTube Music)
3. **Click Transfer** and watch the AI work its magic
4. **Get your new playlist** with a detailed report of any missing tracks

## 🔧 API Setup

### Spotify API
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8080/callback` to redirect URIs
4. Copy your Client ID and Client Secret

### OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

## 📁 Project Structure

```
playthelist/
├── app.py              # Streamlit web interface
├── playlist_agent.py   # Core playlist transfer logic
├── run_app.py         # App launcher script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🛠️ Development

### Command Line Usage
You can also use the tool directly from the command line:
```python
from playlist_agent import transfer_playlist

result = transfer_playlist(
    "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
    target="spotify"
)
print(result)
```

## ⚠️ Limitations

- YouTube Music playlist creation requires YouTube Data API (not implemented)
- Only supports one-way transfers (no bidirectional sync)
- Requires public playlists for access
- Some tracks may not be found due to platform differences

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
