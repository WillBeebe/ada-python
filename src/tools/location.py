import requests


def get_location(ip_address):
    url = f"http://ip-api.com/json/{ip_address}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'success':
        city = data['city']
        region = data['region']
        country = data['country']
        latitude = data['lat']
        longitude = data['lon']

        location = f"{city}, {region}, {country} (Lat: {latitude}, Long: {longitude})"
        return location
    else:
        return "Unable to retrieve location information."


def get_current_location():
  ip_address = requests.get('https://api.ipify.org').text

  location = get_location(ip_address)
  print(f"Your location based on IP {ip_address} is: {location}")

  return location
