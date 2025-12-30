###############################################################################
# Program: service_line.py
# Updated: 30th of December 2025
# Version: 2.4
# Goal: Simulate a single Service Line then a hierarchical one
#       (one chief many collaborators) that work on service 
#       requests by many different strategies.
#       The simulation evaluates many types of 
#       performance-parameters and compare them.
# MIT License
# 
# Copyright (c) 2025 Marco Mattiucci
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################



import numpy as np
import random



###################################################
# SIMULATION PARAMETERS (you can change them):
###################################################
# To be set:
NR_OF_SAMPLES = 1000            # Number of times that the simulator repeats the test
TOTAL_NR_OF_TIME_UNITS = 3000   # Number of temporal units in the timeline for every test
TIME_TO_SERVE_A_REQUEST = 20    # Average time (temporal units) to serve a single request
MULTIPLICATION_FACTOR = 2       # Multiplication factor for getting the max time units to serve a single request
RANDOM_VARIABLE_WEIGHTS = True  # True - the time to serve a request is random; False - the time to serve a request is unique
RANDOM_PRIORITY_SET = True      # True - there are requests with priority - False - there are not priorities
PRIORITY_PROBABILITY_PER_REQUEST = 0.2      # if there is a request this is the probability that is a priority request
REQUEST_PROBABILITY_PER_TIME_UNIT = 0.013   # probability that there is a request in a single time unit
SUBREQUEST_PROBABILITY_PER_REQUEST = 0.8    # probability that a request for hiearchical structure requires delegated executions 
NR_OF_COLLABORATORS = 3                     # The hierarchy is with only one chief and this nr of direct collaborators
###################################################
# CONSTANT PARAMETERS (do not change them):
###################################################
ID_REQUESTS = 1     # Identifier for requests (objects)
ID_SERVICE_LINE = 1 # Identifier for service lines (objects)
ID_HIERARCHY = 1    # Identifier for hierarchies (objects)
ACTIVE_REQUEST = 1  # Value for active requests (to be served)
REQUEST_COMPLETION = 2  # Value for completed requests (to be removed from the queue)
WAITING_REQUEST = 3     # Value for waiting requests (waiting for delegated requests to be completed)
RANDOM_MAX_TIME_TO_SERVE_A_REQUEST = MULTIPLICATION_FACTOR*TIME_TO_SERVE_A_REQUEST # Max time units to serve a single request
SEQUENTIAL = 1  # Value for Sequential Strategy
CONCURRENT = 2  # Value for Concurrent Strategy
LOOKFORMAX = 3  # Value for look for max weight Strategy
LOOKFORMIN = 4  # Value for look for min weight Strategy
RANDOMCHOICE = 5    # Value for (request) random choice Strategy
RESET = "\033[0m"   # Reset colors of characters
RED = "\033[31m"    # Red color character
GREEN = "\033[32m"  # Green color character
BLUE = "\033[34m"   # Blue color character
###################################################



##########################################################################
## Class of objects: myServiceRequest.
##                   This object is a service request.
##########################################################################
class myServiceRequest:

    #####################################
    # ATTRIBUTES(myServiceRequest):
    service_id = None           # Value of the identifier of the request (unique)
    time_to_start = None        # Position of the timeline (time unit) when the request starts
    time_to_live = None         # Real time number of the time units needed for the completion of the problem (real time weight)
    minimum_duration = None     # Weight of the problem related to the request (minimum time units needed for completion)
    time_of_completion = None   # Position of the timeline (time unit) when the related problem is completed
    status = None               # Status of the request: ACTIVE (running), WAITING (for delegated), COMPLETION (removed)
    priority = None             # If this is True then the request has to be served immediately
    list_of_requests_it_is_waiting_for = None   # If the status is WAITING then this is the list of the delegated sub-requests
    ####################################

    #############################################################################################
    # METHODS(myServiceRequest): CONSTRUCTOR
    # This is the constructor of the request-object, it requires the starting time, the priority and the list of the 
    # deledated sub-requests if non-empty.
    def __init__(self,time_to_start,time_to_live,activate_priority,list_of_requests_it_is_waiting_for = []):
        global ID_REQUESTS,ACTIVE_REQUEST, WAITING_REQUEST
        self.service_id = ID_REQUESTS   # set the value od the object identifier
        ID_REQUESTS += 1                # increase the global identifier of the request-objects
        self.time_to_start = time_to_start  # Starting time = time of request arrival
        self.time_to_live = self.minimum_duration = time_to_live    # At the beginning time_to_live and minimum_duration are the same
        self.priority = activate_priority   # Set the priority of the object
        self.list_of_requests_it_is_waiting_for = list_of_requests_it_is_waiting_for    # Set the list of sub-requests
        if list_of_requests_it_is_waiting_for == []:
            self.status = ACTIVE_REQUEST    # if there are not sub-request the object is ACTIVE and running
        else:
            self.status = WAITING_REQUEST   # if there are sub-request the object waits for them to be completed

    #############################################################################################
    # METHODS(myServiceRequest): EXECUTION
    # This methond receives as input the time unit of the timeline we're working on and
    # serves the problem related to the request.
    def serve_request(self,time_unit):
        if self.status == ACTIVE_REQUEST:   # When ACTIVE decrement the time to live
            self.time_to_live -= 1
            if self.time_to_live > 0:       # If the time to live is positive then the problem has been served 
                return True                 # and the simulation goes on (return True)
            else:
                self.status = REQUEST_COMPLETION    # If the time to live is zero the problem has been solved 
                self.time_of_completion = time_unit # Set the completion time with the current unit 
                return True                         # and the simulation goes on (return True)
        elif self.status == WAITING_REQUEST:
            if self.list_of_requests_it_is_waiting_for == []:   # if the request is waiting but there are not sub-request: ERROR!
                print("ERROR FROM .serve_request(): bad request waiting status, id",self.service_id)
                quit()
            else:                                   # If the request is waiting and there are sub-requests, we check their status
                for r in self.list_of_requests_it_is_waiting_for:
                    if r.status != REQUEST_COMPLETION:
                        return False                # if there is at least one non-completed sub-request the request still waits (continue simulation with WAIT)
                self.status = ACTIVE_REQUEST        # otherwise the request goes into an ACTIVE status (verification of results)
                return True                         # continue simulation with ACTIVE
        return False    # For any other status the request is not processed

    #############################################################################################
    # METHODS(myServiceRequest): PRINT DETAILS
    # This methond prints the object attributes:
    def show_request(self):
        if  self.status == ACTIVE_REQUEST:
            print((self.service_id,self.time_to_start,self.time_to_live,self.priority,"A"),end="")
        elif  self.status == WAITING_REQUEST:
            print((self.service_id,self.time_to_start,self.time_to_live,self.priority,"W"),end="")
        elif  self.status == REQUEST_COMPLETION:
            #print((self.service_id,self.time_to_start,self.time_to_live,self.priority,"C"),end="")
            print(end="")
        else:
            print("ERROR FROM .show_request(): bad request status, id",self.service_id)
            quit()
    #############################################################################################




##########################################################################
## Class of objects: myServiceLine.
##                   This object is a service Line with decision and
##                   management tools embedded.
##########################################################################
class myServiceLine:

    #####################################
    # ATTRIBUTES(myServiceLine):
    service_line_id = None  # Value of the identifier of the request (unique)
    queue = None            # list of request objects
    arrivals = None         # LOG of the arrived requests
    nr_of_times_empty_line = None           # Number of time slots where the queue is empty
    percentage_of_active_requests = None    # Real time percentage of the active requests in the queue
    accumulate_nr_of_active_requests = None # Variable used to calculate the mean value of the number of requests to be served in every slot
    max_nr_of_pending_requests = None       # Real time number of requests in the queue that are in active status.
    empty_time_unit = None  # 
    concurrent_idx = None   # Value for rotating the selection of the requests to be served in the concurrent strategy
    service_type = None     # Strategy of the line - can be: SEQUENTIAL,CONCURRENT,LOOKFORMAX,LOOKFORMIN,RANDOMCHOICE
    #####################################

    #############################################################################################
    # METHODS(myServiceLine): CONSTRUCTOR
    # This is the constructor of the Line-object, it requires the service type (the decision strategy).
    def __init__(self,service_type):
        global SEQUENTIAL,CONCURRENT,ID_SERVICE_LINE,LOOKFORMAX
        self.service_line_id = ID_SERVICE_LINE  # set the value od the Line identifier
        ID_SERVICE_LINE += 1                    # increase the global identifier of the Line-objects
        # Initialize attributes:
        self.queue = list()         # Initialize the request queue as an empty list
        self.arrivals = list()      # Initialize the request arrival LOG as an empty list
        self.nr_of_times_empty_line = 0             # Set zero time slots with empty queue
        self.percentage_of_active_requests = 0      # Set zero percentage of active requests
        self.accumulate_nr_of_active_requests = 0   # Set no active requests
        self.max_nr_of_pending_requests = 0         # Set no pending requests
        self.concurrent_idx = 0   # Initialize the rotation of requests for concurrent strategy
        # Verify the service type:
        if service_type == SEQUENTIAL or service_type == CONCURRENT or service_type == LOOKFORMAX or service_type == LOOKFORMIN or service_type == RANDOMCHOICE:
            self.service_type = service_type
        else:
            print("ERROR FROM myServiceLine CONSTRUCTOR: unknown service line type",service_type)
            quit()

    #############################################################################################
    # METHODS(myServiceLine): INSERT NEW PROBLEM TO SOLVE
    # This methond receives as input the time unit, the time to serve the request, the priority of the
    # request, and the list of the related sub-requests. Then it inserts the request in the queue.
    def insert_new_incoming_request(self,time_unit,time_to_serve_the_request = TIME_TO_SERVE_A_REQUEST,activate_priority = False,list_of_requests_it_is_waiting_for = []):
        global REQUEST_PROBABILITY_PER_TIME_UNIT,TIME_TO_SERVE_A_REQUEST,ACTIVE_REQUEST
        # Create the new request object:
        r = myServiceRequest(time_unit,time_to_serve_the_request,activate_priority,list_of_requests_it_is_waiting_for)
        # Append the new request in the queue:
        self.queue.append(r)
        # Verify how many requests in queue are in active status, so they need to be served:
        l = len([r for r in self.queue if r.status == ACTIVE_REQUEST])
        if l > self.max_nr_of_pending_requests:
            self.max_nr_of_pending_requests = l
        # Insert a new item in the arrived request LOG:
        self.arrivals.append((time_unit,time_to_serve_the_request,activate_priority,(list_of_requests_it_is_waiting_for != [])))
        # Return the new request object:
        return r

    #############################################################################################
    # METHODS(myServiceLine): DECISION AND EXECUTION
    # This methond receives as input the time unit. Then process the requests in queue by a specific
    # strategy (one of 5 strategies provided). Also requests with priorities can be managed.
    def process_queued_requests(self,time_unit):
        #
        # If there are priority requests then the first of them in the list has to be served:
        # This is not a decision strategy, it is just mandatory for the system.
        #
        l = len(self.queue)
        if l > 0:
            # handle only if the queue is non-empty;
            # get the number of active requests to be served:
            nr_of_active_requests = len([r for r in self.queue if r.status == ACTIVE_REQUEST])
            # increase the variable to calculate (at the end) the mean value of the active requests number for every time slot:
            self.accumulate_nr_of_active_requests += nr_of_active_requests
            # get the real time percentage of active requests in the queue:
            self.percentage_of_active_requests = nr_of_active_requests/l
            # get the number of active requests with priority set in the queue:
            l_priority = len([r for r in self.queue if r.priority])
            if l_priority > 0:
                # if there are active requests with priority set serve the first one in the queue:
                for r in self.queue:
                    if r.priority:
                        if r.serve_request(time_unit):
                            return True
        #
        # Strategy 1 - Sequential execution strategy - "Bureaucrat":
        #
        if self.service_type == SEQUENTIAL:
            # In this strategy look for the first request in the queue that after served returns True:
            # True means that something has been done.
            for r in self.queue:
                if r.serve_request(time_unit):
                    return True
            # If no request with such condition has been found then the queue is empty:
            self.nr_of_times_empty_line += 1  # increase the number of time units where the queue is empty.
            return False
        #
        # Strategy 2 - Concurrent execution strategy - "meticulous all-rounder":
        #
        elif self.service_type == CONCURRENT:
            # In this strategy the variable concurrent_idx (IDX) is used to select one by one all the active requests.
            # IDX starts from 0 and increases every time an active request is met.
            for r in self.queue:
                # look for the first request with ID greater than IDX that after served returns True:
                if r.serve_request(time_unit) and r.service_id > self.concurrent_idx:
                    # if that request is found and served them IDX gets its ID:
                    self.concurrent_idx = r.service_id
                    # get the remaining active requests in the queue:
                    remaining_requests = [r1 for r1 in  self.queue if (r1.status == ACTIVE_REQUEST or r1.status == WAITING_REQUEST) and r1.service_id > self.concurrent_idx]
                    # if there are not other active requests to be served then IDX restarts from zero (rotation):
                    if len(remaining_requests) == 0: self.concurrent_idx = 0
                    return True
            # If no request with such condition has been found then the queue is empty:
            self.nr_of_times_empty_line += 1   # increase the number of time units where the queue is empty.
            return False
        #
        # Strategy 3 - Look for max execution strategy - "Hard worker":
        #
        elif self.service_type == LOOKFORMAX:
            # In this strategy you first look for the request with the MAXIMUM weight then serve it:
            request_with_max_weight = None  # Set the request ID to None
            max_weight = -1                 # Set the max weight to -1
            for r in self.queue:
                # evaluate the current time to live of every request in the queue:
                if r.time_to_live > max_weight:
                    max_weight = r.time_to_live     # memorize the max weight (time to live)
                    request_with_max_weight = r     # memorize the request with max weight
            if request_with_max_weight == None:
                # If no request with such condition has been found then the queue is empty:
                self.nr_of_times_empty_line += 1   # increase the number of time units where the queue is empty.
                return False
            else:
                # if the request with max time to live has been found then serve it:
                request_with_max_weight.serve_request(time_unit)
                return True
        #
        # Strategy 4 - Look for min execution strategy - "Procrastinator":
        #
        elif self.service_type == LOOKFORMIN:
            # In this strategy you first look for the request with the MINIMUM weight then serve it:
            request_with_min_weight = None # Set the request ID to None
            min_weight = 3*RANDOM_MAX_TIME_TO_SERVE_A_REQUEST  # Set the min weight to 3 times the max time to serve a request
            for r in self.queue:
                # evaluate the current time to live of every request in the queue:
                if r.time_to_live < min_weight:
                    min_weight = r.time_to_live # memorize the min weight (time to live)
                    request_with_min_weight = r # memorize the request with min weight
            if request_with_min_weight == None:
                # If no request with such condition has been found then the queue is empty:
                self.nr_of_times_empty_line += 1 # increase the number of time units where the queue is empty.
                return False
            else:
                # if the request with min time to live has been found then serve it:
                request_with_min_weight.serve_request(time_unit)
                return True
        #
        # Strategy 5 - Random execution strategy:
        #
        elif self.service_type == RANDOMCHOICE:
            if self.queue == []:
                # In this strategy you do nothing if the queue is empty:
                self.nr_of_times_empty_line += 1  # increase the number of time units where the queue is empty.
                return False
            else:
                r = random.choice(self.queue)   # In this strategy you randomly choose a request in the queue
                r.serve_request(time_unit)      # and serve it, no matter what:
                return True
        #
        # Other strategies...
        #
        ######## If you want, you can add here your own strategies ###########
        
        #
        # Error management (bad or unknown strategy parameter):
        #
        else:
            print("ERROR FROM .process_queued_requests(): unknown service line type",service_type)
            quit()

    #############################################################################################
    # METHODS(myServiceLine): TIMELINE SIMULATION
    # This methond receives as input the arrived requests LOG if non empty.
    # It runs the simulation of the service line work from 0 to TOTAL_NR_OF_TIME_UNITS in a unique timeline.
    # The arrivals LOG is very important if you want to run a simulation using the same request of another service line
    # that already worked, this to compare the performances. If you don't use it the method considers it empty and then
    # makes it during the simulation.
    def run(self,arrivals = []):
        global TOTAL_NR_OF_TIME_UNITS, REQUEST_PROBABILITY_PER_TIME_UNIT, RANDOM_MAX_TIME_TO_SERVE_A_REQUEST, TIME_TO_SERVE_A_REQUEST, PRIORITY_PROBABILITY_PER_REQUEST
        # run for the entire timeline:
        for time_unit in range(TOTAL_NR_OF_TIME_UNITS):
            if arrivals == []:
                # there are not predefined arrivals so the request arrivals are simulated now:
                if random.random() <  REQUEST_PROBABILITY_PER_TIME_UNIT:
                    # if the random number (PRNG) is less than REQUEST_PROBABILITY_PER_TIME_UNIT then a new request is arrived:
                    if RANDOM_VARIABLE_WEIGHTS:
                        # the weight of the request is random, get it from the PRNG (it is the minimum time to serve it):
                        random_time_to_serve_a_request = random.randint(1,RANDOM_MAX_TIME_TO_SERVE_A_REQUEST)
                    else:
                        # the weight of the request is NOT random, set it to TIME_TO_SERVE_A_REQUEST
                        random_time_to_serve_a_request = TIME_TO_SERVE_A_REQUEST
                    # evaluate the priority of the request always by a PRNG:
                    activate_prioritized_request = False    # Set to NO priority.
                    if RANDOM_PRIORITY_SET:
                        # the priority can be set (when the RANDOM_PRIORITY_SET parameter is False no priority can be set):
                        if random.random() <  PRIORITY_PROBABILITY_PER_REQUEST:
                            # if the PRNG generates a random number that is less than PRIORITY_PROBABILITY_PER_REQUEST
                            # the request is with priority:
                            activate_prioritized_request = True
                    # insert the new request in the queue:
                    self.insert_new_incoming_request(time_unit,random_time_to_serve_a_request,activate_prioritized_request)
                else:
                    # if the random number (PRNG) is NOT less than REQUEST_PROBABILITY_PER_TIME_UNIT: 
                    self.process_queued_requests(time_unit)     # then serve the existing requests:
            else:
                # there are predefined arrivals so we can get the requests from the existing arrivals LOG provided as input of the method
                # get the list of (time_unit,time_to_serve,priority) from the LOG where time_unit is the same as the current one:
                search_result_list = [(x,y,z,_) for (x,y,z,_) in arrivals if x == time_unit]
                if search_result_list == []:
                    # if the list is empty then we have already inserted all the requests in the LOG
                    # so, we just serve the existing requests in the queue:
                    self.process_queued_requests(time_unit)
                else:
                    # if the list is NOT empty we get the first element of the list and create the corrisponding new request in the queue:
                    (_,time_to_serve_the_request,activate_priority,_) = search_result_list[0]
                    self.insert_new_incoming_request(time_unit,time_to_serve_the_request,activate_priority)
        # At the end of the simulation:
        # 1) look for all the requests in the queue that are completed (status REQUEST_COMPLETION):
        d = [(r.time_of_completion-r.time_to_start-r.minimum_duration) for r in self.queue if r.status == REQUEST_COMPLETION]
        if d == []:
            # if there are not completed requests then a WARNING is issued and the simulation stopped:
            print("SIMULATION WARNING: there are not completed requests for service line [",self.service_line_id,"]")
            print("...simulation cannot go on!")
            quit()
        # if there are complete requests we calculate for each of them the extra time of working that is
        # (actual_end_time - actual_start_time - minimum_required_time)
        # just after that get the mean of the values in the list (average extra time of working during the simulation):
        average_extra_duration = np.mean(np.array(d))
        # 2) calculate the average_active_requests_for_time_unit:
        average_active_requests_for_time_unit = self.accumulate_nr_of_active_requests/TOTAL_NR_OF_TIME_UNITS
        # 3) return the performance parameters of the simulation:
        return np.array([average_extra_duration,average_active_requests_for_time_unit,self.nr_of_times_empty_line,self.percentage_of_active_requests,self.max_nr_of_pending_requests])

    #############################################################################################
    # METHODS(myServiceRequest): PRINT DETAILS
    # This methond prints the object attributes:
    def show_queue(self):
        print("Line",self.service_line_id,end="")
        if self.queue == []: 
            print([],end="")
        else:
            print("[",end="")
            for r in self.queue:
                r.show_request()
            print("]",end="")
    #############################################################################################




##########################################################################
## Class of objects: myServiceLineHierarchy.
##                   This object is a multiple service Line with 
##                   hierarchical structure (one level, one chief, many
##                   collaborators).
##########################################################################
class myServiceLineHierarchy:

    #####################################
    # ATTRIBUTES(myServiceLineHierarchy):
    hierarchy_id = None             # Value of the identifier of the request (unique)
    chief = None                    # Service Line object of the chief
    list_of_collaborators = None    # List of the service lines of the collaborators
    nr_of_collaborators = None      # Number of collaborators
    #####################################

    #############################################################################################
    # METHODS(myServiceLineHierarchy): CONSTRUCTOR
    # This is the constructor of the Hierarchical-Line-object, it requires the service type for
    # both chief and collaborators and the number of collaborators. Chief and collaborators can
    # use different strategies (by default SEQUENTIAL).
    def __init__(self,chief_service_type = SEQUENTIAL, nr_of_collaborators = 2, collaborator_service_type = SEQUENTIAL):
        global ID_HIERARCHY
        self.hierarchy_id = ID_HIERARCHY    # set the identifier of the Hierarchical-Line-object
        ID_HIERARCHY += 1                   # increase the global identifier of the Hierarchical-Line-objects
        self.chief = myServiceLine(chief_service_type) # create the service line object of the chief
        self.nr_of_collaborators = nr_of_collaborators # set the number of collaborators attribute
        self.list_of_collaborators = list()     # create an empty list
        for i in range(nr_of_collaborators):    # insert in the list as many service line objects as the number of collaborators:
            self.list_of_collaborators.append(myServiceLine(collaborator_service_type))

    #############################################################################################
    # METHODS(myServiceLineHierarchy): TIMELINE SIMULATION
    # This methond receives as input the arrived requests LOG if non empty.
    # It runs the simulation of the HIERARCHICAL service line work from 0 to TOTAL_NR_OF_TIME_UNITS in a unique timeline.
    # The arrivals LOG is very important if you want to run a simulation using the same request of another service line
    # that already worked, this to compare the performances. If you don't use it the method considers it empty and then
    # makes it during the simulation.
    def run(self,arrivals = []):
        global TOTAL_NR_OF_TIME_UNITS, REQUEST_PROBABILITY_PER_TIME_UNIT, RANDOM_MAX_TIME_TO_SERVE_A_REQUEST, TIME_TO_SERVE_A_REQUEST, PRIORITY_PROBABILITY_PER_REQUEST
        # run for the entire timeline:
        for time_unit in range(TOTAL_NR_OF_TIME_UNITS):
            # 
            ####### If you want to see the simulation step by step uncomment the following code #########
            #
            #active = [g for g in self.chief.queue if g.status == ACTIVE_REQUEST or g.status == WAITING_REQUEST]
            #if active != []:
            #    print("Time unit:",time_unit)
            #    self.show_hierarchy()
            #    a = input("")
            #    if a == "s": return 0
            #
            if arrivals == []:
                # there are not predefined arrivals so the request arrivals are simulated now:
                if random.random() <  REQUEST_PROBABILITY_PER_TIME_UNIT:
                    # if the random number (PRNG) is less than REQUEST_PROBABILITY_PER_TIME_UNIT then a new request is arrived:
                    if RANDOM_VARIABLE_WEIGHTS:
                        # the weight of the request is random, get it from the PRNG (it is the minimum time to serve it):
                        random_time_to_serve_a_request = random.randint(1,RANDOM_MAX_TIME_TO_SERVE_A_REQUEST)
                    else:
                        # the weight of the request is NOT random, set it to TIME_TO_SERVE_A_REQUEST
                        random_time_to_serve_a_request = TIME_TO_SERVE_A_REQUEST
                    # evaluate the priority of the request always by a PRNG:
                    activate_prioritized_request = False  # Set to NO priority.
                    if RANDOM_PRIORITY_SET:
                        # the priority can be set (when the RANDOM_PRIORITY_SET parameter is False no priority can be set):
                        if random.random() <  PRIORITY_PROBABILITY_PER_REQUEST:
                            # if the PRNG generates a random number that is less than PRIORITY_PROBABILITY_PER_REQUEST
                            # the request is with priority:
                            activate_prioritized_request = True
                    # evaluate if there are sub-requests for the new request and all of their weights:
                    if random.random() <  SUBREQUEST_PROBABILITY_PER_REQUEST:
                        # if the PRNG generates a number less than SUBREQUEST_PROBABILITY_PER_REQUEST the new request can
                        # be subdivided into sub-requests:
                        sub_requests = list()   # Set and empty list of sub-requests
                        # the weights (time to live) of every sub-request and of the main new request is the already calculated
                        # weight divided into n + 1 where n is the number of collaborators. We add one to avoid having 0 weight
                        # any case:
                        random_time_to_serve_a_subrequest = int(random_time_to_serve_a_request/(self.nr_of_collaborators+1)) + 1
                        # insert n + 1 new requests: 1 in the queue of the chief and 1 in the queue of every collaborator:
                        for i in range(self.nr_of_collaborators):
                            sub_requests.append(self.list_of_collaborators[i].insert_new_incoming_request(time_unit,random_time_to_serve_a_subrequest,activate_prioritized_request))       
                        self.chief.insert_new_incoming_request(time_unit,random_time_to_serve_a_subrequest,activate_prioritized_request,sub_requests)
                    else:
                        # if the PRNG generates a number NOT less than SUBREQUEST_PROBABILITY_PER_REQUEST the new request CANNOT
                        # be subdivided into sub-requests, so insert only the new request in the queue of the chief:
                        self.chief.insert_new_incoming_request(time_unit,random_time_to_serve_a_request,activate_prioritized_request)
                else:
                    # if the random number (PRNG) is NOT less than REQUEST_PROBABILITY_PER_TIME_UNIT: 
                    self.chief.process_queued_requests(time_unit)   # serve the requests in the queue of the chief
                    for i in range(self.nr_of_collaborators):       # serve the requests in all the queues of every collaborator
                        self.list_of_collaborators[i].process_queued_requests(time_unit)
            else:
                # there are predefined arrivals so we can get the requests from the existing arrivals LOG provided as input of the method
                # get the list of (time_unit,time_to_serve,priority,is_delegated) from the LOG where time_unit is the same as the current one:
                search_result_list = [(x,y,z,h) for (x,y,z,h) in arrivals if x == time_unit]
                if search_result_list == []:
                    # if the list is empty then we have already inserted all the requests in the LOG
                    # so, we just serve the existing requests in all the queues of the chief and collaborators:
                    self.chief.process_queued_requests(time_unit)
                    for i in range(self.nr_of_collaborators):
                        self.list_of_collaborators[i].process_queued_requests(time_unit)
                else:
                    # if the list is NOT empty we get the first element of the list and create the corrisponding new request in the queues
                    # of the chief and the collaborators:
                    (_,time_to_serve_the_request,activate_priority,delegated) = search_result_list[0]
                    if delegated:   # the request in the LOG can be subdivided into sub-requests:
                        sub_requests = list()   # create the sub-requests and insert them in the queues:
                        for i in range(self.nr_of_collaborators):
                            sub_requests.append(self.list_of_collaborators[i].insert_new_incoming_request(time_unit,time_to_serve_the_request,activate_priority))       
                        self.chief.insert_new_incoming_request(time_unit,time_to_serve_the_request,activate_priority,sub_requests)
                    else:
                        # the request in the LOG CANNOT be subdivided into sub-requests, so
                        # insert only the new request in the queue of the chief:
                        self.chief.insert_new_incoming_request(time_unit,time_to_serve_the_request,activate_priority)
        # At the end of the simulation:
        # 1) look for all the requests in the queue that are completed (status REQUEST_COMPLETION):
        d = [(r.time_of_completion-r.time_to_start-r.minimum_duration) for r in self.chief.queue if r.status == REQUEST_COMPLETION]
        if d == []:
            # if there are not completed requests then a WARNING is issued and the simulation stopped:
            print("SIMULATION WARNING: there are not completed requests for service line [",self.chief.service_line_id,"]")
            print("...simulation cannot go on!")
            quit()
        # if there are complete requests we calculate for each of them the extra time of working that is
        # (actual_end_time - actual_start_time - minimum_required_time) only related to the cbief
        # just after that get the mean of the values in the list (average extra time of working during the simulation):
        average_extra_duration = np.mean(np.array(d))
        # 2) calculate the average_active_requests_for_time_unit (only related to the chief):
        average_active_requests_for_time_unit = self.chief.accumulate_nr_of_active_requests/TOTAL_NR_OF_TIME_UNITS
        # 3) return the performance parameters of the simulation for the chief (the only observable from outside the system):
        return np.array([average_extra_duration,average_active_requests_for_time_unit,self.chief.nr_of_times_empty_line,self.chief.percentage_of_active_requests,self.chief.max_nr_of_pending_requests])
 
    #############################################################################################
    # METHODS(myServiceLineHierarchy): PRINT DETAILS
    # This methond prints the object attributes:
    def show_hierarchy(self):
        print("CHIEF:",self.hierarchy_id,end=" ")
        self.chief.show_queue()
        print()
        for c in self.list_of_collaborators:
            print("Collaborator",end=" ")
            c.show_queue()
            print()
    #############################################################################################
    


#############################################################################################
# PROCEDURE: SHOW SIMULATION PARAMETERS
#############################################################################################
def show_simulation_parameters():
    global NR_OF_SAMPLES, TOTAL_NR_OF_TIME_UNITS, RANDOM_VARIABLE_WEIGHTS, RANDOM_MAX_TIME_TO_SERVE_A_REQUEST, TIME_TO_SERVE_A_REQUEST, RANDOM_PRIORITY_SET, PRIORITY_PROBABILITY_PER_REQUEST, NR_OF_COLLABORATORS
    print("Total time units for simulation (timeline length):",TOTAL_NR_OF_TIME_UNITS)
    if RANDOM_VARIABLE_WEIGHTS:
        print("Time to serve a requests of service: RANDOM from 1 to",RANDOM_MAX_TIME_TO_SERVE_A_REQUEST," time units")
    else:
        print("Time to serve a requests of service:",TIME_TO_SERVE_A_REQUEST," time units")
    if RANDOM_PRIORITY_SET:
        print("Some requests can randomically have priority - probability per request:",PRIORITY_PROBABILITY_PER_REQUEST)
    else:
        print("No requests can have special priority")
    print("Total number of collaborators in the hierarchy with only one chief:",NR_OF_COLLABORATORS)
    print("Some requests can randomically be subdivided in sub-requests - probability per request:",SUBREQUEST_PROBABILITY_PER_REQUEST)
#############################################################################################

    
#############################################################################################
# FUNCTION: GET TOTAL PERFORMANCE SCORE (np.array)
#############################################################################################
def get_total_score(results):
    global TIME_TO_SERVE_A_REQUEST, RANDOM_MAX_TIME_TO_SERVE_A_REQUEST, TOTAL_NR_OF_TIME_UNITS
    max_average_extra_time_for_request = 4*RANDOM_MAX_TIME_TO_SERVE_A_REQUEST
    max_average_active_request_per_time_unit = results[4]
    max_empty_slots = 1.0
    max_queue_length = TOTAL_NR_OF_TIME_UNITS/RANDOM_MAX_TIME_TO_SERVE_A_REQUEST
    max_unserved_requests = 1.0
    return -results[0]/max_average_extra_time_for_request-results[1]/max_average_active_request_per_time_unit+results[2]/TOTAL_NR_OF_TIME_UNITS-results[4]/max_queue_length-results[3]
#############################################################################################


#############################################################################################
# PROCEDURE: SHOW SIMULATION RESULTS (np.array)
#############################################################################################
def show_results(results):
    print("SIMULATION PERFORMED:")
    print(f"{GREEN}##############################################################################################")
    print(f"Average extra time spent for every request:",results[0])
    print(f"Average active requests per time unit:",results[1])
    print(f"The line has been empty on the average for ",f"{results[2]/TOTAL_NR_OF_TIME_UNITS:.2%} of the total time")
    print(f"The maximum length of the queue has been on the average",results[4])
    print(f"After the process on the average the",f"{results[3]:.2%} of the incoming requests remains unserved.")
    print(f"TOTAL SCORE:",get_total_score(results))
    print(f"##############################################################################################{RESET}")
#############################################################################################


#############################################################################################
# PROCEDURE: SHOW CLUSTERS OF REQUESTS (strategy)
#############################################################################################
def show_clusters_of_requests(service_type = SEQUENTIAL):
    service_line = myServiceLine(service_type)  # create a service line following the input strategy
    show_simulation_parameters()                # show the simulation parameters
    show_results(service_line.run())            # run the service line and show the results
    print("Arrived requests:")
    print(service_line.arrivals)                # show the arrivals of requests LOG
    # get the timestamps of the arrivals from the LOG:
    arrivals_timestamps = [x for (x,_,_,_) in service_line.arrivals]
    differences = np.diff(arrivals_timestamps)  # Calculate differences between consecutive timestamps
    p25 = np.percentile(differences,25)         # get the percentile 25
    p90 = np.percentile(differences,90)         # get the percentile 90
    threshold = (p25+p90)/2                     # define the threshold for defining the clusters by the mean of the percentiles
    split_indices = np.where(differences > threshold)[0] + 1    # Identify split points where gap exceeds the threshold
    clusters = np.split(arrivals_timestamps,split_indices)      # Split the array into the defined clusters
    print("Identified clusters of requests:")
    for c in clusters:                          # print the clusters
        print(c)
    cluster_count = len(clusters)                           # get the number of clusters
    durations = np.array([c[-1]-c[0] for c in clusters])    # get the time elapsed from the first to the last request in a cluster
    sizes = np.array([len(c) for c in clusters])            # get the number of requests in each cluster
    # show the results:
    print(f"{GREEN}###############################################################")
    print(f"Cluster count:",cluster_count)
    print(f"Max Cluster duration (time units):",np.max(durations))
    print(f"Average Cluster duration (time units):",np.mean(durations))
    print(f"Max Cluster size (nr of requests):",np.max(sizes))
    print(f"Average Cluster size (nr of requests):",np.mean(sizes))
    print(f"###############################################################{RESET}")
    # draw the timeline and the clusters with different colors:
    print("Timeline, requests and clusters:")
    r_count = 1
    for i in range(TOTAL_NR_OF_TIME_UNITS):
        if any(min(c) <= i <= max(c) for c in clusters):
            if i in arrivals_timestamps:
                print(f"{RED}R",r_count,f"{RESET}",end="")
                r_count += 1
            else:
                print(f"{RED}_{RESET}",end="")
        else:
            if i in arrivals_timestamps:
                print("R",r_count,end="")
                r_count += 1
            else:
                print("_",end="")
    print()
#############################################################################################


#############################################################################################
# PROCEDURE: FULL EMULATION
#            run many service line structures, with the same strategies, NR_OF_SAMPLES times.
#############################################################################################
def emulate_multiple_lines_multiple_strategies():
    global NR_OF_SAMPLES, NR_OF_COLLABORATORS, SEQUENTIAL, CONCURRENT, LOOKFORMAX, LOOKFORMIN, RANDOMCHOICE
    nr_of_simulated_environments = 9  # total number of simulated environments
    # set the np.array for results to zeros:
    simulation_results = np.array([np.zeros(5,dtype=float) for _ in range(nr_of_simulated_environments)])
    # Set the names of the simulations:
    simulation_descriptions = [ "Hierarchical (Chief sequential - Collaborators sequential)",
                                "Hierarchical (Chief concurrent - Collaborators sequential)",
                                "Hierarchical (Chief sequential - Collaborators concurrent)",
                                "Hierarchical (Chief concurrent - Collaborators concurrent)",
                                "Single line (sequential)",
                                "Single line (concurrent)",
                                "Single line (look for max)",
                                "Single line (look for min)",
                                "Single line (random choice)"
    ]
    print("Number of samples:",NR_OF_SAMPLES)   # show the number of times the simulation on sigle timeline will be repeated
    show_simulation_parameters()                # show the simulation parameters
    print("Simulations in progress...")
    # Set a list of None, every structure object in the simulation will be pointed by the variables of this list h[]:
    h = [None for _ in range(nr_of_simulated_environments)]
    for i in range(NR_OF_SAMPLES):  # the simulation of every environment will be performed NR_OF_SAMPLES times
        if i % 100 == 0: print("step",i,"out of",NR_OF_SAMPLES)     # show the progress
        j = 0
        #
        # Hierarchical lines simulated:
        #
        # create the hierarchy SEQUENTIAL CHIEF SEQUENTIAL COLLABORATORS:
        h[j] = myServiceLineHierarchy(chief_service_type = SEQUENTIAL, nr_of_collaborators = NR_OF_COLLABORATORS, collaborator_service_type = SEQUENTIAL)
        # run the simulation and get the results
        simulation_results[j] += h[j].run()
        # the first time get the arrivals too:
        arrivals_for_hierarchy = h[j].chief.arrivals
        arrivals_for_single_line = [(x,(NR_OF_COLLABORATORS+1)*time_to_serve_the_request,y,delegated) for (x,time_to_serve_the_request,y,delegated) in h[j].chief.arrivals if delegated]
        j += 1
        # create the hierarchy CONCURRENT CHIEF SEQUENTIAL COLLABORATORS and run the simulation collecting the results:
        h[j] = myServiceLineHierarchy(chief_service_type = CONCURRENT, nr_of_collaborators = NR_OF_COLLABORATORS, collaborator_service_type = SEQUENTIAL)
        simulation_results[j] += h[j].run(arrivals_for_hierarchy)
        j += 1
        # create the hierarchy SEQUENTIAL CHIEF CONCURRENT COLLABORATORS and run the simulation collecting the results:
        h[j] = myServiceLineHierarchy(chief_service_type = SEQUENTIAL, nr_of_collaborators = NR_OF_COLLABORATORS, collaborator_service_type = CONCURRENT)
        simulation_results[j] += h[j].run(arrivals_for_hierarchy)
        j += 1
        # create the hierarchy CONCURRENT CHIEF CONCURRENT COLLABORATORS and run the simulation collecting the results:
        h[j] = myServiceLineHierarchy(chief_service_type = CONCURRENT, nr_of_collaborators = NR_OF_COLLABORATORS, collaborator_service_type = CONCURRENT)
        simulation_results[j] += h[j].run(arrivals_for_hierarchy)
        j += 1
        #
        # Single lines simulated:
        #
        # create the SEQUENTIAL service line, run the simulation and collect the results:
        h[j] = myServiceLine(SEQUENTIAL)
        simulation_results[j] += h[j].run()
        j += 1
        # create the CONCURRENT service line, run the simulation and collect the results:
        h[j] = myServiceLine(CONCURRENT)
        simulation_results[j] += h[j].run(arrivals_for_single_line)
        j += 1
        # create the LOOKFORMAX service line, run the simulation and collect the results:
        h[j] = myServiceLine(LOOKFORMAX)
        simulation_results[j] += h[j].run(arrivals_for_single_line)
        j += 1
        # create the LOOKFORMIN service line, run the simulation and collect the results:
        h[j] = myServiceLine(LOOKFORMIN)
        simulation_results[j] += h[j].run(arrivals_for_single_line)
        j += 1
        # create the RANDOMCHOICE service line, run the simulation and collect the results:
        h[j] = myServiceLine(RANDOMCHOICE)
        simulation_results[j] += h[j].run(arrivals_for_single_line)
        j += 1
    print("done:",j," strategies.")
    print("Results:") # sort performance results and show them in order from the worst to the best:
    print("---------------------------------------------------------------------------------------------------")
    score = np.array([get_total_score(simulation_results[i]/NR_OF_SAMPLES) for i in range(nr_of_simulated_environments)])
    desc = np.array(simulation_descriptions)
    idx = np.argsort(score)
    score_sorted = score[idx]
    desc_sorted = desc[idx]
    results_sorted = simulation_results[idx]
    for i in range(nr_of_simulated_environments):
        print("Strategy: ",desc_sorted[i]," TOTAL SCORE:",score_sorted[i])
    print("---------------------------------------------------------------------------------------------------")
    for i in range(nr_of_simulated_environments):
        print("Strategy: ",desc_sorted[i]," - ",end="")
        show_results(results_sorted[i]/NR_OF_SAMPLES)
    print("End.")
#############################################################################################

    



            
#################
# MAIN PROGRAM: #
#################

if __name__ == '__main__':

    # show_clusters_of_requests()

    # emulate_multiple_lines_multiple_strategies()

    print("Uncomment one of the previous lines in the main program, also both of them...")
