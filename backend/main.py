from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import models, schemas


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