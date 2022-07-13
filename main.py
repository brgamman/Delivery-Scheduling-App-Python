#Benjamin Gamman, 001439763
"""main.py creates instances of data structures defined in other files, then handles input and output to interact with those data structures through a menu."""
#Overall time complexity: O(
#Overall space complexity: O(

from Package import Package
from Package import PackageTable
from Location import Location
from Location import LocationTable
from Load import Load
from Load import LoadList
from Truck import Truck
from Truck import TruckList
from Schedule import Schedule
from timemath import add_times
from timemath import calc_time
from datetime import datetime
from datetime import time
import sys

def display_menu():
    """This function prints the program's main menu."""
    #Time complexity: O(1)
    #Space complexity: O(1)
    
    print('Select an option:')
    print('-Press p to display the entire delivery plan')
    print('-Press a to display the status of all packages at a specified time')
    print('-Press s to display the status of package(s) matching a search term at a specified time')
    print('-Press q to exit')
    print()
    
#Defines situational constants.
TRUCK_SPEED=18
TRUCK_CAPACITY=16
NUM_TRUCKS=2
START_TIME=time(8,0)

#Calls on classes and methods defined in other files to initialize and populate the program's data structures.

locations=LocationTable()
locations.import_csv('locations.csv')

packages=PackageTable()
packages.import_csv('packages.csv', locations)

loads=LoadList((len(packages.table)-1), TRUCK_CAPACITY, ['Express', 'Delay', 'Final'])
loads.sort(packages, locations)
    
trucks=TruckList(NUM_TRUCKS, START_TIME, TRUCK_SPEED)
trucks.deliver(loads, packages, locations)

schedule=Schedule(locations, packages, loads)

#Handles input and output through the mmenu, utilizing other methods to generate requested output.
#This portion of the program has:
#Time complexity O(N) as the more complex calculations have already been completed and results stored
#Space complexity O(N^2) as the PackageTable and LocationTable constructs are accessed and used by the functions called on the schedule.

command='p'
while command!='q':
    if command=='p':
        schedule.print_schedule()
    elif command=='a':
        try:
            time_str=input('Enter a time for which to view status (enter as "X:XX am" or "X:XX pm"):')
            status_time=datetime.time(datetime.strptime(time_str, '%I:%M %p'))
            print()
            schedule.status_all(status_time)
        except:
            print('Invalid time entered.')
            print()
    elif command=='s':
        print('Use one of the following to search:')
        print('-Package ID')
        print('-Weight (enter as "X kg", no decimal)')
        print('-Destination Address (case sensitive, returns all street addresses containing the search term)')
        print('-Destination City (case sensitive, returns all cities containing the search term)')
        print('-Destination State (enter the state\'s two-letter abbreviation, capitalized)')
        print('-Zip Code (enter the five digit zip code)')
        print('-Deadline (enter as "X:XX am" or "X:XX pm")')
        print('-Status (enter "delivered", "en route", "at hub", or "delayed")')
        print()
        search_term=input('Enter a search term:')
        try:
            time_str=input('Enter a time for which to view status (enter as "X:XX am" or "X:XX pm"):')
            status_time=datetime.time(datetime.strptime(time_str, '%I:%M %p'))
            print()
            schedule.status_search(status_time, search_term)
        except:
            print('Invalid time entered.')
            print()
    else:
        print('Command not recognized, please enter a valid command.')
    display_menu()
    command=input('Enter command:')
    print()

sys.exit()
