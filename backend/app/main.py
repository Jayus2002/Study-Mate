import logging
from fastapi import FastAPI, HTTPException, Depends
from .schemas import PlanRequest, SavedPlan, StudyPlan
from .db.session import create_db_and_tables, get_session
from .services.progress import PlanPersistenceError, get_saved_plan, save_plan
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
@app.on_event("startup")
def startup():
    create_db_and_tables()

@app.get("/health", summary="Health Check", description="Check if the API is running.")
def health_check():
    return {"status": "ok"}

@app.post("/plan", response_model=SavedPlan, summary="Generate Study Plan", 
          description="Generate a personalized study plan based on user input.")
def create_plan(request: PlanRequest,
                session=Depends(get_session)
                ):
    logger.info("开始生成学习计划")
    try:
        generated_plan = generate_plan(request)
        return save_plan(generated_plan, session)
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
    except PlanPersistenceError as e:
        logger.error("Plan persistence error")
        raise HTTPException(status_code=500, detail="学习计划生成成功，但保存失败。") from e

@app.get("/plans/{plan_id}", response_model=SavedPlan)
def read_plan(
    plan_id: int,
    session=Depends(get_session)
):
    saved_plan = get_saved_plan(plan_id, session)
    if saved_plan is None:
        logger.warning(f"Plan with ID {plan_id} not found")
        raise HTTPException(status_code=404, detail="学习计划未找到。")
    return saved_plan
