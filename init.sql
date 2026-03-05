create Extension if not exists postgis;

create Table regions(
    id serial Primary key,
    name varchar(255) not null,
    admin_level varchar(50),
    centroid GEOMETRY(Point, 4326),
    geometry GEOMETRY(MultiPolygon, 4326)
);

create table weather_observations(
    id serial primary key,
    region_id int REFERENCES regions(id),
    source varchar(100),
    rainfall float,
    temp float,
    humidity float,
    timestamp TIMESTAMP Default CURRENT_TIMESTAMP
);

create table risk_scores(
    id serial primary key,
    region_id int REFERENCES regions(id),
    flood_score float,
    landslide_score float,
    heatwave_score float,
    earthquake_score float,
    timestamp TIMESTAMP default CURRENT_TIMESTAMP
);

 create table alerts(
    id serial primary key,
    region_id int REFERENCES regions(id),
    risk_type varchar(50),
    score float,
    message text,
    created_at timestamp default CURRENT_TIMESTAMP,
    sent boolean default false
);
