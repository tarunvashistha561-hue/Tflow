[app]

# ── Basic metadata ──────────────────────────────────────────────────────────
title = Tflow
package.name = tflow
package.domain = com.tarun.tflow

# ── Source ──────────────────────────────────────────────────────────────────
source.dir = .
source.include_exts = py,json,html,css,js,png,jpg,ico,txt

# Explicitly include all asset sub-directories (single-line format for compatibility)
source.include_patterns = templates/*.html,static/css/*.css,static/js/*.js,static/img/*.png,assets/*.png,notes.json

# ── Version ─────────────────────────────────────────────────────────────────
version = 1.0.0

# ── Requirements ────────────────────────────────────────────────────────────
# Kivy is provided by python-for-android; Flask and waitress are pip packages
requirements = python3,kivy,flask,waitress,jnius

# ── Android configuration ───────────────────────────────────────────────────
# Only INTERNET is needed — notes are stored in app-private directory
android.permissions = INTERNET

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

# Architecture: arm64-v8a for modern devices, armeabi-v7a for older ones
android.archs = arm64-v8a,armeabi-v7a

# Allow cleartext HTTP traffic to localhost (required for Flask on 127.0.0.1)
# FIXED: was android.manifest.uses_clear_text_traffic (wrong key, silently ignored)
android.allow_cleartext_traffic = True

# App entry point — PythonActivity hosts our Kivy app
# FIXED: removed invalid android.service line that was causing build errors
android.entrypoint = org.kivy.android.PythonActivity



# ── Screen orientation ───────────────────────────────────────────────────────
orientation = portrait

# ── Fullscreen ───────────────────────────────────────────────────────────────
fullscreen = 0

# ── Icons & splash ────────────────────────────────────────────────────────
android.icon.filename = %(source.dir)s/assets/logo.png

# ── Build tools ──────────────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1

# Build output directory — the APK will appear in: bin/
