#!/usr/bin/env python

import time
import json
import os

current_time = lambda: int(time.time())

def parse_unix_time(tm):
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(float(tm)))

def has_expired(data, expiration, at="at"):
    return data[at] + expiration < current_time()

def load(file_name, expiration, at="at"):
    if os.path.isfile(file_name):
        with open(file_name) as f:
            try:    
                data = json.load(f)              
                if not has_expired(data, expiration, at):
                    return data
            except ValueError:
                pass

        os.remove(file_name)
        return None

def save(data, file_name, at="at"):
    data[at] = current_time()
    with open(file_name, "w") as f:
        json.dump(data, f)

