import re
import os
from dotenv import load_dotenv
from groq import Groq


# <think>와 </think> 사이의 내용을 포함하여 모두 제거
def RemoveThink(text):
    try:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    except Exception as e:
        print("None Json")
    finally:
        return text


# 응답에서 내용 JSON 목록을 추출하는 함수
def ExtractJson(text):
    match = re.search(r"{\s*'content'\s*:\s*'(.*?)'\s*}", text, re.DOTALL)
    if match:
        try:
            # 매칭된 'content' 값 반환
            return match.group(1).strip()  # .strip()으로 불필요한 공백 제거
        except Exception as e:
            print("Error parsing content:", e)
            return ""
    raise ValueError("Valid JSON format not found.")


# LLM 호출 함수
def CallLLM(modelName, content, client):
    try:
        chatCompletion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Please write a Korean self-introduction based on the following content. "
                        "The self-introduction should focus on the applicant's professional experiences, skills, and key qualifications, without including unnecessary personal interests or greetings. "
                        "The result should only include the self-introduction with a length of at least 3000 characters,  without any additional explanation.\n"
                        "Please return the self-introduction in this format:\n"
                        "{ 'content': 'return' }\n"
                    ),
                },
                {"role": "user", "content": content},
            ],
            model=modelName,
            temperature=0.2,
        )

        content = chatCompletion.choices[0].message.content
        print(f"\n[{modelName}] Raw Output:\n{content}\n{'-'*50}")

        return ExtractJson(RemoveThink(content))

    except Exception as e:
        print(f"Exception in {modelName}: {e}")
        return None


# Model 실행 함수
def RunModel(content):
    envPath = os.path.join(os.path.dirname(__file__), "../..", ".env")
    load_dotenv(dotenv_path=os.path.abspath(envPath))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    client = Groq(api_key=GROQ_API_KEY)
    response = CallLLM("gemma2-9b-it", content, client)

    return response
