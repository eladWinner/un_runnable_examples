ids = ["313590697", "209639855"]
from copy import deepcopy
import random
import time


def custom_BFS(start, the_map, deapth=256):
    # a bfs like function to map distance of each tile from a spot
    if the_map[start[0]][start[1]] == 'I':
        return -1
    result = {}
    dist = 0
    at = [start]
    result[start] = 0
    width = len(the_map[0]) - 1
    length = len(the_map) - 1
    at_next = []
    while (dist < deapth):
        for a in at:
            x, y = a
            if x > 0:
                if not result.get((x - 1, y), 0):
                    if the_map[x - 1][y] != "I":
                        result[(x - 1, y)] = dist + 1
                        at_next.append((x - 1, y))
            if x < length:
                pos = (x + 1, y)
                if not result.get(pos, 0):
                    if the_map[x + 1][y] != "I":
                        result[pos] = dist + 1
                        at_next.append(pos)
            if y > 0:
                pos = (x, y - 1)
                if not result.get(pos, 0):
                    if the_map[x][y - 1] != "I":
                        result[pos] = dist + 1
                        at_next.append((x, y - 1))
            if y < width:
                pos = (x, 1 + y)
                if not result.get(pos, 0):
                    if the_map[x][y + 1] != "I":
                        result[pos] = dist + 1
                        at_next.append((x, 1 + y))
        dist += 1
        if 0 == len(at_next):
            break
        at = at_next
        at_next = []
    result[start] = 0
    return result


def print_state(state: dict):
    # debug helper function
    taxi_info = {}
    print("turns left:", state['turns to go'], end=" |")
    for taxi in state['taxis']:
        taxi_info[taxi] = []
    endli = []
    for passer in state["passengers"]:
        loca = state["passengers"][passer]["location"]
        if isinstance(loca, str):
            taxi_info[loca].append(f" {passer}: to={state['passengers'][passer]['destination']}")
        else:
            endli.append(
                f"{passer} at:{state['passengers'][passer]['location']} to:{state['passengers'][passer]['destination']}")
    for taxi in state['taxis']:
        print(taxi, " at: ", state["taxis"][taxi]["location"], end=' ')
        if len(taxi_info[taxi]) != 0:
            print("carrying :", taxi_info[taxi], end='')
        print("fuel :", state["taxis"][taxi]["fuel"], "left |", end='')
    print(" passengers on ground:", endli)


def print_helper_map(the_map: dict, depth, width, num_dest=-1):
    # visualize helper graph TTgraph ( turns to graph )
    if num_dest == -1:
        val = list(the_map.values())[0]
        if isinstance(val, int):
            num_dest = 1
        else:
            num_dest = len(val)
    res = []
    for x in range(depth):
        res.append([])
        for y in range(width):
            res[x].append([-1] * num_dest)
    for val in the_map:
        x, y = val
        res[x][y] = [round(t, 2) for t in the_map[val].values()]
    for x in range(depth):
        print(res[x])


class OptimalTaxiAgent:
    # creates hush-able tuples for state*
    def buildStateFromDictionary(self, state_dict):
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        pas = state_dict['passengers']
        taxis = state_dict['taxis']
        firstTuple = []
        secondTuple = []
        for i in taxis:
            lc = taxis[i]['location']
            fuel = taxis[i]['fuel']
            cap = taxis[i]['capacity']
            merge = (lc, fuel, cap)
            firstTuple.append(merge)
        for i in pas:
            lc = pas[i]['location']
            dest = pas[i]['destination']
            secondTuple.append((lc, dest))
        return (tuple(firstTuple), tuple(secondTuple))

    # convert a state into stored tuple state
    def UpdateDictionaryFromState(self, state_tuple, state_dict):
        # state format tuples : ((  (location,fuel,capacity)**num_taxis ),(  (location)**num_passers )
        for i, taxi in enumerate(state_dict["taxis"]):
            state_dict["taxis"][taxi]["location"] = state_tuple[0][i][0]
            state_dict["taxis"][taxi]["fuel"] = state_tuple[0][i][1]
            state_dict["taxis"][taxi]["capacity"] = state_tuple[0][i][2]
        for i, passer in enumerate(state_dict["passengers"]):
            state_dict["passengers"][passer]["location"] = state_tuple[1][i][0]
            state_dict["passengers"][passer]["destination"] = state_tuple[1][i][1]

    def save_info(self, initial):
        # declare most variables used in class
        self.initial = initial
        self.map = initial["map"]
        self.deapth = len(self.map) - 1
        if (self.deapth < 0):
            print("no map , fatal error incoming")
        self.width = len(self.map[0]) - 1
        # calculating max fuel for helper maps
        self.max_f = 0
        for taxi in initial["taxis"]:
            self.max_f = max((self.max_f, initial["taxis"][taxi]["fuel"]))
        # initializing helper information/ maps
        self.TTmap = {}  # destination is handled by TTmap . so only has pickup location and refuel location .
        self.bfs_map = {}  # both pickup and refuel ""don't care"" about the destination changing
        self.fuelstops = []  # gas stations list
        self.goals = {}  # acting policy
        self.goals_copy = {}
        self.BP_from_turn = 0  # from which turn is best policy avaliable
        self.best_policy = -1  # empty ATM
        self.score = 0

    def start_graphs(self, display_TTmap=False):
        # building deterministic helper maps for each starting passenger starting/ending location and fuel stop
        for x in range(self.deapth + 1):
            for y in range(self.width + 1):
                if self.map[x][y] == "G":
                    self.bfs_map[(x, y)] = custom_BFS((x, y), self.map, self.max_f)
                    self.fuelstops.append((x, y))
        for passer in self.initial["passengers"]:
            passer_loca = self.initial["passengers"][passer]["location"]
            if passer_loca not in self.bfs_map:
                self.bfs_map[passer_loca] = custom_BFS(passer_loca, self.map, self.max_f)
            for desti in self.initial["passengers"][passer]["possible_goals"]:
                if desti not in self.bfs_map:
                    self.bfs_map[desti] = custom_BFS(desti, self.map, self.max_f)
        # building stochastic helper map for each passenger destination
        for passer in self.initial["passengers"]:
            dist_l = self.initial["passengers"][passer]["possible_goals"]
            chance = self.initial["passengers"][passer]["prob_change_goal"]
            self.build_turnsTo_map(passer, dist_l, self.max_f + 1, chance)
        if display_TTmap:
            for passer in self.initial["passengers"]:
                print("### Estimated Turns to Destination for ", passer)
                for tt in range(self.max_f + 1):
                    print("for fuel level:", tt)
                    print_helper_map(self.TTmap[passer][tt], self.deapth + 1, self.width + 1)

    # determnistic distance
    def to_from_bfs(self, too, fromm, fuel):
        """find next move that using helper BFS map moves colest to target"""
        action = -1
        x, y = fromm
        if too not in self.bfs_map:
            print("doesnt have bfs map")
            return -1
        curr_distance = self.bfs_map[too].get(fromm, -1)
        if curr_distance == -1:
            return -1
        else:
            if fuel > 0:  # always true after above statement
                if x > 0:
                    if (x - 1, y) in self.bfs_map[too]:
                        if self.bfs_map[too][(x - 1, y)] < curr_distance:
                            action = (x - 1, y)
                if x < self.deapth:
                    if (x + 1, y) in self.bfs_map[too]:
                        if self.bfs_map[too][(x + 1, y)] < curr_distance:
                            action = (x + 1, y)
                if y < self.width:
                    if (x, y + 1) in self.bfs_map[too]:
                        if self.bfs_map[too][(x, y + 1)] < curr_distance:
                            action = (x, y + 1)
                if y > 0:
                    if (x, y - 1) in self.bfs_map[too]:
                        if self.bfs_map[too][(x, y - 1)] < curr_distance:
                            action = (x, y - 1)
        return action
        # socastic helper map

    def build_turnsTo_map(self, passer_name: str, targets_list: list, max_fuel, change_chance, runtime=250):
        """
        receives info of a single passenger
        builds a dict of lists( of turns to drop off based on current destination) in a map-tile for each fuel level(sorted in list).
        use lower fuel level to calc next layer .
        :return: list of dict
        """
        """ [fuel_level][location_index][distnation_index] . size [max or max in time] [ <=|map| ] [ | target list|]"""
        x, y = self.initial["passengers"][passer_name]["location"]
        if self.map[x][y] == 'I':
            return -1
        self.TTmap[passer_name] = []
        # we need to calculate  wait time for a desired flip. using binomail distrabution we know E[]= 1/p
        # but there  multipale possible destinations so its 1/p *(n-1)
        n = len(targets_list)
        p = change_chance
        if (n > 1):
            e_turns_change = (1 / p) * (n)
        else:
            e_turns_change = -1  # unrelevant
        current_tiles = set(targets_list)
        future_tiles = current_tiles.copy()  # in to speed up we can only update edges will give wrong result in edgecases
        # do first cycle by hand .
        c_fuel = 0
        curr_list = {}
        for tile in targets_list:
            x, y = tile
            new = {}
            for targ in targets_list:
                new[targ] = e_turns_change
            new[tile] = 0  # drops off
            if self.map[x][y] == 'I':
                new[tile] = 999999
            # if you have zero fuel and at and in destinations you can drop off or wait for change .
            # noinspection DuplicatedCode
            curr_list[tile] = new
            if x > 0:
                if self.map[x - 1][y] != 'I':
                    future_tiles.add((x - 1, y))
            if x < self.deapth:
                if self.map[x + 1][y] != 'I':
                    future_tiles.add((x + 1, y))
            if y < self.width:
                if self.map[x][y + 1] != 'I':
                    future_tiles.add((x, y + 1))
            if y > 0:
                if self.map[x][y - 1] != 'I':
                    future_tiles.add((x, y - 1))
        self.TTmap[passer_name].append(curr_list)
        current_tiles = future_tiles.copy()
        for fueal_l in range(1, max_fuel):
            curr_list = {}
            for tile in current_tiles:
                x, y = tile
                new = {}
                for destin in targets_list:
                    _, move, e_turn = self.next_min_turns(passer_name, fueal_l, tile, destin, n, change_chance)
                    if move > 0:  # doesnt wait
                        e_turn += 1  # add
                    new[destin] = (e_turn)
                curr_list[tile] = new
                if x > 0:
                    if self.map[x - 1][y] != 'I':
                        future_tiles.add((x - 1, y))
                if x < self.deapth:
                    if self.map[x + 1][y] != 'I':
                        future_tiles.add((x + 1, y))
                if y < self.width:
                    if self.map[x][y + 1] != 'I':
                        future_tiles.add((x, y + 1))
                if y > 0:
                    if self.map[x][y - 1] != 'I':
                        future_tiles.add((x, y - 1))
            self.TTmap[passer_name].append(curr_list)
            current_tiles = future_tiles.copy()

        # next ideal move in socastic map

    def next_min_turns(self, passer_name, fuel, pos: tuple, destin, num_dest, chance):
        actions = pos  # default action is to stay
        action = 0  # 0 stay , 1 up ,2 right , 3down ,4 left  # pick up and drop off happen by self first
        x, y = pos
        if fuel > len(self.TTmap[passer_name]):
            fuel = len(self.TTmap[passer_name]) - 1

        def calc_turn(locaa, fuell):
            res = (1 - chance) * self.TTmap[passer_name][fuell][locaa][destin]
            res += chance * sum(self.TTmap[passer_name][fuell][locaa].values()) / (num_dest)
            return res

        if pos in self.TTmap[passer_name][fuel - 1]:
            minT = calc_turn(pos, fuel - 1)  # wait
        else:
            minT = 1024
        if fuel > 0:
            n_move = 0
            if x > 0:
                if (x - 1, y) in self.TTmap[passer_name][fuel - 1]:
                    n_move = calc_turn((x - 1, y), fuel - 1)
                    if n_move < minT:
                        minT = n_move
                        action = 1
                        actions = (x - 1, y)
            if x < self.deapth:
                if (x + 1, y) in self.TTmap[passer_name][fuel - 1]:
                    n_move = calc_turn((x + 1, y), fuel - 1)
                    if n_move < minT:
                        minT = n_move
                        action = 3
                        actions = (x + 1, y)
            if y < self.width:
                if (x, y + 1) in self.TTmap[passer_name][fuel - 1]:
                    n_move = calc_turn((x, y + 1), fuel - 1)
                    if n_move < minT:
                        minT = n_move
                        action = 2
                        actions = (x, y + 1)
            if y > 0:
                if (x, y - 1) in self.TTmap[passer_name][fuel - 1]:
                    n_move = calc_turn((x, y - 1), fuel - 1)
                    if n_move < minT:
                        minT = n_move
                        action = 4
                        actions = (x, y - 1)
        if action == 0:
            if pos in self.TTmap[passer_name][fuel - 1]:
                return actions[action], action, self.TTmap[passer_name][fuel - 1][pos][destin]
            return actions[action], action, 100
        return actions, action, minT

    # guesses max turns left to complete goals using helper maps
    def expected_turns_left(self, state, goals,func =max, debug_print=False):
        # weakest link in code
        if func == max:
            maxx = -1
        else:
            maxx=256
        for taxi in goals:
            pos = state["taxis"][taxi]["location"]
            fuel_l = min(state["taxis"][taxi]["fuel"], self.max_f)
            loca_pass = {}
            for passer in state["passengers"]:
                loca_pass[passer] = state["passengers"][passer]["location"]
            curr = 0
            for goal in goals[taxi]:
                a_type, act_goal = goal
                if a_type == 3:
                    if loca_pass[act_goal] == taxi:
                        a_type = 2
                    else:
                        a_type = 1
                if a_type == 0:  # wait
                    curr += act_goal  # act_goal is turns to wait
                elif a_type == 1:
                    if act_goal in self.fuelstops:
                        if pos in self.bfs_map[act_goal]:  # safe 'G' != 'I'
                            curr += self.bfs_map[act_goal][pos] + 1  # 1: refueling
                        else:
                            return -1
                        pos = act_goal  # gasstation position
                        fuel_l = self.initial["taxis"][taxi]["fuel"]
                        continue
                    p_loca = loca_pass[act_goal]
                    desti = state["passengers"][act_goal]["destination"]
                    num_dest = len(state["passengers"][act_goal]["possible_goals"])
                    if isinstance(p_loca, str):  # in a taxi
                        if self.bfs_map[desti] == -1:
                            return -1
                        if self.bfs_map[desti].get(pos, -1) == -1:
                            return -1
                        other_taxi_loca = state["taxis"][p_loca]["location"]
                        r = max(self.bfs_map[desti][pos],  # current taxi distance
                                self.bfs_map[desti].get(other_taxi_loca, -1))  # this taxi distance
                        needed =self.bfs_map[desti][pos]
                        if fuel_l< needed:
                            return -1
                        curr += r
                        pos = desti  # gasstation position
                        fuel_l -= needed
                        continue
                    # from here it pick up
                    if state["passengers"][act_goal]["destination"] == p_loca:
                        if num_dest == 1:  # will never be picked up
                            if debug_print:
                                print("trying to pick up an unpickable passenger ")
                            return -1
                        if  self.bfs_map[desti]==-1:
                            return -1
                        res = self.bfs_map[desti].get(pos, -1)
                        if res == -1:
                            return -1
                        if fuel_l<res:
                            return -1
                        curr += 1 / (
                                (num_dest - 1) / num_dest * state["passengers"][act_goal]["prob_change_goal"]) + 1
                        pos = p_loca
                        fuel_l -= res
                        loca_pass[act_goal] = taxi

                    else:
                        if self.bfs_map[p_loca] ==-1:
                            return -1
                        distance= self.bfs_map[p_loca].get(pos, -1)
                        if distance== -1:  # unreachable
                            if debug_print:
                                print("cant reach  pick uplocation")
                            return -1
                        if fuel_l<distance:
                            return -1
                        # case became unpickable:
                        if p_loca in state["passengers"][act_goal]["possible_goals"]:
                            chance_to_specific = state["passengers"][act_goal]["prob_change_goal"] / num_dest
                            chance_to_back = (num_dest - 1) * chance_to_specific
                            # calc chance to be in to change before arriving
                            maper = [1, 0]
                            for i in range(distance):
                                temp = chance_to_back * maper[1] + (1 - chance_to_specific) * maper[0]
                                maper[1] = chance_to_specific * maper[0] + (1 - chance_to_back) * maper[1]
                                maper[0] = temp
                            curr += maper[1] * (1 / chance_to_back)
                        curr += distance
                        pos = p_loca
                        fuel_l-= distance
                        loca_pass[act_goal] = taxi
                else:  # act ==2 means drop off
                    if pos in self.TTmap[act_goal][fuel_l]:
                        needed=-1
                        if self.bfs_map[state["passengers"][act_goal]["destination"]]!=-1 and pos in self.bfs_map[state["passengers"][act_goal]["destination"]]:
                            needed =self.bfs_map[state["passengers"][act_goal]["destination"]][pos]
                        if fuel_l<needed:
                            return -1
                        destin = state["passengers"][act_goal]["destination"]
                        curr += self.TTmap[act_goal][fuel_l][pos][destin] + 1
                        fuel_l -= needed
                        pos = destin
                        loca_pass[act_goal] = destin
                    else:
                        if debug_print:
                            print("trying to drop off at unreachable spot")
                        return -1
            maxx = func(curr, maxx)
        return maxx

    def __init__(self, initial):
        self.start_init_time = time.time()
        self.odd_bug_fix = False
        # saving basic information from initial
        self.save_info(initial)

        # create helper graphs for act on goals heuristic
        show_TTgraph = False  # recommended to try ( turn to True )
        self.start_graphs(show_TTgraph)

        # pick goals heuristic to get basic policy
        self.find_start_goals(initial)

        # what's expected turns to completion of all goals ( help's to determine when not to reset
        self.expected_maxT = self.expected_turns_left(initial, goals=self.goals ,func=max)

        # give spare time to run optimal on none optimal problems
        spare_time = 50  # seconds
        TS, FT = self.build_transition_state(initial, 300 - spare_time)
        if TS != -1:
            self.best_policy, self.BP_from_turn = self.policy_determination(TS, FT, 300 - spare_time)
        # reset score
        self.score = 0
        self.odd_bug_fix = True
        print("time toke init to run:", time.time() - self.start_init_time)

    def find_start_goals(self, initial, taxi_list=False):
        # finds basic goals order to do incase optimal runs out of time

        state = deepcopy(initial)
        taxi_min={}
        passer_list = {}
        if not taxi_list:
            taxi_list = list(initial["taxis"])
        for taxi in taxi_list:
            goal_test = []
            for passer in initial["passengers"]:
                if passer in passer_list.values():
                    continue
                goal_test = [(3, passer), (3, passer)]
                res = self.expected_turns_left(state, {taxi: goal_test})
                if res == -1:
                    res = 256
                    for gs in self.fuelstops:
                        goal_test2 = [(1, gs), (3, passer), (3, passer)]
                        new_res = self.expected_turns_left(state, {taxi: goal_test2})
                        if new_res!=-1 and new_res < res:
                            res = new_res
                            goal_test = deepcopy(goal_test2)
                        goal_test2 = [(3, passer), (1, gs), (3, passer)]
                        new_res = self.expected_turns_left(state, {taxi: goal_test2})
                        if new_res!= -1 and new_res < res:
                            res = new_res
                            goal_test = deepcopy(goal_test2)
                    if res == 256:
                        for gs in self.fuelstops:
                            for gs2 in self.fuelstops:
                                goal_test2 = [(1, gs), (3, passer), (1, gs2), (3, passer)]
                                new_res = self.expected_turns_left(state, {taxi: goal_test2})
                                if new_res < res:
                                    res = new_res
                                    goal_test = deepcopy(goal_test2)
                if res != 256:
                    if taxi not in taxi_min or res<= taxi_min[taxi]:
                        taxi_min[taxi] =res
                        self.goals[taxi] = goal_test
                        passer_list[taxi]=passer
        self.goals_copy = deepcopy(self.goals)

    def build_transition_state(self, initial, time_limit=-1, debug_print=False):
        # build transition state for all *LOGICAL* state ( a state that helps achive a goal)
        save_expect = self.expected_maxT  # hard to expailn why
        self.expected_maxT = 256  # messes with act()
        initial_tuple = self.buildStateFromDictionary(initial)
        # collect all possible goals
        all_goals = []
        for GS in self.fuelstops:
            all_goals.append((1, GS))
        for passer in initial["passengers"]:
            all_goals.append((3, passer))  # drop off/ pick depending on state
        # info on goals
        all_goals.append((0, 1))
        num_goals = len(all_goals)
        num_taxis = len(initial["taxis"])
        turns_start = initial["turns to go"]
        num_actions_combo = num_goals ** num_taxis + 1  # +1 allways have action reset
        # variables for running
        transaction = {}
        first_at_turn = {initial_tuple: turns_start}
        state = deepcopy(initial)
        new_states = [initial_tuple]
        future_state = []
        # for each turn starting from last ( turns to go == 0 )
        for turnn in range(turns_start, -1, -1):
            if len(new_states) == 0:
                break  # means no new possible logical state
            for state_ST in new_states:
                if time_limit != -1 and (time.time() - self.start_init_time) > time_limit:
                    return -1, -1  # time limit passed
                transaction[state_ST] = {}
                self.UpdateDictionaryFromState(state_ST, state)  # load hush-able state
                # find all logical actions combinations
                actionSet = set()
                actionSet.add("reset")
                for i in range(num_actions_combo):  # can not saprate into pieces due to collision risk
                    j = i
                    doAction = {}
                    for taxi in initial["taxis"]:
                        t = j % num_goals  # index abuse . #me2
                        doAction[taxi] = [all_goals[t]]
                        j -= t
                        j = int(j / num_goals)
                    self.goals = doAction
                    result = self.act(state, False)
                    if result != -1:  # only keep legal actions
                        actionSet.add(result)
                # printing
                if debug_print:
                    print("possible action combos in state:", end='')
                    print_state(state)
                    if len(actionSet) < 5:
                        print(actionSet)  # seems good
                    else:
                        printt = {}  # make more readable with a basic sort
                        for actt in actionSet:
                            if actt[0] not in printt:
                                printt[actt[0]] = []
                            printt[actt[0]].append(actt)
                        for i in printt:
                            print(printt[i])
                # resulting states of actions
                num_passer = len(state["passengers"])
                for doAction in actionSet:
                    transaction[state_ST][doAction] = {}
                    ns = self.run_round(state, act_on=doAction, doRandom=False)
                    new_state_tuple = self.buildStateFromDictionary(ns)
                    del ns  # noat usead no more *bang
                    for taxi in new_state_tuple[0]:
                        if taxi[2] < 0:
                            continue
                    # print("debug",doAction," result:",new_state_tuple)
                    transaction[state_ST][doAction][new_state_tuple] = 1
                    if new_state_tuple not in transaction:
                        transaction[new_state_tuple] = {}
                        first_at_turn[new_state_tuple] = turnn - 1
                        future_state.append(new_state_tuple)
                    if doAction != "reset":
                        for id, passer in enumerate(state["passengers"]):
                            save_current_states = list(transaction[state_ST][doAction].keys())
                            other_dest = state["passengers"][passer]["possible_goals"]
                            num_dest = len(other_dest)
                            chance_to = state["passengers"][passer]["prob_change_goal"] / num_dest
                            for saved_state in save_current_states:
                                p = transaction[state_ST][doAction][saved_state]
                                for dest in other_dest:
                                    if saved_state[1][id][1] != dest:
                                        n_t = []
                                        for i in range(num_passer):
                                            if i == id:
                                                n_t.append((saved_state[1][i][0], dest))
                                            else:
                                                n_t.append(saved_state[1][i])
                                        new_tuple = (saved_state[0], tuple(n_t))
                                        transaction[state_ST][doAction][new_tuple] = p * chance_to
                                        if new_tuple not in transaction:
                                            transaction[new_tuple] = {}
                                            first_at_turn[new_tuple] = turnn - 1
                                            future_state.append(new_tuple)
                                transaction[state_ST][doAction][saved_state] = p * (1 - (num_dest - 1) * chance_to)
                        summ = sum(transaction[state_ST][doAction].values())
                        if round(summ, 3) > 1:  # was/is very useful for debugging
                            print("math error in transaction state , :/ i hope noone sees this")
            new_states = future_state
            future_state = []
        if debug_print:
            print("started on turn:", turns_start, "completed by turn: ", turnn)
            print(transaction)
            # print(first_at_turn)

        self.expected_maxT = save_expect  # fix
        return transaction, first_at_turn

    # todo check if its fast enough for every input
    def policy_determination(self, transition_probabilities, first_at_turn, time_limit=-1):
        # just calculate values for each action path
        rewards = {"drop off": 100, "reset": -50, "refuel": -10}
        """ will give each practical state a value """
        min_start = min(first_at_turn.values())  # first turn at which some states are unreachable
        best_policy = [{}]  # best policy at turn 0 doesn't matter / exists . so a blank
        value_calc_upwards = [{}]  # at each turn at each state calc max future expected reward
        for state_tuple in transition_probabilities:
            value_calc_upwards[0][state_tuple] = 0
        max_turns = self.initial["turns to go"]
        for turn in range(1,
                          max_turns + 1):  # todo can optimize by splitting with min_start. should saves 5-7% run time
            if time_limit != -1 and time_limit < time.time() - self.start_init_time:
                return best_policy, turn - 1
            value_calc_upwards.append({})
            best_policy.append({})
            for state_tuple in transition_probabilities:
                max_value = -1
                for action in transition_probabilities[state_tuple]:
                    # [value of state last turn *  chance of getting state from action. for possible states from action]
                    cur_value = sum([value_calc_upwards[turn - 1].get(st, 0) *
                                     transition_probabilities.get(state_tuple, {action: {st: 0}})[action][st]
                                     for st in transition_probabilities[state_tuple][action]])
                    # now add value from the action
                    if isinstance(action, str):
                        if action != "reset":
                            print("what the hell that's not my code")
                        cur_value += rewards[action]
                    else:
                        for act in action:
                            cur_value += rewards.get(act[0], 0)
                    if cur_value > max_value:
                        max_value = cur_value
                        value_calc_upwards[turn][state_tuple] = cur_value
                        best_policy[turn][state_tuple] = action
        print("###expected_value of initial :",
              value_calc_upwards[max_turns][self.buildStateFromDictionary(self.initial)])
        return best_policy, max_turns

    # partly copied from check.py
    def run_round(self, state_og, debug_print=0, act_on=-1, doRandom=True):
        """
        run a round of the game
        """
        score = 0
        state = deepcopy(state_og)
        one_round = False
        flag = False
        if act_on != -1:
            one_round = True
        while state["turns to go"]:
            if not one_round:
                action = self.act(state, False)
            else:
                if flag:
                    return state
                action = act_on
                flag = True
            if action == -1:
                return -1
            is_action_legal = True
            if not is_action_legal:
                print(f"You returned an illegal action! that is:", action)
                raise RuntimeError
            if action == "reset":
                state["taxis"] = deepcopy(self.initial["taxis"])
                state["passengers"] = deepcopy(self.initial["passengers"])
                state["turns to go"] -= 1
                score -= 50
                continue
            else:  # environment step
                for p in state['passengers']:
                    passenger_stats = state['passengers'][p]
                    if doRandom:
                        if random.random() < passenger_stats['prob_change_goal']:
                            # change destination
                            passenger_stats['destination'] = random.choice(passenger_stats['possible_goals'])
                state["turns to go"] -= 1
            if action == "terminate":
                if debug_print > 0:
                    print(f"End of simulation, the score was {score}!")
                return score
            for atomic_action in action:
                taxi_name = atomic_action[1]
                if atomic_action[0] == 'move':
                    state['taxis'][taxi_name]['location'] = atomic_action[2]
                    state['taxis'][taxi_name]['fuel'] -= 1
                elif atomic_action[0] == 'pick up':
                    passenger_name = atomic_action[2]
                    if state["passengers"][passenger_name]["location"] == state["passengers"][passenger_name][
                        "destination"]:
                        continue
                    state['taxis'][taxi_name]['capacity'] -= 1
                    state['passengers'][passenger_name]['location'] = taxi_name
                elif atomic_action[0] == 'drop off':
                    passenger_name = atomic_action[2]
                    state['passengers'][passenger_name]['location'] = state['taxis'][taxi_name]['location']
                    state['taxis'][taxi_name]['capacity'] += 1
                    score += 100
                elif atomic_action[0] == 'refuel':
                    state['taxis'][taxi_name]['fuel'] = self.initial['taxis'][taxi_name]['fuel']
                    score -= 10
                elif atomic_action[0] == 'wait':
                    pass
                else:
                    raise NotImplemented
        if debug_print > 0:
            print(f"End of simulation, the score was {score}!")
        return score

    def act(self, state, debug_print=False):
        """
        complex , if there is best policy does it.
        else follows general goals to gain score suboptimally
        """
        if self.best_policy != -1:  # if there is a best policy, so just do it yesterday you said tomorrow
            if state["turns to go"] <= self.BP_from_turn:
                best_action = self.best_policy[state["turns to go"]][self.buildStateFromDictionary(state)]
                if debug_print:
                    print_state(state)
                    print("best policy:",best_action)
                return best_action
            elif self.BP_from_turn >self.expected_maxT+3: # hope it converdged by than
                best_action = self.best_policy[self.BP_from_turn][self.buildStateFromDictionary(state)]
                if debug_print:
                    print_state(state)
                    print("best policy:",best_action)
                return best_action
        if debug_print:
            print_state(state)

        actions = []
        # goals change to tuple ( type , passenger or location)
        # 0 -wait
        # 1- determnistic go to using bfs map
        # 2- socastic drop off
        # 3- 2 or 1
        # hand crafted goals
        namee = list(state["passengers"].keys())[0]  # first passenger in state
        if len(self.goals) == 0:
            self.goals = deepcopy(self.goals_copy)  # higher policy
        goals = self.goals
        taxi_with_goals = []
        taxi_used_position = {}
        new_m = self.expected_turns_left(state, goals ,func=max)
        if new_m ==-1 or new_m > self.expected_maxT + 1:  # check if to reset
            taxi_list = []
            for taxi in state["taxis"]:
                if state["taxis"][taxi]["capacity"] == self.initial["taxis"][taxi]["capacity"]:
                    taxi_list.append(taxi)
            self.find_start_goals(state, taxi_list)
            for taxi in state["taxis"]:
                res =self.expected_turns_left(state, goals,func=min)
                if res==-1 or res> self.expected_maxT:
                    self.goals[taxi]=[]
            goals = deepcopy(self.goals)
            new_m = self.expected_turns_left(state, goals, func=min)
            if new_m ==-1 or new_m > self.expected_maxT + 1:
                self.goals = deepcopy(self.goals_copy)
                if state["turns to go"] > self.expected_maxT :#and self.score > 50:
                    if debug_print:
                        print("do a reset ***", new_m, self.expected_maxT)
                    self.score -= 50
                    return "reset"
        for taxi in state["taxis"]:
            taxi_with_goals.append(taxi)
            if taxi not in goals or len(goals[taxi]) == 0:
                self.find_start_goals(state, [taxi])
                if state["turns to go"] > 1.1 * self.expected_maxT and self.score > 50:  # todo play with scaler
                    self.score -= 50
                    if debug_print:
                        print("out of goals **** reseting")
                    return "reset"
                actions.append(("wait", taxi))
                taxi_used_position[taxi] = state["taxis"][taxi]["location"]
                continue
            act_type, goto = goals[taxi][0]
            location_taxi = state["taxis"][taxi]["location"]
            fuel_t = state["taxis"][taxi]["fuel"]

            if act_type == 3:
                if state["passengers"][goto]["location"] == taxi:
                    act_type = 2
                else:
                    act_type = 1
            if act_type == 2:  # go drop off
                if isinstance(goto, str):
                    passenger = goto
                    num_destinations = len(state["passengers"][passenger]["possible_goals"])
                    destin = state["passengers"][passenger]["destination"]
                    chance = state["passengers"][passenger]["prob_change_goal"]
                    # calc next move with lowest time to drop off
                    next_move, act_t, _ = self.next_min_turns(passenger, fuel_t, location_taxi, destin,
                                                              num_destinations,
                                                              chance)
                    if act_t == 0:  # algorithm says its best to stay
                        if state["passengers"][passenger]["location"] == taxi and state["passengers"][passenger][
                            "destination"] == state["taxis"][taxi]["location"]:
                            actions.append(("drop off", taxi, passenger))
                            self.score += 100
                            goals[taxi].pop(0)  # move to next goal
                        else:
                            actions.append(("wait", taxi))  # cant drop off but its faster to wait inorder to drop off
                        taxi_used_position[taxi] = location_taxi
                    else:  # dont stay = go !!!
                        x_m,y_m = next_move
                        if self.map[x_m][y_m] =="I":
                            actions.append(("wait", taxi))
                            taxi_used_position[taxi] = state["taxis"][taxi]["location"]
                        x_m, y_m = next_move
                        if self.map[x_m][y_m] == "I":
                            actions.append(("wait", taxi))
                            taxi_used_position[taxi] = state["taxis"][taxi]["location"]
                            continue
                        actions.append(("move", taxi, next_move))
                        taxi_used_position[taxi] = next_move
                        continue
                else:
                    # redundant for debugging
                    print("what are you dropping off that isnt a passenger ?")
                    return -1
            elif act_type == 1:  # pick up or refuel
                if isinstance(goto, str):  # pick up
                    move_to = state["passengers"][goto]["location"]
                    if isinstance(move_to, str):  # trying to pick passenger in other taxi
                        desti = state["passengers"][goto]["destination"]
                        if self.bfs_map[desti] == -1:
                            actions.append(("wait", taxi))
                            taxi_used_position[taxi] = location_taxi
                            continue
                        if location_taxi in self.bfs_map[desti]:
                            if state["taxis"][move_to]["location"] in self.bfs_map[desti]:
                                if self.bfs_map[desti][location_taxi] + 1 < self.bfs_map[desti][
                                    state["taxis"][move_to]["location"]]:  # if other taxi is farther i wait
                                    actions.append(("wait", taxi))
                                    taxi_used_position[taxi] = location_taxi
                                    continue
                                else:
                                    result = self.to_from_bfs(desti, location_taxi, fuel_t)
                                    if result == -1:
                                        if self.odd_bug_fix:
                                            actions.append(("wait", taxi))
                                            taxi_used_position[taxi] = location_taxi
                                            continue
                                        return -1
                                    x_m, y_m = result
                                    if self.map[x_m][y_m] == "I":
                                        actions.append(("wait", taxi))
                                        taxi_used_position[taxi] = state["taxis"][taxi]["location"]
                                        continue
                                    actions.append(("move", taxi, result))
                                    taxi_used_position[taxi] = result
                                    continue
                            else:
                                return -1
                        else:
                            actions.append(("wait", taxi))
                            taxi_used_position[taxi] = location_taxi
                else:
                    move_to = goto
                if state["taxis"][taxi]["location"] == move_to:  # arrived to location
                    if isinstance(goto, str):
                        if state["passengers"][goto]["destination"] != state["passengers"][goto]["location"]:
                            if state["taxis"][taxi]["capacity"] > 0:
                                actions.append(("pick up", taxi, goto))
                                goals[taxi].pop(0)  # next goal
                            else:
                                # todo think if there is a fix other than not getting here
                                if debug_print:
                                    print("trying to pick up while full , fatal error")
                                return -1
                        else:
                            actions.append(("wait", taxi))
                        taxi_used_position[taxi] = location_taxi
                    else:
                        x, y = state["taxis"][taxi]["location"]
                        if state["map"][x][y] == 'G':
                            actions.append(("refuel", taxi))
                            self.score -= 10
                            taxi_used_position[taxi] = location_taxi
                            goals[taxi].pop(0)  # next goal
                        else:
                            print("why did you move to empty tile? ( no passenger or gas stop or drop off")
                            exit(71)
                else:  # dindt arrive = move
                    if isinstance(move_to, str):
                        actions.append(("wait", taxi))
                        taxi_used_position[taxi] = location_taxi
                        continue
                    result = self.to_from_bfs(move_to, location_taxi, fuel_t)
                    if result == -1:
                        if self.odd_bug_fix :
                            actions.append(("wait", taxi))
                            taxi_used_position[taxi] = location_taxi
                            continue
                        else:
                            return -1
                    x_m, y_m = result
                    if self.map[x_m][y_m] == "I":
                        actions.append(("wait", taxi))
                        taxi_used_position[taxi] = state["taxis"][taxi]["location"]
                        continue
                    actions.append(("move", taxi, result))
                    taxi_used_position[taxi] = result
                    continue
            else:  # todo  choose restart or wait smartly
                actions.append(("wait", taxi))
                taxi_used_position[taxi] = location_taxi
        # collision avoidance here .
        flag = True
        while flag:
            flag = False
            collision_histo = {}
            for taxi in taxi_used_position:
                if taxi_used_position[taxi] not in collision_histo:
                    collision_histo[taxi_used_position[taxi]] = []
                collision_histo[taxi_used_position[taxi]].append(taxi)
            for loca in collision_histo:
                if len(collision_histo[loca]) > 1:
                    if debug_print:
                        print("collision in coming!!!!")
                    priority = -1  # needs to complete actions before others
                    for i, taxi_act in enumerate(actions):
                        if state["taxis"][taxi_act[1]]["fuel"] == 0:
                            if taxi_act[0] != "drop off":  # wait a turn
                                return "reset"  # unfixable
                        if taxi_act[0] in ["pick up", "drop off", "refuel"]:
                            priority = i  # the taxi
                    if priority != -1:
                        for i, taxi_act in enumerate(actions):
                            if i != priority:
                                t_name = taxi_act[1]
                                actions[i] = ("wait", t_name)
                                taxi_used_position[t_name] = state["taxis"][t_name]["location"]
                                flag = True
                    else:
                        lowest_priority = -1  # does nothing
                        t_name = ""
                        for i, taxi_act in enumerate(actions):
                            if taxi_act[0] == "wait":
                                lowest_priority = i
                                t_name = taxi_act[1]
                        if lowest_priority != -1:
                            has_pass = self.initial["taxis"][t_name]["capacity"] - state["taxis"][t_name]["capacity"]
                            fuel_l = state["taxis"][t_name]["fuel"]
                            # waiting for drop off and doesn't have fuel to move back
                            if has_pass > 0 and fuel_l == 1 and state["taxis"][t_name]["location"] in self.bfs_map:
                                for i, taxi_act in enumerate(actions):
                                    if taxi_act[1] != t_name:
                                        t2_name = taxi_act[1]
                                        actions[i] = ("wait", t2_name)
                                        taxi_used_position[t2_name] = state["taxis"][t2_name]["location"]
                                        flag = True
                            else:
                                # need to move t_name , but to where i wish cars could fly
                                x, y = state["taxis"][t_name]["location"]
                                if x < self.deapth:
                                    if self.map[x + 1][y] != 'I':
                                        if (x + 1, y) not in taxi_used_position:
                                            actions[lowest_priority] = ("move", t_name, (x + 1, y))
                                            taxi_used_position[t_name] = (x + 1, y)
                                            flag = True
                                if y < self.width:
                                    if self.map[x][y + 1] != 'I':
                                        if (x, y + 1) not in taxi_used_position:
                                            actions[lowest_priority] = ("move", t_name, (x, y + 1))
                                            taxi_used_position[t_name] = (x, y + 1)
                                            flag = True
                                if x > 0:
                                    if self.map[x - 1][y] != 'I':
                                        if (x - 1, y) not in taxi_used_position:
                                            actions[lowest_priority] = ("move", t_name, (x - 1, y))
                                            taxi_used_position[t_name] = (x - 1, y)
                                            flag = True
                                if y > 0:
                                    if self.map[x][y - 1] != 'I':
                                        if (x, y - 1) not in taxi_used_position:
                                            actions[lowest_priority] = ("move", t_name, (x, y - 1))
                                            taxi_used_position[t_name] = (x, y - 1)
                                            flag = True
                                if flag == False:  # every spot taken :/
                                    # fucking
                                    # no option swap position and hope random works fast
                                    collision_histo[loca].remove(t_name)
                                    rand = random.choice(collision_histo[loca])
                                    swap = state["taxis"][rand]["location"]
                                    actions[lowest_priority] = ("move", t_name, swap)
                                    taxi_used_position[t_name] = swap
                        else:  # all are moving into collision
                            # calculating is wayyy too complex . random is correct at least half the time
                            rand = random.choice(collision_histo[loca])
                            for i, taxi_act in enumerate(actions):
                                if taxi_act[1] != rand:
                                    t_name = taxi_act[1]
                                    actions[i] = ("wait", t_name)
                                    taxi_used_position[t_name] = state["taxis"][t_name]["location"]
                                    flag = True
        # print_state(state)
        if debug_print:
            print(actions)
        return tuple(actions)
        raise NotImplemented


class TaxiAgent:
    def __init__(self, initial):
        self.other_taxi = OptimalTaxiAgent(initial)
        self.initial = initial

    def act(self, state):
        return self.other_taxi.act(state)
        raise NotImplemented
