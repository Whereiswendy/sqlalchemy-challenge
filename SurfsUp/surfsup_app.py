from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Helper Functions for Queries in Part 1 
def get_most_recent_date(session):
    return session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

def get_date_one_year_ago(most_recent_date):
    return dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

def get_most_active_station_id(session):
    return session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

def get_most_active_station_details(session):
    most_active_station_id = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    most_active_station_name = session.query(Station.name).filter(Station.station == most_active_station_id).first()[0]

    return most_active_station_id, most_active_station_name

@app.route("/")
def welcome():
    """List all available api routes."""
    session = Session(engine)
    most_active_station_id, most_active_station_name = get_most_active_station_details(session)
    session.close()

    return (
        f"""
        <html>
            <head>
                <title>Surf's Up Climate App API</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; text-align: center; }}
                    .container {{ display: flex; align-items: center; }}
                    .image {{ flex: 1; }}
                    .text-box {{ 
                        flex: 2; 
                        background-color: #001f3f; 
                        color: white; 
                        padding: 20px; 
                        margin-left: 20px; 
                        border-radius: 10px; 
                        display: flex; 
                        align-items: center; 
                        line-height: 1.5; 
                    }}
                    ul {{ list-style-type: none; padding: 0; }}
                    li {{ margin: 10px 0; }}
                    li.class2 {{ margin-top: 20px; }} /* Add space above class2 items */
                    a {{ text-decoration: none; color: #2980b9; }}
                    a:hover {{ text-decoration: underline; }}
                    p {{ text-align: justify; margin: 0; }}
                    img {{ display: block; margin: 0 auto; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); }}
                    hr {{ margin: 40px 0; }}
                    .explore {{ color: #001f3f; font-weight: bold; }}
                    .dark-orange {{ color: #FF8C00; }} /* Dark orange color */
                </style>
            </head>
            <body>
                <h1>Welcome to Wendy's Surf's Up Climate API App!</h1>
                <hr>
                <div class="container">
                    <div class="image">
                        <img src="https://media.discordapp.net/attachments/1154032578240712835/1244179539740069950/whereiswens_surfing_in_hawaii_dc855044-36b3-4e68-bb57-840caf940d04.png?ex=66542bfe&is=6652da7e&hm=ceb2adfdddd94802f51639965ed16a972607d5a4e5f7d0c254d4d6b860ede26e&=&format=webp&quality=lossless&width=592&height=592" alt="Surf Image" width="400"/>
                    </div>
                    <div class="text-box">
                        <p>Catch the wave of climate data with our Surf's Up Climate App! This app uses data from the Global Historical Climatology Network (GHCN), managed by the National Centers for Environmental Information (NCEI). It includes historical weather observations from various stations across Hawaii, covering key metrics like daily precipitation and temperature. This data is stored in a SQLite database file called hawaii.sqlite, featuring two main tables: Measurement and Station. The Measurement table holds climate data, while the Station table contains metadata about each weather station, including its location and identifier. This treasure trove of data allows for deep dives into historical weather patterns and trends in this beautiful region.</p>
                    </div>
                </div>
                <hr>
                <p class="explore">Explore our awesome routes:</p>
                <ul>
                    <li class="class1"><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a> - Last year's precipitation data</li>
                    <li class="class1"><a href="/api/v1.0/stations">/api/v1.0/stations</a> - List of all weather stations</li>
                    <li class="class1"><a href="/api/v1.0/2017-01-01">/api/v1.0/&lt;start&gt;</a> - Min, Avg, and Max temperatures from a start date (Format: /api/v1.0/YYYY-MM-DD)</li>
                    <li class="class1"><a href="/api/v1.0/2017-01-01/2017-12-31">/api/v1.0/&lt;start&gt;/&lt;end&gt;</a> - Min, Avg, and Max temperatures from a date range (Format: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD)</li>
                    <li class="class2"><strong>Most Active Station:</strong> <span class="dark-orange">{most_active_station_name} ({most_active_station_id})</span></li>
                    <li class="class2"><a href="/api/v1.0/tobs">/api/v1.0/tobs</a> - Last year's temperature observations from the most active station ({most_active_station_name})</li>
                </ul>
            </body>
        </html>
        """
    )

# Route and Function for Precipitation Data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the most recent date
    most_recent_date = get_most_recent_date(session)

    # Get the date one year ago
    date_one_year_ago = get_date_one_year_ago(most_recent_date)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_one_year_ago).all()
    
    session.close()

    # Convert query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(precipitation_dict)

# Route and Function for Stations Data
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Perform a query to retrieve the station data
    stations_data = session.query(Station.station).all()
    
    session.close()

    # Convert the query results to a list
    stations_list = [station[0] for station in stations_data]
    return jsonify(stations_list)

# Route and Function for Temperature Observations
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Get the most active station ID
    most_active_station_id = get_most_active_station_id(session)
    
    # Calculate the date one year from the last date in dataset
    most_recent_date = get_most_recent_date(session)
    date_one_year_ago = get_date_one_year_ago(most_recent_date)
    
    # Query the last 12 months of temperature observation data for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= date_one_year_ago).all()
    
    session.close()

    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
    return jsonify(tobs_list)

# Route and Function for Temperature Range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    session = Session(engine)
    
    if end:
        # Calculate TMIN, TAVG, TMAX for dates between the start and end date
        temperature_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        # Calculate TMIN, TAVG, TMAX for dates greater than or equal to the start date
        temperature_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()
    
    session.close()

    # Convert the query results to a dictionary
    temperature_dict = {
        "TMIN": temperature_data[0][0],
        "TAVG": temperature_data[0][1],
        "TMAX": temperature_data[0][2]
    }
    return jsonify(temperature_dict)

if __name__ == "__main__":
    app.run(debug=True)