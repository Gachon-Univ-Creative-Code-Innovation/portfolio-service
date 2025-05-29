import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

from src.Extractor.READMEFetcher import GetREADMEandImage
from src.Utils.Model import RunModel
from src.ConnectDB.ReadDB import (
    ReadAllPortfolioList,
    ReadDBList,
    ReadStorageURL,
    ReadLikeCount,
)
from src.ConnectDB.Upload2DB import (
    SavePortfolioData,
    UpdatePortfolioData,
    LikePortfolio,
    UnlikePortfolio,
    UploadImageToStorage,
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
    title: str, content: str, is_public: bool, isTemp: bool, image: str = None
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


# 자신의 포트폴리오 리스트를 가져오는 API
@app.get("/api/portfolio/list")
async def GetMyPortfolioList(isDesc: bool = True):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        portfolioList = ReadDBList(userID, isDesc)

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


# 모든 포트폴리오 리스트를 가져오는 API
@app.get("/api/portfolio/all")
async def GetAllPortfolioList(isDesc: bool = True):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312
        portfolioList = ReadAllPortfolioList(userID, isDesc)

        return {
            "status": 200,
            "message": "모든 포트폴리오 리스트 가져오기 성공",
            "data": portfolioList,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "모든 포트폴리오 리스트 가져오기 실패",
                "data": None,
            },
        )


# 포트폴리오 상세 페이지를 가져오는 API
@app.get("/api/portfolio/detail")
async def GetPortfolioDetail(portfolioID):
    try:
        userID = 312
        content = ReadStorageURL(portfolioID, userID)
        like = ReadLikeCount(portfolioID)
        if content is None:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "포트폴리오 접근 권한이 없습니다.",
                    "data": None,
                },
            )
        return {
            "status": 200,
            "message": "포트폴리오 상세 페이지 가져오기 성공",
            "data": {"content": content, "like_count": like},
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": f"포트폴리오 상세 페이지 가져오기 실패: {e}",
                "data": None,
            },
        )


# 포트폴리오 수정하는 API
@app.put("/api/portfolio/update")
async def UpdatePortfolio(
    portfolioID: int,
    title: str,
    content: str,
    isPublic: bool,
    isTemp: bool,
    image: str = None,
):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # DB에 저장하는 코드
        UpdatePortfolioData(
            portfolioID, title, content, userID, isPublic, image, isTemp
        )

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


# 이미지 업로드 API
@app.post("/api/portfolio/upload-image")
async def UploadPortfolioImage(
    title: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        """이 부분은 token 연동 후"""
        # accessToken = GetTokenFromHeader(request)
        # userID = GetDataFromToken(accessToken, "user_id")
        userID = 312

        # 임시 파일로 저장
        tempPath = f"temp_{userID}_{image.filename}"
        with open(tempPath, "wb") as buffer:
            buffer.write(await image.read())

        # Storage에 업로드
        imageURL = UploadImageToStorage(tempPath, title, userID)
        os.remove(tempPath)

        if not imageURL:
            return JSONResponse(
                status_code=400,
                content={"status": 400, "message": "이미지 업로드 실패", "data": None},
            )

        return {
            "status": 200,
            "message": "이미지 업로드 성공",
            "data": {"image_url": imageURL},
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": f"이미지 업로드 실패: {e}",
                "data": None,
            },
        )


# 헬스 체크
@app.get("/api/portfolio/health-check")
async def HealthCheck():
    return {"status": 200, "message": "서버 상태 확인", "data": "Working"}
