import requests

NOTION_TOKEN = "os.environ.get("NOTION_TOKEN")"
PARENT_PAGE_ID = "3129979fd60d80b4b97bd7ad44e2189d"

def create_patch_note_db():
    url = "https://api.notion.com/v1/databases"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": { "type": "page_id", "page_id": PARENT_PAGE_ID },
        "title": [
            { "type": "text", "text": { "content": "📦 독스헌트 AI 공식 패치노트" } }
        ],
        "properties": {
            "제목": { "title": {} },
            "날짜": { "date": {} },
            "분류": {
                "select": {
                    "options": [
                        { "name": "🚀 신규 기능", "color": "blue" },
                        { "name": "🛠️ 기능 개선", "color": "green" },
                        { "name": "🐛 버그 수정", "color": "red" },
                        { "name": "⚙️ 시스템 점검", "color": "gray" }
                    ]
                }
            },
            "버전": { "rich_text": {} },
            "상태": {
                "select": {
                    "options": [
                        { "name": "📝 작성 중", "color": "default" },
                        { "name": "✅ 배포 완료", "color": "green" },
                        { "name": "🚀 업데이트 예고", "color": "purple" }
                    ]
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        db_id = response.json().get("id")
        print(f"✅ 독스헌트 AI 패치노트 데이터베이스 생성 성공!")
        print(f"📌 신규 Database ID: {db_id}")
        return db_id
    else:
        print(f"❌ 생성 실패: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    create_patch_note_db()
