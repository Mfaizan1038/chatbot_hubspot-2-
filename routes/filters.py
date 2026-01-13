from fastapi import APIRouter, HTTPException
from schemas import FilterRequest, FilterResponse
from services.filter_builder import build_filter

router = APIRouter()

@router.post("/filter", response_model=FilterResponse)
def create_filter(req: FilterRequest):
    result = build_filter(req.context, req.query)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
