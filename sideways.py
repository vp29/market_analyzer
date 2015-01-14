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

    print str(a) + "+" + str(b) + "x"
    return a, b

def genY(intercept, slope, start, end):
    y = []
    for i in range(start, end):
        y.append(intercept + slope*i)
    return y

market = open('channel_down.txt', 'r')

i=0
total = 0.0
for line in market:
    prices.append(Price(float(line), i))
    total = total + float(line)
    average.append(Price(total/(i+1), i))
    i = i+1

print "printing prices"
for price in prices:
    print "price: " + str(price) + " average: " + str(average[price.index])

maxPeak = 0.0
minTrough = float('inf')

resDiff = []
supDiff = []
maxDiff = 0.0
maxNegDiff = 0.0

tempResPrice = []
tempSupPrice = []

bigPosDiff = []
bigNegDiff = []

maxNumResIndex = 0
maxNumSupIndex = 0

for i, price in enumerate(prices):
    if i > 0 and i < len(prices) - 1:
        if price.price > prices[i-1].price and price.price > prices[i+1].price:
            peaks.append(price)
            if(price.price > maxPeak):
                maxPeak = price.price
        elif price.price < prices[i-1].price and price.price < prices[i+1].price:
            troughs.append(price)
            if(price.price < minTrough):
                minTrough = price.price

for i in range(0, len(prices)-1):
    #first do resistance line
    #find line with highest number of matched peaks
    try:
        tempResPrice = [x for x in prices if x.index > i]
        resInter, resSlope = leastSquare(tempResPrice)
        resDiff = []
        maxDiff = 0.0

        for price in tempResPrice:
            curDiff = price.price - (resInter + resSlope*price.index)
            if curDiff > maxDiff:
                maxDiff = curDiff
            resDiff.append(Price(curDiff, price.index))

        posDiff = [x for x in resDiff if x.price >= 0.8*maxDiff]
        if(len(posDiff) > maxNumResIndex):
            bigPosDiff = posDiff
            maxNumResIndex = len(posDiff)
    except:
        print "error: " + str(i)

    #next do support line
    try:
        tempSupPrice = [x for x in prices if x.index > i]
        supInter, supSlope = leastSquare(tempSupPrice)
        supDiff = []
        maxNegDiff = 0.0

        for price in tempSupPrice:
            curDiff = price.price - (supInter + supSlope*price.index)
            if curDiff < 0 and curDiff*-1 > maxNegDiff:
                maxNegDiff = curDiff*-1
            supDiff.append(Price(curDiff, price.index))

        negDiff = [x for x in supDiff if x.price*-1 >= 0.6*maxNegDiff]
        if(len(negDiff) > maxNumSupIndex):
            bigNegDiff = negDiff
            maxNumSupIndex = len(negDiff)
    except:
        print "error: " + str(i)


#posDiff = [x for x in resDiff if x.price >= 0.8*maxDiff]
#negDiff = [x for x in supDiff if x.price*-1 >= 0.4*maxNegDiff]
tempPeaks = []
tempTrough = []
for dif in bigPosDiff:
    for price in prices:
        if price.index == dif.index:
            tempPeaks.append(price)
for dif in bigNegDiff:
    for price in prices:
        if price.index == dif.index:
            tempTrough.append(price)
print len(tempPeaks)
print len(tempTrough)
resInter, resSlope = leastSquare(tempPeaks)
supInter, supSlope = leastSquare(tempTrough)

inter, slope = leastSquare(prices)

priceY = []
#put prices in list for plotting
for price in prices:
    priceY.append(price.price)

resY  = genY(resInter, resSlope, maxNumResIndex, len(prices)-1)
supY  = genY(supInter, supSlope, maxNumSupIndex, len(prices)-1)
meanY = genY(inter, slope, 0, len(prices))

plt.plot(range(0,len(prices)), priceY, 'r',
         range(0,len(prices)), meanY,  'y',
         range(maxNumResIndex, len(prices)-1), resY, 'g',
         range(maxNumSupIndex, len(prices)-1), supY, 'b')
plt.show()
#print "\nPrinting peaks: max peak = " + str(maxPeak)
#for peak in peaks:
#    print peak

#print "\nPrinting troughs: min Trough = " + str(minTrough)
#for trough in troughs:
#    print trough

#peaks = [x for x in peaks if x.price >= maxPeak*0.9]
#troughs = [x for x in troughs if x.price <= minTrough/0.9]

#print "\nPrinting near peaks: max peak = " + str(maxPeak)
#for peak in peaks:
#    print peak

#print "\nPrinting near troughs: min Trough = " + str(minTrough)
#for trough in troughs:
#    print trough

if len(peaks) > 2 and len(troughs) > 2:
    print "may be sideways"
else:
    print "probaly not sideways"
