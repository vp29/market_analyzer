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
    def __init__(self, buy_time, sell_time, sell_cutoff, buy_price, sell_price):
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.sell_cutoff = sell_cutoff
        self.sell_price = sell_price
        self.buy_price = buy_price


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
def generate_a_graph(prices, priceY, meanY, maxResIndex, resY, maxSupIndex, supY, index_or_title, identifiying_text,**kwargs):
    ##kwargs is used to find buy price and sell price points
    plotly.tools.set_credentials_file(username='shemer77', api_key='m034bapk2z', stream_ids=['0373v57h06', 'cjbitbcr9j'])


    trace0 = plotly.graph_objs.Scatter(
    x=range(0,len(prices)),
    y=priceY,
    name='Stock Data'
    )

    trace1 = plotly.graph_objs.Scatter(
    x=range(0, len(prices)),
    y=meanY,
    name="Mean"
    )
    trace2 = plotly.graph_objs.Scatter(
    x=range(maxResIndex, len(prices)-1),
    y=resY,
    name='Resistance'
    )
    trace3 = plotly.graph_objs.Scatter(
    x= range(maxSupIndex, len(prices)-1),
    y=supY,
    name='Support'
    )
    data = plotly.graph_objs.Data([trace0, trace1,trace2,trace3])

    if kwargs:
        print kwargs
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
    #add auto_open=False arg to turn off iopening the browser
    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    unique_url = py.plot(fig, filename=str(index_or_title))
    print unique_url



