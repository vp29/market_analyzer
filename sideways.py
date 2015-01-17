__author__ = 'Erics'

import matplotlib.pyplot as plt
import google_intraday as gi

class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

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

def trendType(resSlope, supSlope, resInt, supInt, nextInd, bsPoint, curPrice, resRange, supRange):
    potBuy = False
    nextRes = resInt + resSlope*nextInd
    nextSup = supInt + supSlope*nextInd
    resRise = resSlope*resRange
    supRise = supSlope*supRange
    diff = nextRes - nextSup
    resNorm = resRise/curPrice
    supNorm = supRise/curPrice
    print "resRise: " + str(resRise) + " supRise: " + str(supRise)
    print "resNorm: " + str(resNorm) + " supNorm: " + str(supNorm)
    normCutoff = 0.01
    if resNorm < normCutoff and resNorm > -normCutoff \
            and supNorm < normCutoff and supNorm > -normCutoff:
        potBuy = True
        print "Sideways moving market."
    elif ((resNorm < normCutoff and resNorm > -normCutoff) \
                  or (supNorm < normCutoff and supNorm > -normCutoff)):
        if((resNorm < normCutoff and resNorm > -normCutoff) and supNorm > 0):
            print "Triangle upward trend.  Predicted to break down."
        elif((supNorm < normCutoff and supNorm > -normCutoff) and resNorm < 0):
            print "Triangle downward trend.  Predicted to break up."
    elif (resNorm > 0 and supNorm > 0) \
        and ((resNorm <= supNorm and resNorm >= 0.8*supNorm) \
            or (supNorm <= resNorm and supNorm >= 0.8*resNorm)):
            potBuy = True
            print "Upward trending channel."
    elif (resNorm < 0 and supNorm < 0) \
        and ((resNorm <= supNorm and abs(0.8*resNorm) <= abs(supNorm)) \
            or (supNorm <= resNorm and abs(0.8*supNorm) <= abs(resNorm))):
            potBuy = True
            print "Downward trending channel."
    elif (resNorm < 0 and supNorm > 0) \
            or (resNorm < 0 and resNorm < supNorm)\
            or (resNorm > 0 and resNorm < supNorm):
        print "Wedge trend.  May break up or down."

    #print "buy point:  " + str((nextSup + diff*bsPoint))
    #print "sell point: " + str((nextRes - diff*bsPoint))
    return (nextSup + diff*bsPoint), (nextRes - diff*bsPoint), potBuy

market = open('ibm30sec.txt', 'r')

#data = DataReader("RGS",  "yahoo", datetime(2000,1,1), datetime(2000,10,1))
samplePeriod = 300
data = gi.GoogleIntradayQuote("TGT", samplePeriod, 50)

#i=0
#for line in market:
#    prices.append(Price(float(line), i))
#    i = i+1

analysisRange = 2400 #len(data.close) #set max points for analysis at a given step
stepSize = 10
bought = False
sellCutoff = 0.0
soldPrice = 0.0
boughtPrice = 0.0
boughtIndex = 0
start = 0
for j in range(start, len(data.close) - analysisRange, stepSize):
    print j
    prices = []
    maxPrice = 0.0
    print str(data.date[j]) + ' - ' + str(data.date[j+analysisRange])
    for i, item in enumerate(data.close[j:j+analysisRange]):
        maxPrice = item if item > maxPrice else maxPrice
        prices.append(Price(item, i))

    if bought:
        if prices[-1].price >= sellCutoff:
            soldPrice = prices[-1].price
            bought = False
            print "time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds"
            print "bought at: " + str(boughtPrice)
            print "sold at  : " + str(soldPrice)
        else:
            continue

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

    for i in range(0, len(prices) - 1):
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

    #check that there are at least 2 areas that have matches, and one is in the middle
    posMatches = [False, False, False]
    negMatches = [False, False, False]
    for i in range(0,3):
        for diff in bigPosDiff:
            if diff.index in range(maxResIndex + i*(len(prices)-maxResIndex)/3, maxResIndex + (i+1)*(len(prices)-maxResIndex)/3):
                posMatches[i] = True
        for diff in bigNegDiff:
            if diff.index in range(maxSupIndex + i*(len(prices)-maxSupIndex)/3, maxSupIndex + (i+1)*(len(prices)-maxSupIndex)/3):
                negMatches[i] = True

    print posMatches
    print negMatches

    buyPoint, sellPoint, potBuy = trendType(resSlope, supSlope, resInter, supInter,
                                    len(prices), .1, prices[-1].price,
                                    len(prices)-1 - maxResIndex, len(prices)-1 - maxSupIndex )

    #only consider buying when suport matches in middle and at least one side
    potBuy = potBuy and (negMatches[1] and (negMatches[0] or negMatches[2])) \
             and (posMatches[1] and (posMatches[0] and posMatches[2]))

    if sellPoint > buyPoint and potBuy:
        if prices[-1].price <= buyPoint and bought == False:
            bought = True
            boughtPrice = prices[-1].price
            sellCutoff = sellPoint
            boughtIndex = j
            print "Buy current price : " + str(prices[-1].price)
            print "Sell at price     : " + str(sellPoint)
        elif prices[-1].price >= sellPoint and bought == True:
            bought = False
            print "Sell current price: " + str(prices[-1].price)
            print "Buy at price      : " + str(buyPoint)

    '''plt.figure(1)
    plt.subplot(211)
    plt.plot(range(0,len(prices)), priceY, 'r',
             range(0,len(prices)), meanY,  'y',
             range(maxResIndex, len(prices)-1), resY, 'g',
             range(maxSupIndex, len(prices)-1), supY, 'b')
    plt.axis([0, len(prices), 0, maxPrice + 1])

    plt.subplot(212)
    plt.plot(range(0,len(prices)), priceY, 'r',
             range(0,len(prices)), meanY,  'y',
             range(maxResIndex, len(prices)-1), resY, 'g',
             range(maxSupIndex, len(prices)-1), supY, 'b')

    plt.show()'''
