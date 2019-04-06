# import Flask, jsonify and other dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



# Create an app, being sure to pass __name__
app = Flask(__name__)

# Define what to do when a user hits the index route and list all routes
@app.route("/")
def welcome():
    return (
        f"Welcome to Climate APP!<br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns a JSON list of percipitation data for the last 12 months<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a JSON list of stations<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns a JSON list of Temperature Observations (tobs) for the last 12 months<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"Returns a JSON list of the min, average, max temperature for a given start date, like 2014-01-01 <br/><br/>"
        f"/api/v1.0/start/end<br/>"
        f"Returns a JSON list of the min, average, max temperature for a given start-end range, like 2014-01-01/2014-01-10 <br/><br/>"
    )

# Define what to do when a user hits the /precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a JSON list of percipitation for the last 12 months"""
    # Query to pull the last 12 months date, same as in jupyter notebook
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    year_ago=last_date-dt.timedelta(days=365)

    # Query to pull date and prcp from measurement
    results=session.query(Measurement.date,Measurement.prcp).\
        order_by(Measurement.date.desc()).filter(Measurement.date>=year_ago).all()

    # parse into dictionary
    prcp_list=[]
    for date, prcp in results:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
    # Query all stations, same as in jupyter notebook
    results_s = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # parse into dictionary
    station_list=[]
    for station, name, latitude, longitude, elevation in results_s:
        station_dict={}
        station_dict["station"]=station
        station_dict["name"]=name
        station_dict["latitude"]=latitude
        station_dict["longitude"]=longitude
        station_dict["elevation"]=elevation
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations for the last 12 months"""
    # Query to pull the last 12 months date, same as before
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    year_ago=last_date-dt.timedelta(days=365)
    
    # Query date and tobs as before
    results_t=session.query(Measurement.date,Measurement.tobs).\
        order_by(Measurement.date.desc()).filter(Measurement.date>=year_ago).all()
    # parse into dictionary
    tobs_list=[]
    for date, tobs in results_t:
        tobs_dict={}
        tobs_dict["date"]=date
        tobs_dict["tobs"]=tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_from(start):
    """Returns a JSON list of the min, average, max temperature for a given start date"""
    # Query to pull the data from the start date (as start)
    start_from_results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).all()
    
    # parse into dictionary
    start_from_list=[]
    for tmin, tavg, tmax in start_from_results:
        start_from_dict={}
        start_from_dict["Min Temperature"]=tmin
        start_from_dict["Average Tempreature"]=tavg
        start_from_dict["Max Temperature"]= tmax
        start_from_list.append(start_from_dict)

    return jsonify(start_from_list)


@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    """Returns a JSON list of the min, average, max temperature for a given range date"""
    # Query to pull the data from the date range (as start and end)
    range_results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    
    # parse into dictionary
    range_list=[]
    for tmin, tavg, tmax in range_results:
        range_dict={}
        range_dict["Min Temperature"]=tmin
        range_dict["Average Tempreature"]=tavg
        range_dict["Max Temperature"]= tmax
        range_list.append(range_dict)

    return jsonify(range_list)


if __name__ == "__main__":
    app.run(debug=True)


