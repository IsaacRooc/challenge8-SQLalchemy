###################################################################################################
# import dependencies 
import numpy as np
import pandas as pd
import datetime as dt
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )
#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = result[0]
        row["prcp"] = result[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#########################################################################################
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the json representation of your dictionary.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)
#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):
    # check if start date is provided
    try:
        start_date = dt.datetime.strftime(start, '%Y-%m-%d')
    except ValueError:
    # handle invalid date string here
        start_date = None

    # calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # create a dictionary for the results
    trip_results = {}
    trip_results['Start Date'] = start_date.strftime("%Y-%m-%d")
    trip_results['End Date'] = session.query(func.max(Measurement.date)).scalar()
    trip_results['Temperature Observations (TOBS)'] = results[0]

    # return the JSON representation of the dictionary
    return jsonify(trip_results)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start, end):
    # go back one year from start/end date and get Min/Avg/Max temp
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end = end_date - last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # create a dictionary for the results
    trip_results = {}
    trip_results['Start Date'] = start.strptime("%Y-%m-%d")
    trip_results['End Date'] = end.strptime("%Y-%m-%d")
    trip_results['Temperature Observations (TOBS)'] = trip_data[0]

    # return the JSON representation of the dictionary
    return jsonify(trip_results)
#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)