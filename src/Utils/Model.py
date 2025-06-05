import re
import os
import requests
from dotenv import load_dotenv


# <think>와 </think> 사이의 내용을 포함하여 모두 제거
def RemoveThink(text):
    try:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    except Exception as e:
        print("None Json")
        return text


# 응답에서 내용 JSON 목록을 추출하는 함수
def ExtractJson(text):
    return RemoveThink(text).strip()


# LLM 호출 함수 (vLLM 서버용)
def CallLLM(modelName, content, vllm_url):
    try:
        if not vllm_url:
            raise ValueError("VLLM_SERVER_URL 환경변수가 설정되지 않았습니다.")
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "model": modelName,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Please write a Korean self-introduction based on the following content. "
                        "The self-introduction should focus on the applicant's professional experiences, skills, and key qualifications, without including unnecessary personal interests or greetings. "
                        "Do not repeat similar expressions. Stop writing when the key information is sufficiently delivered. "
                        "Use a clear and professional tone suitable for a written portfolio. Avoid overly emotional language or exaggerated claims. "
                        "Organize the text into coherent paragraphs covering work experience, core skills, strengths, and future goals. "
                        "Keep technical terms and project names exactly as given. "
                        "Output should be plain Korean text without markdown, quotation marks, or formatting."
                    ),
                },
                {"role": "user", "content": content},
            ],
        }

        response = requests.post(f"{vllm_url}", json=payload, headers=headers)
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]

        return ExtractJson(RemoveThink(content))

    except Exception as e:
        return None


# 실행 함수
def RunModel(content):
    envPath = os.path.join(os.path.dirname(__file__), "../..", ".env")
    load_dotenv(dotenv_path=os.path.abspath(envPath))

    VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL")
    modelName = "google/gemma-3-4b-it"

    return CallLLM(modelName, content, VLLM_SERVER_URL)
