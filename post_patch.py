import requests
import json
import sys
import os
from datetime import datetime

# 설정
NOTION_TOKEN = "os.environ.get("NOTION_TOKEN")"
DATABASE_ID = "3129979fd60d81cc8e99cb28f8f8c5e1"

def post_patch_note(title, category, version, content=""):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 노션 데이터베이스 구조에 맞춘 데이터
    data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "제목": {
                "title": [ { "text": { "content": title } } ]
            },
            "분류": {
                "select": { "name": category }
            },
            "버전": {
                "rich_text": [ { "text": { "content": version } } ]
            },
            "날짜": {
                "date": { "start": datetime.now().strftime("%Y-%m-%d") }
            },
            "상태": {
                "select": { "name": "✅ 배포 완료" }
            }
        }
    }
    
    # 본문 내용 추가 (Children)
    if content:
        data["children"] = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": { "rich_text": [{ "text": { "content": "업데이트 내용" } }] }
            },
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
        print(f"✅ DocsHunt AI 패치노트 등록 성공: {title} ({version})")
        print(f"🔗 링크: https://www.notion.so/{response.json().get('id').replace('-', '')}")
    else:
        print(f"❌ 등록 실패 (상태 코드: {response.status_code})")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("\n[사용법] python3 post_patch.py \"제목\" \"분류\" \"버전\" \"내용(선택)\"")
        print("[분류 예시] 🚀 신규 기능, 🛠️ 기능 개선, 🐛 버그 수정, ⚙️ 시스템 점검")
    else:
        title = sys.argv[1]
        category = sys.argv[2]
        version = sys.argv[3]
        content = sys.argv[4] if len(sys.argv) > 4 else ""
        post_patch_note(title, category, version, content)
