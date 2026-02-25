import requests
import json
import os
from datetime import datetime

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DB_ID", "3129979fd60d81cc8e99cb28f8f8c5e1")

def fetch_notion_patches():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "sorts": [ { "property": "날짜", "direction": "descending" } ],
        "page_size": 20
    }
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        return []

    results = res.json().get("results", [])
    patches = []
    
    for page in results:
        props = page.get("properties", {})
        
        # 초안전 데이터 추출기
        def safe_get(p_name, p_type):
            prop = props.get(p_name, {})
            if not prop: return ""
            
            if p_type == "title":
                items = prop.get("title", [])
                return items[0].get("plain_text", "") if items else ""
            if p_type == "date":
                return (prop.get("date") or {}).get("start", "")
            if p_type == "select":
                return (prop.get("select") or {}).get("name", "기타")
            if p_type == "rich_text":
                items = prop.get("rich_text", [])
                return items[0].get("plain_text", "") if items else ""
            return ""

        title = safe_get("업데이트명", "title")
        date = safe_get("날짜", "date")
        category = safe_get("분류", "select")
        version = safe_get("버전", "rich_text")
        status = safe_get("상태", "select")
        
        # '배포 완료' 상태이거나 상태가 없으면 추가
        if "배포" in status or status == "" or "✅" in status:
            patches.append({
                "id": page.get("id"),
                "title": title,
                "date": date,
                "category": category,
                "version": version or "-",
                "url": f"https://www.notion.so/{page.get('id').replace('-', '')}"
            })
            
    return patches

if __name__ == "__main__":
    print("🔄 노션 최신 패치노트 로드...")
    data = fetch_notion_patches()
    output = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patches": data
    }
    with open("patches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ patches.json 생성 성공! (총 {len(data)}건)")
