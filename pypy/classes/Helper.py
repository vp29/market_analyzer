__author__ = 'Erics'
import csv
import Data
from datetime import datetime
import time
from Data import Data
from Diff import Diff
from Trade import Trade


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

    @staticmethod
    def analyze_db(db, initial_val):
        trades = []

        trades = db.read_trades()

        sidewaysprofitablemovingmarketcounter = 0
        upwardsprofitablemovingmarketcounter = 0
        downwardsprofitablemovingmarketcoutner = 0

        sidewaysunprofitablecounter = 0
        upwardunprofitablecoutner = 0
        downwardunprofitablecoutner = 0

        start_time = trades[0].buy_time if trades[0].long_short == "long" else trades[0].sell_time
        end_time = trades[-1].buy_time if trades[-1].long_short == "short" else trades[-1].sell_time
        open_trades = []
        max_trades = 10
        single_trade = False #only allow once entrance into stock at any given time
        stocks = []
        total = initial_val
        total_used = 0
        total_possible = 0

        #we cant be long and short at the same time, so we have to keep track
        long_stocks = []
        short_stocks = []

        for i in range(start_time, end_time+20, 20):
            for trade in trades:
                enter_time = trade.buy_time if trade.long_short == "long" else trade.sell_time
                if i == enter_time:
                    if len(open_trades) < max_trades and (not single_trade or (single_trade and trade.symbol not in stocks)):
                        if (trade.long_short == "long" and trade.symbol not in short_stocks) or \
                            (trade.long_short == "short" and trade.symbol not in long_stocks):
                            stocks.append(trade.symbol)
                            if trade.long_short == "long":
                                long_stocks.append(trade.symbol)
                            else:
                                short_stocks.append(trade.symbol)
                            investment_amount = total/(max_trades)
                            print investment_amount
                            #total -= investment_amount
                            open_trades.append(Trade(trade.buy_time, trade.sell_time, 0.0, trade.buy_price, trade.sell_price, trade.long_short, investment_amount, trade.symbol, trade.actual_type))
                            total_used += len(open_trades)
                            total_possible += max_trades



            for trade in open_trades:
                exit_time = trade.sell_time if trade.long_short == "long" else trade.buy_time
                if i == exit_time:
                    stocks.remove(trade.symbol)
                    pgain = 0.0
                    if trade.long_short == "long":
                        long_stocks.remove(trade.symbol)
                        pgain = float((trade.sell_price - trade.buy_price))/float(trade.buy_price)
                    else:
                        short_stocks.remove(trade.symbol)
                        pgain = float((trade.sell_price - trade.buy_price))/float(trade.sell_price)
                    total += trade.investment*(1.0 + pgain) - trade.investment
                    gain = str(pgain)
                    print "stock: " + trade.symbol + " gain: " + gain
                    t = datetime.fromtimestamp(float(trade.sell_time))
                    fmt = "%Y-%m-%d %H:%M:%S"
                    print t.strftime(fmt)

                    if float(gain) > 0.000000000000:
                        if 'Upward' in trade.actual_type:
                            upwardsprofitablemovingmarketcounter += 1
                        elif 'Downward' in trade.actual_type:
                            downwardsprofitablemovingmarketcoutner += 1
                        elif 'Sideways' in trade.actual_type:
                            sidewaysprofitablemovingmarketcounter += 1
                    if float(gain) < 0.000000000000:
                        if 'Upward' in trade.actual_type:
                            upwardunprofitablecoutner += 1
                        elif 'Downward' in trade.actual_type:
                            downwardunprofitablecoutner += 1
                        elif 'Sideways' in trade.actual_type:
                            sidewaysunprofitablecounter += 1

                    print trade.actual_type
                    open_trades.remove(trade)

        print sidewaysprofitablemovingmarketcounter
        print upwardsprofitablemovingmarketcounter
        print downwardsprofitablemovingmarketcoutner

        print sidewaysunprofitablecounter
        print upwardunprofitablecoutner
        print downwardunprofitablecoutner
        print "end total: " + str(total)
        print "end gain:  " + str((total-initial_val)/initial_val)
        print "utilisation: " + str(float(total_used)/float(total_possible))