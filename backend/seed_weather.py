import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    print("🚀 Starting Data Injection Sequence...\n")

    # 1. Create a Test Region
    region_payload = {
        "name": "Test Coastal Zone",
        "admin_level": "District",
        "latitude": 19.0760,
        "longitude": 72.8777
    }
    
    print("📍 Creating Region...")
    region_res = requests.post(f"{BASE_URL}/regions", json=region_payload)
    
    if region_res.status_code != 200:
        print(f"❌ Failed to create region: {region_res.text}")
        return
        
    region_id = region_res.json()["id"]
    print(f"✅ Region created with ID: {region_id}\n")

    # 2. Inject 14 Days of Weather Data
    print("⛈️ Injecting 14 days of weather history...")
    base_date = datetime.now() - timedelta(days=14)
    
    for i in range(14):
        current_date = base_date + timedelta(days=i)
        
        # # Creating a "dangerous" weather pattern to trigger a high score
        # weather_payload = {
        #     "region_id": region_id,
        #     "temp": round(random.uniform(35.0, 42.0), 1),      # High heat
        #     "humidity": round(random.uniform(70.0, 95.0), 1),  # High humidity
        #     "rainfall": round(random.uniform(10.0, 50.0), 1),  # Heavy rain
        #     "timestamp": current_date.isoformat()
        # }
        # Creating a "dangerous" weather pattern to trigger a high score
        weather_payload = {
            "region_id": region_id,
            "temp": round(random.uniform(35.0, 42.0), 1),      
            "humidity": round(random.uniform(70.0, 95.0), 1),  
            "rainfall": round(random.uniform(10.0, 50.0), 1),  
            "timestamp": current_date.isoformat(),
            "source": "simulated_test"  # <-- ADD THIS LINE
        }
        
        res = requests.post(f"{BASE_URL}/weather", json=weather_payload)
        if res.status_code == 200:
            print(f"   Day {i+1} injected: Temp {weather_payload['temp']}°C, Rain {weather_payload['rainfall']}mm")
        else:
            print(f"   ❌ Failed to inject Day {i+1}: {res.text}")

    # 3. Trigger the AI Models!
    print("\n🧠 Waking up Neural Networks and calculating risk...")
    risk_res = requests.get(f"{BASE_URL}/risk/{region_id}")
    
    if risk_res.status_code == 200:
        data = risk_res.json()
        print("\n========================================")
        print("🎯 AI RISK ASSESSMENT COMPLETE")
        print("========================================")
        print(f"🌊 Flood Risk:    {data['flood_score']}%")
        print(f"🔥 Heatwave Risk: {data['heatwave_score']}%")
        print("========================================")
    else:
        print(f"❌ ML Inference failed: {risk_res.text}")

if __name__ == "__main__":
    run_test()