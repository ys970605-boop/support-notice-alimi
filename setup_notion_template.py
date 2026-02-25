import requests
import json
import time
from datetime import datetime

NOTION_TOKEN = "os.environ.get("NOTION_TOKEN")"
PAGE_ID = "3129979fd60d80b4b97bd7ad44e2189d"
DATABASE_ID = "3129979fd60d81cc8e99cb28f8f8c5e1"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def clean_page():
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        blocks = res.json().get("results", [])
        for block in blocks:
            # 신규 데이터베이스는 유지 (child_database 타입 체크)
            if block['type'] == 'child_database':
                continue
            requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)
            time.sleep(0.1)
    print("🧹 페이지 청소 완료!")

def setup_dashboard():
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    desc = ("🚀 DocsHunt AI 공식 패치노트 관리 시스템\n"
            "이곳은 독스헌트 AI의 모든 업데이트 내역을 기록하고 관리하는 공간입니다. "
            "아래 데이터베이스에 기록된 내용은 서비스 내 '소식' 탭과 연동될 수 있습니다.")
    data = {
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{ "type": "text", "text": { "content": desc } }],
                    "icon": { "type": "emoji", "emoji": "📦" },
                    "color": "blue_background"
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{ "type": "text", "text": { "content": "📌 관리 가이드" } }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{ "type": "text", "text": { "content": "새 패치 등록: 아래 표에서 [새로 만들기] 버튼 클릭" } }]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    }
    requests.patch(url, headers=headers, json=data)
    print("✨ 대시보드 틀 구성 완료!")

def add_example_patch():
    """실제 사용자가 복사해서 쓸만한 고품질 예시 데이터 추가"""
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "제목": { "title": [{ "text": { "content": "PDF 자동 요약 기능 베타 오픈" } }] },
            "날짜": { "date": { "start": datetime.now().strftime("%Y-%m-%d") } },
            "분류": { "select": { "name": "🚀 신규 기능" } },
            "버전": { "rich_text": [{ "text": { "content": "v1.5.0" } }] },
            "상태": { "select": { "name": "✅ 배포 완료" } }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": { "rich_text": [{ "text": { "content": "업데이트 상세" } }] }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{ "type": "text", "text": { "content": "사용자가 업로드한 PDF 파일의 핵심 내용을 AI가 3줄로 요약해주는 기능이 추가되었습니다. 이제 긴 문서를 읽지 않아도 빠르게 파악이 가능합니다." } }]
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=payload)
    print("📝 예시 패치노트 등록 완료!")

if __name__ == "__main__":
    clean_page()
    setup_dashboard()
    add_example_patch()
