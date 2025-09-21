import os
from typing import List, Optional, Dict, Any, Union
from fastapi import FastAPI, UploadFile, Form, Request, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import Image
import io
import json

from .schemas import CATEGORY_SCHEMAS, DEFAULT_CATEGORY
from .scoring import compute_quality

load_dotenv()

BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "120.0"))
WM_EDGE_DENSITY = float(os.getenv("WATERMARK_EDGE_DENSITY", "0.12"))
MIN_QUALITY = int(os.getenv("MIN_QUALITY_SCORE", "70"))

app = FastAPI(title="Smart Catalog MVP")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class ScoreRequest(BaseModel):
    category: str
    attrs: Dict[str, Any]
    known_hashes: Optional[List[str]] = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    categories = list(CATEGORY_SCHEMAS.keys())
    return templates.TemplateResponse("index.html", {"request": request, "categories": categories, "min_quality": MIN_QUALITY})

@app.get("/schema")
async def get_schema(category: Optional[str] = None):
    c = category or DEFAULT_CATEGORY
    return {"category": c, "required": CATEGORY_SCHEMAS.get(c, [])}

@app.post("/score")
async def score_endpoint(
    images: Union[UploadFile, List[UploadFile], None] = File(None),
    payload: str = Form(...),
):
    data = json.loads(payload)
    category = data.get("category", DEFAULT_CATEGORY)
    attrs = data.get("attrs", {})
    known_hashes = data.get("known_hashes", [])

    pil_images = []
# normalize images -> list[UploadFile]
    if images is None:
        files_in = []
    elif isinstance(images, list):
        files_in = images
    else:
        files_in = [images]

    for f in files_in:
        content = await f.read()
        pil_images.append(Image.open(io.BytesIO(content)))

    result = compute_quality(
        images=pil_images,
        attrs=attrs,
        category=category,
        known_hashes=known_hashes,
        blur_threshold=BLUR_THRESHOLD,
        wm_edge_density_thresh=WM_EDGE_DENSITY,
        min_quality_score=MIN_QUALITY,
    )
    return result
