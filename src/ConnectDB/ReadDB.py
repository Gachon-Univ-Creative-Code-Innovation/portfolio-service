import json
from src.Utils.DBClient import DBClientCall, BucketCall
from supabase import Client
from urllib.parse import urlparse


# 유저 ID로 대표 이미지와 storage url 가져오기
def ReadDBList(userID, isPublic, isDesc):
    supabase: Client = DBClientCall()

    # SQL 실행
    response = (
        supabase.table("Portfolio")
        .select("title, image, portfolio_content, is_public")
        .eq("user_id", userID)
        .eq("is_public", isPublic)
        .order("created_at", desc=isDesc)
        .execute()
    )

    return response.data


# DB에서 메타데이터 가져오기
def ReadMetaData(url: str, userID: int):
    supabase: Client = DBClientCall()

    # 직접 쿼리
    response = (
        supabase.table("Portfolio")
        .select("user_id, is_public, portfolio_content")
        .eq("portfolio_content", url)
        .execute()
    )

    # 값 없을 때
    if not response.data:
        return None

    record = response.data[0]

    # 권한 확인
    if record["user_id"] == int(userID):
        return json.dumps(record["portfolio_content"], indent=2)
    elif record["is_public"] is True:
        return json.dumps(record["portfolio_content"], indent=2)
    else:
        return None


# 포트폴리오의 좋아요 수 가져오기
def ReadLikeCount(portfolioID: int):
    supabase: Client = DBClientCall()

    response = (
        supabase.table("Portfolio_Like")
        .select("user_id")
        .eq("portfolio_id", portfolioID)
        .execute()
    )

    count = len(response.data)

    return count


# url로 storage에서 값 가져오기
def ReadStorageURL(portfolio_url, userID):
    supabase: Client = DBClientCall()

    url = ReadMetaData(portfolio_url, userID)

    path = urlparse(
        url
    ).path  # e.g. /storage/v1/object/public/portfolio-bucket/portfolio_312_title.txt
    key = path.split("/public/portfolio-bucket/")[-1]

    # Storage에서 값 가져오기
    response = supabase.storage.from_(BucketCall()).download(key)

    # 오류 처리
    if hasattr(response, "error") and response.error:
        print("Storage Read Error")
        return None

    try:
        content = response.decode("utf-8")
        return content
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
