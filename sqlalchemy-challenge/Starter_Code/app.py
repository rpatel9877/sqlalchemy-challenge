# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# # reflect an existing database into a new model
Base = automap_base()


# # reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# # Create our session (link) from Python to the DB
session = Session(engine)

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return """
    Welcome to the Climate Analysis API!<br/>
    Available Routes:<br/>
    /api/v1.0/precipitation<br/>
    /api/v1.0/stations<br/>
    /api/v1.0/tobs<br/>
    /api/v1.0/temp/start/end
    """


# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = (
        session.query(measurement.date, measurement.prcp)
        .filter(measurement.date >= prev_year)
        .all()
    )
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


# Stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


# Monthly Temperature
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = (
        session.query(measurement.tobs)
        .filter(measurement.station == "USC00519281")
        .filter(measurement.date >= prev_year)
        .all()
    )
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


# Statistics
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs),
    ]

    if not end:
        results = session.query(*sel).filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = (
        session.query(*sel)
        .filter(measurement.date >= start)
        .filter(measurement.date <= end)
        .all()
    )
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
