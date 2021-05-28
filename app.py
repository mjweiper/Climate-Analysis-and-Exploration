import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#DATABASE SETUP
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#refelect the tables
Base.prepare(engine, reflect=True)

#save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#FLASK SETUP
app = Flask(__name__)

#flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    """Last 12 Months of Precipitation Data"""
    last_year = dt.datetime(2016, 8, 23)
    results = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date > last_year).all()
    
    session.close()

    #Create a dictionary from the row data and append to a list
    prcp_data = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = prcp.date
        prcp_dict["Precipitation"] = prcp.prcp
        prcp_data.append(prcp.dict)
    
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    """Stations in the Dataset"""
    results2 = session.query(Station.station, Station.name).\
                order_by(Station.station).all()
    stations = list(np.ravel(results2))

    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs<br/>")
def tobs():

    session = Session(engine)
    """Return a list of Tobs for most active station for the last year"""
    last_year = dt.datetime(2016, 8, 23)
    results3 = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').filter(Measurement.date > last_year).all()

    session.close()

    #Create a dictionary from the row data and append to a list
    tobs_data = []
    for tobs in results3:
        tobs_dict = {}
        tobs_dict["Date"] = tobs.date
        tobs_dict["Tobs"] = tobs.tobs
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start><br/>")
def start(start):
    
    session = Session(engine)
    """Return a list of the min. temp, the avg temp, and the max temp for a given start date"""
    start_time = dt.datetime.strptime(start, '%Y-%m-%d')
    results4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).all()
    
    session.close()

    #When given the start only, calculate TMIN, TAVG, TMAX for all dates greater than and equal to the start date
    list1 = []
    for tobs in results4:
        results_dict1 = {}
        results_dict1["StartDate"] = start_time
        results_dict1["TMIN"] = tobs[0]
        results_dict1["TAVG"] = tobs[1]
        results_dict1["TMAX"] = tobs[2]
        list1.append(results_dict1)

    return jsonify(list1)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)
    """Return a list of the min. temp, the avg temp, and the max temp for a given start and end date"""
    start_time = dt.datetime.strptime(start, '%Y-%m-%d')
    end_time = dt.datetime.strptime(end, '%Y-%m-%d')
    results5 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).filter(Measurement.date <= end_time)
    
    session.close()

    #When given the start and the end date, calculate the TMIN, TAVG, TMAX for dates between the start and the end date
    list2 = []
    for tobs in results5:
        results_dict2 = {}
        results_dict2["StartDate"] = start_time
        results_dict2["EndDate"] = end_time
        results_dict2["TMIN"] = tobs[0]
        results_dict2["TAVG"] = tobs[1]
        results_dict2["TMAX"] = tobs[2]
        list2.append(results_dict2)

    return jsonify(list2)

#RUN
if __name__ == "__main__":
    app.run(debug=True)