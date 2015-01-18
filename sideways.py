__author__ = 'Erics'

import matplotlib.pyplot as plt
import google_intraday as gi
from function_script import matchIndexes,genY, leastSquare, findMatches, Price
import time

import cProfile
#python -m cProfile -o profile.prof sideways.py
#snakeviz profile.prof
"""
class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

"""

minimumPercent = 2

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

def analyzeStock(stock, samplePeriod, analysisRange, stepSize, showChart):
    trades = open('trades.txt', 'a')
    data = gi.GoogleIntradayQuote(stock, samplePeriod, 50)

    #i=0
    #for line in market:
    #    prices.append(Price(float(line), i))
    #    i = i+1

    bought = False
    sellCutoff = 0.0
    soldPrice = 0.0
    boughtPrice = 0.0
    boughtIndex = 0
    boughtTime = ""
    start = 0
    for j in range(start, len(data.close) - analysisRange, stepSize):
        start_time = time.time()
        print j
        prices = []
        maxPrice = 0.0
        print str(data.date[j]) + ' - ' + str(data.date[j+analysisRange])
        for i, item in enumerate(data.close[j:j+analysisRange]):
            maxPrice = item if item > maxPrice else maxPrice
            prices.append(Price(item, i))

        if bought:
            if prices[-1].price >= sellCutoff:
                trades.write("(" + stock + ") time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds\n")
                trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
                trades.write("(" + stock + ") sold at  : " + str(soldPrice) + '\n')
                trades.write("(" + stock + ") percent gain: " + str(float(soldPrice-boughtPrice)/boughtPrice) + '\n')
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
            """A- This is potentially a very intesive loop. Function overhead in python is high. Maybe better to not turn it into a function?"""
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

        if sellPoint > buyPoint*(1.0 + minimumPercent/100) and potBuy:
            if prices[-1].price <= buyPoint and bought == False:
                bought = True
                boughtPrice = prices[-1].price
                sellCutoff = sellPoint
                boughtIndex = j
                boughtTime = data.date[j+analysisRange]
                print "Buy current price : " + str(prices[-1].price)
                print "Sell at price     : " + str(sellPoint)
            elif prices[-1].price >= sellPoint and bought == True:
                bought = False
                print "Sell current price: " + str(prices[-1].price)
                print "Buy at price      : " + str(buyPoint)

        if showChart==True:
            plt.figure(1)
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

            plt.show()
        end_time = time.time()
        print("total time taken this loop: ", end_time - start_time)

    if bought == True:
        trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
        trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')

stocks = open('fortune500.txt', 'r')

#data = DataReader("RGS",  "yahoo", datetime(2000,1,1), datetime(2000,10,1))
samplePeriod = 300
analysisRange = 2400 #len(data.close) #set max points for analysis at a given step
stepSize = 10

for line in stocks:
    line = line[:-1] if "\n" in line else line
    print line
    analyzeStock(stock=line, samplePeriod=samplePeriod, analysisRange=analysisRange, stepSize=stepSize, showChart=False)


#whats with your dates
#why false, true, true
#http://gyazo.com/4585b43a224831e154a90f1037117977
#There needs to be a check in place(if not already put?) that will make sure that the difference between the spread
#and the resistance is meaningful along with making sure the stock price is appropriate for our accoutn balance
# i.e. we dont want to trade soemthign with 5 cents between the support and resistance, espeically when its
#priced at 300$ per share which we could be something like 95% of our account balance
#then again you can make teh argument that with tight stop losses it might be worth putting 60%-90% of our free money in a single trade
#if the potential for profit is high
