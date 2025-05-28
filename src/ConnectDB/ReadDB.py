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
def ReadStorageURL(portfolio_id, userID):
    supabase: Client = DBClientCall()

    # 1. portfolio_id로 row 조회
    response = (
        supabase.table("Portfolio")
        .select("portfolio_content, user_id, is_public")
        .eq("portfolio_id", portfolio_id)
        .execute()
    )

    if not response.data:
        return None

    record = response.data[0]
    portfolio_content_url = record["portfolio_content"]
    # 권한 체크 (본인 또는 공개)
    if not (record["user_id"] == int(userID) or record["is_public"] is True):
        return None

    # 2. Storage에서 값 가져오기
    path = urlparse(portfolio_content_url).path
    key = path.split("/public/portfolio-bucket/")[-1]
    response = supabase.storage.from_(BucketCall()).download(key)

    if hasattr(response, "error") and response.error:
        return None

    try:
        content = response.decode("utf-8")
        return content
    except Exception as e:
        return None
