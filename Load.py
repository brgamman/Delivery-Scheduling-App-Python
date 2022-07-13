#Benjamin Gamman, 001439763
"""Load.py defines the Load and LoadList classes and associated methods."""

from Package import Package
from Package import PackageTable
from Location import Location
from Location import LocationTable
from datetime import time
from math import ceil

class Load:
    """The Load class holds information about one load of packages to be delivered."""
    #Space complexity: O(N)
    #The Load object has list data members that may contain up to N items, if every package or stop is assigned to the same load.
    
    def __init__(self, capacity, label=''):
        """Initializes a Load with the specified capacity and label, leaving other information as blank/default values."""
        #Space Complexity: O(1)
        #Each load has only a limited number of values assigned to its members when initialized, though it may be expanded to O(N) later when items are added to lists.
        #Time complexity: O(1)
        #Each Load object takes O(1) time to initialize, so O(N) time is used to create a variable number of them.        

        self.label=label
        self.stops=set()
        self.package_list=[]
        self.truck_requirement=0
        self.truck_assigned=0
        self.departure_time=time(0,0)
        self.route=[]
        self.capacity=capacity

    def print_route(self, locations, packages):
        """This method prints the time, distance, location, and packages delivered at each stop for one load of packages."""
        #Space Complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects, which are each O(N^2).
        #Time complexity: O(N^2)
        #The method loops through print commands for each stop in a load's route list, and through each package in the load's package list within that.
        #The nested loops, each of which has potentially O(N) time complexity, multiply to O(N^2).

        print(self.label+' Load'+', '+'Truck '+str(self.truck_assigned))
        print('     Time:        Distance:      Stop Address:                   Packages Delivered:')
        for stop in self.route:
            print('     '+str(stop[4])+'     '+'{0:>4.1f}'.format(stop[2])+' miles     '
                +'{0:<29}'.format(locations.table[stop[0]].address[:29]), end='   ')
            for id in self.package_list:
                if packages.table[id].delivery_time==stop[4]:
                    print('#'+str(id), end='  ')
            print()
        print()
        
    def add(self, package, packages, locations, loadslist):
        """Adds the specified Package object to the specific load, and recursively adds bundled packages."""
        #Space Complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects, which are each O(N^2).
        #Time complexity: O(N^2)
        #The add method can call itself recursively, but also has safeguard checks built-in to only do so if the target package is not already sorted.
        #This means that while a call to the function not resulting in recursion would have time complexity O(N) (checking each other package),
        #a call triggering recursion will still only have worst case time and space complexities of O(N2).
        #This is because in a worst case in which a package is connected to every other package by either bundle or shared location,
        #the function will end up calling itself for each other package, but not calling itself for the same packages repeatedly,
        #for a total of O(N) checks made by each of O(N) packages for a maximum of O(N^2) time complexity.
        #Because of the check that the package has not already been sorted, any subsequent calls after that worst case will only have O(1) time complexity though,
        #as all packages would have been sorted.
        
        #First checks that the package selected is not yet sorted (assigned to a load), that the load is not already at capacity,
        #and that the package is not required to be on a different truck than that assigned to the load.
        #If accepted, the package's ID is added to the load's list of packages and the load's index in LoadList is attached to the Package object,
        #so that the Load's information can be accessed using the Package object later.
        if (package.sorted==False and len(self.package_list)<self.capacity
            and (self.truck_requirement==0
            or package.truck_requirement==0
            or self.truck_requirement==package.truck_requirement)):
                self.package_list.append(package.id)
                package.load_ind=loadslist.index(self)
                package.sorted=True                    
                
                #If the load does not have a truck requirement already and the package does, sets the same value for the load.
                if self.truck_requirement==0 and package.truck_requirement!=0:
                    self.truck_requirement=package.truck_requirement

                #If the package has an associated bundle, recursively adds those packages.
                if package.bundle!=set():
                    for id in package.bundle:
                        if packages.table[id].sorted==False and len(self.package_list)<self.capacity:
                            self.add(packages.table[id], packages, locations, loadslist)

                #If the package's destination key indicates a known address, adds that location to the load's stops.
                #Then recursively adds other packages with the same destination, provided they are not delayed.
                if package.destination>0:
                    self.stops.add(package.destination)
                    for id in locations.table[package.destination].package_list:
                        if (packages.table[id].delay_time==time(0,0)
                        and packages.table[id].sorted==False and len(self.package_list)<self.capacity):
                            self.add(packages.table[id], packages, locations, loadslist)

class LoadList:
    """The LoadList class holds a list of all loads into which packages are sorted."""
    #Space complexity: O(N)
    #Though each indivdual Load may be O(N), and the LoadList will contain a variable number of them, their total size will not exceed O(N).
    #The Load's variable size data members are lists of packages and stops, the total number of either of which cannot exceed O(N) across all loads
    #(each package is in one and only one load, and there wll not be more stops, other than starting and ending at the hub, than the number of packages).
    #So, the size of LoadList can be expressed as: (size of static size members)+(size of all package list items)+(size of all route list items)
    #                                               =(O(1) for those of each Load*number of loads)+O(N)+O(N)
    #                                               =c*O(1)+2*O(N)
    #                                               =O(1)+O(2N)
    #                                               =O(N)

    
    def __init__(self, num_packages, load_capacity, labels=[]):
        """Initializes the LoadList by generating the minimum number of loads required to include all packages and assigning them the provided labels."""
        #Space Complexity: O(N)
        #Each Load object may be O(N) eventually, but is O(1) at initialization (before items are added to lists),
        #so O(N) space is used to create a variable number of them.
        #Time complexity: O(N)
        #Each Load object takes O(1) time to initialize, so O(N) time is used to create a variable number of them.
        
        self.list=[]
        min_loads=ceil(num_packages/load_capacity)
        for i in range(min_loads):
            if len(labels)>i:
                next_label=labels[i]
            else:
                next_label='Load '+str(i+1)
            new_load=Load(load_capacity, next_label)
            self.list.append(new_load)

    def sort(self, packages, locations):
        """This method sorts all of the packages in the provided PackagesList object into loads to be delivered together."""
        #Space Complexity: O(N^2)
        #The method accesses the PackageTable and LocationTable objects, which are each O(N^2).
        #Time complexity: O(N^2)
        #The most complex portion of the method uses nested loops to check for locations near a load's existing stops
        #and add those locations' packages to the load by calling the Load.add(Package) method.
        #These loops can be reduced to "for at most the remaining capacity of the load, add qualifying package."
        #The time complexity of the add method may be O(N^2) for one worst case scenario (with maximum recursion), but any subsequent calls would then be O(1),
        #else it could execute repeated calls each at O(N).
        #So these loops could execute a worst case of 1*O(N^2)+N*O(1)=O(N^2) or N*O(N)=O(N^2), in either case giving the loop O(N^2) time complexity.
        #That s the most complex portion of the method, so its overall time complexity is also O(N^2).

        #The algorithm I designed requires three loads, so this generates additional loads if less were created initially.
        while len(self.list)<3:
            new_load=Load(self.list[0].capacity, 'Load '+str(len(self.list)+1))
            self.list.append(new_load)

        #Packages with deadlines before 10:30 are sorted into the first load, to ensure they make the early deadline on time.
        #Dependencies (bundled packages or those going to the same location) are also added automatically by recursive calls in the add method.
        for p in packages.table[1:]:
            if p.deadline!=time(0,0) and p.deadline<time(10,30):
                self.list[0].add(p, packages, locations, self.list)

        #Packages with destinations in ring 2 and within 3 miles of already-added stops (and with no delays at the location) are added to the first load.
        #The first load will have to range far from the hub to deliver early deadlines and dependencies,
        #so this takes care of stops that might be remote for other routes but will add less mileage here.
        #For efficiency, breaks out of loops if the load is full.
        for id in self.list[0].package_list:
            if len(self.list[0].package_list)==self.list[0].capacity:
                break
            for l in locations.table:
                if len(self.list[0].package_list)==self.list[0].capacity:
                    break
                if (l.ring==2 and l.delay==False
                and locations.distances[packages.table[id].destination][l.key]<3.0):
                    for id2 in l.package_list:
                        self.list[0].add(packages.table[id2], packages, locations, self.list)
                        if len(self.list[0].package_list)==self.list[0].capacity:
                            break

        #Determines the "dominant region" representing approximately half of the map for the first load and adds packages that are in ring 2 and that region (with no delay) to the load.
        #Adding these stops from ring 2 will make the shape of the route more of a circuit,
        #while keeping them in its dominant region prevents it from traversing the entire perimeter of the map.
        #For efficiency, breaks out of loops if the load is full.
        region_sum=0
        for stop in self.list[0].stops:
            region_sum+=locations.table[stop].region
        dominant_region=round(region_sum/len(self.list[0].stops))
        for p in packages.table[1:]:
            if len(self.list[0].package_list)==self.list[0].capacity:
                break
            l=locations.table[p.destination]
            if l.ring==2 and l.region==dominant_region and p.delay_time==time(0,0):
                self.list[0].add(p, packages, locations, self.list)

        #Packages with a delay are added to the second load.
        #This is essential because they cannot leave with the first load (deadlines before these packages are available),
        #but leaving in the third load may not get them to their destinations in time.
        for p in packages.table[1:]:
            if p.delay_time!=time(0,0):
                self.list[1].add(p, packages, locations, self.list)

        #Determines the second load's dominant region and adds packages to the load from destinations that are either:
        #in the dominant region and within 2 miles of existing stops (being in the dominant region means they are likely to be near multiple stops, so a wider range of distances is okay),
        #or in the non-dominant region within 1 mile of existing stops (some regional crossover is okay, and revisiting these areas later would likely be less efficient,
        #but they need to be very close to existing stops to be worth it).
        #For efficiency, breaks out of loops if the load is full.
        region_sum=0
        for stop in self.list[1].stops:
            region_sum+=locations.table[stop].region
        dominant_region=round(region_sum/len(self.list[1].stops))
        for id in self.list[1].package_list:
            if len(self.list[1].package_list)==self.list[1].capacity:
                break
            for l in locations.table:
                if len(self.list[1].package_list)==self.list[1].capacity:
                    break
                if ((l.region==dominant_region
                and locations.distances[packages.table[id].destination][l.key]<2.0)
                or (l.region!=dominant_region
                and locations.distances[packages.table[id].destination][l.key]<1.0)):
                    for id2 in l.package_list:
                        self.list[1].add(packages.table[id2], packages, locations, self.list)
                        if len(self.list[1].package_list)==self.list[1].capacity:
                            break
                        
        #While there are any packages left unsorted, they are placed in the last load in the list. If that load is full, a new Load object is generated and added.
        #Most of the packages remaining with known destinations should be grouped relatively well,
        #or at least in clusters that were not reached by the geographical sorting done on the earlier loads.
        #This section also covers packages with unknown destinations (applies to those with incorrect information provided and new address not yet available as well).
        #These packages are thereby delivered toward the end of the day, when their destinations will hopefully be known/updated,
        #and in a load that is not strictly bound geographically to avoid disturbing more carefully sorted routes.
        leftovers=True
        while leftovers==True:
            leftovers=False
            if len(self.list[len(self.list)-1].package_list)==self.list[len(self.list)-1].capacity:
                new_load=Load(self.list[0].capacity, 'Load '+str(len(self.list)+1))
                self.list.append(new_load)
            for p in packages.table[1:]:
                if p.sorted==False:
                    Leftovers=True
                    self.list[len(self.list)-1].add(p, packages, locations, self.list)
