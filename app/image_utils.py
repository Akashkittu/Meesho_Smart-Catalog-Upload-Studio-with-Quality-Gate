from typing import Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import imagehash

def pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def variance_of_laplacian(cv_img: np.ndarray) -> float:
    return cv2.Laplacian(cv_img, cv2.CV_64F).var()

def phash_hex(img: Image.Image) -> str:
    return str(imagehash.phash(img))

def watermark_edge_density(cv_img: np.ndarray) -> float:
    """A rough heuristic:
    - Convert to gray, run Canny, look at four corner ROIs.
    - Compute edge pixel density in corner bands; return max density across corners.
    """
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    h, w = edges.shape
    bw, bh = max(w // 5, 60), max(h // 5, 60)  

    rois = [
        edges[0:bh, 0:bw],           
        edges[0:bh, w-bw:w],          
        edges[h-bh:h, 0:bw],            
        edges[h-bh:h, w-bw:w],           
    ]
    densities = []
    for r in rois:
        total = r.size
        cnt = np.count_nonzero(r)
        densities.append(cnt / float(total))
    return float(max(densities))
