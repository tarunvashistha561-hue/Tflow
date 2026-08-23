"""
main.py — Android launcher for Digital Notebook.
Uses Kivy to create a fullscreen WebView that loads the Flask server.
This is the entry point when the app is packaged as an APK via Buildozer.
"""

import threading
import time
import os
import sys

# ─── Platform detection ────────────────────────────────────────────────────

IS_ANDROID = False
try:
    import android  # type: ignore[import]  # noqa: F401 — available only on Android
    IS_ANDROID = True
except ImportError:
    pass


# ─── Flask server helper ───────────────────────────────────────────────────

def start_flask_server():
    """Start the Flask server using waitress (production WSGI) on Android,
    or the built-in dev server on desktop for testing."""
    from app import app as flask_app

    if IS_ANDROID:
        try:
            from waitress import serve
            print("[main.py] Starting waitress server on 127.0.0.1:5000")
            serve(flask_app, host="127.0.0.1", port=5000, threads=4)
        except ImportError:
            print("[main.py] waitress not found — using Flask dev server")
            flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    else:
        flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def wait_for_flask(host="127.0.0.1", port=5000, timeout=15.0):
    """
    Poll until Flask is accepting connections, instead of a bare sleep().
    Retries every 200 ms for up to `timeout` seconds.
    """
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                print("[main.py] Flask is ready.")
                return True
        except OSError:
            time.sleep(0.2)
    print("[main.py] WARNING: Flask did not start within timeout.")
    return False


# ─── Kivy imports ─────────────────────────────────────────────────────────

# Kivy is only installed inside the Buildozer APK runtime.
# Wrap imports so the IDE / desktop Python doesn't raise ModuleNotFoundError.
try:
    from kivy.app import App  # type: ignore[import]
    from kivy.uix.widget import Widget  # type: ignore[import]
    from kivy.clock import Clock  # type: ignore[import]
except ImportError:  # pragma: no cover — only hits on desktop without Kivy
    App = object  # type: ignore[assignment,misc]
    Widget = object  # type: ignore[assignment]
    Clock = None  # type: ignore[assignment]


# ─── Stub run_on_ui_thread for desktop ────────────────────────────────────

if not IS_ANDROID:
    # Provide a no-op stub so the decorator reference doesn't crash on desktop
    def run_on_ui_thread(fn):  # type: ignore[misc]
        """No-op stub — real implementation is provided by android.runnable on-device."""
        return fn
else:
    # On Android, import the real decorator now that the runtime is ready
    from android.runnable import run_on_ui_thread  # type: ignore[import]  # noqa: F401


# ─── WebView Widget ───────────────────────────────────────────────────────

class AndroidWebViewWidget(Widget):
    """Widget that hosts an Android WebView filling the entire screen."""

    def __init__(self, url: str, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self._webview = None
        if IS_ANDROID and Clock is not None:
            Clock.schedule_once(lambda dt: self._create_webview(), 0)

    @run_on_ui_thread
    def _create_webview(self):
        """Create and configure the native Android WebView on the UI thread."""
        # These autoclass imports MUST happen inside the UI thread on Android
        from jnius import autoclass  # type: ignore[import]

        WebView        = autoclass('android.webkit.WebView')
        WebViewClient  = autoclass('android.webkit.WebViewClient')
        WebSettings    = autoclass('android.webkit.WebSettings')
        LinearLayout   = autoclass('android.widget.LinearLayout')  # noqa: F841
        LayoutParams   = autoclass('android.view.ViewGroup$LayoutParams')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        activity = PythonActivity.mActivity

        webview = WebView(activity)
        settings = webview.getSettings()

        # Enable JavaScript (required for our UI)
        settings.setJavaScriptEnabled(True)
        # Enable DOM storage
        settings.setDomStorageEnabled(True)
        # Responsive meta tag support
        settings.setUseWideViewPort(True)
        settings.setLoadWithOverviewMode(True)
        # Disable built-in zoom controls (handled by CSS)
        settings.setBuiltInZoomControls(False)
        settings.setDisplayZoomControls(False)
        # Cache for offline resilience (notes are local anyway)
        settings.setCacheMode(WebSettings.LOAD_DEFAULT)
        # Text encoding
        settings.setDefaultTextEncodingName("UTF-8")

        # Use a clean WebViewClient (no external browser pop-ups)
        webview.setWebViewClient(WebViewClient())
        webview.setScrollBarStyle(0)  # No scrollbars (handled by CSS)

        # Fullscreen layout
        layout_params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT,
        )
        webview.setLayoutParams(layout_params)

        # Attach to activity
        activity.addContentView(webview, layout_params)
        webview.loadUrl(self.url)

        self._webview = webview
        print(f"[main.py] WebView loaded: {self.url}")


# ─── Kivy App Class ───────────────────────────────────────────────────────

class DigitalNotebookApp(App):
    """Main Kivy application class."""

    APP_URL = "http://127.0.0.1:5000"

    def build(self):
        """Build the root widget.
        Flask is started here — AFTER Kivy has initialised — to avoid
        the startup race condition that crashes the app on Android.
        """
        self.title = "Tflow"

        # Start Flask server in a daemon background thread
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()

        # Wait until Flask is actually accepting connections (max 15 s)
        wait_for_flask()

        return AndroidWebViewWidget(url=self.APP_URL)

    def on_pause(self):
        """Allow the app to be paused (Android lifecycle)."""
        return True

    def on_resume(self):
        """Resume without restarting the Flask server."""
        pass


# ─── Entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not IS_ANDROID:
        # Desktop mode: start Flask then open browser
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()

        import webbrowser
        print("=" * 60)
        print("  Digital Notebook — Desktop mode")
        print("  Waiting for Flask to start…")
        wait_for_flask()
        print("  Opening http://127.0.0.1:5000 in browser…")
        print("  (On Android, a native WebView will be used)")
        print("=" * 60)
        webbrowser.open("http://127.0.0.1:5000")
        try:
            flask_thread.join()
        except KeyboardInterrupt:
            print("\n[main.py] Shutting down.")
            sys.exit(0)
    else:
        DigitalNotebookApp().run()
