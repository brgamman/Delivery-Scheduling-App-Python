#Benjamin Gamman, 001439763
"""Truck.py defines the Truck and TruckList classes and associated methods."""

from Package import Package
from Package import PackageTable
from Location import Location
from Location import LocationTable
from Load import Load
from Load import LoadList
from timemath import add_times
from timemath import subtract_times
from timemath import calc_time
from datetime import datetime
from datetime import time
from math import fabs

class Truck:
    """The Truck class defines a set of values relevant to the actual delivery of the packages (speed, truck number, and the time that truck will be available to pick up its next load)."""
    #Space complexity: O(1)
    #The Truck object's data consists of only fixed-size data.
    
    def __init__(self, num, start_time, speed):
        """Initializes the Truck with a provided identifying number (its index in TruckList), the start time for the day, and the specified speed."""
        #Space complexity: O(1)
        #Time complexity: O(1)
        #A fixed number of assignments are performed to fixed-size data members.
        
        self.number=num
        self.speed_mph=speed
        self.time_available=start_time

class TruckList:
    """The TruckList class holds a list indexing the Truck objects by truck number, used to facilitate a delivery algorithm in which the trucks' route schedules are interdependent."""
    #Space complexity: O(N)
    #The TruckList contains a variable number of Truck objects which are each O(1).
    
    def __init__(self, num_trucks, start_time, speed):
        """Initializes TruckList by generating the specified number of Truck objects."""
        #Space complexity: O(N)
        #Time complexity: O(N)
        #O(1) operations for each Truck initialized in the process are performed N times (for the number of trucks, which cannot exceed the number of packages to be delivered).

        #The number of trucks used in this sense cannot functionally be greater than the number of drivers, as trucks with different numbers will be able to be in use at the same time.
        self.list=[None]
        for n in range(num_trucks):
            new_truck=Truck(n+1, start_time, speed)
            self.list.append(new_truck)

    def next_stop_greedy(self, prev_stop, stops_set, locations):
        """This method employs a greedy algorithm with some built-in correction to select and return the next stop from a list of options given the previous stop."""
        #This is defined as a separate method from the rest of the routing algorithm because it is used repeatedly (in TruckList.deliver()), so is more efficiently defined once here.
        #Space Complexity: O(N^2)
        #The method accesses the LocationTable object, which is O(N^2).
        #Time complexity: O(N)
        #Each use of this greedy selection performs two (non-nested) loops through the provided set of stops (which cannot exceed the total number of packages in length).
        #Each loop is therefore O(N), and O(N)+O(N)=O(2N)=O(N).
        
        #First, applies a simple greedy algorithm to select the location within the provided set that is closest to the previous stop.
        #"Ties" in which two options are the same distance away are not addressed yet, as they will be in the second loop for corrections.
        dist=100
        next_stop=0
        for stop in stops_set:
            dist_diff=dist-locations.distances[stop][prev_stop]
            if dist_diff>0.001:
                next_stop=stop
                dist=locations.distances[stop][prev_stop]

        #Then, each option is checked against the "greedy" winner. If their distances differ by less than 0.5 miles and the further option is closer to the hub, it is selected instead.
        #The distance that is checked against remains unchanged though, to avoid a chain of switches in which each is within 0.5 miles of the last but may be much further from the original "greedy" choice.
        #Choosing the point further from the hub here decreases the likelihood of leaving it for last, resulting in a long return distance to the hub at the end of the route.
        #This must be done in a second separate loop to ensure that only the best "greedy" choice is compared to other options on this basis, not any intermediate options.        
        for stop in stops_set:
            if (fabs(locations.distances[stop][prev_stop]-locations.distances[next_stop][prev_stop])<0.5
            and locations.distances[stop][0]-locations.distances[next_stop][0]>1.0):
                next_stop=stop
        return next_stop

    def deliver(self, loads, packages, locations):
        """This method determines routes for all loads of packages and "delivers" the using the trucks in TruckList."""
        #Space Complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects, each of which is O(N^2) space complexity.
        #Time complexity: O(N^3)
        #Choosing stops by calling the core greedy selection method gives O(N^2) time complexity:
        #At most one call for each stop, each of which loops through a list of possible stops no greater than N, and performing an O(N) task O(N) times gives O(N)*O(N)=O(N^2) complexity.
        #Other portions of the algorithm use nested loops to dynamically check for and apply available updates to packages destinations while they have been loaded and are en route.
        #It can logically be abstracted that the location check loop will execute only once for each package that needs to be updated (it is then marked as not needing update), 
        #so even though this task is nested within other loops handling other functions, it will still only add
        #(number of updates*number of locations)=O(N)*O(N)=O(N2) operations to the program, not multiply that number by the number of loops those operations are split between,
        #and then the overall time complexity of the section it is contained within is O(N2) + O(N2) = O(N2).

        #The routing process iterates through each load in LoadList, determining their routes sequentially as later loads' delivery times may be affected by earlier loads' times.
        for load in loads.list:

            #First, the load is assigned to a truck. If the load has a nonzero truck requirement, it is assigned to that truck.
            #Otherwise, it is assigned to whichever truck is available to depart from the hub next.
            #The load's departure time is then set to the time that its assigned truck will be available to pick it up from the hub.
            #If any packages in the load have a delay time (delayed arrival at the hub and thereby availability to load onto a truck) later than that time,
            #the load's departure time is changed to the latest such delay time.
            if load.truck_requirement!=0:
                load.truck_assigned=load.truck_requirement
            else:
                next_truck=self.list[1]
                for t in self.list[1:]:
                    if t.time_available<next_truck.time_available:
                        next_truck=t
                load.truck_assigned=next_truck.number
            load.departure_time=self.list[load.truck_assigned].time_available
            for id in load.package_list:
                if packages.table[id].delay_time>load.departure_time:
                    load.departure_time=packages.table[id].delay_time

            #The route must start at the hub, so the initial stop (stop "0") added to the load's route data member is there (location 0).
            #The stop's location key is added as a list because the route data will later become a matrix of information, so this will allow other "columns" to be appended later.
            #A new set is created of remaining stops that can be modified, leaving the load's original set of stops intact.
            load.route.append([locations.table[0].key])
            remaining_stops=set()
            for stop in load.stops:
                remaining_stops.add(stop)

            #The earliest deadline on the route and the location of the package with that deadline are determined.
            #If packages are tied with the same earliest deadline, the location closest to the hub is chosen.
            first_deadline_stop=0
            first_deadline=time(23,59)
            for id in load.package_list:
                if (packages.table[id].deadline!=time(0,0) and packages.table[id].deadline<first_deadline):
                    first_deadline=packages.table[id].deadline
                    first_deadline_stop=packages.table[id].destination
                elif (packages.table[id].deadline==first_deadline
                and locations.distances[packages.table[id].destination][0]<locations.distances[first_deadline_stop][0]):
                    first_deadline=packages.table[id].deadline
                    first_deadline_stop=packages.table[id].destination
                    
            #If that deadline is within an hour of the load's departure time, the following steps are used to determine a route.
            #The first stop added to the route is the first deadline location determined previously.
            if add_times(load.departure_time, time(1,0))>=first_deadline:
                deadline=True
                next_stop=first_deadline_stop
                
                #While any remaining stops have that same deadline, the nearest of those locations from the preceding location is added to the route next.
                #This is a greedy selection, but not using the method above because it must consider only locations with the same deadline,
                #and this variation of the greedy selection is employed only here.
                #It breaks ties based on average distances, choosing the location with greater average distance first,
                #on the basis that it will be more advantageous to leave shorter distances available for later at no cost to distance here.
                while deadline==True:
                    load.route.append([next_stop])
                    remaining_stops.remove(next_stop)
                    deadline=False
                    next_stop_dist=100
                    next_stop=0
                    for stop in remaining_stops:
                        if locations.table[stop].deadline==first_deadline:
                            deadline=True
                            stop_dist=locations.distances[stop][load.route[len(load.route)-1][0]]
                            if (next_stop_dist-stop_dist>0.001
                            or (fabs(next_stop_dist-stop_dist)<=0.001
                            and locations.table[stop].avg_dist>locations.table[next_stop].avg_dist)):
                                next_stop=stop
                                next_stop_dist=stop_dist
                                
                #After those stops have been added to the route, the greedy selection method above selects next stops to add to the route until the remaining stops set is empty.
                #This means that all known destinations have been visited, but does not necessarily complete the route;
                #destination keys of packages with unknown/incorrect addresses were not added to the load's set of stops, so they may not have been visited yet.
                #This will be accounted for later in the portion of the algorithm determining times.
                while remaining_stops!=set():
                    next_stop=self.next_stop_greedy(load.route[len(load.route)-1][0], remaining_stops, locations)
                    load.route.append([next_stop])
                    remaining_stops.remove(next_stop)
                    
            #If the load's first deadline is more than an hour after departure, these steps are taken instead.
            else:

                #The route's first stop is determined based on two poles within the load's required stops that are far from each other and on average from other locations.
                #This is similar to the process used to assign locations to regions during import,
                #but restricted to stops in the load being considered and without the ring-based constraints (as a load may be heavily skewed toward one ring or another).
                #Pole 1 of the route is set as the stop with the highest average distance.
                #Pole 2 is set as the stop furthest from Pole 1.
                #The "tie-breaking" calculations used in determining the overall regional poles earlier are not employed here.
                #Given the smaller number of locations in a load vs. the entire set of destinations, ties are less likely,
                #and breaking them in a precise way is less likely to be worth the calculations as it will affect only one load rather than the overall distribution of the packages.
                route_pole1=0
                high_dist=0
                for l in load.stops:
                    if locations.table[l].avg_dist>high_dist:
                        route_pole1=l
                        high_dist=locations.table[l].avg_dist
                route_pole2=route_pole1
                high_dist=0
                for l in load.stops:
                    if locations.distances[l][route_pole1]>high_dist:
                        route_pole2=l
                        high_dist=locations.distances[l][route_pole1]

                #The first stop is selected as the location in the load's set of stops that has the highest sum of distances to the two route poles, minus its distance from the hub.
                #(The route poles themselves are excluded from consideration as a start point.)
                #Considering the sum of pole distances results in a start point that is more or less midway between the poles, and somewhat out from a direct line between them
                #(based on the idea of the Pythagorean theorem, it will be further from the poles than a point along that direct line).
                #This helps make the route more of a circuit in shape, while also factoring in the distance to the hub helps avoid a long initial distance to get to the start point.
                first_stop=0
                high_dist=0
                for l in load.stops:
                    composite_dist=(locations.distances[l][route_pole1]
                                    +locations.distances[l][route_pole2]
                                    -locations.distances[l][0])
                    if composite_dist>high_dist and l!=route_pole1 and l!=route_pole2:
                        first_stop=l
                        high_dist=composite_dist
                load.route.append([first_stop])
                remaining_stops.remove(first_stop)

                #After that first stop is selected, the above greedy selection method is used to choose the order of the known remaining stops.
                #As with the previous case, packages without known destinations are not considered for now.
                while remaining_stops!=set():
                    next_stop=self.next_stop_greedy(load.route[len(load.route)-1][0], remaining_stops, locations)
                    load.route.append([next_stop])
                    remaining_stops.remove(next_stop)                            

            #Next, the route data member is expanded into a matrix including the location key, distance from previous stop,
            #total distance of the route so far, and elapsed time from the start of the route for each stop.
            #Actual delivery times are still excluded for now, as these pieces of information will be used to adjust the route's start time.
            #The initial information for starting at the hub is added first (0 miles from itself, 0 miles travelled so far, and 0:00 elapsed on the route).
            #Then a loop calculates those values based on each other sequentially combined with the previous stop's values, for each stop currently on the route.
            load.route[0].append(0.0)
            load.route[0].append(0.0)
            load.route[0].append(time(0,0))
            for i in range(1, len(load.route)):
                load.route[i].append(locations.distances[load.route[i][0]][load.route[i-1][0]])
                load.route[i].append(load.route[i][1]+load.route[i-1][2])
                route_time=calc_time(load.route[i][2], self.list[load.truck_assigned].speed_mph)
                load.route[i].append(route_time)

            #This section of the algorithm begins to consider packages with unknown/incorrect addresses.
            #If such a package is included in the load, a marker variable is set reflecting that an update is expected.
            #In that case, the load's departure time is updated to be as late as possible while still meeting the last deadline along the route.
            #This maximizes the chance that any package loaded onto a truck without a known destination at that time will be updated with the correct destination before reaching that stop,
            #so that it can be delivered with any others that may be at the same location and avoid returning and making redundant stops later.
            update_expected=False
            for id in load.package_list:
                if packages.table[id].update_time!=time(0,0):
                    update_expected=True
            if update_expected==True:
                last_deadline=time(0,0)
                last_deadline_route_index=0
                for stop in load.route:
                    if locations.table[stop[0]].deadline!=time(0,0):
                        last_deadline=locations.table[stop[0]].deadline
                        last_deadline_route_index=load.route.index(stop)          
                delayed_time=subtract_times(last_deadline, add_times(load.route[last_deadline_route_index][3], time(0,1)))
                if delayed_time>load.departure_time:
                    load.departure_time=delayed_time

            #This section handles the actual "delivery" of packages to the stops on the load's route.
            #All of the load's packages are initially added to the undelivered set, while the delivered set is initially empty.
            #For each stop along the route, the time of the stop (departure time plus time on the route so far) is added to the next column of the route matrix.
            #Then, each of the packages in the undelivered set are checked.
            undelivered=set(load.package_list)
            delivered=set()
            load.route[0].append(load.departure_time)
            for i in range(1, len(load.route)):
                route_time=calc_time(load.route[i][2], self.list[load.truck_assigned].speed_mph)
                load.route[i].append(add_times(load.departure_time, route_time))
                for id in undelivered:

                    #If an update is expected (meaning to a package's destination) and the update time is at or before the current stop's time,
                    #the package's destination data is changed to the location key matching the correct address.
                    #This reflects the system relaying updated information to the truck/driver as it comes in, so that even though a package might have been loaded without knowing its destination,
                    #and the route was determined without that knowledge but included the same destination for other packages,
                    #if the truck goes to that stop after the package's information is updated, it can be delivered along with the others.
                    #Its expected update time is then reset so that it isn't re-updated at each stop, and it is added to the correct location's package list as well.
                    if (update_expected==True
                    and packages.table[id].update_time!=time(0,0)
                    and packages.table[id].update_time<=load.route[i][4]):
                        for l in locations.table:
                            if l.address==packages.table[id].corrected_address:
                                packages.table[id].destination=l.key
                                packages.table[id].update_time=time(0,0)
                                l.package_list.append(id)

                    #Then, if a package's destination matches the current stop, it is delivered (added to the delivered set and marked with the stop's time).
                    if packages.table[id].destination==load.route[i][0]:
                        packages.table[id].delivery_time=load.route[i][4]
                        delivered.add(id)
                        
            #After delivering packages to a stop, the set of undelivered is updated to remove any that are now in the delivered set.
            #This improves efficiency by reducing the number of packages that must be checked at each subsequent stop,
            #and keeps track of any leftover packages after the route’s initially known locations have all been visited.
            undelivered=undelivered.difference(delivered)

            #This section handles what happens if a package is left undelivered after the previously calculated route.
            #(This would occur if an update was expected, and the correct stop either was not already on the route or was reached before the update was made.)
            #First, a set of known destinations is made (undelivered packages' positive location keys).
            #(There would be known destinations at this point if updates had already been made but were not for stops along the portion of the route following the update time.)
            #As long as undelivered packages remain in the load, the truck will continue extending the route to deliver them.
            while undelivered!=set():
                next_stop=0
                known_destinations=set()
                for id in undelivered:
                    if packages.table[id].destination>0:
                        known_destinations.add(packages.table[id].destination)

                #If there are known destinations, the greedy selection method is used to choose the next stop from among them,
                # which is then added to the route and the package is delivered as above.
                if known_destinations!=set():
                    next_stop=self.next_stop_greedy(load.route[len(load.route)-1][0], known_destinations, locations)
                    load.route.append([next_stop])
                    i=len(load.route)-1
                    load.route[i].append(locations.distances[load.route[i][0]][load.route[i-1][0]])
                    load.route[i].append(load.route[i][1]+load.route[i-1][2])
                    leg_time=calc_time(load.route[i][1], self.list[load.truck_assigned].speed_mph)
                    load.route[i].append(add_times(load.route[i-1][3], leg_time))
                    load.route[i].append(add_times(load.departure_time, load.route[i][3]))
                    for id in undelivered:
                        if (update_expected==True
                        and packages.table[id].update_time!=time(0,0)
                        and packages.table[id].update_time<=load.route[i][4]):
                            for l in locations.table:
                                if l.address==packages.table[id].corrected_address:
                                    packages.table[id].destination=l.key
                                    packages.table[id].update_time=(0,0)
                                    l.package_list.append(id)
                        if packages.table[id].destination==load.route[i][0]:
                            packages.table[id].delivery_time=load.route[i][4]
                            delivered.add(id)
                    undelivered=undelivered.difference(delivered)
                    
                #If there are no known destinations at this point, meaning that packages are still awaiting updated information, the truck returns to the hub to wait.
                #The next expected update time is determined, and if it is later than the time the truck returns to the hub, the truck continues to wait until that time.
                #This case adds a second consecutive "stop" at the hub to the route if needed, the first showing the truck's arrival time and the second showing its departure.
                #After that, the loop will repeat, and at least that package's location will be added to known destinations, triggering the previous case.
                else:
                    load.route.append([0])
                    i=len(load.route)-1
                    load.route[i].append(locations.distances[0][load.route[i-1][0]])
                    load.route[i].append(load.route[i][1]+load.route[i-1][2])
                    leg_time=calc_time(load.route[i][1], self.list[load.truck_assigned].speed_mph)
                    load.route[i].append(add_times(load.route[i-1][3], leg_time))
                    load.route[i].append(add_times(load.departure_time, load.route[i][3]))
                    next_update_time=time(23,59)
                    for id in undelivered:
                        if packages.table[id].update_time!=time(0,0) and packages.table[id].update_time<next_update_time:
                            next_update_time=packages.table[id].update_time                    
                    if next_update_time>load.route[i][4]:
                        load.route.append([0])
                        load.route[i+1].append(0.0)
                        load.route[i+1].append(load.route[i][1])
                        load.route[i+1].append(subtract_times(next_update_time, load.departure_time))
                        load.route[i+1].append(next_update_time)

            #Lastly, a final stop is added to the route to mark the truck's return to the hub and display the route's final length and end time.
            #The assigned truck's availability time is also updated to the route's end time, signifying that it will then be available to deliver another load as this method repeats for any following.
            load.route.append([0])
            i=len(load.route)-1
            load.route[i].append(locations.distances[0][load.route[i-1][0]])
            load.route[i].append(load.route[i][1]+load.route[i-1][2])
            leg_time=calc_time(load.route[i][1], self.list[load.truck_assigned].speed_mph)
            load.route[i].append(add_times(load.route[i-1][3], leg_time))
            load.route[i].append(add_times(load.departure_time, load.route[i][3]))
            self.list[load.truck_assigned].time_available=load.route[i][4]
