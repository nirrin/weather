#!/usr/bin/env python

from flask import Flask
import json
import location
import open_weather_map
from flask import render_template

app = Flask(__name__)

with open('./etc/configuration.json') as conf_file:
    configuration = json.load(conf_file)

loc = location.get_location(configuration["google_api_key"], configuration["address"], configuration["location_file"], configuration["location_expiration"]) 

@app.route("/")
def current_weather():
    weather = open_weather_map.get_current_weather(configuration["open_weather_map_api_key"], float(loc["latitude"]), float(loc["longtitude"]), configuration["current_weather_file"], configuration["current_weather_expiration"])    
    return render_template("current_weather.html", current_weather=weather)   

@app.route("/maps")
def weather_maps():    
    return render_template("windyty.html", lat=float(loc["latitude"]), lon=float(loc["longtitude"])) 

if __name__ == "__main__":    

    app.run(port = int(configuration["web_port"]))
