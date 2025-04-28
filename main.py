from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.Extractor.READMEFetcher import GetREADMEandImage
from src.Utils.Model import RunModel


app = FastAPI(title="Portfolio AI API")

# 포트폴리오 글과 이미지 생성 API
@app.post("/api/portfolio/make")
async def MakeProtfolio(gitURL: str):
    try:
        """ 이 부분은 token 연동 후 """
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        content, image = await GetREADMEandImage(userID, gitURL)
        text = RunModel(content)

        return {
            "status": 200,
            "message": "요청에 성공하였습니다.",
            "data": {
                "text": text,
                "image": image
                }
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "포트폴리오 생성 실패", "data": None},
        )