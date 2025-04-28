import requests
from urllib.parse import urlparse
import base64
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


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
async def FetchREADME(userID: int, gitURL: str):
    try:
        params = {"userID": userID, "gitURL": gitURL}
        async with httpx.AsyncClient() as client:
            # 주소값이 변환될 수도 있음
            response = await client.get(f"http://localhost:8000/api/career/db/readme", params=params)

        if response.status_code == 200:
            return response.json()["data"][0]["result"]["meta_data"], response.json()["data"][0]["img_url"]
        else:
            # 에러 메시지 로깅 등 가능
            return None
    except Exception as e:
        return None
    
# 두 글의 유사도 확인
def check_similarity(text1, text2, threshold=0.7):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    
    cosineSim = cosine_similarity(tfidf[0], tfidf[1])
    
    return cosineSim[0][0] >= threshold

# 글 정규화 (html, markdown, 불필요한 공백 제거)
def NormalizationText(text):
    textHTML = re.sub(r'<.*?>', '', text)
    textMarkdown = re.sub(r'(\*\*|\*|__|_|\#|\`|[!\[\]\(\)])', '', textHTML)
    resultText = re.sub(r'\n\n+', '\n', textMarkdown)
    
    return resultText
    
# README 내용과 이미지를 가져오는 함수
async def GetREADMEandImage(userID, gitURL):
    # DB README 내용 가져오기
    try:
        DBContent, imgURL = await FetchREADME(userID, gitURL)
        DBContent = NormalizationText(DBContent)
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
    if check_similarity(DBContent, WebContent):
        return DBContent, imgURL
    else:
        return WebContent +"\n"+ DBContent, imgURL