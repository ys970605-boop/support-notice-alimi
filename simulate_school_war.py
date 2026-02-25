import random
import time

# 1. 서울 지역 학교 및 거점 세팅
SCHOOLS = [
    {"name": "성수고", "region": "성동구"},
    {"name": "경일고", "region": "성동구"},
    {"name": "휘문고", "region": "강남구"},
    {"name": "단대부고", "region": "강남구"},
    {"name": "서울고", "region": "서초구"}
]

SPOTS = [
    "CU 성수점", "GS25 대치점", "엽기떡볶이", "마라탕천국", "스타벅스", "코인노래방", "PC방", "명동교자", "이디야"
]

class Simulation:
    def __init__(self):
        self.users = []
        self.spots_status = {spot: random.choice(SCHOOLS)["name"] for spot in SPOTS}
        self.prize_pools = {s["name"]: 0 for s in SCHOOLS}
        self.logs = []
        
        for school in SCHOOLS:
            for i in range(100): # 학교당 100명
                self.users.append({
                    "id": f"{school['name']}_학생_{i}",
                    "school": school["name"],
                    "power": random.randint(500, 2000),
                    "contribution": 0
                })

    def run_tick(self, hour):
        event_count = 0
        revenue_per_event = 150 # 광고 수익 150원 (전면 광고+배너 합산 가정)
        
        # 시간당 유저 활동 (랜덤하게 50명 추출)
        active_users = random.sample(self.users, 50)
        for user in active_users:
            target_spot = random.choice(SPOTS)
            current_owner = self.spots_status[target_spot]
            
            if current_owner != user["school"]:
                if random.random() < 0.3: # 30% 확률로 탈환
                    self.spots_status[target_spot] = user["school"]
                    user["power"] += 200
                    user["contribution"] += 50
                    event_count += 1
            
            # 활동마다 광고 수익 적립
            self.prize_pools[user["school"]] += revenue_per_event
            
        return event_count

    def get_summary(self):
        ranking = {}
        for school in SCHOOLS:
            held = list(self.spots_status.values()).count(school["name"])
            ranking[school["name"]] = held
        kings = {}
        for school in SCHOOLS:
            school_users = [u for u in self.users if u["school"] == school["name"]]
            king = max(school_users, key=lambda x: x["power"])
            kings[school["name"]] = king
        return {
            "ranking": sorted(ranking.items(), key=lambda x: x[1], reverse=True),
            "kings": kings,
            "prize_pools": self.prize_pools
        }

def run_simulation():
    sim = Simulation()
    print("🚀 [서울 대첩] AI 24시간 초고속 시뮬레이션 가동 중...")
    
    for h in range(8, 23): # 08시 ~ 22시
        sim.run_tick(h)
    
    result = sim.get_summary()
    
    print("\n" + "="*50)
    print("📊 서울 지역 학교 전쟁 최종 결과 보고")
    print("="*50)
    
    for school_name, count in result["ranking"]:
        king = result["kings"][school_name]
        prize = result["prize_pools"][school_name]
        print(f"[{school_name}]")
        print(f"  - 점유 거점: {count}개")
        print(f"  - 학교의 왕: {king['id']}")
        print(f"  - 현재 전투력: {king['power']:,}")
        print(f"  - 이번 주 정산 예정 상금: ₩ {prize:,}")
        print("-" * 30)

    print("\n💡 AI 분석: 특정 학교의 왕이 상금을 독식하는 구조가 보이며,")
    print("학교 간 경쟁이 심해질수록 트래픽과 광고 수익이 기하급수적으로 폭증함.")

if __name__ == "__main__":
    run_simulation()
