"""
app.py — Flask application for Digital Notebook.
Serves the HTML UI and exposes a JSON REST API backed by NoteManager.
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    abort,
    send_file,
    send_from_directory,
)
from note_manager import NoteManager

# ─── App setup ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = "digital-notebook-secret-2026"

# Single NoteManager instance (file-based storage)
note_manager = NoteManager(os.path.join(BASE_DIR, "notes.json"))


# ─── HTML page routes ─────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Home screen — list all notes."""
    notes = note_manager.get_all_notes()
    total = note_manager.count()
    return render_template("index.html", notes=notes, total=total)


@app.route("/add", methods=["GET"])
def add_note_page():
    """Display the Add Note form."""
    return render_template("add_note.html")


@app.route("/edit/<int:note_id>", methods=["GET"])
def edit_note_page(note_id: int):
    """Display the Edit Note form populated with existing data."""
    note = note_manager.get_note_by_id(note_id)
    if note is None:
        abort(404)
    return render_template("edit_note.html", note=note)


# ─── REST API routes (consumed by JavaScript) ─────────────────────────────────


@app.route("/api/notes", methods=["GET"])
def api_get_notes():
    """GET /api/notes — Return all notes as JSON."""
    notes = note_manager.get_all_notes()
    return jsonify({"success": True, "notes": notes, "total": len(notes)})


@app.route("/api/notes", methods=["POST"])
def api_add_note():
    """POST /api/notes — Create a new note from JSON body."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request body."}), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    try:
        note = note_manager.add_note(title, content)
        return jsonify({"success": True, "note": note}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 422


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def api_get_note(note_id: int):
    """GET /api/notes/<id> — Return a single note as JSON."""
    note = note_manager.get_note_by_id(note_id)
    if note is None:
        return jsonify({"success": False, "error": "Note not found."}), 404
    return jsonify({"success": True, "note": note})


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def api_update_note(note_id: int):
    """PUT /api/notes/<id> — Update title and/or content."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request body."}), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    try:
        note = note_manager.update_note(note_id, title, content)
        return jsonify({"success": True, "note": note})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 422
    except KeyError as e:
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def api_delete_note(note_id: int):
    """DELETE /api/notes/<id> — Remove a note permanently."""
    deleted = note_manager.delete_note(note_id)
    if deleted:
        return jsonify({"success": True, "message": "Note deleted."})
    return jsonify({"success": False, "error": "Note not found."}), 404


@app.route("/api/search")
def api_search():
    """GET /api/search?q=<query> — Search notes by title and content."""
    query = request.args.get("q", "").strip()
    results = note_manager.search_notes(query)
    return jsonify({"success": True, "notes": results, "total": len(results), "query": query})


# ─── PWA routes ──────────────────────────────────────────────────────────────


@app.route("/pwa")
def pwa():
    """Serve the standalone PWA — works offline, installable on Android."""
    return send_file(os.path.join(BASE_DIR, "DigitalNotebook_App.html"))


@app.route("/sw.js")
def service_worker():
    """Serve the service worker from root scope (required for PWA offline)."""
    return send_file(
        os.path.join(BASE_DIR, "sw.js"),
        mimetype="application/javascript",
    )


# ─── Error handlers ───────────────────────────────────────────────────────────


@app.errorhandler(404)
def not_found(error):
    """Return JSON for API routes, clean page for HTML routes."""
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Not found."}), 404
    return render_template("404.html"), 404


# ─── Entry point ──────────────────────────────────────────────────────────────


if __name__ == "__main__":
    # Development server — use waitress for production/APK
    print("=" * 60)
    print("  Digital Notebook — Starting server")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
