__author__ = 'Erics'
import csv
import Data
from datetime import datetime
import time
from Data import Data
from Diff import Diff
from Trade import Trade
import plotly.plotly as py
import plotly.graph_objs


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
                    try:
                        data_val = Data(float(row[3]), float(row[1]), float(row[2]), float(row[4]), int(row[5]), time.mktime(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").timetuple()))
                        data.append(data_val)
                    except:
                        None
                        #print "Cannot parse line: " + row
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
    def analyze_db_more_indepth(db, initial_val, margin_perc=.5):
        trades = []

        trades = db.read_trades()

        trades = Helper.order_trades(trades)

        prof_sideways_trade = 0
        prof_updwards_trade = 0
        prof_downwards_trade = 0

        unprof_sideways_trade = 0
        unprof_upwards_trade = 0
        unprof_downwards_trade = 0

        long_prof_sideways_trade = 0
        long_prof_updwards_trade = 0
        long_prof_downwards_trade = 0

        long_unprof_sideways_trade = 0
        long_unprof_upwards_trade = 0
        long_unprof_downwards_trade = 0

        short_prof_sideways_trade = 0
        short_prof_updwards_trade = 0
        short_prof_downwards_trade = 0

        short_unprof_sideways_trade = 0
        short_unprof_upwards_trade = 0
        short_unprof_downwards_trade = 0

        start_time = trades[0].buy_time if trades[0].long_short == "long" else trades[0].sell_time
        end_time = trades[-1].buy_time if trades[-1].long_short == "short" else trades[-1].sell_time
        open_trades = []
        max_trades = 10
        single_trade = False #only allow once entrance into stock at any given time
        stocks = []
        total = initial_val
        total_used = 0
        total_possible = 0

        max_drawdown = total/max_trades
        max_gain = total/max_trades

        #we cant be long and short at the same time, so we have to keep track
        long_stocks = []
        short_stocks = []

        fmt = "%Y-%m-%d %H:%M:%S"

        start_year = 2007
        cur_year_start = 1167631200 #2007 timestamp
        year_time = 31536000 #seconds in a year
        long_gain = [0]
        short_gain = [0]
        long_trades = [0]
        short_trades = [0]
        total_long_gain = [1]
        total_short_gain = [1]
        end_value = [initial_val]
        j = 0



        for i in range(start_time, end_time+60, 60):
            for trade in trades:
                enter_time = trade.buy_time if trade.long_short == "long" else trade.sell_time
                if enter_time < i:
                    trades.remove(trade)
                    continue
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
                            print trade.symbol + " -  " + str(investment_amount)
                            #total -= investment_amount
                            t = Trade(trade.buy_time, trade.sell_time, 0.0, trade.buy_price, trade.sell_price, trade.long_short, investment_amount, trade.symbol, trade.actual_type)
                            t.exit_url = trade.exit_url
                            open_trades.append(t)
                            total_used += len(open_trades)
                            total_possible += max_trades
                elif trade.enter_time > i:
                    break

            for trade in open_trades:
                exit_time = trade.sell_time if trade.long_short == "long" else trade.buy_time
                if i == exit_time:
                    if exit_time > cur_year_start + year_time:
                        j += 1
                        end_value.append(total)
                        long_gain.append(0)
                        short_gain.append(0)
                        long_trades.append(0)
                        short_trades.append(0)
                        total_long_gain.append(1)
                        total_short_gain.append(1)
                        cur_year_start += year_time
                    stocks.remove(trade.symbol)
                    pgain = 0.0
                    if trade.long_short == "long":
                        long_stocks.remove(trade.symbol)
                        pgain = float((trade.sell_price - trade.buy_price))/float(trade.buy_price)
                        long_gain[j] += pgain
                        long_trades[j] += 1
                        total_long_gain[j] *= (1 + pgain/max_trades)
                        t = datetime.fromtimestamp(float(trade.sell_time))
                        time = datetime.fromtimestamp(float(trade.buy_time)).strftime(fmt) + " - " + t.strftime(fmt)
                    else:
                        short_stocks.remove(trade.symbol)
                        pgain = float((trade.sell_price - trade.buy_price))/float(trade.sell_price)
                        short_gain[j] += pgain
                        short_trades[j] += 1
                        total_short_gain[j] *= (1 + pgain/max_trades)
                        t = datetime.fromtimestamp(float(trade.sell_time))
                        time = t.strftime(fmt) + " - " + datetime.fromtimestamp(float(trade.buy_time)).strftime(fmt)
                    if pgain > .7 or pgain < -.7:
                        continue
                    total += float(1.0/(1.0-margin_perc))*trade.investment*(1.0 + pgain) - float(1.0/(1.0-margin_perc))*trade.investment
                    gain = str(pgain)
                    print "stock: " + trade.symbol + " gain: " + gain + " type: " + trade.long_short + \
                          "\n\tsell: " + str(trade.sell_price) + " buy : " + str(trade.buy_price)
                    print time

                    #if pgain > .5 or pgain < -.5:
                    #    raw_input("Press Enter to continue...")

                    if float(gain) > 0.000000000000:
                        if 'Upward' in trade.actual_type:
                            prof_updwards_trade += 1
                            if trade.long_short=="long": long_prof_updwards_trade +=1
                            else: short_prof_updwards_trade += 1
                        elif 'Downward' in trade.actual_type:
                            prof_downwards_trade += 1
                            if trade.long_short=="long": long_prof_downwards_trade +=1
                            else: short_prof_downwards_trade += 1
                        elif 'Sideways' in trade.actual_type:
                            prof_sideways_trade += 1
                            if trade.long_short=="long": long_prof_sideways_trade +=1
                            else: short_prof_sideways_trade += 1
                    if float(gain) < 0.000000000000:
                        print trade.exit_url
                        if 'Upward' in trade.actual_type:
                            unprof_upwards_trade += 1
                            if trade.long_short=="long": long_unprof_upwards_trade +=1
                            else: short_unprof_upwards_trade += 1
                        elif 'Downward' in trade.actual_type:
                            unprof_downwards_trade += 1
                            if trade.long_short=="long": long_unprof_downwards_trade +=1
                            else: short_unprof_downwards_trade += 1
                        elif 'Sideways' in trade.actual_type:
                            unprof_sideways_trade += 1
                            if trade.long_short=="long": long_unprof_sideways_trade +=1
                            else: short_unprof_sideways_trade += 1

                    #print trade.actual_type
                    open_trades.remove(trade)

        print "# sideways profitable: ",  prof_sideways_trade
        print "# upwards profitable counter: " , prof_updwards_trade
        print "# downwards profitable: ", prof_downwards_trade

        print "# sideways unprofitable: ", unprof_sideways_trade
        print "# upwards unprofitable: " , unprof_upwards_trade
        print "# downwards unproftiable: ", unprof_downwards_trade

        print "total # of trades: " + str(unprof_downwards_trade+prof_downwards_trade+ prof_updwards_trade + unprof_upwards_trade + unprof_sideways_trade + prof_sideways_trade)

        print "percent of profitable sideways trades: " + str(float(prof_sideways_trade)/(float(prof_sideways_trade)+float(unprof_sideways_trade)))
        print "percent of profitable upwards trades: " + str(float(prof_updwards_trade)/(float(prof_updwards_trade)+float(unprof_upwards_trade)))
        print "percent of profitable downwards trades: " + str(float(prof_downwards_trade)/(float(prof_downwards_trade)+float(unprof_downwards_trade)))

        print "LONG: percent of profitable sideways trades: " + str(float(long_prof_sideways_trade)/(float(long_prof_sideways_trade)+float(long_unprof_sideways_trade)))
        print "LONG: percent of profitable upwards trades: " + str(float(long_prof_updwards_trade)/(float(long_prof_updwards_trade)+float(long_unprof_upwards_trade)))
        print "LONG: percent of profitable downwards trades: " + str(float(long_prof_downwards_trade)/(float(long_prof_downwards_trade)+float(long_unprof_downwards_trade)))

        try:
            print "SHORT: percent of profitable sideways trades: " + str(float(short_prof_sideways_trade)/(float(short_prof_sideways_trade)+float(short_unprof_sideways_trade)))
            print "SHORT: percent of profitable upwards trades: " + str(float(short_prof_updwards_trade)/(float(short_prof_updwards_trade)+float(short_unprof_upwards_trade)))
            print "SHORT: percent of profitable downwards trades: " + str(float(short_prof_downwards_trade)/(float(short_prof_downwards_trade)+float(short_unprof_downwards_trade)))
        except:
            None

        for i, x in enumerate(long_gain):
            print str(start_year) + " long avg gain: " + str(float(long_gain[i])/float(long_trades[i])) + \
                " total gain: " + str(total_long_gain[i])
            print str(start_year) + " short avg gain: " + str(float(short_gain[i])/float(short_trades[i])) + \
                " total gain: " + str(total_short_gain[i])
            if i < len(long_gain)-1:
                print str(start_year) + " start value: " + str(end_value[i]) + " end value: " + str(end_value[i+1])
                print str(start_year) + " total gain: " + str(float((end_value[i+1] - end_value[i])/end_value[i]))
            start_year += 1
        print str(start_year-1) + " start value: " + str(end_value[-1]) + " end value: " + str(total)
        print str(start_year-1) + " total gain: " + str(float((total - end_value[-1])/end_value[-1]))

        print "lowest_account_balance: ", max_drawdown
        print "highest_account_balance: ", max_gain
        print "end total: " + str(total)
        print "end gain:  " + str((total-initial_val)/initial_val)
        print "utilisation: " + str(float(total_used)/float(total_possible))


    @staticmethod
    def order_trades(trades):
        ordered = []
        short = []
        long = []
        for trade in trades:
            if trade.long_short == 'long':
                trade.enter_time = trade.buy_time
                long.append(trade)
            else:
                trade.enter_time = trade.sell_time
                short.append(trade)
        long.extend(short)
        ordered = sorted(long, key=lambda x: x.enter_time)
        return ordered

    @staticmethod
    def calculate_rsi(data):
        rsi = 0.0
        prev = 0.0
        gain = 0.0
        loss = 0.0
        for i, item in enumerate(data):
            if i == 0:
                prev = item.close
            elif i < 14:
                cur_diff = item.close - prev
                if cur_diff > 0:
                    gain += cur_diff
                else:
                    loss += cur_diff
                prev = item.close
            elif i == 14:
                cur_diff = item.close - prev
                if cur_diff > 0:
                    gain += cur_diff
                else:
                    loss += cur_diff
                prev = item.close
                avg_gain = gain/14
                avg_loss = loss/14
            else:
                cur_diff = item.close - prev
                prev = item.close
                cur_loss = 0.0
                cur_gain = 0.0
                if cur_diff > 0:
                    cur_gain = cur_diff
                else:
                    cur_loss = cur_diff
                avg_gain = (avg_gain*13 + cur_gain)/14
                avg_loss = (avg_loss*13 + cur_loss)/14

        rs = avg_gain/abs(avg_loss)
        rsi = 100 - 100/(1+rs)

        return rsi

    @staticmethod
    def generate_a_graph(resLine, supLine, meanLine, prices, index_or_title, identifiying_text, exit_price,**kwargs):
        res_y = resLine.get_values()
        sup_y = supLine.get_values()
        mean_y = meanLine.get_values()
        exit_y = [exit_price] * len(mean_y)
        price_y = []
        #put prices in list for plotting
        for price in prices:
            price_y.append(price.close)

        ##kwargs is used to find buy price and sell price points
        plotly.tools.set_credentials_file(username='shemer77', api_key='m034bapk2z', stream_ids=['0373v57h06', 'cjbitbcr9j'])


        trace0 = plotly.graph_objs.Scatter(
        x=range(0,len(prices)),
        y=price_y,
        name='Stock Data'
        )

        trace1 = plotly.graph_objs.Scatter(
        x=range(0, len(prices)),
        y=mean_y,
        name="Mean"
        )
        trace2 = plotly.graph_objs.Scatter(
        x=range(resLine.start, len(prices)-1),
        y=res_y,
        name='Resistance'
        )
        trace3 = plotly.graph_objs.Scatter(
        x= range(supLine.start, len(prices)-1),
        y=sup_y,
        name='Support'
        )
        trace4 = plotly.graph_objs.Scatter(
        x=range(0, len(exit_y)),
        y=exit_y,
        name="Exit cutoff"
        )
        data = plotly.graph_objs.Data([trace0, trace1,trace2,trace3,trace4])

        if kwargs:
            #print kwargs
            trace5 = plotly.graph_objs.Scatter(
              x= kwargs['buy_index'],
              y=kwargs['buy_price'],
              name='Buy Price',
              marker = plotly.graph_objs.Marker(
                  size=12
                )
              )

            trace6 = plotly.graph_objs.Scatter(
              x= kwargs['sold_index'],
              y=kwargs['sold_price'],
              name='Sell Price',
              marker = plotly.graph_objs.Marker(
                  size=12
                )
              )
            data = plotly.graph_objs.Data([trace0, trace1,trace2,trace3,trace4,trace5,trace6])


        layout = plotly.graph_objs.Layout(
        title=str(identifiying_text)
            )
        fig = plotly.graph_objs.Figure(data=data, layout=layout)
        #add auto_open=False arg to turn off iopening the browser
        unique_url = ""
        try:
            unique_url = py.plot(fig, filename=str(index_or_title),auto_open=False)
        except:
            None
        print unique_url
        return str(unique_url)