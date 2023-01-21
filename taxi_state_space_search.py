import search
import random
import math
import time

ids = ["313590697", "209639855"]
fix_h_2= True

def custom_BFS( start ,map,deapth =256):
    if map[start[0]][start[1]]=='I':
        return -1
    marks={}
    dist=0
    at= [start]
    marks[start[0]*1000+start[1]]=0
    width=len(map[0])-1
    length=len(map)-1
    at_next=[]
    while(dist<deapth):
        for a in at:
            x=a[0]
            y=a[1]
            if x>0:
                if not marks.get(x*1000-1000+y,0):
                    if map[x-1][y]!="I":
                        marks[x*1000-1000+y]=dist+1
                        at_next.append((x-1,y))
            if x<length:
                if not marks.get(x*1000+1000+y,0):
                    if map[x+1][y]!="I":
                        marks[x*1000+1000+y]=dist+1
                        at_next.append((x+1,y))
            if y>0:
                if not marks.get(x*1000-1+y,0):
                    if map[x][y-1]!="I":
                        marks[x*1000-1+y]=dist+1
                        at_next.append((x,y-1))
            if y<width:
                if not marks.get(x*1000+1+y,0):
                    if map[x][y+1]!="I":
                        marks[x*1000+1+y]=dist+1
                        at_next.append((x,1+y))
        dist+=1
        if 0==len(at_next):
            break
        at=at_next
        at_next=[]
    marks[start[0]*1000+start[1]]=0
    return marks

class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""
    def isPossible(self,initial):
        map=initial['map']
        pas = initial['passengers']
        taxis=initial['taxis']
        if (len(map) ==0 or 0== len(map[0])):
            return False  # no map
        for i in pas:
            index = pas[i]['location']
            if(map[index[0]][index[1]]=='I'):
                return False #count passengers on 'I'

        for i in taxis:
            index = taxis[i]['location']
            if (map[index[0]][index[1]] == 'I'):
                return False   #count taxi started on 'I'
        for i,passer in enumerate(pas):
            loca = pas[passer]["location"]
            if (1000*loca[0]+loca[1]) not in self.desti_intrest[i]:
                #unreachable
                return False

        return True

    def buildStateFromDictionary(self,dict):
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        pas = dict['passengers']
        taxis = dict['taxis']
        firstTuple = []
        secondTuple = []
        for i in taxis:
            lc = taxis[i]['location']
            fuel = taxis[i]['fuel']
            merge = (lc, fuel, 0) # starts with max fuel , zero capacity
            firstTuple.append(merge)
        for i in pas:
            lc = pas[i]['location']
            secondTuple.append(lc)
        return (tuple(firstTuple), tuple(secondTuple))

    def buildDictionaryFromState(self,state):
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        new_dict = {}
        new_dict["map"] = self.map
        newDict1={}
        taxis = state[0]
        pas = state[1]
        for st_data,t_info in zip(taxis,self.taxi_info):
            data = {'location': st_data[0], 'fuel': t_info[1], 'capacity': t_info[2]}
            newDict1.update({t_info[0]: data}) # current fuel / capacity isnt used
        new_dict['taxis'] = newDict1
        newDict1={}
        for st_data,p_info in zip(pas,self.passer_info):
            data = {'location': st_data, 'destination': p_info[1]}
            newDict1.update({p_info[0]: data})
        new_dict['passengers'] = newDict1
        return new_dict

    def initBFS(self):
        self.passer_intrest = []
        self.desti_intrest = []
        self.intrest_graph = {}
        max_fuel = 0
        for taxi in self.taxi_info:
            max_fuel = max(max_fuel, int(taxi[1]))
        for passer in self.initial["passengers"]:
            result=custom_BFS(self.initial["passengers"][passer]["location"], self.map, max_fuel)
            if result==-1: return -1
            self.passer_intrest.append(result)
            result=custom_BFS(self.initial["passengers"][passer]["destination"], self.map, 512)
            if result == -1: return -1
            self.desti_intrest.append(result) # all map
        for x, row in enumerate(self.map):
            for y, spot in enumerate(row):
                if (spot == "G"):
                    result=custom_BFS((x, y), self.initial["map"], max_fuel)
                    if result == -1: return -1
                    self.intrest_graph[1000 * x + y] = result
        return 0

    def __init__(self, initial):
        #save all static data and organizes it
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.initial = initial
        self.map = initial['map']
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        # taxi location is ( X , Y ) : 0<X,Y < 256
        # passengers location is{ unpicked up : (X,Y ) , picked up : ( Taxi_Id) , destination :(-1) }
        "save taxi information"
        self.taxi_info = []
        taxi_l = list(initial['taxis'])
        taxi_l.sort()
        for taxi in taxi_l:
            self.taxi_info.append((taxi, initial['taxis'][taxi]["fuel"], initial['taxis'][taxi]["capacity"]))
        "save passenger information"
        self.passer_info = []
        passer_l = list(initial['passengers'])
        passer_l.sort()
        for passer in passer_l:
            self.passer_info.append((passer, initial['passengers'][passer]["destination"]))
        self.turn_off = False
        #checks if possible ++
        if self.initBFS() ==-1 or not self.isPossible(initial):
            # no way to pass massage forward ... .. .... ... time to rebel with a noon nap
            """ tell boss mission is impossible.
            boss says: 'you must try anyway for at least 3 hours!!!'
            = i sleep zzzZZZZzz"""
            self.turn_off=True
            #time.sleep(55) # bad idea sorry
            #return -1
            #return (-2,-2,0) # doesnt work

        state = self.buildStateFromDictionary(initial)
        search.Problem.__init__(self, state)


    def actions(self, state):
        if self.turn_off: return [] # sleep sleep problem
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # create a list of tuple and then use "tuple(list)" function

        map = self.map
        state = state
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        # taxi location is ( X , Y ) : 0<X,Y < 256
        # passengers location is{ unpicked up : (X,Y ) , picked up : ( Taxi_Id) , destination :(-1) }
        all_actions = []
        map_width = len(map[0]) - 1  # checked above none empty
        map_depth = len(map) - 1
        passenger_location = []  # for quick lookup
        for passer in state[1]:
            passenger_location.append(passer)
        each_taxi_action = []
        for id, taxi in enumerate(state[0]):
            each_taxi_action.append([])
            x = int(taxi[0][0])
            y = int(taxi[0][1])
            fuel = int(taxi[1])
            capacity = int(taxi[2])
            t_name = self.taxi_info[id][0]
            if fuel > 0:  # has fuel
                if x > 0:
                    if map[x - 1][y] != "I":
                        each_taxi_action[id].append(("move", t_name, (x - 1, y)))
                if x < map_depth:
                    if map[x + 1][y] != "I":
                        each_taxi_action[id].append(("move", t_name, (x + 1, y)))
                if y > 0:
                    if map[x][y - 1] != "I":
                        each_taxi_action[id].append(("move", t_name, (x, y - 1)))
                if y < map_width:
                    if map[x][y + 1] != "I":
                        each_taxi_action[id].append(("move", t_name, (x, y + 1)))
            if (x, y) in passenger_location:
                if capacity < self.taxi_info[id][2]:
                    p_id=0
                    c=passenger_location.count((x, y))
                    for j in range(c):
                            p_id = passenger_location.index((x, y),p_id)
                            p_name = self.passer_info[p_id][0]
                            each_taxi_action[id].append(("pick up", t_name, p_name))
                            p_id+=1
            if (id,) in passenger_location:
                in_taxi = []
                for i in range(len(passenger_location)):
                    if passenger_location[i] == (id,):
                        in_taxi.append(i)
                for i in in_taxi:
                    destination = self.passer_info[i][1]
                    if destination == (x, y):
                        p_name = self.passer_info[i][0]
                        each_taxi_action[id].append(("drop off", t_name, p_name))
            if map[x][y] == "G":  # refuel or wait
                each_taxi_action[id].append(("refuel", t_name))
            else:
                each_taxi_action[id].append(("wait", t_name))
        # end off looping
        now = [[]]
        new = []
        for each_t in each_taxi_action:
            for act in each_t:
                for prev in now:
                    a = prev.copy()
                    a.append(act)
                    new.append(a)
            now = new
            new = []
        for actt in now:
            all_actions.append(tuple(actt))
        return tuple(all_actions)

    def result(self, state, action,debug=False):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = state
        new_state = [[], []]
        new_state[1] = list(state[1])
        for i, acti in enumerate(action):
            act = acti[0]
            if (act == 'move'):
                new_state[0].append((acti[2], state[0][i][1]-1, state[0][i][2]))
            if (act == 'refuel'):
                new_state[0].append((state[0][i][0], self.taxi_info[i][1], state[0][i][2]))
            if (act == 'pick up'):
                new_state[0].append((state[0][i][0], state[0][i][1], state[0][i][2] + 1))
                for j, p in enumerate(self.passer_info):
                    if p[0] == acti[2]:
                        new_state[1][j] = tuple([i])
                        break
            if (act == 'drop off'):
                new_state[0].append((state[0][i][0], state[0][i][1], state[0][i][2] - 1))
                for j, p in enumerate(self.passer_info):
                    if p[0] == acti[2]:
                        new_state[1][j] = tuple([-1])
                        break
            if (act == 'wait'):
                new_state[0].append(state[0][i])
        new_state[0]=tuple(new_state[0])
        new_state[1]=tuple(new_state[1])
        if debug:
            print("current state: " + str(state))
            print("action: " + str(action))
            print("new state: "+ str(new_state))
        return tuple(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

        goalll=True
        for pas_loc in state[1]:
            if pas_loc!=(-1,):
                return  False
        return goalll

    def h(self, node):

        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        #return self.h_1(node)
        return self.h_2(node)
        return 0

    def h_1(self, node):
        """
        This is a simple heuristic
        """
        state=node.state
        cost = 0
        for id,pass_loc in enumerate(state[1]):
            if len(pass_loc)==2:#passenger is in starting position
                cost += 2
            elif pass_loc[0] >-1: #passenger is in taxi , pass_loc[0] is taxi Id or -1:  #
                cost += 1
            # else: cost +=0 # not in taxi and at destination
        return cost

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        cost = 0
        state = node.state
        pass
        for p_data,p_info in zip(state[1],self.passer_info):
            pass_dest = p_info[1]
            pass_loc = p_data
            pass
            if len(pass_loc) == 1:  # passenger is taxi 1
                if pass_loc[0] ==-1:
                    cost+=0
                else:
                    taxi_loc = state[0][pass_loc[0]][0]
                    cost += abs(taxi_loc[0] - pass_dest[0]) + abs(taxi_loc[1] - pass_dest[1])
            else:  # not in taxi and not in destination
                cost += abs(pass_loc[0] - pass_dest[0]) + abs(pass_loc[1] - pass_dest[1])
            # else: cost +=0 # not in taxi and at destination
        num_of_taxi_carrying=0
        for t_info in self.taxi_info:
            if fix_h_2:
                num_of_taxi_carrying+=t_info[2]
            else:
                num_of_taxi_carrying+=1
        return cost

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)
