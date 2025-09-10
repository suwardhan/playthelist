import streamlit as st
import os
from playlist_agent import transfer_playlist, detect_platform
import time

# Page configuration
st.set_page_config(
    page_title="PlayTheList - Cross-Platform Playlist Transfer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1DB954, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 3rem;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #1DB954, #FF6B6B);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎵 PlayTheList</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transfer your playlists between YouTube Music and Spotify</p>', unsafe_allow_html=True)

# Sidebar for information
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Paste a playlist URL** from YouTube Music or Spotify
    2. **Choose your target platform** (Spotify or YouTube Music)
    3. **Click Transfer** and wait for the magic to happen
    4. **Get your new playlist** with a list of any missing tracks
    
    **Supported platforms:**
    - 🟢 YouTube Music → Spotify
    - 🟢 Spotify → YouTube Music (coming soon)
    """)
    
    st.header("🔧 Requirements")
    st.markdown("""
    Make sure you have set up your environment variables:
    - `SPOTIFY_CLIENT_ID`
    - `SPOTIFY_CLIENT_SECRET` 
    - `SPOTIFY_REDIRECT_URI`
    - `OPENAI_API_KEY`
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Transfer Your Playlist")
    
    # Input form
    with st.form("playlist_transfer_form"):
        playlist_url = st.text_input(
            "Playlist URL",
            placeholder="https://www.youtube.com/playlist?list=... or https://open.spotify.com/playlist/...",
            help="Paste the full URL of the playlist you want to transfer"
        )
        
        target_platform = st.selectbox(
            "Transfer to",
            ["spotify", "youtube"],
            format_func=lambda x: "🎵 Spotify" if x == "spotify" else "📺 YouTube Music"
        )
        
        submitted = st.form_submit_button("🔄 Transfer Playlist", use_container_width=True)
        
        if submitted:
            if not playlist_url:
                st.error("Please enter a playlist URL")
            else:
                # Detect platform
                detected_platform = detect_platform(playlist_url)
                if not detected_platform:
                    st.error("❌ Unsupported playlist URL. Please use a YouTube Music or Spotify playlist URL.")
                else:
                    st.info(f"🔍 Detected source platform: **{detected_platform.title()}**")
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Start transfer
                        status_text.text("🔄 Starting playlist transfer...")
                        progress_bar.progress(20)
                        
                        # Simulate progress updates
                        status_text.text("📥 Extracting tracks from source playlist...")
                        progress_bar.progress(40)
                        time.sleep(1)
                        
                        status_text.text("🔍 Searching for matching tracks...")
                        progress_bar.progress(60)
                        time.sleep(1)
                        
                        status_text.text("🎯 Using AI to find best matches...")
                        progress_bar.progress(80)
                        time.sleep(1)
                        
                        # Perform actual transfer
                        result = transfer_playlist(playlist_url, target=target_platform)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Transfer completed!")
                        
                        # Display results
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.success("🎉 Playlist transferred successfully!")
                        st.markdown(f"**New Playlist:** [{result['playlist_url']}]({result['playlist_url']})")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Show missing tracks if any
                        if result.get('missing'):
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.warning(f"⚠️ {len(result['missing'])} tracks could not be found:")
                            for track in result['missing']:
                                st.text(f"• {track}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.success("🎯 All tracks were successfully transferred!")
                            
                    except Exception as e:
                        progress_bar.progress(0)
                        status_text.text("❌ Transfer failed")
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error(f"❌ Error: {str(e)}")
                        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.header("📊 Transfer Stats")
    
    # Placeholder for stats (could be enhanced with actual data)
    st.metric("Total Transfers", "0", "0")
    st.metric("Success Rate", "0%", "0%")
    st.metric("Avg. Tracks Found", "0", "0")
    
    st.header("🎯 Tips")
    st.markdown("""
    **For better results:**
    - Use playlists with popular songs
    - Check that your API keys are configured
    - Be patient - transfers can take a few minutes
    
    **Troubleshooting:**
    - Make sure playlist URLs are public
    - Verify your Spotify/YouTube Music access
    - Check the console for detailed error messages
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Made with ❤️ using Streamlit | "
    "<a href='https://github.com/yourusername/playthelist' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
