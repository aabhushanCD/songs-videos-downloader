# songs-videos-downloader

🎵 Fast parallel YouTube playlist downloader — download audio (MP3 up to 320kbps) or video (MP4 up to 4K) from the CLI. Powered by yt-dlp with auto FFmpeg.

# yt-playlist-dl

A fast, parallel YouTube playlist and video downloader built with `yt-dlp`. Download entire playlists or single videos as high-quality **MP3 audio** or **MP4 video** — all from an interactive command-line interface.

---

## Features

- **Audio or Video** — choose at runtime; no code changes needed
- **Best quality downloads** — audio up to 320 kbps MP3, video up to 4K MP4
- **Parallel downloads** — configurable worker threads for faster playlist downloads
- **Smart playlist extraction** — automatically strips extra URL params to get a clean playlist URL
- **Download archive** — skips already-downloaded files automatically (`.archive.txt`)
- **Single video support** — works on individual video URLs too, not just playlists
- **Auto FFmpeg** — no manual FFmpeg install required (`imageio-ffmpeg` handles it)

---

## Requirements

- Python 3.8+
- See [`requirements.txt`](requirements.txt)

```
yt-dlp>=2024.1.1
imageio-ffmpeg>=0.4.9
```

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/aabhushanCD/songs-videos-downloader


# 2. Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
python downloader.py
```

You will be prompted step by step:

```
===================================================
  YouTube Playlist / Video Downloader
===================================================

Enter YouTube playlist or video URL: https://www.youtube.com/playlist?list=...

What do you want to download?
  [1] Audio (MP3)
  [2] Video (MP4)
Enter 1 or 2: 1

Audio quality (MP3 bitrate):
  [1] 320 kbps  — best quality
  [2] 192 kbps  — good quality  (default)
  [3] 128 kbps  — smaller files
Enter 1 / 2 / 3 [default 2]: 1

Parallel workers? (default 4): 4
```

Downloaded files are saved to the `downloads/` folder.

---

## Quality Options

### Audio (MP3)

| Option | Bitrate  | Best For                    |
| ------ | -------- | --------------------------- |
| 1      | 320 kbps | Audiophiles, archiving      |
| 2      | 192 kbps | General listening (default) |
| 3      | 128 kbps | Storage-constrained devices |

### Video (MP4)

| Option | Resolution     | Notes                                |
| ------ | -------------- | ------------------------------------ |
| 1      | Best available | Auto-picks highest quality (default) |
| 2      | 1080p          | Full HD                              |
| 3      | 720p           | HD                                   |
| 4      | 480p           | SD                                   |
| 5      | 360p           | Low bandwidth                        |
| 6      | 4K (2160p)     | Ultra HD, large file size            |

> Video downloads merge the best available video + audio streams into a single `.mp4` file. If the exact resolution isn't available, it automatically falls back to the next best option.

---

## Output Structure

```
downloads/
├── .archive.txt          ← tracks downloaded videos (prevents re-downloads)
├── 1 - Song Title.mp3
├── 2 - Another Song.mp3
└── ...
```

---

## Keeping yt-dlp Updated

YouTube frequently changes its internal APIs. If downloads start failing, update `yt-dlp`:

```bash
pip install -U yt-dlp
```

---

## Dependencies

| Package                                                       | Purpose                                   |
| ------------------------------------------------------------- | ----------------------------------------- |
| [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)                  | Core downloader engine                    |
| [`imageio-ffmpeg`](https://github.com/imageio/imageio-ffmpeg) | Bundles FFmpeg — no manual install needed |

---

## License

MIT License — free to use, modify, and distribute.
