# app/data.py

"""import requests_cache"""
import pandas as pd
"""from retry_requests import retry
"""
import requests

# Setup the requests cache and retry on error
"""cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)"""

def get_wind_data(latitude, longitude, year):
    url = "https://archive-api.open-meteo.com/v1/archive"
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["wind_speed_10m", "wind_speed_100m"],
        "wind_speed_unit": "ms"
    }
    response = requests.get(url, params=params).json()

    # Process response
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(response['hourly']['time'][0]),
            periods=len(response['hourly']['time']),
            freq='h'
        ),
        "wind_speed_10m": response['hourly']['wind_speed_10m'],
        "wind_speed_100m": response['hourly']['wind_speed_100m']
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe.set_index('date', inplace=True)  # Set DatetimeIndex
    return hourly_dataframe
