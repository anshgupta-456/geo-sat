from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
from database import Base

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    admin_level = Column(String(50))
    centroid = Column(Geometry('Point', srid=4326)) #srid 4326 is the standard Gps coordinate system for longitude and latitude
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))

    weather = relationship("WeatherObservation", back_populates="region")
    alerts = relationship("Alert", back_populates="region")

class WeatherObservation(Base):
    __tablename__="weather_observation"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    source = Column(String(100))
    rainfall = Column(Float)
    temp = Column(Float)
    humidity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    region = relationship("Region", back_populates="weather")

class RiverLevel(Base):
    __tablename__ = "river_levels"

    id = Column(Integer, primary_key=True, index = True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    water_level = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    flood_score = Column(Float)
    landslide_score = Column(Float)
    heatwave_score = Column(Float)
    earthquake_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__="alerts"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    risk_type = Column(String(50))
    score = Column(Float)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
    region = relationship("Region", back_populates="alerts")

