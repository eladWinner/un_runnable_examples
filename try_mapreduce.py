import sys

from mrjob.job import MRJob
from mrjob.step import MRStep

class month_upper_and_lower_limit(MRJob):
    """
    game plan:
    step 1 find avrage of each day
        map each value by date(( date , curtain),(value , one ))
        sum up value and one
        calculate avrage
    step 2 ???
        create new table?
        than mapper
        and find max and min ?
    step 3 print :D
    """
    def steps(self):
        return [
            MRStep(mapper=self.mapper_select
                ,combiner=self.combiner_does_it_even_work
                ,reducer=self.reducer_to_sum
                )
            ,MRStep(reducer=self.reducer_find_max)
        ]
    # this shit doesnt work . shit = mrjob . correct result is printed but FFFFFFFFFFFFFFFffffffff
    def mapper_select(self, _, line):
        # yield each selected value
        linee= line.split(',')
        if (linee[0]!="StartedOn"): # not hadder
            StartedOn = linee[0].split(' ')
            valuee = float( linee[1])
            curtain = linee[3]
            date_list=StartedOn[0].split('/')
            day =date_list[0]
            month=date_list[1]
            #year = date_list[2]
            yield (day,month,curtain),(valuee,1)# i gave up on doing this correctly IT DOESNT WORK
            #yield (day,month,year,curtain),(valuee,1)# ((date),curtain) , (value , one )

    def combiner_does_it_even_work(self, category, val  ): #
        #yield (category ,(sum(val),sum(val2))
        sum1 =0
        sum2=0
        for v in val:
            sum1+=v[0]
            sum2+=v[1]
        yield (category, (sum1,sum2) )


    def reducer_to_sum(self,category, val ):
        # send all (curtain, value) pairs to the same reducer.
        c=0
        sum=0
        for v in val:
            c+=v[1]
            sum+=v[0]
        yield None , ( round(sum/c,4),category )
        #yield None , ( round(val[0]/val[1],2),category )


    def reducer_find_max(self, _,pairs):
        whyWHY={}
        for p in pairs:
            keyy=str(p[1][1])+","+str(p[1][2])
            whyWHY[keyy]=whyWHY.get(keyy,[-100,100])
            if(whyWHY[keyy][0]<p[0]):
                whyWHY[keyy][0]=p[0]
            if (whyWHY[keyy][1] > p[0]):
                whyWHY[keyy][1] = p[0]
        for r in whyWHY:
            rs=r.split(',') # ill cheat all day with ugly code
            yield [rs[0],rs[1]] , whyWHY[r][0]
            yield [rs[0],rs[1]], whyWHY[r][1]


if __name__ == '__main__':
    month_upper_and_lower_limit.run()