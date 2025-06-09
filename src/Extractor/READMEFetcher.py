import requests
from urllib.parse import urlparse
import base64
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import traceback


# GitHub API를 사용하여 README.md 파일을 가져오는 함수
# Readme 앞부분 읽음
def GetREADME(repoURL, gitToken=None):
    url = urlparse(repoURL)
    path = url.path.strip("/").split("/")
    if len(path) >= 2:
        owner, repo = path[0], path[1]
    else:
        print("Invalid GitHub URL.")
        return None

    apiURL = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if gitToken:
        headers = {"Authorization": f"Bearer {gitToken}"} if gitToken else {}

    response = requests.get(apiURL, headers=headers)
    if response.status_code == 200:
        return base64.b64decode(response.json()["content"]).decode("utf-8")[:1000]

    return None


# Github 서비스에서 README DB 정보 가져오는 코드
# Readme 앞부분과 이미지 return
async def FetchREADME(userID: int, gitURL: str, authorization_header: str = None):
    try:
        headers = {"accept": "application/json"}
        if authorization_header:
            headers["Authorization"] = authorization_header
        params = {"userID": str(userID), "gitURL": gitURL}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://a6b22e375302341608e5cefe10095821-1897121300.ap-northeast-2.elb.amazonaws.com:8000/api/github-service/db/readme",
                params=params,
                headers=headers,
            )
        if response.status_code == 200:
            return (
                response.json()["data"]["meta_data"],
                response.json()["data"]["img_url"],
            )
        else:
            return None
    except Exception as e:
        traceback.print_exc()
        return None


# 두 글의 유사도 확인
def CheckSimilarity(text1, text2, threshold=0.7):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])

    cosineSim = cosine_similarity(tfidf[0], tfidf[1])

    return cosineSim[0][0] >= threshold


# 글 정규화 (html, markdown, 불필요한 공백 제거)
def NormalizationText(text):
    if text is None:
        return None
    textHTML = re.sub(r"<.*?>", "", text)
    textMarkdown = re.sub(r"(\*\*|\*|__|_|\#|\`|[!\[\]\(\)])", "", textHTML)
    resultText = re.sub(r"\n\n+", "\n", textMarkdown)

    return resultText


# README 내용과 이미지를 가져오는 함수
async def GetREADMEandImage(userID, gitURL, request=None):
    # DB README 내용 가져오기
    try:
        authorization_header = request.headers.get("Authorization") if request else None
        fetch_result = await FetchREADME(userID, gitURL, authorization_header)
        if fetch_result is not None:
            DBContent, imgURL = fetch_result
            DBContent = NormalizationText(DBContent)
        else:
            DBContent = None
            imgURL = None
    except Exception as e:
        DBContent = None
        imgURL = None

    # 웹에서 README 내용 가져오기
    WebContent = GetREADME(gitURL)
    WebContent = NormalizationText(WebContent)

    # 없는 값일 경우
    if DBContent is None:
        return WebContent, imgURL

    if WebContent is None:
        return DBContent, imgURL

    # 유사도 확인
    if CheckSimilarity(DBContent, WebContent):
        return DBContent, imgURL
    else:
        return (
            (WebContent + "\n" + DBContent)
            if WebContent and DBContent
            else (WebContent or DBContent)
        ), imgURL
