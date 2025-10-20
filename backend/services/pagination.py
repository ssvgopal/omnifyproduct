from typing import Any, Dict, List, Tuple


DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def get_pagination_params(query: Dict[str, Any]) -> Tuple[int, int]:
    try:
        page = max(int(query.get("page", 1)), 1)
    except Exception:
        page = 1
    try:
        page_size = int(query.get("page_size", DEFAULT_PAGE_SIZE))
    except Exception:
        page_size = DEFAULT_PAGE_SIZE
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    offset = (page - 1) * page_size
    return offset, page_size


def build_paginated_response(items: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
    return {
        "data": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


