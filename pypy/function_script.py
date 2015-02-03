import time
import plotly.plotly as py
import plotly.graph_objs
import threading

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
    def __init__(self, buy_time, sell_time, sell_cutoff, buy_price, sell_price, investment=0.0, symbol="",actual_type=""):
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.sell_cutoff = sell_cutoff
        self.sell_price = sell_price
        self.buy_price = buy_price
        self.investment = investment
        self.symbol = symbol
        self.actual_type = actual_type


def analyze_db(c, initial_val):
    trades = []
    for row in c.execute("SELECT * FROM stocks ORDER BY buy_date ASC;"):
        trades.append(Trade(row[2], row[3], 0.0, row[4], row[5], 0.0, row[1], row[7]))

    sidewaysmovingmarketcounter = 0
    upwardsmovingmarketcounter = 0
    downwardsmovingmarketcoutner = 0

    start_time = trades[0].buy_time
    end_time = trades[-1].buy_time
    open_trades = []
    max_trades = 10
    total = initial_val
    for i in range(start_time, end_time, 20):
        for trade in trades:
            if i == trade.buy_time:
                if len(open_trades) < max_trades:
                    investment_amount = total/(max_trades)
                    print investment_amount
                    #total -= investment_amount
                    open_trades.append(Trade(trade.buy_time, trade.sell_time, 0.0, trade.buy_price, trade.sell_price, investment_amount, trade.symbol,trade.actual_type))

        for trade in open_trades:
            if i == trade.sell_time:
                total += trade.investment*(1.0 + float((trade.sell_price - trade.buy_price))/float(trade.buy_price)) - trade.investment
                print "stock: " + trade.symbol + " gain: " + str(float((trade.sell_price - trade.buy_price))/float(trade.buy_price))
                if 'Upward' in trade.actual_type:
                    upwardsmovingmarketcounter += 1
                elif 'Downward' in trade.actual_type:
                    downwardsmovingmarketcoutner += 1
                elif 'Sideways' in trade.actual_type:
                    sidewaysmovingmarketcounter += 1
                print trade.actual_type
                open_trades.remove(trade)

    print sidewaysmovingmarketcounter
    print upwardsmovingmarketcounter
    print downwardsmovingmarketcoutner
    print "end total: " + str(total)
    print "end gain:  " + str((total-initial_val)/initial_val)

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




