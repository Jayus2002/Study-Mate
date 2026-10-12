import json
from json import JSONDecodeError
from pydantic import ValidationError
import os
from dotenv import load_dotenv
from openai import (
    APIconnectionError,
    APIstatusError,
    APItimeoutError,
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

load_dotenv()
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")

if not api_key:
    raise ValueError("LLM_API_KEY is not set in the environment variables.")
if not base_url:
    raise ValueError("LLM_BASE_URL is not set in the environment variables.")
if not model:
    raise ValueError("LLM_MODEL is not set in the environment variables.")

client = OpenAI(api_key=api_key, base_url=base_url,
                timeout=20, max_retries=0
                )


def generate_plan(request: PlanRequest,client=None) -> StudyPlan:
    client = client or OpenAI(api_key=api_key, base_url=base_url, timeout=20, max_retries=0)
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
      "topics": "当天主题",
      "tasks": ["任务1", "任务2"],
      "expected_output": "当天完成后应该达到的结果"
    }}
  ]
}}
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=build_messages(request),
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except (APIconnectionError) as e:
        raise PlannerUpstreamError(f"Connection error: {str(e)}")
    except (APIstatusError) as e:
        raise PlannerUpstreamError(f"API status error: {str(e)}")
    except (APItimeoutError) as e:
        raise PlannerTimeoutError(f"Timeout error: {str(e)}")

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise PlannerOutputError("No content returned from the LLM.")
    try:
        data = json.loads(raw_content)
    except JSONDecodeError as e:
        raise PlannerOutputError(f"Invalid JSON format: {str(e)}")
    
    # response = client.chat.completions.create(
    #     model=model,
    #     messages=[
    #         {"role": "system", "content": "你是一个严谨的学习规划 Agent。"},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.3,
    #     response_format={"type": "json_object"},
    # )
    # content = response.choices[0].message.content
    # if not content:
    #     raise ValueError("No content returned from the LLM.")
    
    plan = StudyPlan.model_validate_json(content)

    if len(plan.days) != request.duration_days:
        raise ValueError(f"Expected {request.duration_days} days in the plan, but got {len(plan.days)}.")
    return plan