from src.Utils.DBClient import DBClientCall, BucketCall
from supabase import Client
from urllib.parse import urlparse


# 유저 ID로 대표 이미지와 storage url 가져오기
def ReadDBList(userID, isDesc):
    supabase: Client = DBClientCall()

    # SQL 실행
    response = (
        supabase.table("portfolio_with_like")
        .select("*")
        .eq("user_id", userID)
        .order("created_at", desc=isDesc)
        .execute()
    )

    return response.data


# 전체 포트폴리오 리스트를 가져오기
def ReadAllPortfolioList(userID, isDesc):
    supabase: Client = DBClientCall()

    # SQL 실행
    response = (
        supabase.table("portfolio_with_like")
        .select("*")
        .eq("is_public", True)
        .neq("user_id", userID)
        .order("created_at", desc=isDesc)
        .execute()
    )

    return response.data


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


# ID로 storage에서 값 가져오기
def ReadStorageURL(portfolio_id, userID):
    supabase: Client = DBClientCall()

    response = (
        supabase.table("Portfolio")
        .select("portfolio_content, user_id, is_public")
        .eq("portfolio_id", portfolio_id)
        .execute()
    )

    if not response.data:
        return None

    record = response.data[0]
    contentURL = record["portfolio_content"]
    # 권한 체크 (본인 또는 공개)
    if not (record["user_id"] == int(userID) or record["is_public"] is True):
        return None

    path = urlparse(contentURL).path
    key = path.split("/public/portfolio-bucket/")[-1]
    response = supabase.storage.from_(BucketCall()).download(key)

    if hasattr(response, "error") and response.error:
        return None

    try:
        content = response.decode("utf-8")
        return content
    except Exception as e:
        return None
