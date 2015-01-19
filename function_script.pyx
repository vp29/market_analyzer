#from __future__ import division
import cython
import google_intraday as gi
import time

"""Eventually if we port everything into this file some of these functions can be turned into cdef so they dont have
to use the python api"""

class Price:
    price = 0.0
    index = 0
    def __init__(self, price, index):
        self.price = price
        self.index = index

    def __repr__(self):
        return '<%r> %f' % (self.index, self.price)

@cython.cdivision(True)
def leastSquare(list data):
    '''Y=a+bX, b=r*SDy/SDx, a=Y'-bX'
    b=slope
    a=intercept
    X'=Mean of x values
    Y'=Mean of y values
    SDx = standard deviation of x
    SDy = standard deviation of y'''

    cdef int num = len(data)
    cdef float xy = 0.0
    cdef float xx = 0.0
    cdef float x = 0.0
    cdef float y = 0.0
    for price in data:
        xy = xy + price.price*price.index
        xx = xx + price.index*price.index
        x = x + price.index
        y = y+ price.price

    cdef float b = (num*xy - x*y)/(num*xx-x*x)
    cdef float a = (y - b*x)/num

    return a, b


@cython.cdivision(True)
def findMatches(list tempPrice, int maxNumIndex, int maxIndex, bint neg, double cutoff, int index):
    cdef float currDiff,curMaxDiff, curInter,curSlope
    cdef signed int multiplier
    cdef list diff

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


def genY(float intercept, float slope,int start,unsigned int end):
    cdef int i
    y = []
    for i in xrange(start, end):
        y.append(intercept + slope*i)
    return y



