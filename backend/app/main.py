from fastapi import FastAPI, HTTPException

from .services.planner import generate_plan, PlanRequest, StudyPlan
from .schemas import PlanRequest, StudyPlan

app = FastAPI(
    title = "Study Mate API",
    description = "An API for generating personalized study plans using OpenAI's GPT-4 model.",
    version = "0.1.0",
)

@app.get("/health", summary="Health Check", description="Check if the API is running.")
def health_check():
    return {"status": "ok"}

@app.post("/plan", response_model=StudyPlan, summary="Generate Study Plan", 
          description="Generate a personalized study plan based on user input.")
def create_plan(request: PlanRequest):
    try:
        return generate_plan(request)
    except Exception as e:
        raise HTTPException(status_code=502,
                             detail=str(e)
                             )