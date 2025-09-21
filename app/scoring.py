from typing import List, Dict, Any, Tuple
from PIL import Image
from .image_utils import pil_to_cv, variance_of_laplacian, phash_hex, watermark_edge_density
from .schemas import CATEGORY_SCHEMAS, DEFAULT_CATEGORY

class QualityIssue:
    def __init__(self, code: str, message: str, tip: str, weight: int):
        self.code = code
        self.message = message
        self.tip = tip
        self.weight = weight

    def as_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "tip": self.tip,
            "weight": self.weight,
        }

def compute_quality(
    images: List[Image.Image],
    attrs: Dict[str, Any],
    category: str,
    known_hashes: List[str],
    blur_threshold: float = 120.0,
    wm_edge_density_thresh: float = 0.12,
    min_quality_score: int = 70,
) -> Dict[str, Any]:

    issues: List[QualityIssue] = []
    tips: List[str] = []
    weights_total = 0

    
    req = CATEGORY_SCHEMAS.get(category, CATEGORY_SCHEMAS.get(DEFAULT_CATEGORY, []))
    missing = [k for k in req if not attrs.get(k)]
    if missing:
        
        penalty = min(10 * len(missing), 40)
        issues.append(QualityIssue(
            code="ATTR_MISSING",
            message=f"Missing required attributes: {', '.join(missing)}",
            tip="Fill all mandatory fields; use Listing Copilot to autocomplete.",
            weight=penalty,
        ))

    
    seen_hash_dupe = False
    blur_flag = False
    wm_flag = False

    for img in images:
        cv = pil_to_cv(img)

        
        var = variance_of_laplacian(cv)
        if var < blur_threshold:
            blur_flag = True

        
        dens = watermark_edge_density(cv)
        if dens >= wm_edge_density_thresh:
            wm_flag = True

        
        h = phash_hex(img)
        if h in known_hashes:
            seen_hash_dupe = True
        known_hashes.append(h) 

    if blur_flag:
        issues.append(QualityIssue(
            code="IMG_BLUR",
            message="One or more images appear blurry (low sharpness).",
            tip="Upload a sharper image; avoid motion blur; use good lighting.",
            weight=30,
        ))
    if wm_flag:
        issues.append(QualityIssue(
            code="IMG_WATERMARK",
            message="Possible watermark/text overlay detected in image corners.",
            tip="Remove watermarks/text overlays; upload a clean product image.",
            weight=20,
        ))
    if seen_hash_dupe:
        issues.append(QualityIssue(
            code="IMG_DUPLICATE",
            message="Duplicate image detected (perceptual hash match).",
            tip="Provide distinct angles or close-ups; avoid reusing the same image.",
            weight=25,
        ))

    
    score = 100
    for it in issues:
        score -= it.weight
        weights_total += it.weight
    score = max(0, min(100, score))

    
    gate_pass = score >= min_quality_score

    return {
        "category": category,
        "required_attrs": req,
        "missing_attrs": missing,
        "issues": [i.as_dict() for i in issues],
        "quality_score": score,
        "gate_pass": gate_pass,
        "gate_threshold": min_quality_score,
    }
