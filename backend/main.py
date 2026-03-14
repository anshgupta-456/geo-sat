from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from database import get_db
import models, schemas
from fastapi import Path
import ml_model
app = FastAPI(title="Geo-Intelligent Disaster response API")

@app.get("/")
def health_check(db: Session = Depends(get_db)):
    # root endpoint to check whether the api is connected or not to the database
    try:
        db.execute(text("Select 1"))
        return{
            "status": "success",
            "message": "connected to postgis successfully"
        }
    except Exception as e:
        return{
            "status": "system online",
            "database": f"connection failed:{str(e)}"
        }
# @app.get("/api/regions")
# def get_regions():
#     return{"message":"will return list of regions with geometry bounding boxes"}
@app.post("/api/regions", response_model=schemas.RegionResponse)
def create_region(region: schemas.RegionCreate, db:Session = Depends(get_db)):
    # creating new region in the db
    wkt_point = f"SRID=4326;POINT({region.longitude} {region.latitude})"

    db_region = models.Region(
        name=region.name,
        admin_level=region.admin_level,
        centroid=wkt_point
    )

    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

@app.get("/api/regions")
def get_regions(db: Session = Depends(get_db)):
    regions = db.query(models.Region).all()
    return regions
@app.post("/api/weather", response_model=schemas.WeatherResponse)
def ingest_weather(weather: schemas.WeatherCreate, db: Session = Depends(get_db)):
    db_weather = models.WeatherObservation(**weather.model_dump())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather


@app.get("/api/risk/{region_id}", response_model=schemas.RiskResponse)
def calculate_risk(region_id: int, db: Session = Depends(get_db)):
    # 1. Fetch the last 14 weather records for this region, descending order
    recent_weather = db.query(models.WeatherObservation)\
        .filter(models.WeatherObservation.region_id == region_id)\
        .order_by(desc(models.WeatherObservation.timestamp))\
        .limit(14).all()

    if not recent_weather:
        raise HTTPException(status_code=404, detail="No weather data found for this region")

    # 2. Reverse the list so it flows chronologically (oldest -> newest) for the LSTM
    recent_weather.reverse()

    # Pad if there are less than 14 days of data in the DB
    while len(recent_weather) < 14:
        recent_weather.insert(0, recent_weather[0])

    # 3. Format the data for the ML wrapper, including the timestamp!
    weather_history = [
        {
            "temp": w.temp, 
            "rainfall": w.rainfall, 
            "humidity": w.humidity,
            "timestamp": w.timestamp
        }
        for w in recent_weather
    ]

    # ==========================================
    # 4. RUN DEEP LEARNING INFERENCE
    # ==========================================
    floodrisk = ml_model.predict_flood_risk(weather_history)
    
    # We still use your basic formula for heatwaves using the latest day
    # latest_weather = recent_weather[-1]
    # heatrisk = min((latest_weather.temp/45.0)*100, 100) if latest_weather.temp > 35 else 10.0
    # 🚀 NEW: The Transformer is now online!
    heatrisk = ml_model.predict_heatwave_risk(weather_history)
    # 5. Save the Risk Score
    risk_score = models.RiskScore(
        region_id = region_id,
        flood_score = round(floodrisk, 2),
        heatwave_score = round(heatrisk, 2),
        landslide_score = 0.0,
        earthquake_score = 0.0
    )
    db.add(risk_score)
    db.commit()
    db.refresh(risk_score)
    
    # 6. Generate Alerts
    alerts_created = False
    if risk_score.flood_score >= 80.0:
        flood_alert = models.Alert(
            region_id = region_id,
            risk_type = "flood",
            score = risk_score.flood_score,
            message = f"Urgent: severe flood risk detected({risk_score.flood_score}%) in region {region_id}. Immediate action recommended!"
        )
        db.add(flood_alert)
        alerts_created = True
        
    if risk_score.heatwave_score >= 80.0:
        heatwave_alert = models.Alert(
            region_id = region_id,
            risk_type = "heatwave",
            score = risk_score.heatwave_score,
            message = f"Urgent: severe heatwave risk detected({risk_score.heatwave_score}%) in region {region_id}. Immediate action recommended!"
        )
        db.add(heatwave_alert)
        alerts_created = True
        
    if alerts_created:
        db.commit()
        
    return risk_score

@app.get("/api/alerts/{region_id}", response_model=list[schemas.AlertResponse])
def get_alerts(region_id: int, db: Session = Depends(get_db)):
    # fetches all disaster alerts for a specific region descending order
    alerts = db.query(models.Alert).filter(models.Alert.region_id == region_id).order_by(desc(models.Alert.created_at)).all()
    return alerts

@app.patch("/api/alerts/{alert_id}/send", response_model=schemas.AlertResponse)
def mark_alert_sent(alert_id: int, db: Session = Depends(get_db)):
    # mark the specific disaster alert as sent as previous it was shown false
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.sent = True
    db.commit()
    db.refresh(alert)
    return alert