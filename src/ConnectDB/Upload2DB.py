from src.Utils.DBClient import DBClientCall, BucketCall
from datetime import datetime
import tempfile
from unidecode import unidecode
import re


# portfolio_id 가져오기
def GetNextPortfolioID():
    supabase = DBClientCall()

    response = (
        supabase.table("Portfolio")
        .select("portfolio_id")
        .order("portfolio_id", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]["portfolio_id"] + 1

    return 1


# DB에 해당 내용 저장
def SaveDBData(userID, title, content, isPublic, image, isTemp):
    supabase = DBClientCall()

    portfolioContent = SaveStorage(content, title, userID)
    portfolioID = GetNextPortfolioID()

    data = {
        "portfolio_id": portfolioID,
        "user_id": userID,
        "title": title,
        "portfolio_content": portfolioContent,
        "image": image or "",
        "is_public": isPublic,
        "is_temp": isTemp,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    supabase.table("Portfolio").insert(data).execute()


# Storage에 저장하는 코드
def SaveStorage(content, title, userID):
    supabase = DBClientCall()
    bucketName = BucketCall()

    title = unidecode(title)
    re.sub(r"[^a-zA-Z0-9_\-\.]", "_", title)
    fileName = f"portfolio_{userID}_{title}.txt"

    # Storage에 저장
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", mode="w", encoding="utf-8"
    ) as temp_file:
        temp_file.write(content)
        tempPath = temp_file.name

    response = supabase.storage.from_(bucketName).upload(
        path=fileName,
        file=tempPath,
        file_options={"contentType": "text/plain", "upsert": "True"},
    )

    # 오류 처리
    if hasattr(response, "error") and response.error:
        print("Storage Save Error")
        return None

    # Bucket 접근 URL return
    return supabase.storage.from_(bucketName).get_public_url(fileName)


# 통합적 저장 코드
def SavePortfolioData(title, content, userID, isPublic, image):
    try:
        SaveDBData(userID, title, content, isPublic, image)
    except Exception as e:
        print(f"Error saving portfolio data: {e}")


# DB 내용 수정
def UpdateDBData(portfolioID, userID, title, content, isPublic, image, isTemp):
    supabase = DBClientCall()

    portfolioContent = UpdateStorage(content, title, userID)

    data = {
        "title": title,
        "portfolio_content": portfolioContent,
        "image": image or "",
        "is_public": isPublic,
        "is_temp": isTemp,
        "updated_at": datetime.utcnow().isoformat(),
    }

    supabase.table("Portfolio").update(data).eq("portfolio_id", portfolioID).execute()


# Storage 내용 수정 (기존 파일 덮어쓰기)
def UpdateStorage(content, title, userID):
    supabase = DBClientCall()
    bucketName = BucketCall()

    title = unidecode(title)
    re.sub(r"[^a-zA-Z0-9_\-\.]", "_", title)
    fileName = f"portfolio_{userID}_{title}.txt"

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", mode="w", encoding="utf-8"
    ) as temp_file:
        temp_file.write(content)
        tempPath = temp_file.name

    response = supabase.storage.from_(bucketName).upload(
        path=fileName,
        file=tempPath,
        file_options={"contentType": "text/plain", "upsert": "True"},
    )

    if hasattr(response, "error") and response.error:
        print("Storage Update Error")
        return None

    return supabase.storage.from_(bucketName).get_public_url(fileName)


# 통합 업데이트 함수
def UpdatePortfolioData(portfolioID, title, content, userID, isPublic, image):
    try:
        UpdateDBData(portfolioID, userID, title, content, isPublic, image, isTemp=False)
    except Exception as e:
        print(f"Error updating portfolio data: {e}")


# 포트폴리오의 좋아요 하기
def LikePortfolio(portfolioID: int, userID: int):
    supabase = DBClientCall()

    # 포트폴리오에 좋아요 추가하기
    data = {
        "portfolio_id": portfolioID,
        "user_id": userID,
    }
    supabase.table("Portfolio_Like").insert(data).execute()


# 포트폴리오의 좋아요 취소하기
def UnlikePortfolio(portfolioID: int, userID: int):
    supabase = DBClientCall()

    try:
        response = (
            supabase.table("Portfolio_Like")
            .delete()
            .eq("portfolio_id", portfolioID)
            .eq("user_id", userID)
            .execute()
        )

        # Supabase Python client는 `data` 필드에 삭제된 행의 정보가 담김
        if not response.data:
            return False

        return True

    except Exception as e:
        return {"message": f"서버 오류: {str(e)}", "status": "error"}
