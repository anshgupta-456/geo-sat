from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

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
@app.get("/api/regions")
def get_regions():
    return{"message":"will return list of regions with geometry bounding boxes"}