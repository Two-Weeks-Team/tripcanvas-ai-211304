from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from ai_service import call_inference

router = APIRouter()

class PlanRequest(BaseModel):
    query: str = Field(..., description="User's travel query or goal")
    preferences: Dict[str, Any] = Field(..., description="User's travel preferences (style, season, budget, etc.)")

class PlanResponse(BaseModel):
    summary: str = Field(..., description="Brief summary of the generated plan")
    items: List[Any] = Field(..., description="Detailed items such as day‑by‑day activities")
    score: Optional[float] = Field(None, description="Confidence or relevance score")

class InsightsRequest(BaseModel):
    selection: str = Field(..., description="The chosen element (e.g., a destination or activity)")
    context: Dict[str, Any] = Field(..., description="Additional context for generating insights")

class InsightsResponse(BaseModel):
    insights: List[Any] = Field(..., description="Generated insights")
    next_actions: List[str] = Field(..., description="Suggested next steps for the user")
    highlights: List[str] = Field(..., description="Key highlights extracted from the context")

@router.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    messages = [
        {"role": "system", "content": "You are a travel planning assistant. Generate a concise trip brief based on the user's query and preferences."},
        {"role": "user", "content": f"Query: {request.query}\nPreferences: {request.preferences}"},
    ]
    raw_result = await call_inference(messages)
    if not isinstance(raw_result, dict):
        raise HTTPException(status_code=502, detail="Invalid AI response format")
    return PlanResponse(
        summary=raw_result.get("summary", ""),
        items=raw_result.get("items", []),
        score=raw_result.get("score"),
    )

@router.post("/insights", response_model=InsightsResponse)
async def get_insights(request: InsightsRequest):
    messages = [
        {"role": "system", "content": "Provide concise, actionable insights for the given selection and context."},
        {"role": "user", "content": f"Selection: {request.selection}\nContext: {request.context}"},
    ]
    raw_result = await call_inference(messages)
    if not isinstance(raw_result, dict):
        raise HTTPException(status_code=502, detail="Invalid AI response format")
    return InsightsResponse(
        insights=raw_result.get("insights", []),
        next_actions=raw_result.get("next_actions", []),
        highlights=raw_result.get("highlights", []),
    )
