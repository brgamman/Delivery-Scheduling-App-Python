#Benjamin Gamman, 001439763
"""Package.py defines the Package and PackageTable classes and associated methods."""

from datetime import datetime
from datetime import time
from Location import Location
from Location import LocationTable
import csv


class Package:
    """The Package class stores data associated with individual packages. Destinations are stored as a location key rather than full addresses, to avoid redundant data and maintain consistency."""
    #Space complexity: O(N)
    #In most cases closer to O(1), but it is possible to reach N pieces of data in the object
    #if an individual package is bundled with all other packages and thus has a bundle set of size N.

    def __init__(self, id):
        """Initializes a Package object with a unique ID number; other information is set to default values."""
        #Time complexity: O(1)
        #Though more will be required to populate the object's fields later, initialization executes only a set number of assignments.
        #Space complexity: O(1)
        #Although a Package object may use up to O(N) space, this will be filled in the import process, not initialization.

        self.id = id
        self.destination=0
        self.weight=0
        self.truck_requirement=0
        self.delay_time=time(0,0)
        self.deadline=time(0,0)
        self.bundle=set()
        self.update_time=time(0,0)
        self.corrected_address=''
        self.notes=''
        self.sorted=False
        self.load_ind=-1
        self.delivery_time=time(0,0)

    def print_package_status(self, packages, locations, loads, status_time):
        """This method prints information about a provided Package object along with its status at a specified time."""
        #Time complexity: O(1)
        #This executes a set number of instructions for a single Package object.
        #Space complexity: O(N^2)
        #The method accesses PackageTable and LocationTable structures that use O(N^2) space.       
        
        print('{0:>11}'.format(self.id), end='   ')
        print('{0:>4}'.format(str(self.weight)), end=' kg     ')
        print('{0:>29}'.format(locations.table[self.destination].address[:29]), end='  ')
        print('{0:>16}'.format(locations.table[self.destination].city), end=', ')
        print(locations.table[self.destination].state, end=' ')
        print(locations.table[self.destination].zip, end='     ')
        if self.deadline==time(0,0):
            print('{0:>8}'.format('EOD'), end='     ')
        else:
            print(self.deadline.strftime('%H:%M %p'), end='     ')
        if self.delivery_time<=status_time:
            print('Delivered by Truck '+str(loads.list[self.load_ind].truck_assigned)
                  +' at '+self.delivery_time.strftime('%H:%M %p'))
        elif loads.list[self.load_ind].departure_time<=status_time:
            print('En route, loaded onto Truck '+str(loads.list[self.load_ind].truck_assigned)
                  +' at '+loads.list[self.load_ind].departure_time.strftime('%I:%M %p'))
        elif self.delay_time>status_time:
            print('Delayed, arriving at the Hub at '+self.delay_time.strftime('%I:%M %p'))
        else:
            print('At the Hub')

class PackageTable:
    """The PackageTable class functions as a direct access hash table to index all created Package objects."""
    #Space complexity: O(N^2)
    #It is possible for each Package object to have N items in its bundled packages set. These can (and often will) be repeated in the corresponding packages' sets,
    #so the table's size will be N packages times O(N) for each package, giving O(N^2).
    
    def __init__(self):
        """Initializes an empty PackageTable. The first entry is filled with None so that the the highest index of the table will match the most recently added Package's ID."""
        self.table=[None]
        #Time complexity: O(1)
        #Though more will be required to populate the object's fields later, initialization executes only a set number of assignments.
        #Space complexity: O(1)
        #Although a PackageTable object may use up to O(N^2) space, this will be filled in the import process, not initialization.

    def insert(self, package):
        """This method inserts a Package by increasing the table's size by 1 (to match the new index to the Package's ID, assuming Packages are added in order), then inserting the Package at the index of its ID number."""
        #Time complexity: O(1)
        #Only two operations are performed, appending a list item and the assignment of a reference variable for the Package object being added.
        #Space complexity: O(N^2)
        #Insertion accesses the PackageTable, which is O(N^2).

        self.table.append(None)
        self.table[package.id]=package
        
    def lookup(self, locations, loads, search_term, status_time):
        """This method searches the table of packages for those matching a provided search term or status at a specified time and returns a list of matching Package objects."""
        #Time complexity: O(N)
        #In the case that the search term registers as a package id number, just one Package object is added to the matches list and returned.
        #Otherwise each package is checked for one of two sets of criteria depending n the search term,
        #performing the checks and operations N times in either case, producing O(N) runtime.
        #Space complexity: O(N^2)
        #Lookup accesses the PackageTable, which is O(N^2).
        
        matches=[]
        
        #Immediately selects the package with matching ID if search term is a valid ID number, in which case only this is returned.
        if search_term.isdigit() and int(search_term)<len(self.table):
            matches=[self.table[int(search_term)]]

        #Searches based on status at specified time if search term is a designated status.
        elif search_term in {'delivered', 'en route', 'at hub', 'delayed'}:
            for p in self.table[1:]:
                if ((search_term=='delivered' and p.delivery_time<=status_time)
                or (search_term=='en route' and p.delivery_time>status_time
                and loads.list[p.load_ind].departure_time<=status_time)
                or (search_term=='at hub' and p.delay_time<=status_time
                and loads.list[p.load_ind].departure_time>status_time)
                or (search_term=='delayed' and p.delay_time>status_time)):
                    matches.append(p)
                    
        #Otherwise, compares search term to several other pieces of the Package's information.
        else:
            for p in self.table[1:]:
                if (search_term==str(p.weight)+' kg'
                or search_term in locations.table[p.destination].address
                or search_term in locations.table[p.destination].city
                or search_term==locations.table[p.destination].state
                or search_term==locations.table[p.destination].zip):
                    matches.append(p)
                if ':' in search_term:
                    if datetime.time(datetime.strptime(search_term, '%I:%M %p'))==p.deadline:
                        matches.append(p)
        return matches

    def import_csv(self, packages_file, locations):
        """This method populates the PackageTable with information from a csv file."""
        #Time complexity: O(N^2)
        #The most complex portions of the method involve taking actions in nested loops for each line in the import file (each package) and locations in the locations table
        #("for each package, for each location").
        #There is also a loop for each package through its bundle list, which could reach O(N^2) in a worst case that all packages are bundled together.
        #Space complexity: O(N^2)
        #This method will populate a PackageTable object, which will use O(N^2) space, from a csv file which will contain a corresponding O(N^2) pieces of data,
        #although this will be closer to O(N) as long as bundles of packages are relatively small, which should usually be the case.

        #Opens the file, then generates a Package object and adds appropriate information to the object from each line of the file.
        #This requires a csv file to be formatted correctly, with the various different types of "notes" split into their own distinct columns.
        packages_import=csv.reader(open(packages_file), delimiter=',')
        for line in packages_import:
            p=Package(int(line[0]))
            p_address=line[1]
            if line[5]!='EOD':
                p.deadline=datetime.time(datetime.strptime(line[5], '%I:%M %p'))
            p.weight=int(line[6])
            if line[7]!='':
                b=line[7].split('/')
                for x in b:
                    p.bundle.add(int(x))
            if line[8]!='':
                p.delay_time=datetime.time(datetime.strptime(line[8], '%H:%M'))
            if line[9]!='':
                p.truck_requirement=int(line[9])
            p.notes=line[12]

            #If the package has the wrong address, removes its existing destination information, then sets a time at which the corrected address's key will replace it.
            if line[10]!='':
                p.update_time=datetime.time(datetime.strptime(line[10], '%H:%M'))
                p.destination=-1
                p.corrected_address=line[11]
                p_address=''

            #Then assigns the package a location key based on the address in the file, and fills city, state, and zip information for the location object if not already filled.
            for l in locations.table:
                if l.address==p_address:
                    p.destination=l.key
                    l.package_list.append(p.id)
                    if l.city=='':
                        l.city=line[2]
                        l.state=line[3]
                        l.zip=line[4]
                    if ((p.deadline!=time(0,0) and p.deadline<l.deadline)
                    or (p.deadline!=time(0,0) and l.deadline==time(0,0))):
                        l.deadline=p.deadline
                    if p.delay_time!=time(0,0):
                        l.delay=True

            #Then inserts the Package object into the PackageTable.
            self.insert(p)

        #Lastly, runs through the table checking for packages with "bundle" information ("must be delivered with").
        #Each package in the current package's bundle has the current package added to its own bundle.
        #This creates a web of two-way connections, so that all packages connected by bundles are placed in the same load when any one of them is sorted later.
        #Ths must be done in a separate loop after all Packages have been created and added to the table,
        #otherwise those referenced in a bundle may not have been generated yet and would be missed.
        for p in self.table[1:]:
            if p.bundle!={}:
                for id in p.bundle:
                    self.table[id].bundle.add(p.id)
