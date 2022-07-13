#Benjamin Gamman, 001439763
"""timemath.py defines functions used to perform basic calculations with time values."""

from datetime import time
from math import ceil

def add_times(t1, t2):
    """This function adds together two provided time values and returns the resulting sum."""
    #Space complexity: O(1)
    #Time complexity: O(1)
    
    hours=(t1.hour+t2.hour+int((t1.minute+t2.minute)/60))%24
    minutes=((t1.minute+t2.minute)%60+int((t1.second+t2.second)/60))%60
    seconds=(t1.second+t2.second)%60
    new_time=time(hours, minutes, seconds)
    return new_time

def subtract_times(t1, t2):
    """This function subtracts one provided time value from another and returns the resulting dfference."""
    #Space complexity: O(1)
    #Time complexity: O(1)
    
    t1_seconds=t1.hour*3600+t1.minute*60+t1.second
    t2_seconds=t2.hour*3600+t2.minute*60+t2.second
    new_seconds=t1_seconds-t2_seconds
    hours=int(new_seconds/3600)
    minutes=int((new_seconds%3600)/60)
    seconds=(new_seconds%60)
    new_time=time(hours, minutes, seconds)
    return new_time

def calc_time(dist, speed_mph):
    """This function calculates how long it takes to travel a specified distance (in miles) at the specified speed (in mph) and returns the calculated time."""
    #Space complexity: O(1)
    #Time complexity: O(1)
    
    elapsed_secs=dist/speed_mph*3600
    hours=int(elapsed_secs/3600)
    minutes=int((elapsed_secs%3600)/60)
    seconds=round(elapsed_secs%60)
    if seconds==60:
        minutes+=1
        seconds=0
    elapsed_time=time(hours, minutes, seconds)
    return elapsed_time
