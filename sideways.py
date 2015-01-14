__author__ = 'Erics'

import numpy
import matplotlib.pyplot as plt

class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

prices = []
peaks = []
troughs = []

average = []

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

    #print str(a) + "+" + str(b) + "x"
    return a, b

def genY(intercept, slope, start, end):
    y = []
    for i in range(start, end):
        y.append(intercept + slope*i)
    return y

def matchIndexes(group1, group2):
    matched = []
    for item1 in group1:
        for item2 in group2:
            if item2.index == item1.index:
                matched.append(item2)
    return matched

def findMatches(tempPrice, maxNumIndex, maxIndex, neg, cutoff, index):
    '''tempPrice == list of prices
    maxNumIndex is the number of indexes matched
    neg == True if support
    cutoff = multiplier for neg diff cutoff'''
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

market = open('sideways.txt', 'r')

i=0
for line in market:
    prices.append(Price(float(line), i))
    i = i+1

resDiff = []
supDiff = []
maxDiff = 0.0
maxNegDiff = 0.0

tempResPrice = []
tempSupPrice = []

#largest amount of matches
bigPosDiff = []
bigNegDiff = []

#number of largest amount of matches
maxNumResIndex = 0
maxNumSupIndex = 0

#index of larges amount of matches
maxResIndex = 0
maxSupIndex = 0

for i in range(0, len(prices)-1):
    #first do resistance line
    #find line with highest number of matched peaks
    try:
        tempResPrice = [x for x in prices if x.index > i]
        bigPosDiff, maxNumResIndex, maxResIndex = findMatches(tempResPrice, maxNumResIndex, maxResIndex, False, 0.8, i)
    except:
        None

    #next do support line
    try:
        tempSupPrice = [x for x in prices if x.index > i]
        bigNegDiff, maxNumSupIndex, maxSupIndex = findMatches(tempSupPrice, maxNumSupIndex, maxSupIndex, True, 0.6, i)
    except:
        None

tempPeaks = matchIndexes(bigPosDiff, prices)
tempTrough = matchIndexes(bigNegDiff, prices)

#print len(tempPeaks)
#print len(tempTrough)

resInter, resSlope = leastSquare(tempPeaks)
supInter, supSlope = leastSquare(tempTrough)

inter, slope = leastSquare(prices)

priceY = []
#put prices in list for plotting
for price in prices:
    priceY.append(price.price)

resY = genY(resInter, resSlope, maxResIndex, len(prices)-1)
supY = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
meanY = genY(inter, slope, 0, len(prices))

plt.plot(range(0,len(prices)), priceY, 'r',
         range(0,len(prices)), meanY,  'y',
         range(maxResIndex, len(prices)-1), resY, 'g',
         range(maxSupIndex, len(prices)-1), supY, 'b')
plt.show()

if resSlope < 0.001 and supSlope < 0.001:
    print "Sideways moving market."
elif resSlope > 0 and supSlope > 0:
    if (resSlope <= supSlope and resSlope >= 0.8*supSlope) \
            or (supSlope <= resSlope and supSlope >= 0.8*resSlope):
        print "Upward trending channel."
elif resSlope < 0 and supSlope < 0:
    if (resSlope <= supSlope and resSlope >= 0.8*supSlope) \
            or (supSlope <= resSlope and supSlope >= 0.8*resSlope):
        print "Downward trending channel."
elif (resSlope < 0 and supSlope > 0) \
        or (resSlope < 0 and resSlope < supSlope)\
        or (resSlope > 0 and resSlope < supSlope):
    print "Wedge trend.  May break up or down."
