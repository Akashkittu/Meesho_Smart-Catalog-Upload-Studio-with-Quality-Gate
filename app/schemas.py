from typing import Dict, List


CATEGORY_SCHEMAS: Dict[str, List[str]] = {
    "T-Shirt": ["brand", "size", "color", "material"],
    "Saree": ["brand", "color", "fabric", "length"],
    "Footwear": ["brand", "size", "color", "gender"],
}

DEFAULT_CATEGORY = "T-Shirt"
