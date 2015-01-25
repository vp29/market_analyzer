import time



class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

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

    cutDiff = [g for g in diff if g.price*multiplier >= cutoff*curMaxDiff]
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



