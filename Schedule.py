#Benjamin Gamman, 001439763
"""Schedule.py defines the Schedule class and associated methods."""

from Package import Package
from Package import PackageTable
from Location import Location
from Location import LocationTable
from Load import Load
from Load import LoadList
from datetime import time

class Schedule:
    """The Schedule class holds references to the other data structures (LocationsList, PackagesList, and LoadsList) needed to execute the menu's command options."""
        #Space complexity: O(1)
        #Although the Schedule object will reference much more complex data structures, it will contain only references to them and no complex data itself.

    def __init__(self, locations, packages, loads):
        """Initializes the Schedule's data members to reference the provided data structures."""
        #Space complexity: O(1)
        #Although the objects being referenced are more complex, the Schedule object only stores references to them, and their data is not accessed in initializing the Schedule.
        #Time complexity: O(1)
        #Just three assignments of reference variables are performed.

        self.locations=locations
        self.packages=packages
        self.loads=loads

    def print_schedule(self):
        """This method prints the entire schedule, by printing the route travelled for each load of packages."""
        #Space complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects referenced by the Schedule, each of which is O(N^2) space complexity.
        #Time complexity: O(N^2)
        #A loop calls the Load.print_route() method, which will then loop through each of the load route's stops to print.
        #However many loads there are and however stops are distributed among them, there will ultimately be no more stops in total than packages
        #(excluding starting and stopping at the hub, which even if doubling the number of stops would still be O(N)+O(N)=O(N)).
        #So, this will result in performing those print operations for stops O(N) times, each of which will check O(N) packages in the load,
        #multiplying to O(N^2) time complexity overall.

        print('Delivery Schedule:')
        print()
        mileage=0.0
        for load in self.loads.list:
            load.print_route(self.locations, self.packages)
            mileage+=load.route[len(load.route)-1][2]
        print('Total Miles: '+'{:.1f}'.format(mileage))
        print()

    def status_all(self, status_time):
        """This method displays information and status for all packages at a specified time."""
        #Space complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects referenced by the Schedule, each of which is O(N^2) space complexity.
        #Time complexity: O(N)
        #A loop calls the Package.print_package_status() method, which is O(1), for each package (N times). This results in N*O(1)=O(N) time complexity.
        
        print('Status of all packages at '+status_time.strftime('%I:%M %p')+':')
        print('Package ID:   Weight:     Destination:                                                 Deadline:     Status:')
        for p in self.packages.table[1:]:
              p.print_package_status(self.packages, self.locations, self.loads, status_time)
        print()

    def status_search(self, status_time, search_term):
        """This method displays information and status for each package matching a provided search term at a specified time, using the PackageList's lookup() method."""
        #Space complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects referenced by the Schedule, each of which is O(N^2) space complexity.
        #Time complexity: O(N)
        #This method calls the PackageTable.lookup() method, which is O(N).
        #Then, a loop calls the Package.print_package_status() method, which is O(1), for each package (N times). This portion has N*O(1)=O(N) time complexity.
        #Combined, these two portions of the method give O(N)+O(N)=O(2N)=O(N) time complexity for the method.
        
        print('Status of packages matching \"'+str(search_term)+'\" at '+status_time.strftime('%I:%M %p')+':')
        print('Package ID:   Weight:     Destination:                                                 Deadline:     Status:')
        matches=self.packages.lookup(self.locations, self.loads, search_term, status_time)
        if matches==[]:
            print('No matching packages found')
        for p in matches:
              p.print_package_status(self.packages, self.locations, self.loads, status_time)
        print()
