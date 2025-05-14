import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pypresence import Presence
import time

SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback" # spotify settings should match
SPOTIFY_SCOPE = "user-read-playback-state"

DISCORD_CLIENT_ID = "YOUR_DISCORD_CLIENT_ID"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE
))

rpc = Presence(DISCORD_CLIENT_ID)
rpc.connect()

def get_current_track():
    try:
        current_track = sp.current_playback()
        if not current_track or not current_track["is_playing"]:
            return None
        track = current_track["item"]
        track_info = {
            "name": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
            "album": track["album"]["name"] if track["album"]["name"] else "no album",
            "image_url": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "duration": track["duration_ms"] / 1000,
            "progress": current_track["progress_ms"] / 1000,
            "is_playing": current_track["is_playing"]
        }
        # print(f"Fetched track: {track_info['name']}, Album art URL: {track_info['image_url']}")  # Debug log
        return track_info
    except Exception as e:
        print(f"Error fetching track: {e}")
        return None

def update_discord_presence(track_info):
    if not track_info:
        rpc.clear()
        # print("No track playing, cleared RPC")
        return

    image_key = track_info["image_url"] if track_info["image_url"] else "none_logo"

    try:
        end_time = int(time.time() + (track_info["duration"] - track_info["progress"]))
        rpc.update(
            details=f"{track_info['name']}",
            state=f"by {track_info['artists']}",
            large_image=image_key,
            large_text=track_info['album'],
            # small_image="playing_logo" if track_info["is_playing"] else "paused_logo",
            # small_text="Playing" if track_info["is_playing"] else "Paused",
            start=int(time.time() - track_info["progress"]),
            end=end_time
        )
        # print(f"Updated RPC: {track_info['name']} by {track_info['artists']}, Image key: {image_key}")
    except Exception as e:
        print(f"Error updating RPC: {e}")

def main():
    print("Starting Spotify Discord RPC...")
    last_track = None

    while True:
        track_info = get_current_track()
        
        if track_info != last_track:
            update_discord_presence(track_info)
            last_track = track_info

        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping Spotify Discord RPC...")
        rpc.clear()
        rpc.close()