
########################################################################################################################
import requests, json
from requests.auth import HTTPBasicAuth
# BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
# CITY = "Hyderabad"

# BASE_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine?"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
lat = '29.3867'
lon = '73.9031'
API_KEY = "de39c02a0818896ce4fc9c7c6d56326c"

# upadting the URL
URL = BASE_URL + "lat=" + lat + "&lon=" + lon + "&appid=" + API_KEY
print(URL)
# HTTP request
response = requests.get(URL)
# print(response)
# print(response.content())
print(response.json())
# print(response.text())


########################################################################################################################
BASE_URL = "https://api.openweathermap.org/data/3.0/onecall?"
lat = '29.3867'
lon = '73.9031'
API_KEY = "de39c02a0818896ce4fc9c7c6d56326c"

# upadting the URL
URL1 = BASE_URL + "lat=" + lat + "&lon=" + lon + "&appid=" + API_KEY
# URL1 = 'http://api.openweathermap.org/data/3.0/onecall?lat=30.489772&lon=-99.771335&lang=en'
print(URL1)

response = requests.get(
  url = URL1,
  # auth=HTTPBasicAuth('im.karan23', 's*6H,%Y!Q.TD.!J')
)
print(response.json())

########################################################################################################################
BASE_URL = "https://api.openweathermap.org/data/2.5/onecall?"
lat = '29.3867'
lon = '73.9031'
API_KEY = "de39c02a0818896ce4fc9c7c6d56326c"

# upadting the URL
URL2 = BASE_URL + "lat=" + lat + "&lon=" + lon + "&appid=" + API_KEY
print(URL2)

response = requests.get(url = URL2)
# print(response.json())

#########################################################################################################
