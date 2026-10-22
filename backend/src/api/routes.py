"""Documentation will be here"""

from fastapi import APIRouter

from src.api.schemas import AnalysisRequest, AnalysisResponse
from src.services.analysis_service import analyze_message

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    result = analyze_message(request.message)

    return AnalysisResponse(**result)