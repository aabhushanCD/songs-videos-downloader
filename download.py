import yt_dlp
import os
import imageio_ffmpeg
from concurrent.futures import ThreadPoolExecutor, as_completed

DOWNLOAD_DIR = "downloads"
MAX_WORKERS = 4


# ─────────────────────────────────────────────
#  Build ydl options based on user choice
# ─────────────────────────────────────────────
def get_ydl_opts(ffmpeg_path: str, mode: str, quality: str) -> dict:
    """
    mode    : "audio" | "video"
    quality : depends on mode
              audio  → "320" | "192" | "128"  (kbps)
              video  → "2160" | "1440" | "1080" | "720" | "480" | "360"
    """
    base = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(playlist_index)s - %(title)s.%(ext)s",
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": True,
        "noprogress": True,
        "concurrent_fragment_downloads": 4,
        "buffersize": 1024 * 16,
        "http_chunk_size": 1024 * 1024 * 10,
        "download_archive": f"{DOWNLOAD_DIR}/.archive.txt",
    }

    if mode == "audio":
        base["format"] = "bestaudio/best"
        base["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": quality,   # e.g. "320"
        }]

    else:  # video
        if quality == "best":
            # Best available video + best audio merged
            fmt = "bestvideo+bestaudio/best"
        else:
            # Try exact height, fall back to best available at or below that height
            fmt = (
                f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]"
                f"/bestvideo[height<={quality}]+bestaudio"
                f"/best[height<={quality}]"
                f"/bestvideo+bestaudio/best"
            )
        base["format"] = fmt
        base["merge_output_format"] = "mp4"
        base["postprocessors"] = [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }]

    return base


# ─────────────────────────────────────────────
#  Playlist helpers
# ─────────────────────────────────────────────
def extract_playlist_url(url: str) -> str:
    """Strip everything except the list= param and return a clean playlist URL."""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    if "list" in params:
        pid = params["list"][0]
        clean = f"https://www.youtube.com/playlist?list={pid}"
        print(f"[INFO] Clean playlist URL: {clean}")
        return clean
    return url


def fetch_playlist_entries(playlist_url: str) -> list:
    playlist_url = extract_playlist_url(playlist_url)
    print("\nFetching playlist info...")

    opts = {
        "extract_flat": "in_playlist",
        "quiet": False,
        "ignoreerrors": True,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if info is None:
        print("\n[ERROR] Could not fetch playlist. Try:")
        print("  1. Update yt-dlp:  pip install -U yt-dlp")
        print("  2. Check the playlist is public")
        raise SystemExit(1)

    print(f"[DEBUG] Type: {info.get('_type','?')} | Title: {info.get('title','N/A')}")

    if info.get("_type") == "video" or "entries" not in info:
        print("[INFO] Single video detected.")
        return [info]

    entries = [e for e in info["entries"] if e]
    if not entries:
        print("[ERROR] Playlist has 0 valid entries.")
        raise SystemExit(1)

    print(f"[OK] Found {len(entries)} tracks in '{info.get('title','playlist')}'")
    return entries


# ─────────────────────────────────────────────
#  Download a single entry
# ─────────────────────────────────────────────
def download_single(entry: dict, ffmpeg_path: str, mode: str, quality: str) -> tuple:
    title = entry.get("title", entry.get("id", "unknown"))
    vid_id = entry.get("id")
    url = (
        f"https://www.youtube.com/watch?v={vid_id}"
        if vid_id
        else entry.get("url", "")
    )
    if not url:
        return title, False

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(ffmpeg_path, mode, quality)) as ydl:
            ydl.download([url])
        return title, True
    except Exception as exc:
        print(f"  FAILED: {title} — {exc}")
        return title, False


# ─────────────────────────────────────────────
#  Main download orchestrator
# ─────────────────────────────────────────────
def download_playlist(playlist_url: str, mode: str, quality: str, workers: int):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    entries = fetch_playlist_entries(playlist_url)

    label = f"MP3 @ {quality} kbps" if mode == "audio" else f"MP4 @ {quality}p"
    print(f"\nDownloading {len(entries)} item(s) | {label} | {workers} workers\n")

    done, failed, total = 0, 0, len(entries)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(download_single, entry, ffmpeg_path, mode, quality): entry
            for entry in entries
        }
        for future in as_completed(futures):
            title, success = future.result()
            if success:
                done += 1
                print(f"  ✓  [{done + failed}/{total}] {title}")
            else:
                failed += 1
                print(f"  ✗  [{done + failed}/{total}] {title}")

    print(f"\n{'='*55}")
    print(f"Done! {done} succeeded, {failed} failed.")
    print(f"Saved to ./{DOWNLOAD_DIR}/")


# ─────────────────────────────────────────────
#  CLI prompt helpers
# ─────────────────────────────────────────────
def prompt_mode() -> str:
    print("\nWhat do you want to download?")
    print("  [1] Audio (MP3)")
    print("  [2] Video (MP4)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "audio"
        if choice == "2":
            return "video"
        print("  Please enter 1 or 2.")


def prompt_audio_quality() -> str:
    print("\nAudio quality (MP3 bitrate):")
    print("  [1] 320 kbps  — best quality")
    print("  [2] 192 kbps  — good quality  (default)")
    print("  [3] 128 kbps  — smaller files")
    mapping = {"1": "320", "2": "192", "3": "128", "": "192"}
    while True:
        choice = input("Enter 1 / 2 / 3 [default 2]: ").strip()
        if choice in mapping:
            return mapping[choice]
        print("  Please enter 1, 2, or 3.")


def prompt_video_quality() -> str:
    print("\nVideo quality (max resolution):")
    print("  [1] Best available  (default)")
    print("  [2] 1080p")
    print("  [3] 720p")
    print("  [4] 480p")
    print("  [5] 360p")
    print("  [6] 4K  (2160p)")
    mapping = {
        "1": "best", "": "best",
        "2": "1080",
        "3": "720",
        "4": "480",
        "5": "360",
        "6": "2160",
    }
    while True:
        choice = input("Enter 1–6 [default 1]: ").strip()
        if choice in mapping:
            return mapping[choice]
        print("  Please enter a number from 1 to 6.")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  YouTube Playlist / Video Downloader")
    print("=" * 55)

    url = input("\nEnter YouTube playlist or video URL: ").strip().strip('"').strip("'")

    mode = prompt_mode()

    if mode == "audio":
        quality = prompt_audio_quality()
    else:
        quality = prompt_video_quality()

    workers_input = input(f"\nParallel workers? (default {MAX_WORKERS}): ").strip()
    workers = int(workers_input) if workers_input.isdigit() else MAX_WORKERS

    print("\n" + "=" * 55)
    download_playlist(url, mode, quality, workers)