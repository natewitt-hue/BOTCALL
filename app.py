"""
render_server.py — TSL WittGPT Data Server (Render Cloud)
─────────────────────────────────────────────────────────────────────────────
Stores all Snallabot exports IN MEMORY (Python dict) instead of on disk.
Render's free tier wipes the filesystem on every restart, so disk storage
is useless. The in-memory store survives as long as the dyno is running.

When Render cold-starts (after 15 min idle):
  1. Store is empty — bot will see 404s temporarily
  2. Run /export in Snallabot to re-populate (takes ~30 seconds)
  3. Bot reads fresh data immediately after

Deploy on Render:
  - Build command:  pip install flask gunicorn
  - Start command:  gunicorn render_server:app --bind 0.0.0.0:$PORT
  - Instance type:  Free
─────────────────────────────────────────────────────────────────────────────
"""

import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ── In-memory data store ──────────────────────────────────────────────────────
# { "standings.json": <dict>, "roster_774242334.json": <dict>, ... }
_store: dict[str, dict] = {}
_last_updated: dict[str, str] = {}   # filename → ISO timestamp


# ── Smart filename detection ──────────────────────────────────────────────────

def _detect_filename(path: str, payload: dict) -> str:
    """
    Derive the storage filename from the URL path.
    Handles Snallabot's roster path pattern:
      /export/ps5/625743/team/774242334/roster  →  roster_774242334.json
      /export/standings                          →  standings.json
      /export/passing                            →  passing.json
    """
    parts = [p for p in path.strip("/").split("/") if p]

    # Roster pattern: ...team/<teamId>/roster
    if "roster" in parts:
        idx = parts.index("roster")
        team_id = parts[idx - 1] if idx > 0 else "unknown"
        return f"roster_{team_id}.json"

    # Free agents
    if "freeagents" in parts or "free_agents" in parts:
        return "roster_freeagents.json"

    # Standard: last path segment is the file stem
    stem = parts[-1] if parts else "data"
    # Strip any accidental .json suffix before re-adding
    stem = stem.replace(".json", "")
    return f"{stem}.json"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    """Root — health check + list of stored files."""
    if not _store:
        return (
            "<h1>TSL Data Server Active</h1>"
            "<p>⚠️ No files yet — run <b>/export current</b> in Snallabot to populate.</p>"
            "<p>The in-memory store is empty (server just restarted or no exports received).</p>"
        ), 200

    file_links = "".join(
        f'<li><a href="/{fn}">{fn}</a> — {_last_updated.get(fn, "?")}</li>'
        for fn in sorted(_store.keys())
    )
    return (
        f"<h1>TSL Data Server Active</h1>"
        f"<p>{len(_store)} files in memory:</p>"
        f"<ul>{file_links}</ul>"
    ), 200


@app.route("/export", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/export/<path:path>", methods=["POST", "GET"])
def handle_export(path):
    """
    POST  — receive a Snallabot export and store it in memory.
    GET   — health check for Snallabot's URL verification ping.
    """
    if request.method == "GET":
        return jsonify({"status": "online", "files": len(_store)}), 200

    payload = request.get_json(force=True, silent=True)
    if not payload:
        return "No valid JSON received", 400

    filename = _detect_filename(path, payload)
    _store[filename] = payload
    _last_updated[filename] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print(f"[Export] Stored: {filename} ({len(json.dumps(payload))} bytes)")
    return f"Saved {filename}", 200


@app.route("/<path:filename>", methods=["GET"])
def serve_file(filename):
    """
    Serve any stored file as JSON.
    WittGPT's data_manager fetches from here.
    """
    # Ensure .json extension
    if not filename.endswith(".json"):
        filename += ".json"

    if filename not in _store:
        return jsonify({"error": f"{filename} not found — re-run Snallabot export"}), 404

    return Response(
        json.dumps(_store[filename]),
        status=200,
        mimetype="application/json",
    )


@app.route("/status", methods=["GET"])
def status():
    """Machine-readable status for monitoring."""
    return jsonify({
        "status":       "online",
        "files_stored": len(_store),
        "files":        sorted(_store.keys()),
        "last_updated": _last_updated,
    }), 200


@app.route("/clear", methods=["POST"])
def clear():
    """Emergency clear endpoint — wipe all stored data."""
    _store.clear()
    _last_updated.clear()
    return jsonify({"status": "cleared"}), 200


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
