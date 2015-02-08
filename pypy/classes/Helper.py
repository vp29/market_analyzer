__author__ = 'Erics'
import csv
import Data
from datetime import datetime
import time
from Data import Data
from Diff import Diff


class Helper:

    @staticmethod
    def read_csv(filename):
        data = []
        with open(filename, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i = 0
            for row in spamreader:
                if len(row) != 7:
                    continue
                if '.' not in str(row[4]) and len(str(row[4])) >=4:
                    continue
                if i % 5 == 0:
                    data_val = Data(float(row[3]), float(row[1]), float(row[2]), float(row[4]), int(row[5]), time.mktime(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").timetuple()))
                    data.append(data_val)
                i += 1
        return data

    @staticmethod
    def least_square(data):
        '''Y=a+bX, b=r*SDy/SDx, a=Y'-bX'
        b=slope
        a=intercept
        X'=Mean of x values
        Y'=Mean of y values
        SDx = standard deviation of x
        SDy = standard deviation of y'''

        num = len(data)
        xy = 0.0
        xx = 0.0
        x = 0.0
        y = 0.0
        for i, price in enumerate(data):
            xy += price.close*price.index
            xx += price.index*price.index
            x += price.index
            y += price.close

        b = (num*xy - x*y)/(num*xx-x*x)
        a = (y - b*x)/num

        return a, b

    @staticmethod
    def find_matches(diff, max_num_index, max_index, multiplier, cutoff, index):

        temp_diff = []
        cur_max_diff = 0.0

        for i, val in enumerate(diff):
            if val*multiplier > cur_max_diff:
                cur_max_diff = val*multiplier
            temp_diff.append(Diff(val, i+index))

        temp_diff = [g for g in temp_diff if g.diff*multiplier >= cutoff*cur_max_diff]

        if len(temp_diff) > max_num_index:
            big_diff = temp_diff
            max_num_index = len(temp_diff)
            max_index = index

        return big_diff, max_num_index, max_index

    @staticmethod
    def match_indexes(list1, list2):
        matched = []
        for item1 in list1:
            matched.append(list2[item1.index])
        return matched

    @staticmethod
    def trendType(resSlope, supSlope, resInt, supInt, nextInd, sup_per, res_per, curPrice, resRange, supRange):
        actual_type = ""

        potBuy = False
        nextRes = resInt + resSlope*nextInd
        nextSup = supInt + supSlope*nextInd
        resRise = resSlope*resRange
        supRise = supSlope*supRange
        diff = nextRes - nextSup
        resNorm = resRise/curPrice
        supNorm = supRise/curPrice
        normCutoff = 0.01
        if -normCutoff < resNorm < normCutoff\
                and -normCutoff < supNorm < normCutoff:
            potBuy = True
            actual_type = "Sideways moving market."
        elif ((-normCutoff < resNorm < normCutoff)
                or (-normCutoff < supNorm < normCutoff)):
            if -normCutoff < resNorm < normCutoff and supNorm > 0:
                actual_type = "Triangle upward trend.  Predicted to break down."

            elif -normCutoff < supNorm < normCutoff and resNorm < 0:
                actual_type = "Triangle downward trend.  Predicted to break up."
                pass
        elif (resNorm > 0 and supNorm > 0) \
            and ((0.9*supNorm <= resNorm <= supNorm)
                 or (0.9*resNorm <= supNorm <= resNorm)):
                potBuy = True
                actual_type = "Upward trending channel."
        elif (resNorm < 0 and supNorm < 0) \
                and ((resNorm <= supNorm and abs(0.9*resNorm) <= abs(supNorm))
                     or (supNorm <= resNorm and abs(0.9*supNorm) <= abs(resNorm))):
                potBuy = True
                actual_type = "Downward trending channel."
        elif (resNorm < 0 > supNorm) \
                or (resNorm < 0 and resNorm < supNorm)\
                or (supNorm > resNorm > 0):
            actual_type = "Wedge trend.  May break up or down."

        #print "buy point:  " + str((nextSup + diff*bsPoint))
        #print "sell point: " + str((nextRes - diff*bsPoint))
        return (nextSup + diff*sup_per), (nextRes - diff*res_per), potBuy, actual_type