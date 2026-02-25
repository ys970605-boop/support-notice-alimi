import requests
import json
import sys
from datetime import datetime

import os

# 환경 변수에서 토큰과 ID를 가져옵니다. (GitHub Secrets 설정 필요)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_PAGE_ID", "3129979fd60d80b4b97bd7ad44e2189d")

def post_to_notion(title, category, content=""):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 노션 페이지 구조에 맞춘 데이터 (페이지의 하위 페이지로 생성)
    data = {
        "parent": { "page_id": DATABASE_ID },
        "properties": {
            "title": [
                { "text": { "content": f"[{category}] {title}" } }
            ]
        }
    }
    
    # 페이지 본문에 내용 추가
    if content:
        data["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{ "type": "text", "text": { "content": content } }]
                }
            }
        ]

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"✅ 패치노트 등록 성공: {title}")
    else:
        print(f"❌ 등록 실패 (오류 코드: {response.status_code})")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n[사용법] python3 post_patch.py \"제목\" \"분류\" \"상세내용(선택)\"")
    else:
        title = sys.argv[1]
        category = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        post_to_notion(title, category, content)
