import json
from json import JSONDecodeError
from pydantic import ValidationError
import os
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    OpenAI,
)

from ..schemas import PlanRequest, StudyPlan


class PlannerError(Exception):
    pass

class PlannerTimeoutError(PlannerError):
    pass

class PlannerUpstreamError(PlannerError):
    pass

class PlannerConfigError(PlannerError):
    pass

class PlannerOutputError(PlannerError):
    pass

def build_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    print(f"LLM_BASE_URL: {base_url}")
    if not api_key:
        raise PlannerConfigError("LLM_API_KEY is not set in the environment variables.")
    if not base_url:
        raise PlannerConfigError("LLM_BASE_URL is not set in the environment variables.")

    return OpenAI(api_key=api_key, base_url=base_url, timeout=20, max_retries=0)


def generate_plan(request: PlanRequest,client=None) -> StudyPlan:
    load_dotenv()
    model = os.getenv("LLM_MODEL")
    print(f"LLM_MODEL: {model}")
    if not model:
        raise PlannerConfigError("LLM_MODEL is not set in the environment variables.")
    client = client or build_client()
    prompt = f"""
你是一名专业学习规划师。
请为用户制定学习计划。
用户目标：{request.goal}
学习时长： {request.duration_days} days
每天学习时间： {request.daily_minutes} minutes
已有基础： {request.background or "未知"}

要求：
1.必须返回 {request.duration_days} 天的计划
2.每天包含一个 topic
3.每天包含 2 到 4 个 tasks
4.每天包含 expected_output
5.任务难度应该循序渐进
6.只返回 JSON，不要返回 Markdown
7.JSON 格式必须是：
{{
  "title": "计划标题",
  "summary": "计划概述",
  "days": [
    {{
      "day": 1,
      "topic": "当天主题",
      "tasks": ["任务1", "任务2"],
      "expected_output": "当天完成后应该达到的结果"
    }}
  ]
}}
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
            temperature=0,
            response_format={"type": "json_object"},
        )

    except (APITimeoutError) as e:
        raise PlannerTimeoutError(f"Timeout error: {str(e)}") from e    
    except (APIConnectionError) as e:
        raise PlannerUpstreamError(f"Connection error: {str(e)}") from e
    except (APIStatusError) as e:
        raise PlannerUpstreamError(f"API status error: {str(e)}") from e


    raw_content = response.choices[0].message.content
    if not raw_content:
        raise PlannerOutputError("No content returned from the LLM.")
    try:
        data = json.loads(raw_content)
    except JSONDecodeError as e:
        raise PlannerOutputError(f"Invalid JSON format: {str(e)}") from e
    try:
        plan = StudyPlan.model_validate(data)
    except ValidationError as e:
        raise PlannerOutputError(f"Validation error: {str(e)}") from e

    if len(plan.days) != request.duration_days:
        raise PlannerOutputError(f"Expected {request.duration_days} days in the plan, but got {len(plan.days)} days.")

    return plan