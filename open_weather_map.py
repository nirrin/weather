#!/usr/bin/env python

import time
import collections
import requests
import json
import location
import utils
import gpxpy.geo

current_weather = None

conditions = {200: "thunderstorm with light rain",
201: "thunderstorm with rain",
202: "thunderstorm with heavy rain",
210: "light thunderstorm",
211: "thunderstorm",
212: "heavy thunderstorm",
221: "ragged thunderstorm",
230: "thunderstorm with light drizzle",
231: "thunderstorm with drizzle",
232: "thunderstorm with heavy drizzle", 
300: "light intensity drizzle",
301: "drizzle",
302: "heavy intensity drizzle",
310: "light intensity drizzle rain",
311: "drizzle rain",
312: "heavy intensity drizzle rain",
313: "shower rain and drizzle",
314: "heavy shower rain and drizzle",
321: "shower drizzle",
500: "light rain",
501: "moderate rain",
502: "heavy intensity rain",
503: "very heavy rain",
504: "extreme rain",
511: "freezing rain",
520: "light intensity shower rain",
521: "shower rain",
522: "heavy intensity shower rain",
531: "ragged shower rain",
600: "light snow",
601: "snow",
602: "heavy snow",
611: "sleet",
612: "shower sleet",
615: "light rain and snow",
616: "rain and snow",
620: "light shower snow",
621: "shower snow",
622: "heavy shower snow",
701: "mist",
711: "smoke",
721: "haze",
731: "sand, dust whirls",
741: "fog",
751: "sand",
761: "dust",
762: "volcanic ash",
771: "squalls",
781: "tornado",
800: "clear sky",
801: "few clouds",
802: "scattered clouds",
803: "broken clouds",
804: "overcast clouds",
900: "tornado",
901: "tropical storm",
902: "hurricane",
903: "cold",
904: "hot",
905: "windy",
906: "hail",
951: "calm",
952: "light breeze",
953: "gentle breeze",
954: "moderate breeze",
955: "fresh breeze",
956: "strong breeze",
957: "high wind, near gale",
958: "gale",
959: "severe gale",
960: "storm",
961: "violent storm",
962: "hurricane"}

def get_condition(code):
    try:
        return conditions[int(code)]
    except KeyError:
        return code


def get_icon(icon):
    return "http://openweathermap.org/img/w/" + icon + ".png"

Weather = collections.namedtuple("Weather", [   "clouds", 
                                                "name", 
                                                "visibility", 
                                                "country", 
                                                "sunset", 
                                                "sunrise", 
                                                "main", 
                                                "description", 
                                                "id", 
                                                "icon", 
                                                "latitude", 
                                                "longtitude",
                                                "time", 
                                                "pressure", 
                                                "temperature", 
                                                "humidity", 
                                                "speed", 
                                                "degree",
                                                "rain",
                                                "snow"])

def get_cities(cities_file, cities_expiration):
    cities = utils.load(cities_file, cities_expiration)
    if cities != None:
        cities.pop("at", None)
        return cities

    url = "http://openweathermap.org/help/city_list.txt"
    cities_list = requests.get(url).text.split("\n")
    cities = { }
    header = True
    for city_element in cities_list:        
        if header:
            header = False
            continue

        elements = city_element.split("\t")
        if len(elements) < 5:
            continue

        city_id = int(elements[0])
        name = elements[1]        
        latitude = float(elements[2])
        longtitude = float(elements[3])
        country = elements[4]
        cities[city_id] = { "name": name, "latitude": latitude, "longtitude": longtitude, "country": country }
    utils.save(cities, cities_file)
    cities.pop("at", None)
    return cities

def closest_city(cities_file, cities_expiration, latitude, longtitude):
    cities = get_cities(cities_file, cities_expiration)
    if cities == None:
        return None

    closest_distance = float("inf")
    city = 0
    for city_id, city_data in  cities.iteritems():
        distance = gpxpy.geo.haversine_distance(latitude, longtitude, city_data["latitude"], city_data["longtitude"])
        print distance, city_data
        if distance < closest_distance:
            closest_distance = distance
            city = city_id
    return city, cities[city], closest_distance


def get_current_weather(open_weather_map_api_key, latitude, longtitude, current_weather_file, current_weather_expiration):
    global current_weather

    if current_weather and not utils.has_expired(current_weather, current_weather_expiration):
        return current_weather
    
    current_weather = utils.load(current_weather_file, current_weather_expiration)
    if current_weather:
        return current_weather

    url = "http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&units=metric&APPID={2}".format(("%.2f" % latitude), ("%.2f" %longtitude), open_weather_map_api_key)

    response = requests.get(url).json()    

    if response["cod"] == 200:      
        current_weather = { "clouds": float(response["clouds"]["all"]) if "clouds" in response and "all" in response["clouds"] else 0.0,
                            "name": response["name"],
                            "visibility": float(response["visibility"]) if "visibility" in response else 0.0,
                            "country": response["sys"]["country"],
                            "sunset": utils.parse_unix_time(response["sys"]["sunset"]),
                            "sunrise": utils.parse_unix_time(response["sys"]["sunrise"]),
                            "main": response["weather"][0]["main"],
                            "description": response["weather"][0]["description"],
                            "id": get_condition(response["weather"][0]["id"]),
                            "icon": get_icon(response["weather"][0]["icon"]),
                            "latitude": float(response["coord"]["lat"]),
                            "longtitude": float(response["coord"]["lon"]),
                            "time": utils.parse_unix_time(response["dt"]),
                            "pressure": float(response["main"]["pressure"]) if "main" in response and "pressure" in response["main"] else 0.0,
                            "temperature": float(response["main"]["temp"]) if "main" in response and "temp" in response["main"] else 0.0,
                            "humidity": float(response["main"]["humidity"]) if "main" in response and "humidity" is response["main"] else 0.0,
                            "speed": float(response["wind"]["speed"]) if "wind" in response and "speed" in response["wind"] else 0.0,
                            "degree": float(response["wind"]["deg"]) if "wind" in  response and "deg" in response["wind"] else 0.0,
                            "rain": float(response["rain"]["rain.3h"]) if "rain" in response and "rain.3h" in response["rain"] else 0.0,
                            "snow": float(response["snow"]["snow.3h"]) if "snow" in response and "snow.3h" in response["snow"] else 0.0 }       
        utils.save(current_weather, current_weather_file)                    
        return current_weather
    else:       
        return None

def get_weather_forecast(open_weather_map_api_key, latitude, longtitude, current_weather_file, current_weather_expiration):
    # global current_weather

    # if current_weather and not utils.has_expired(current_weather, current_weather_expiration):
    #     return current_weather
    
    # current_weather = utils.load(current_weather_file, current_weather_expiration)
    # if current_weather:
    #     return current_weather

    url = "http://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&units=metric&APPID={2}".format(("%.2f" % latitude), ("%.2f" %longtitude), open_weather_map_api_key)

    print url    

    response = requests.get(url).json()  

    print response 

    # if response["cod"] == 200:      
    #     current_weather = { "clouds": float(response["clouds"]["all"]) if "clouds" in response and "all" in response["clouds"] else 0.0,
    #                         "name": response["name"],
    #                         "visibility": float(response["visibility"]) if "visibility" in response else 0.0,
    #                         "country": response["sys"]["country"],
    #                         "sunset": utils.parse_unix_time(response["sys"]["sunset"]),
    #                         "sunrise": utils.parse_unix_time(response["sys"]["sunrise"]),
    #                         "main": response["weather"][0]["main"],
    #                         "description": response["weather"][0]["description"],
    #                         "id": get_condition(response["weather"][0]["id"]),
    #                         "icon": get_icon(response["weather"][0]["icon"]),
    #                         "latitude": float(response["coord"]["lat"]),
    #                         "longtitude": float(response["coord"]["lon"]),
    #                         "time": utils.parse_unix_time(response["dt"]),
    #                         "pressure": float(response["main"]["pressure"]) if "main" in response and "pressure" in response["main"] else 0.0,
    #                         "temperature": float(response["main"]["temp"]) if "main" in response and "temp" in response["main"] else 0.0,
    #                         "humidity": float(response["main"]["humidity"]) if "main" in response and "humidity" is response["main"] else 0.0,
    #                         "speed": float(response["wind"]["speed"]) if "wind" in response and "speed" in response["wind"] else 0.0,
    #                         "degree": float(response["wind"]["deg"]) if "wind" in  response and "deg" in response["wind"] else 0.0,
    #                         "rain": float(response["rain"]["rain.3h"]) if "rain" in response and "rain.3h" in response["rain"] else 0.0,
    #                         "snow": float(response["snow"]["snow.3h"]) if "snow" in response and "snow.3h" in response["snow"] else 0.0 }       
    #     utils.save(current_weather, current_weather_file)                    
    #     return current_weather
    # else:       
    #     return None        

if __name__ == "__main__":
    with open('./etc/configuration.json') as conf_file:
        configuration = json.load(conf_file)

    loc = location.get_location(configuration["google_api_key"], configuration["address"], configuration["location_file"], configuration["location_expiration"]) 
    print "weather at %s: " % str(loc)
    print closest_city(configuration["cities_file"], configuration["cities_expiration"], loc["latitude"], loc["longtitude"])

    #get_weather_forecast(configuration["open_weather_map_api_key"], loc["latitude"], loc["longtitude"], configuration["current_weather_file"], configuration["current_weather_expiration"])
    # weather = get_current_weather(configuration["open_weather_map_api_key"], loc["latitude"], loc["longtitude"], configuration["current_weather_file"], configuration["current_weather_expiration"])
    # print weather