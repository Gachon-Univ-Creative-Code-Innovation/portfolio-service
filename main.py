import os
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.Extractor.READMEFetcher import GetREADMEandImage
from src.Utils.Model import RunModel
from src.Utils.GetJWT import GetDataFromToken, GetTokenFromHeader
from src.ConnectDB.ReadDB import (
    ReadAllPortfolioList,
    ReadDBList,
    ReadStorageURL,
    ReadLikeCount,
    ReadFirstPortfolioID,
    ReadPortfolio,
)
from src.ConnectDB.Upload2DB import (
    SavePortfolioData,
    UpdatePortfolioData,
    LikePortfolio,
    UnlikePortfolio,
    UploadImageToStorage,
    DeletePortfolio,
)


app = FastAPI(title="Portfolio AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 포트폴리오 글과 이미지 생성 API
@app.get("/api/portfolio-service/make")
async def MakeProtfolio(gitURL: str, request: Request):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

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
@app.post("/api/portfolio-service/save")
async def SavePortfolio(
    request: Request,
    title: str,
    content: str,
    is_public: bool,
    isTemp: bool,
    image: str = None,
):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

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
@app.get("/api/portfolio-service/list")
async def GetMyPortfolioList(request: Request, isDesc: bool = True):
    try:
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

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
@app.get("/api/portfolio-service/all")
async def GetAllPortfolioList(request: Request, isDesc: bool = True):
    try:
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")
        print(userID)
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


# 특정 UserID의 포트폴리오 ID를 가져오는 API
@app.get("/api/portfolio-service/user")
async def GetUserPortfolioList(userID: int):
    try:
        portfolioID = ReadFirstPortfolioID(userID)

        return {
            "status": 200,
            "message": "유저 포트폴리오 리스트 가져오기 성공",
            "data": portfolioID,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "유저 포트폴리오 리스트 가져오기 실패",
                "data": None,
            },
        )


# 포트폴리오 상세 페이지를 가져오는 API
@app.get("/api/portfolio-service/detail")
async def GetPortfolioDetail(request: Request, portfolioID: int):
    try:
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")
        content = ReadStorageURL(portfolioID, userID)
        like = ReadLikeCount(portfolioID)
        # title, author, date
        ex = ReadPortfolio(portfolioID)
        if content is None:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "포트폴리오 접근 권한이 없습니다.",
                    "data": None,
                },
            )
        # ex: (title, author, date)
        title = ex[0] if ex else None
        author = ex[1] if ex else None
        date = ex[2].split("T")[0].replace("-", ".") if ex and ex[2] else None
        if date:
            y, m, d = date.split(".")
            date = f"{y}.{m.zfill(2)}.{d.zfill(2)}"
        return {
            "status": 200,
            "message": "포트폴리오 상세 페이지 가져오기 성공",
            "data": {
                "content": content,
                "like_count": like,
                "title": title,
                "author": author,
                "date": date,
            },
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
@app.put("/api/portfolio-service/update")
async def UpdatePortfolio(
    request: Request,
    portfolioID: int,
    title: str,
    content: str,
    isPublic: bool,
    isTemp: bool,
    image: str = None,
):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

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


# 포트폴리오 좋아요 API
@app.post("/api/portfolio-service/like")
async def ToggleLike(request: Request, portfolioID: int):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

        try:
            # 먼저 좋아요 추가 시도
            LikePortfolio(portfolioID, userID)
            return {
                "status": 200,
                "message": "포트폴리오 좋아요 성공",
                "data": {"liked": True},
            }
        except Exception:
            # 이미 좋아요가 있으면 취소 시도
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
                "data": {"liked": False},
            }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": f"포트폴리오 좋아요 토글 실패: {e}",
                "data": None,
            },
        )


# 포트폴리오 삭제 API
@app.delete("/api/portfolio-service/delete")
async def DeletePortfolioAPI(request: Request, portfolioID: int):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

        # DB에서 삭제
        if not DeletePortfolio(portfolioID, userID):
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "포트폴리오 삭제 실패",
                    "data": None,
                },
            )

        return {
            "status": 200,
            "message": "포트폴리오 삭제 성공",
            "data": None,
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": f"포트폴리오 삭제 실패: {e}",
                "data": None,
            },
        )


# 이미지 업로드 API
@app.post("/api/portfolio-service/upload-image")
async def UploadPortfolioImage(
    request: Request,
    title: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        """이 부분은 token 연동 후"""
        accessToken = GetTokenFromHeader(request)
        userID = GetDataFromToken(accessToken, "user_id")

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
@app.get("/api/portfolio-service/health-check")
async def HealthCheck():
    return {"status": 200, "message": "서버 상태 확인", "data": "Working"}
