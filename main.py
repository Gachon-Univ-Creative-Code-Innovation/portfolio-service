from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.Extractor.READMEFetcher import GetREADMEandImage
from src.Utils.Model import RunModel
from src.ConnectDB.ReadDB import ReadDBList, ReadStorageURL, ReadLikeCount
from src.ConnectDB.Upload2DB import (
    SavePortfolioData,
    UpdatePortfolioData,
    LikePortfolio,
    UnlikePortfolio,
)


app = FastAPI(title="Portfolio AI API")


# 포트폴리오 글과 이미지 생성 API
@app.get("/api/portfolio/make")
async def MakeProtfolio(gitURL: str):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        content, image = await GetREADMEandImage(userID, gitURL)
        text = RunModel(content)

        return {
            "status": 200,
            "message": "요청에 성공하였습니다.",
            "data": {"text": text, "image": image},
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "포트폴리오 생성 실패", "data": None},
        )


# 쓴 글을 저장하는 API
@app.post("/api/portfolio/save")
async def SavePortfolio(
    title: str, content: str, is_public: bool, image: str, isTemp: bool
):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # DB에 저장하는 코드
        SavePortfolioData(title, content, userID, is_public, image, isTemp)

        return {
            "status": 200,
            "message": "포트폴리오 저장 성공",
            "data": None,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "포트폴리오 저장 실패", "data": None},
        )


# 포트폴리오 리스트를 가져오는 API
@app.get("/api/portfolio/list")
async def GetPortfolioList(is_public: bool, isDesc: bool = True):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        portfolioList = ReadDBList(userID, is_public, isDesc)

        return {
            "status": 200,
            "message": "포트폴리오 리스트 가져오기 성공",
            "data": portfolioList,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "포트폴리오 리스트 가져오기 실패",
                "data": None,
            },
        )


# 포트폴리오 상세 페이지를 가져오는 API
@app.get("/api/portfolio/detail")
async def GetPortfolioDetail(portfolioID):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        portfolio = ReadStorageURL(portfolioID, userID)
        like = ReadLikeCount(portfolioID)
        portfolio[-1]["like_count"] = like

        return {
            "status": 200,
            "message": "포트폴리오 상세 페이지 가져오기 성공",
            "data": portfolio,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "포트폴리오 접근 권한이 없습니다.",
                "data": None,
            },
        )


# 포트폴리오 수정하는 API
@app.put("/api/portfolio/update")
async def UpdatePortfolio(
    portfolioID: int, title: str, content: str, isPublic: bool, image: str
):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # DB에 저장하는 코드
        UpdatePortfolioData(portfolioID, title, content, userID, isPublic, image)

        return {
            "status": 200,
            "message": "포트폴리오 수정 성공",
            "data": None,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "포트폴리오 수정 실패", "data": None},
        )


# 포트폴리오의 좋아요 누르는 API
@app.post("/api/portfolio/like")
async def Like(portfolioID: int):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # 포트폴리오에 좋아요 추가하기
        LikePortfolio(portfolioID, userID)

        return {
            "status": 200,
            "message": "포트폴리오 좋아요 성공",
            "data": None,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "포트폴리오 좋아요 실패",
                "data": None,
            },
        )


# 포트폴리오의 좋아요 취소하는 API
@app.delete("/api/portfolio/unlike")
async def Unlike(portfolioID: int):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # 포트폴리오에 좋아요 취소하기
        if not UnlikePortfolio(portfolioID, userID):
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "포트폴리오 좋아요 취소 실패",
                    "data": None,
                },
            )

        return {
            "status": 200,
            "message": "포트폴리오 좋아요 취소 성공",
            "data": None,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "포트폴리오 좋아요 취소 실패",
                "data": None,
            },
        )


# 헬스 체크
@app.get("/api/portfolio/health-check")
async def HealthCheck():
    return {"status": 200, "message": "서버 상태 확인", "data": "Working"}
