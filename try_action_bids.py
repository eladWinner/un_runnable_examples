#TODO change the name of this file according to your ID
import math

def create_new_2d(key ,size):

    starting_bet =4.5
    scale =2
    mid =1
    new_arr =[0 for i in range(size)]
    #[ current value , current key ( in range 0-31), [ 32 last postion missmatch] , reward avrage , count]
    return[starting_bet +(mid -key)*scale,0,new_arr ,0,0]

class BiddingAgent:

    def __init__(self):
        self.count = 1
        self.correct=0
        self.arr_size =32
        self.max_num_or_agents =8
        self.observed_max_num_or_agents =0
        self.threeDarray =[]
        for i in range(self.max_num_or_agents):
            self.threeDarray.append(create_new_2d(i ,self.arr_size))
        self.target_postion = 0

        # plan is to make 2D* array
        #[current value , current key ( in range 0-31), [ 32 last postion missmatch]

    def get_bid(self, num_of_agents, P, q, v):
        #return v/3.75 # backup plan ;P
        """"
        :param num_of_agents: number of agents competing in this round
        :param P:P_1,...P_n, where P_i is the probability of a user clicking on position i (n <= num_agents)
        :param q: quality score
        :param v: value in case of click
        :return:
        """
        #TODO This is your place to shine. Go crazy!
        if ( num_of_agents> self.max_num_or_agents):
            print("why!?! so many agents ?!! becuase of you i died . RIP in peace  ")
            exit(3)
        self.observed_max_num_or_agents = num_of_agents

        p_gradent =[]
        minn= min( num_of_agents , len(P)) # number of slots that matter 
        for i in range( minn-1):
            p_gradent.append(P[i]-P[i+1])
        p_gradent.append(P[minn-1]-0.001) # based on constant 
        maxx=max(p_gradent)
        targeted_spot=p_gradent.index(maxx)

        expected_rew = v *q * P[targeted_spot]
        expected_pay = 5.88 / 3 # 5.88 = E ( V)12 *E ( Q) 0.49 #  this is dummy 3 bid
        if expected_pay > expected_rew : # if not worth it go low
            targeted_spot=min(len(P),num_of_agents)-1

        self.target_postion =targeted_spot

        return self.threeDarray[targeted_spot][0] *P[targeted_spot]


    def notify_outcome(self, reward, outcome, position):
        """
        :param reward: The auction's reward
        :param outcome: The auction's payment
        :param position: The position obtained at the auction
        :return: We won't use its return value
        """

        self.count+=1
        logg=math.log2(self.count)
        scale =0.17/logg

        diff = position - self.target_postion # if negative : bid was too high else: too low 

        if ( diff ==0 ):
            self.correct+=1
        if (position == -1): # current bid was too low 
            diff=2
        #[ current value , current key ( in range 0-31), [ 32 last postion missmatch] , reward  , count]
        array_pos=self.threeDarray [self.target_postion]

	# adding info of where bid spot is for future use  
        if ( diff == 0): # if got correct still need to go to middle 
           if ( self.target_postion ==0 ):
               array_pos[2][array_pos[1]] = -0.15
           elif  (self.target_postion ==self.observed_max_num_or_agents-1 ):
               array_pos[2][array_pos[1]] = 0.4 # go up to under mine
           else:
               array_pos[2][array_pos[1]] = 0.2
        else:
            array_pos[2][array_pos[1]] = diff
	# looping key 
        array_pos[1]+=1
        if (array_pos[1] ==self.arr_size):
            array_pos[1]=0
	
        summ=sum(array_pos[2])

        array_pos[0]+=summ*scale
        array_pos[4]+=1
        array_pos[3]+=reward-outcome
        #TODO decide what/if/when to store. Could be used for future use

        pass

    def get_id(self):
        """
        #TODO Make sure this function returns your ID, which is the name of this file!
        :return:
        """
        return "id_209639855_208606830"