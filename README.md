# Smart Catalog MVP — Upload Studio with Quality Gate

This is a minimal **prototype** of the *Smart Catalog* idea:
- Real-time **image lint** (blur, watermark heuristic, duplicate via pHash)
- **Attribute completeness** check by category
- A single **Quality Score (0–100)** with **fix-tips**
- Minimal web UI (drag & drop or select image + form) backed by **FastAPI**

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload --port 8000

# Open http://127.0.0.1:8000
```

## API

- `POST /score` — multipart form: `images[]` (0..n), `payload` (JSON string with `category`, `attrs`, optional `known_hashes`).
- `GET /schema?category=Name` — returns required attributes for a category (used by the UI).

## Notes

- **Blur**: variance of Laplacian threshold (configurable).
- **Watermark heuristic**: detects dense edge text overlays in corners (very rough for MVP).
- **Duplicate**: `imagehash.phash`. The server can also accept a list of `known_hashes` from the client.
- **Quality Score**: starts at 100, subtracts per-issue with caps.

