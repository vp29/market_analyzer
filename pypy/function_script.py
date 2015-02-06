import time
import plotly.plotly as py
import plotly.graph_objs
import threading
import datetime
def background(f):
    '''
    a threading decorator
    use @background above the function you want to run in the background
    '''
    def bg_f(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return bg_f

class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

class Data:
    date = None
    open = 0.0
    high = 0.0
    low = 0.0
    close = 0.0
    def __init__(self, date, open, high, low, close):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close

class Trade:
    buy_time = 0
    sell_time = 0
    sell_cutoff = 0.0
    buy_price = 0.0
    sell_price = 0.0
    investment = 0.0
    symbol = ""
    actual_type = ""
    long_short = ""
    def __init__(self, buy_time, sell_time, sell_cutoff, buy_price, sell_price, long_short, investment=0.0, symbol="",actual_type=""):
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.sell_cutoff = sell_cutoff
        self.sell_price = sell_price
        self.buy_price = buy_price
        self.long_short = long_short
        self.investment = investment
        self.symbol = symbol
        self.actual_type = actual_type


def analyze_db(c, initial_val):
    trades = []
    for row in c.execute("SELECT * FROM stocks ORDER BY buy_date ASC;"):
        trades.append(Trade(row[2], row[3], 0.0, row[4], row[5], row[8], 0.0, row[1], row[7]))

    prof_sideways_trade = 0
    prof_updwards_trade = 0
    prof_downwards_trade = 0

    shortprofit = 0
    shortnon = 0
    longprofit = 0
    longnon = 0

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
                        investment_amount = total/max_trades
                        print investment_amount

                        #checking to see if we're reaching a new low in the max drawdown
                        if investment_amount < max_drawdown:
                            max_drawdown = investment_amount

                        #checking to see if we're reaching a new total gain high
                        if investment_amount > max_gain:
                            max_gain = investment_amount

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
                t = datetime.datetime.fromtimestamp(float(trade.sell_time))
                fmt = "%Y-%m-%d %H:%M:%S"
                print t.strftime(fmt)

                if float(gain) > 0.000000000000:
                    if trade.long_short == "long":
                        longprofit += 1
                    else:
                        shortprofit += 1
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
                    if trade.long_short == "long":
                        longnon += 1
                    else:
                        shortnon += 1
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

                print trade.actual_type
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

    print "SHORT: percent of profitable sideways trades: " + str(float(short_prof_sideways_trade)/(float(short_prof_sideways_trade)+float(short_unprof_sideways_trade)))
    print "SHORT: percent of profitable upwards trades: " + str(float(short_prof_updwards_trade)/(float(short_prof_updwards_trade)+float(short_unprof_upwards_trade)))
    print "SHORT: percent of profitable downwards trades: " + str(float(short_prof_downwards_trade)/(float(short_prof_downwards_trade)+float(short_unprof_downwards_trade)))

    print "lowest_account_balance: ", max_drawdown
    print "highest_account_balance: ", max_gain
    

    print "percent short profit " + str(float(shortprofit)/float(shortprofit+shortnon))
    print "percent long profit " + str(float(longprofit)/float(longprofit+longnon))
    print "end total: " + str(total)
    print "end gain:  " + str((total-initial_val)/initial_val)
    print "utilisation: " + str(float(total_used)/float(total_possible))

def leastSquare(data):
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
    for price in data:
        xy = xy + price.price*price.index
        xx = xx + price.index*price.index
        x = x + price.index
        y = y+ price.price

    b = (num*xy - x*y)/(num*xx-x*x)
    a = (y - b*x)/num

    return a, b



def findMatches(tempPrice,maxNumIndex,maxIndex, neg, cutoff, index):


    multiplier = 1
    if neg:
        multiplier = -1

    curInter, curSlope = leastSquare(tempPrice)
    diff = []
    curMaxDiff = 0.0

    for curPrice in tempPrice:
        currDiff = curPrice.price - (curInter + curSlope*curPrice.index)
        if neg:
            if currDiff < 0 and currDiff*multiplier > curMaxDiff:
                curMaxDiff = currDiff*multiplier
        else:
            if currDiff*multiplier > curMaxDiff:
                curMaxDiff = currDiff*multiplier
        diff.append(Price(currDiff, curPrice.index))

    #print diff
    #print len(diff)
    cutDiff = [g for g in diff if g.price*multiplier >= cutoff*curMaxDiff]
    #print cutDiff
    #print len(cutDiff)

    if len(cutDiff) > maxNumIndex:
        bigDiff = cutDiff
        maxNumIndex = len(cutDiff)
        maxIndex = index

    return bigDiff, maxNumIndex, maxIndex



def matchIndexes(group1, group2):
    matched = []
    for item1 in group1:
        for item2 in group2:
            if item2.index == item1.index:
                matched.append(item2)
    return matched


def genY(intercept, slope,start,end):

    y = []
    for i in xrange(start, end):
        y.append(intercept + slope*i)
    return y



@background
def generate_a_graph(prices,resInter,resSlope,boughtIndex,j,supInter,supSlope,inter,slope, maxResIndex, maxSupIndex, index_or_title, identifiying_text,**kwargs):
    res_y = genY(resInter, resSlope, j-boughtIndex-960, j-boughtIndex)
    sup_y = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
    mean_y = genY(inter, slope, 0, len(prices))
    price_y = []
    #put prices in list for plotting
    for price in prices:
        price_y.append(price.price)

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
    x=range(maxResIndex, len(prices)-1),
    y=res_y,
    name='Resistance'
    )
    trace3 = plotly.graph_objs.Scatter(
    x= range(maxSupIndex, len(prices)-1),
    y=sup_y,
    name='Support'
    )
    data = plotly.graph_objs.Data([trace0, trace1,trace2,trace3])

    if kwargs:
        #print kwargs
        trace4 = plotly.graph_objs.Scatter(
          x= kwargs['buy_index'],
          y=kwargs['buy_price'],
          name='Buy Price',
          marker = plotly.graph_objs.Marker(
              size=12
            )
          )

        trace5 = plotly.graph_objs.Scatter(
          x= kwargs['sold_index'],
          y=kwargs['sold_price'],
          name='Sell Price',
          marker = plotly.graph_objs.Marker(
              size=12
            )
          )
        data = plotly.graph_objs.Data([trace0, trace1,trace2,trace3,trace4,trace5])


    layout = plotly.graph_objs.Layout(
    title=str(identifiying_text)
        )
    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    #add auto_open=False arg to turn off iopening the browser
    unique_url = py.plot(fig, filename=str(index_or_title),auto_open=False)
    print unique_url
    return str(unique_url)




