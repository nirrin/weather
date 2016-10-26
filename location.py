#!/usr/bin/env python

import requests
import json
import time
import os
import utils

current_location = None

def get_location(google_api_key, address, location_file, location_expiration):
    global current_location

    if current_location and not utils.has_expired(current_location, location_expiration):
        return current_location
    
    current_location = utils.load(location_file, location_expiration)
    if current_location:
        return current_location

    url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(address, google_api_key)
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        current_location = {    "latitude": float(location["lat"]),
                                "longtitude": float(location["lng"]) }
        utils.save(current_location, location_file)
        return current_location
    else:        
        return None     

if __name__ == "__main__":
    with open('./etc/configuration.json') as conf_file:
        configuration = json.load(conf_file)

    print get_location(configuration["google_api_key"], configuration["address"], configuration["location_file"], configuration["location_expiration"])   


