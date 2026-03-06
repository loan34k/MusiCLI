import threading
import subprocess
import psutil
import yt_dlp
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

# -------------------- Global variables --------------------
queue = []
current_process = None
p = None
current_track = None
ydl_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "quiet": True,
    "noplaylist": True,
    "js_runtimes": {"node": {}},
    "no_warnings": True,
}

# -------------------- Utilitary functions --------------------
def search_youtube(query):
    return f"ytsearch1:{query}"

def info(url):
    try:
        ydl_opts_local = ydl_opts.copy()
        ydl_opts_local.update({
            "quiet": True,
            "nowarnings": True,
            "logger": None,
        })
        with yt_dlp.YoutubeDL(ydl_opts_local) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                info = info["entries"][0]
            return {"title": info.get("title", "Unknown title"), "url": info["url"]}
    except Exception as e:
        raise 
def is_playing():
    return current_process is not None and current_process.poll() is None

# -------------------- Player thread --------------------
def player_loop():
    global current_process, p, current_track
    while True:
        if not is_playing() and queue:
            next_track = queue.pop(0)
            current_track = next_track
            current_process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", next_track["url"]],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            p = psutil.Process(current_process.pid)

            with patch_stdout():
                print(f"▶ Now playing: {next_track['title']}")
        time.sleep(0.5)

# -------------------- Starting thread --------------------
threading.Thread(target=player_loop, daemon=True).start()

# -------------------- Principal loop --------------------
def main():
    global current_process, p, current_track, queue
    session = PromptSession()

    while True:
        with patch_stdout():
            cmd = session.prompt("> ").lower()

        if cmd == "exit":
            if current_process:
                current_process.terminate()
            break

        elif cmd.startswith("play "):
            url = search_youtube(cmd[5:])
            try:
                audio_info = info(url)
                queue.append(audio_info)
                if is_playing():
                    with patch_stdout():
                        print(f"Added to queue: {audio_info['title']}")
            except Exception as e:
                with patch_stdout():
                    print(f"❌ Could not play '{cmd[5:].strip()}'")
        elif cmd == "pause" and p and is_playing():
            p.suspend()
            with patch_stdout():
                print("⏸ Paused")

        elif cmd == "resume" and p and is_playing():
            p.resume()
            with patch_stdout():
                print("▶ Resumed")

        elif cmd == "skip" and is_playing():
            current_process.terminate()
            current_process = None
            p = None
            with patch_stdout():
                print("⏭ Skipped")

        elif cmd == "stop":
            if is_playing():
                current_process.terminate()
            current_process = None
            p = None
            queue.clear()
            with patch_stdout():
                print("⏹ Stopped and cleared queue")

        elif cmd == "queue":
            with patch_stdout():
                if queue:
                    print("Current queue:")
                    for idx, track in enumerate(queue, start=1):
                        print(f"  {idx}. {track['title']}")
                else:
                    print("Queue is empty.")

        elif cmd == "clear":
            print("\033c", end="")

        elif cmd == "now":
            if is_playing() and current_track is not None:
                with patch_stdout():
                    print(f"▶ Now playing: {current_track['title']}")
            else:
                with patch_stdout():
                    print("No track is currently playing.")

        elif cmd == "restart":
            if is_playing() and current_track is not None:
                current_process.terminate()
                current_process = None
                p = None
                queue.insert(0, current_track)
                with patch_stdout():
                    print(f"⏮ Restarted: {current_track['title']}")
            else:
                with patch_stdout():
                    print("No track is currently playing to restart.")

        elif cmd == "clearqueue":
            queue.clear()
            with patch_stdout():
                print("Queue cleared.")

        elif cmd == "help":
            with patch_stdout():
                print("Available commands:")
                print("  play <query or url> - Search and play a track from YouTube")
                print("  pause - Pause the current track")
                print("  resume - Resume the paused track")
                print("  skip - Skip the current track")
                print("  stop - Stop playback and clear the queue")
                print("  exit - Exit the application")
                print("  queue - Show the current queue")
                print("  clear - Clear the terminal")
                print("  now - Show the currently playing track")
                print("  restart - Restart the currently playing track")
                print("  clearqueue - Clear the entire queue")
        else:
            with patch_stdout():
                print("Unknown command.")

if __name__ == "__main__":
    main()
