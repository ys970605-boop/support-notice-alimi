import requests
from datetime import datetime
import time

NOTION_TOKEN = "os.environ.get("NOTION_TOKEN")"
DATABASE_ID = "3129979fd60d81cc8e99cb28f8f8c5e1"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_patch(title, category, version, content, status="✅ 배포 완료"):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "제목": { "title": [{ "text": { "content": title } }] },
            "날짜": { "date": { "start": datetime.now().strftime("%Y-%m-%d") } },
            "분류": { "select": { "name": category } },
            "버전": { "rich_text": [{ "text": { "content": version } }] },
            "상태": { "select": { "name": status } }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": { "rich_text": [{ "text": { "content": "업데이트 상세 내용" } }] }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{ "type": "text", "text": { "content": content } }]
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    patches = [
        ("HWP/HWPX 한글 문서 분석 기능 정식 지원", "🚀 신규 기능", "v2.1.0", "공공기관 및 기업에서 널리 사용되는 아래아한글(HWP, HWPX) 파일에 대한 AI 분석 및 요약 기능이 추가되었습니다."),
        ("AI 응답 속도 최적화 (기존 대비 2배 향상)", "🛠️ 기능 개선", "v2.1.1", "대규모 언어 모델(LLM) 파이프라인 최적화를 통해 답변 속도가 약 50% 단축되었습니다."),
        ("모바일 웹 브라우저 레이아웃 깨짐 현상 수정", "🐛 버그 수정", "v2.1.2", "아이폰 및 안드로이드 환경에서 버튼이 겹쳐 보이던 현상을 수정하였습니다.")
    ]
    for p in patches:
        add_patch(p[0], p[1], p[2], p[3])
        time.sleep(0.5)
    print("🎉 모든 예시 데이터가 노션에 반영되었습니다!")
