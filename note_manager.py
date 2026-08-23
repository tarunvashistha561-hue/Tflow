"""
note_manager.py — NoteManager class for Digital Notebook.
Handles all CRUD operations using JSON file storage (no SQL).
Follows PEP 8 and uses modular, exception-safe design.
"""

import json
import os
from datetime import datetime


# ─── Constants ───────────────────────────────────────────────────────────────

NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.json")
DATE_FORMAT = "%Y-%m-%d %H:%M"


# ─── NoteManager ─────────────────────────────────────────────────────────────


class NoteManager:
    """
    Manages all note operations: load, save, add, update, delete, search.
    Persists data exclusively through JSON file handling.
    """

    def __init__(self, filepath: str = NOTES_FILE) -> None:
        """
        Initialise the NoteManager.

        Args:
            filepath: Absolute or relative path to the JSON data file.
        """
        self.filepath = filepath
        self._ensure_file_exists()

    # ── Private helpers ────────────────────────────────────────────────────

    def _ensure_file_exists(self) -> None:
        """Create the notes file with an empty list if it does not exist."""
        if not os.path.exists(self.filepath):
            self.save_notes([])

    def _now(self) -> str:
        """Return the current datetime as a formatted string."""
        return datetime.now().strftime(DATE_FORMAT)

    def _generate_id(self, notes: list) -> int:
        """
        Generate a unique integer ID that is not already in use.

        Args:
            notes: The current list of note dictionaries.

        Returns:
            A unique positive integer ID.
        """
        if not notes:
            return 1
        existing_ids = {note.get("id", 0) for note in notes}
        new_id = max(existing_ids) + 1
        # Guard against duplicate IDs if max caused a collision somehow
        while new_id in existing_ids:
            new_id += 1
        return new_id

    # ── Core file-handling methods ─────────────────────────────────────────

    def load_notes(self) -> list:
        """
        Load all notes from the JSON file.

        Handles:
            - Missing file → returns []
            - Empty file   → returns []
            - Corrupted JSON → returns []

        Returns:
            A list of note dictionaries, ordered newest-first.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if not isinstance(data, list):
                    return []
                # Return newest-first
                return sorted(data, key=lambda n: n.get("created_at", ""), reverse=True)
        except FileNotFoundError:
            self._ensure_file_exists()
            return []
        except json.JSONDecodeError:
            # Back up corrupted file and start fresh
            self._backup_corrupted_file()
            self.save_notes([])
            return []
        except Exception as e:
            print(f"[NoteManager] Unexpected error loading notes: {e}")
            return []

    def save_notes(self, notes: list) -> bool:
        """
        Persist the list of notes to the JSON file atomically.

        Args:
            notes: The complete list of note dictionaries to save.

        Returns:
            True on success, False on failure.
        """
        try:
            # Write to a temp file first, then rename for atomicity
            tmp_path = self.filepath + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.filepath)
            return True
        except Exception as e:
            print(f"[NoteManager] Error saving notes: {e}")
            return False

    def _backup_corrupted_file(self) -> None:
        """Rename corrupted JSON file to a timestamped backup."""
        try:
            backup = self.filepath + f".corrupt.{int(datetime.now().timestamp())}"
            os.rename(self.filepath, backup)
            print(f"[NoteManager] Corrupted file backed up as: {backup}")
        except Exception:
            pass  # Best-effort backup

    # ── CRUD operations ────────────────────────────────────────────────────

    def add_note(self, title: str, content: str) -> dict:
        """
        Create and store a new note.

        Args:
            title:   The note title (must not be empty).
            content: The note body (must not be empty).

        Returns:
            The newly created note dictionary.

        Raises:
            ValueError: If title or content is blank.
        """
        title = title.strip()
        content = content.strip()

        if not title:
            raise ValueError("Note title cannot be empty.")
        if not content:
            raise ValueError("Note content cannot be empty.")

        notes = self.load_notes()
        now = self._now()
        note = {
            "id": self._generate_id(notes),
            "title": title,
            "content": content,
            "created_at": now,
            "updated_at": now,
        }
        notes.append(note)
        # Save unordered (load_notes handles ordering)
        self.save_notes(notes)
        return note

    def update_note(self, note_id: int, title: str, content: str) -> dict:
        """
        Update an existing note's title and/or content.

        Args:
            note_id: The integer ID of the note to update.
            title:   The new title (must not be empty).
            content: The new content (must not be empty).

        Returns:
            The updated note dictionary.

        Raises:
            ValueError: If title or content is blank.
            KeyError:   If no note with the given ID exists.
        """
        title = title.strip()
        content = content.strip()

        if not title:
            raise ValueError("Note title cannot be empty.")
        if not content:
            raise ValueError("Note content cannot be empty.")

        notes = self.load_notes()
        for note in notes:
            if note.get("id") == note_id:
                note["title"] = title
                note["content"] = content
                note["updated_at"] = self._now()
                self.save_notes(notes)
                return note

        raise KeyError(f"Note with ID {note_id} not found.")

    def delete_note(self, note_id: int) -> bool:
        """
        Remove a note by its ID.

        Args:
            note_id: The integer ID of the note to delete.

        Returns:
            True if deleted successfully, False if ID not found.
        """
        notes = self.load_notes()
        original_count = len(notes)
        notes = [n for n in notes if n.get("id") != note_id]

        if len(notes) == original_count:
            return False  # ID not found

        self.save_notes(notes)
        return True

    def get_note_by_id(self, note_id: int) -> dict | None:
        """
        Retrieve a single note by its ID.

        Args:
            note_id: The integer ID to look up.

        Returns:
            The note dictionary, or None if not found.
        """
        notes = self.load_notes()
        for note in notes:
            if note.get("id") == note_id:
                return note
        return None

    def search_notes(self, query: str) -> list:
        """
        Case-insensitive search across note titles and content.

        Args:
            query: The search string.

        Returns:
            A list of matching note dictionaries (newest-first).
        """
        if not query or not query.strip():
            return self.load_notes()

        query_lower = query.strip().lower()
        notes = self.load_notes()
        return [
            note
            for note in notes
            if query_lower in note.get("title", "").lower()
            or query_lower in note.get("content", "").lower()
        ]

    def get_all_notes(self) -> list:
        """Return all notes ordered newest-first."""
        return self.load_notes()

    def count(self) -> int:
        """Return the total number of stored notes."""
        return len(self.load_notes())
