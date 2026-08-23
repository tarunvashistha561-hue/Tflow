# Digital Notebook 📓

A fully-functional **Android Note-Taking App** built with:
- **Python 3** + **Flask** — backend logic and REST API
- **HTML5 / CSS3 / JavaScript** — beautiful, responsive UI
- **JSON file handling** — persistent storage (no SQL database)
- **Kivy + python-for-android** — Android packaging

---

## ✨ Features

| Feature | Details |
|---|---|
| **Create notes** | Title + content with validation |
| **View notes** | Card layout, newest first |
| **Search** | Instant, case-insensitive, with highlighting |
| **Edit notes** | Pre-populated form, updates timestamp |
| **Delete notes** | Confirmation dialog before deleting |
| **Persistent storage** | All notes saved to `notes.json` |
| **Dark mode** | Automatic via `prefers-color-scheme` |
| **Material Design** | Cards, FAB, shadows, animations |

---

## 📁 Project Structure

```
DigitalNotebook/
├── app.py              ← Flask app & REST API routes
├── note_manager.py     ← NoteManager class (CRUD + file handling)
├── main.py             ← Android/desktop launcher (Kivy WebView)
├── notes.json          ← Auto-created JSON storage
├── requirements.txt    ← Python dependencies
├── buildozer.spec      ← Android APK build configuration
│
├── templates/
│   ├── index.html      ← Home screen
│   ├── add_note.html   ← Add note form
│   └── edit_note.html  ← Edit note form
│
├── static/
│   ├── css/style.css   ← Complete design system
│   └── js/script.js    ← Search, modals, API, validation
│
└── assets/
    └── logo.png        ← App icon
```

---

## 🚀 Quick Start (Desktop / Testing)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

> **Tip:** You can also run `python main.py` which opens the browser automatically.

---

## 📱 Android APK Build Instructions

> **Requirements:** Linux or WSL2 (Buildozer does not support Windows natively).
> Recommended: Ubuntu 20.04+ or Debian 11+

### Step 1 — Install system dependencies

```bash
sudo apt update && sudo apt install -y \
    python3-pip build-essential git \
    libssl-dev libffi-dev python3-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev openjdk-17-jdk unzip
```

### Step 2 — Install Buildozer

```bash
pip install buildozer cython
```

### Step 3 — Navigate to project directory

```bash
cd /path/to/DigitalNotebook
```

### Step 4 — Build the APK (first build downloads NDK/SDK — ~1 GB)

```bash
buildozer android debug
```

The APK will be created at:
```
bin/digitalnotebook-1.0.0-arm64-v8a-debug.apk
```

### Step 5 — Deploy to a connected Android device

```bash
buildozer android deploy run logcat
```

> **Tip:** Enable **Developer Options → USB Debugging** on your Android device.

---

## 🔌 REST API Reference

All routes are served by Flask on `http://127.0.0.1:5000`.

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Home page |
| `GET` | `/add` | Add note form |
| `GET` | `/edit/<id>` | Edit note form |
| `GET` | `/api/notes` | Get all notes |
| `POST` | `/api/notes` | Create a note |
| `GET` | `/api/notes/<id>` | Get single note |
| `PUT` | `/api/notes/<id>` | Update a note |
| `DELETE` | `/api/notes/<id>` | Delete a note |
| `GET` | `/api/search?q=<query>` | Search notes |

### Example API usage

```bash
# Create a note
curl -X POST http://127.0.0.1:5000/api/notes \
     -H "Content-Type: application/json" \
     -d '{"title": "Shopping List", "content": "Milk, Bread, Eggs"}'

# Search notes
curl http://127.0.0.1:5000/api/search?q=shopping

# Delete a note
curl -X DELETE http://127.0.0.1:5000/api/notes/1
```

---

## 📦 JSON Storage Format

All notes are stored in `notes.json`:

```json
[
  {
    "id": 1,
    "title": "Shopping List",
    "content": "Milk, Bread, Eggs",
    "created_at": "2026-08-23 10:30",
    "updated_at": "2026-08-23 10:30"
  }
]
```

The `NoteManager` class handles:
- ✅ Missing file → creates it automatically
- ✅ Empty file → returns empty list
- ✅ Corrupted JSON → backs up file, starts fresh
- ✅ Duplicate IDs → generates unique ID
- ✅ Atomic writes → writes to `.tmp` then renames

---

## 🎨 Design System

| Token | Value |
|---|---|
| Primary | `#4F46E5` |
| Secondary | `#6366F1` |
| Background | `#F8FAFC` |
| Card | `#FFFFFF` |
| Card radius | `15px` |
| Button radius | `12px` |
| Font | Inter (Google Fonts) |

Dark mode is supported automatically via `prefers-color-scheme: dark`.

---

## 🔮 Future Enhancements

The codebase is designed to easily add:

- [ ] Categories & Tags
- [ ] Note favourites / archive
- [ ] Export to PDF or TXT
- [ ] PIN lock / biometric authentication
- [ ] Cloud backup (Firebase / Supabase)
- [ ] Voice notes
- [ ] Reminder notifications
- [ ] Themes & custom colours
- [ ] Share notes
- [ ] Recycle Bin

---

## 📄 License

MIT License — Free to use, modify, and distribute.
