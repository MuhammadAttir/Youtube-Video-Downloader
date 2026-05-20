# StreamPull — YouTube Downloader

A clean, production-ready YouTube downloader built with **Flask** + **yt-dlp**. Download MP4 videos (up to 1080p) or MP3 audio (up to 320kbps) directly from your browser.

---

## ✨ Features

- 🎬 **MP4 Video** — 144p · 240p · 360p · 480p · 720p · 1080p · Best
- 🎵 **MP3 Audio** — 128kbps · 192kbps · 320kbps
- 🌗 **Dark / Light Mode** toggle
- 📺 Video thumbnail, title, duration, and uploader preview
- ⚡ Fast AJAX fetch — no page reloads
- 🔒 Rate limiting & input validation
- 🗑️ Auto-delete temp files after download
- 📱 Fully responsive (mobile, tablet, desktop)
- 🎨 Premium UI with smooth animations

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · Flask 3 · Flask-Limiter |
| Download Engine | yt-dlp (latest) |
| Audio Conversion | FFmpeg |
| Frontend | HTML5 · TailwindCSS CDN · Vanilla JS |
| Fonts | Syne (display) · DM Sans (body) |

---

## 🚀 Quick Start

### 1. Clone the project

```bash
git clone <repo-url>
cd ytdl
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

FFmpeg is **required** for:
- Merging video + audio streams (HD quality)
- MP3 audio conversion

**Windows:** Download from https://ffmpeg.org/download.html and add to PATH.

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

### 5. Configure environment

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 6. Run the app

```bash
python run.py
```

Open **http://localhost:5000** in your browser.

---

## 📁 Project Structure

```
ytdl/
├── app/
│   ├── static/
│   │   ├── css/main.css          # Custom styles
│   │   └── js/app.js             # Frontend logic
│   ├── templates/
│   │   ├── base.html             # Base layout
│   │   └── index.html            # Main page
│   ├── routes/
│   │   ├── main_routes.py        # Page routes
│   │   └── download_routes.py    # API endpoints
│   ├── services/
│   │   ├── youtube_service.py    # Metadata fetching
│   │   └── downloader.py        # yt-dlp download logic
│   ├── utils/
│   │   ├── helpers.py            # Formatting helpers
│   │   ├── validators.py         # Input validation
│   │   └── cleanup.py            # Temp file cleanup
│   └── __init__.py               # App factory
├── downloads/                    # Temp download dir
├── temp/                         # Temp processing dir
├── config.py                     # Configuration
├── run.py                        # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🌐 API Endpoints

### `POST /api/info`

Fetch video metadata and available formats.

**Request body:**
```json
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Video Title",
    "thumbnail": "https://...",
    "duration": "3:33",
    "uploader": "Channel Name",
    "mp4_qualities": ["360p", "480p", "720p", "1080p", "best"],
    "mp3_qualities": ["128kbps", "192kbps", "320kbps"],
    "estimated_size": "45.2 MB"
  }
}
```

### `POST /api/download`

Download the video or audio file.

**Request body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "720p"
}
```

**Response:** File download (binary stream with `Content-Disposition` header).

---

## ⚙️ Configuration

Edit `config.py` or your `.env` file:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (required) | Flask session secret |
| `DEBUG` | `False` | Debug mode |
| `FFMPEG_LOCATION` | auto-detect | Path to ffmpeg binary |
| `COOKIES_FILE` | None | cookies.txt for restricted videos |
| `TEMP_FILE_TTL` | `600` | Seconds before temp files are deleted |

---

## 🔒 Rate Limits

| Endpoint | Limit |
|---|---|
| `/api/info` | 20 requests/minute |
| `/api/download` | 10 requests/minute |
| Global | 200/day · 50/hour |

---

## 📝 Legal Notice

This tool is for **personal, educational use only**. Do not download copyrighted content without permission. Respect YouTube's Terms of Service. The developers assume no liability for misuse.

---

## 🐛 Troubleshooting

**FFmpeg not found error:**
Make sure `ffmpeg` is in your system PATH, or set `FFMPEG_LOCATION` in `.env`.

**Video unavailable:**
Some videos are geo-restricted or require login. Use a `cookies.txt` file from your browser.

**Large file timeout:**
For very long videos, the server may take several minutes. This is normal.

**Rate limit hit:**
Wait a minute and try again. Limits are per-IP.
