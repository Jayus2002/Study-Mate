import logging
from fastapi import FastAPI, HTTPException
from .schemas import PlanRequest, StudyPlan
from .services.planner import (
    generate_plan,
    PlannerError,
    PlannerConfigError,
    PlannerTimeoutError,
    PlannerUpstreamError,
    PlannerOutputError,
)
logger = logging.getLogger(__name__)

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
    logger.info("开始生成学习计划")
    try:
        return generate_plan(request)
    except PlannerConfigError as e:
        logger.error("Planner configuration error")
        raise HTTPException(status_code=500, detail="服务配置错误，请检查服务器配置。") from e
    except PlannerTimeoutError as e:
        logger.error("Planner timeout error")
        raise HTTPException(status_code=504, detail="请求超时，请稍后再试。") from e
    except PlannerUpstreamError as e:
        logger.error("Planner upstream error")
        raise HTTPException(status_code=502, detail="上游服务错误，请稍后再试。") from e
    except PlannerOutputError as e:
        logger.error("Planner output error")
        raise HTTPException(status_code=500, detail="生成的学习计划格式不正确。") from e
    except PlannerError as e:
        logger.error("Planner error")
        raise HTTPException(status_code=500, detail="生成学习计划时发生错误。") from e