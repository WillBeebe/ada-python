# https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
import os

import requests

api_key = os.environ.get("OPEN_WEATHER_API_KEY")

def get_weather(city: str, state: str, units: str) -> str:
  unit_param = 'imperial'
  if units == 'c':
    unit_param = 'metric'

  response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&limit=1&appid={api_key}")
  data = response.json()
  lat = data[0]['lat']
  lng = data[0]['lon']
  response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units={unit_param}&appid={api_key}")
  data = response.json()

  return f"{data['current']['temp']} degrees"
