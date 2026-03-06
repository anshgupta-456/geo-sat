from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from database import get_db
import models, schemas
from fastapi import Path

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
    # calculate and return the risk score for the give region
    latest_weather = db.query(models.WeatherObservation).filter(models.WeatherObservation.region_id == region_id).order_by(desc(models.WeatherObservation.timestamp)).first()

    if not latest_weather:
        raise HTTPException(status_code=404, detail="No weather data found for this region")
    
    # algo
    #heatwave score: if temp>35 max score is 100
    heat_score = min((latest_weather.temp/45.0)*100, 100) if latest_weather.temp>35 else 10.0

    # flood score: if rainfall is massive. Max score is 100
    flood_score = min((latest_weather.rainfall/150)*100,100) if latest_weather.rainfall>50 else 10.0

    risk_score = models.RiskScore(
        region_id=region_id,
        flood_score=round(flood_score,2),
        heatwave_score=round(heat_score,2),
        landslide_score=0.0, #placeholder
        earthquake_score=0.0 #placeholder
    )
    db.add(risk_score)
    db.commit()
    db.refresh(risk_score)
    return risk_score