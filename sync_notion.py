import json
import requests
import time
from datetime import datetime

import os

# 설정 (GitHub Secrets에 NOTION_TOKEN을 등록해야 합니다.)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
PAGE_ID = os.environ.get("NOTION_PAGE_ID", "3129979fd60d80b4b97bd7ad44e2189d")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_existing_pages():
    """이미 등록된 페이지 제목들을 가져와 중복 방지"""
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: return set()
        
        results = response.json().get("results", [])
        existing_titles = set()
        for block in results:
            if block['type'] == 'child_page':
                existing_titles.add(block['child_page']['title'])
        return existing_titles
    except:
        return set()

def sync():
    with open("notices.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    notices = data.get("notices", [])[:10] # 일단 상위 10개만 테스트
    existing_titles = get_existing_pages()
    
    print(f"🔄 노션 동기화 시작: {PAGE_ID}")
    
    success_count = 0
    for n in notices:
        title = f"[{n['source']}] {n['title']}"
        if title in existing_titles:
            continue
            
        payload = {
            "parent": { "page_id": PAGE_ID },
            "properties": {
                "title": [ { "text": { "content": title } } ]
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{ "type": "text", "text": { "content": f"공고일: {n.get('regDate', '-')}\n마감일: {n.get('deadline', '-')}\n링크: {n['url']}" } }]
                    }
                }
            ]
        }

        res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
        if res.status_code == 200:
            success_count += 1
            print(f"✅ 등록: {title}")
        
        time.sleep(0.5)

    print(f"🎉 완료! 새롭게 등록된 공고: {success_count}건")

if __name__ == "__main__":
    sync()
