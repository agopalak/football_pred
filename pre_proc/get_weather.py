__author__ = 'agopalak'

import forecastio
import datetime
import pytz
import json
import os
from geopy import geocoders
import logging

# Setting up logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.INFO)

# Forecast.io API key
forecastIO_api_key = os.environ['FORECASTIO_API_KEY']

# GoogleV3 API Key
googlev3_api_key = os.environ['GOOGLEV3_API_KEY']

# Setting up access to Google V3
googv3 = geocoders.GoogleV3(api_key=googlev3_api_key)

# Location Format: <City>, <State Abbreviation>
# Date Format: MM/DD/YYYY
# Time Format: HH:MM:SS AM|PM
# Limitations: No format checking done

def fetch_weather(city, gdate, gtime):

    # Preparing Date, Time data for API calls
    (month, day, year) = map(int, gdate.split('/'))
    (hour, minute) = map(int, (gtime.split())[0].split(':'))

    # Handling AM/PM
    if (gtime.split())[1] == 'PM':
        if hour != 12:
            hour += 12

    # Geo Location of a given city
    geoloc = googv3.geocode(city)

    # Time Zone for a given Latitude & Longitude
    tz = googv3.timezone((geoloc.latitude, geoloc.longitude))
    #print city, tz
    logger.debug('City: %s, Time Zone: %s', city, tz)

    # Date in UTC Format
    date = datetime.datetime(year, month, day, hour, minute)
    #print date
    logger.debug('Date: %s', date)

    # Get Weather Information for given location & time
    forecast = forecastio.load_forecast(forecastIO_api_key, geoloc.latitude,\
                                        geoloc.longitude, time=date)
    forecast_data = forecast.currently()

    #print forecast_data.d
    return forecast_data.d

if __name__ == '__main__':
    fetch_weather('Tampa, FL', '12/19/2010', '1:00 PM')
