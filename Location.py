#Benjamin Gamman, 001439763
"""Location.py defines the Location and LocationTable classes and associated methods."""

from datetime import time
from math import fabs
import csv

class Location:
    """The Location class stores data associated with individual locations, except for distances to each other."""
    #Space complexity: O(N)
    #In most cases closer to O(1), but it is possible to reach N pieces of data in the object if an individual location has all packages in its package list.

    def __init__(self, name, address, key):
        """Initializes a Location object with a name, address, and unique key; other information is set to default values."""
        #Time complexity: O(1)
        #Though more will be required to populate the object's fields later, initialization executes only a set number of assignments.
        #Space complexity: O(1)
        #Although a Location object may use up to O(N) space, this will be filled in the import process, not initialization.
        
        self.key=key
        self.name=name
        self.address=address
        self.city=''
        self.state=''
        self.zip=''
        self.package_list=[]
        self.deadline=time(0,0)
        self.avg_dist=0
        self.ring=0
        self.region=0
        self.delay=False

class LocationTable:
    """The LocationTable class contains two data structures: a table to index all created Location objects, and a matrix to hold distance information at corresponding indices."""
    #Space complexity: O(N^2)
    #The class is composed of two data structures. 
    #The table holding the location objects themselves will be O(N). Although one individual location may also be O(N),
    #that is only the case if its package list contains all packages, in which case all other location objects would have empty package lists and be O(1), so O(N)+c*O(1) gives O(N).
    #Another way to arrive at this conclusion is to reason that altogether, the table will contain a set amount of data for each location, O(N),
    #plus one entry for each package in their package lists collectively, O(N), giving O(N)+O(N)=O(N).
    #However, the matrix of distances will be O(N^2) as each location's row contains an entry for each location, making ths the LocationTable's overall space complexity.

    def __init__(self):
        """Initializes a LocationTable with emptry data structures."""
        #Time complexity: O(1)
        #Though more will be required to populate the object's fields later, initialization executes only a set number of assignments.
        #Space complexity: O(1)
        #Although a LocationTable object may use up to O(N^2) space, this will be filled in the import process, not initialization.
        
        self.table=[]
        self.distances=[]

    def import_csv(self, locations_file):
        """This method populates the LocationTable's data structures with information from a csv file."""
        #Time complexity: O(N^2)
        #The most complex portions of the method involve taking actions in nested loops through locations ("for each location, for each location"),
        #to populate and fill in the matrix of distances.
        #Space complexity: O(N^2)
        #This method will populate a LocationTable object, which will use O(N^2) space, from a csv file which will contain a corresponding O(N^2) pieces of data.
        
        #Opens the file and uses each line to generate a Location object, add the object to a table, and add distances to a row of the distance matrix.
        #Each location is assigned a key value that will correspond to its index in the table and each dimension of the distances matrix.
        locations_import=csv.reader(open(locations_file), delimiter=',')
        for line in locations_import:
            dist_list_str=line[2:]
            dist_list=[]
            for d in dist_list_str:
                if d!='':
                    dist_list.append(float(d))
                else:
                    dist_list.append(None)
            self.distances.append(dist_list)
            l=Location(line[0], line[1], len(self.distances)-1)
            self.table.append(l)
            
        #Because city, state, and zip are added during the import of packages later, and no packages are associated with the hub, this information is added here.
        #"(HUB)" is also added to the address of the hub to make it easer to identify in printouts of routes.
        self.table[0].address=self.table[0].address+' (HUB)'
        self.table[0].city='Salt Lake City'
        self.table[0].state='UT'
        self.table[0].zip='84107'

        #This fills in each entry in the distance table with the equivalent entry from the half of the matrix filled in by the original spreadsheet
        #(so entry[i][j]=entry[j][i], making the table bi-directional).
        for i in range(len(self.distances)):
            for j in range(len(self.distances)):
                if self.distances[i][j]!=None and self.distances[j][i]==None:
                    self.distances[j][i]=self.distances[i][j]
                    
        #Assigns each location to a "ring" based on its distance from the hub; ring 1 is closer than average to the hub, ring 2 is further.
        #This will be used later in the process of sorting the packages into loads.
        for l in self.table:
                l.avg_dist=sum(self.distances[l.key])/27
                if self.distances[l.key][0]<self.table[0].avg_dist:
                    l.ring=1
                else:
                    l.ring=2

        #First determines two "poles," locations that are distant from each other.
        #Pole 1 is the location wth the highest average distance from all others in ring 2.
        #Pole 2 is the location furthest from Pole 1 in ring 2.
        #If two points are meaningfully tied, defaults to the point further from the hub.
        #This splits the map into 2 regions roughly along a line, to be used in sorting the packages later.
        pole1=self.table[0]
        high_dist=0
        for l in self.table:
            diff_from_high=l.avg_dist-high_dist
            if diff_from_high>0.001 and l.ring==2:
                pole1=l
                high_dist=l.avg_dist
            elif fabs(diff_from_high)<0.001 and l.ring==2:
                if self.distances[l.key][0]-self.distances[pole1.key][0]>0.001:
                    pole1=l
                    high_dist=l.avg_dist
        pole2=self.table[0]
        high_dist=0
        for l in self.table:
            diff_from_high=self.distances[l.key][pole1.key]-high_dist
            if diff_from_high>0.001 and l.ring==2:
                pole2=l
                high_dist=self.distances[l.key][pole1.key]
            elif fabs(diff_from_high)<0.001 and l.ring==2:
                if self.distances[l.key][0]-self.distances[pole2.key][0]>0.001:
                    pole2=l
                    high_dist=self.distances[l.key][pole1.key]
                    
        #Each location is assigned to a region based on which pole is nearer.
        #If equidistant between the poles and in ring 1, chooses the pole closer to the hub.
        #If equidistant between the poles and in ring 2, chooses the pole further from the hub.
        for l in self.table:
            p1_dist=self.distances[l.key][pole1.key]
            p2_dist=self.distances[l.key][pole2.key]
            if p1_dist-p2_dist<-0.001:
                l.region=1
            elif p1_dist-p2_dist>0.001:
                l.region=2
            else:
                if l.ring==1:
                    if self.distances[pole1.key][0]<self.distances[pole2.key][0]:
                        l.region=1
                    else:
                        l.region=2
                elif l.ring==2:
                    if self.distances[pole1.key][0]>self.distances[pole2.key][0]:
                        l.region=1
                    else:
                        l.region=2
