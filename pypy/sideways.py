__author__ = 'Erics'

import google_intraday as gi
from function_script import matchIndexes,genY, leastSquare, findMatches, Price

#b/c we dont want to share variables for testing sometimes
from variables import analysisRange, stop_loss_perc,minimumPercent,samplePeriod,stepSize,startingMoney, initial_investment
import time

#import cProfile
#python -m cProfile -o profile.prof sideways.py
#snakeviz profile.prof


global_percent_gain = 0.0
global_stock_values = []

def trendType(resSlope, supSlope, resInt, supInt, nextInd, bsPoint, curPrice, resRange, supRange):
    potBuy = False
    nextRes = resInt + resSlope*nextInd
    nextSup = supInt + supSlope*nextInd
    resRise = resSlope*resRange
    supRise = supSlope*supRange
    diff = nextRes - nextSup
    resNorm = resRise/curPrice
    supNorm = supRise/curPrice
    #print "resRise: " + str(resRise) + " supRise: " + str(supRise)
    #print "resNorm: " + str(resNorm) + " supNorm: " + str(supNorm)
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



def analyzeStock(stock, samplePeriod, analysisRange, stepSize, showChart, investment):
    global global_percent_gain
    trades = open('trades.txt', 'a')
    data = gi.GoogleIntradayQuote(stock, samplePeriod, 50)

    print len(data.close)

    #i=0
    #for line in market:
    #    prices.append(Price(float(line), i))
    #    i = i+1


    bought = False
    sellCutoff = 0.0
    sold_price = 0.0
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
                sold_price = prices[-1].price
                global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
                trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
                trades.write("(" + stock + ") time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds\n")
                trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
                trades.write("(" + stock + ") sold at  : " + str(sold_price) + '\n')
                trades.write("(" + stock + ") percent gain: " + str(float(sold_price-boughtPrice)/boughtPrice * 100) + '\n')
                trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                bought = False
                investment = investment*(1+float(sold_price-boughtPrice)/boughtPrice)
                print "time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds"
                print "bought at: " + str(boughtPrice)
                print "sold at  : " + str(sold_price)
            elif prices[-1].price <= (boughtPrice - boughtPrice*stop_loss_perc/100):
                bought = False
                sold_price = prices[-1].price
                global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
                trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
                trades.write("(" + stock + ") Stop Loss time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds\n")
                trades.write("(" + stock + ") Stop Loss bought at: " + str(boughtPrice) + '\n')
                trades.write("(" + stock + ") Stop Loss sold at  : " + str(sold_price) + '\n')
                trades.write("(" + stock + ") Stop Loss percent lost: " + str(float(sold_price-boughtPrice)/boughtPrice * 100) + '\n')
                trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                investment = investment*(1+float(sold_price-boughtPrice)/boughtPrice)
                print "Stop Loss bought at: " + str(boughtPrice)
                print "Stop Loss sold at: " + str(sold_price)
                continue
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
        try:
            resInter, resSlope = leastSquare(tempPeaks)
            supInter, supSlope = leastSquare(tempTrough)
        except:
            continue

        inter, slope = leastSquare(prices)

        price_y = []
        #put prices in list for plotting
        for price in prices:
            price_y.append(price.price)

        res_y = genY(resInter, resSlope, maxResIndex, len(prices)-1)
        sup_y = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
        mean_y = genY(inter, slope, 0, len(prices))

        #check that there are at least 2 areas that have matches, and one is in the middle
        pos_matches = [False, False, False]
        neg_matches = [False, False, False]
        for i in range(0,3):
            for diff in bigPosDiff:
                if diff.index in range(maxResIndex + i*(len(prices)-maxResIndex)/3, maxResIndex + (i+1)*(len(prices)-maxResIndex)/3):
                    pos_matches[i] = True
            for diff in bigNegDiff:

                if diff.index in range(maxSupIndex + i*(len(prices)-maxSupIndex)/3, maxSupIndex + (i+1)*(len(prices)-maxSupIndex)/3):
                    neg_matches[i] = True

        #print pos_matches
        #print neg_matches

        buy_point, sell_point, pot_buy = trendType(resSlope, supSlope, resInter, supInter,
                                        len(prices), .1, prices[-1].price,
                                        len(prices)-1 - maxResIndex, len(prices)-1 - maxSupIndex )

        #only consider buying when suport matches in middle and at least one side
        pot_buy = pot_buy and (neg_matches[1] and (neg_matches[0] or neg_matches[2])) \
                 and (pos_matches[1] and (pos_matches[0] and pos_matches[2]))

        if sell_point > buy_point*(1.0 + minimumPercent/100) and pot_buy:
            if prices[-1].price <= buy_point and bought == False:
                bought = True
                boughtPrice = prices[-1].price
                sellCutoff = sell_point
                boughtIndex = j
                boughtTime = data.date[j+analysisRange]
                print "Buy current price : " + str(prices[-1].price)
                print "Sell at price     : " + str(sell_point)
            elif prices[-1].price >= sell_point and bought == True:
                bought = False
                print "Sell current price: " + str(prices[-1].price)
                print "Buy at price      : " + str(buy_point)


        end_time = time.time()
        print("total time taken this loop: ", end_time - start_time)

    if bought:
        sold_price = data.close[-1]
        global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
        trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
        trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
        trades.write("(" + stock + ") current price: " + str(data.close[-1]) + '\n')
        trades.write("(" + stock + ") perceant gain: " + str(float(data.close[-1]-boughtPrice)/boughtPrice * 100) + '\n')
        trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
        investment = investment*(1+float(data.close[-1]-boughtPrice)/boughtPrice)

    return investment


def analyzefile(samplePeriod, analysisRange, stepSize, showChart, investment):
    global global_percent_gain
    import csv
    stock = 'bitcoin'

    market_prices = []
    #with open('data/bitstampUSD.csv', 'rb') as csvfile:
    with open('data/cop10yeod.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            market_prices.append(float(row[1]))
    trades = open('trades.txt', 'a')




    bought = False
    sellCutoff = 0.0
    sold_price = 0.0
    boughtPrice = 0.0
    boughtIndex = 0
    boughtTime = ""
    start = 0
    for j in range(start, len(market_prices) - analysisRange, stepSize):
        start_time = time.time()
        #print j
        prices = []
        maxPrice = 0.0
        for i, item in enumerate(market_prices[j:j+analysisRange]):
            prices.append(Price(item, i))
        if bought:
            if prices[-1].price >= sellCutoff:
                sold_price = prices[-1].price
                global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
                trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
                trades.write("(" + stock + ") time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds\n")
                trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
                trades.write("(" + stock + ") sold at  : " + str(sold_price) + '\n')
                trades.write("(" + stock + ") percent gain: " + str(float(sold_price-boughtPrice)/boughtPrice * 100) + '\n')
                trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                bought = False
                investment = investment*(1+float(sold_price-boughtPrice)/boughtPrice)
                print "time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds"
                print "bought at: " + str(boughtPrice)
                print "sold at  : " + str(sold_price)
            elif prices[-1].price <= (boughtPrice - boughtPrice*stop_loss_perc/100):
                bought = False
                sold_price = prices[-1].price
                global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
                trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
                trades.write("(" + stock + ") Stop Loss time to sell: " + str((j-boughtIndex)*samplePeriod) + " seconds\n")
                trades.write("(" + stock + ") Stop Loss bought at: " + str(boughtPrice) + '\n')
                trades.write("(" + stock + ") Stop Loss sold at  : " + str(sold_price) + '\n')
                trades.write("(" + stock + ") Stop Loss percent lost: " + str(float(sold_price-boughtPrice)/boughtPrice * 100) + '\n')
                trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                investment = investment*(1+float(sold_price-boughtPrice)/boughtPrice)
                print "Stop Loss bought at: " + str(boughtPrice)
                print "Stop Loss sold at: " + str(sold_price)
                continue
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
            except Exception as e:
                None
            #next do support line
            try:
                tempSupPrice = [x for x in prices if x.index > i]
                bigNegDiff, maxNumSupIndex, maxSupIndex = findMatches(tempSupPrice, maxNumSupIndex, maxSupIndex, True, 0.6, i)
            except Exception as e:
                #print e
                None
        tempPeaks = matchIndexes(bigPosDiff, prices)
        tempTrough = matchIndexes(bigNegDiff, prices)

        #print len(tempTrough)
        try:
            resInter, resSlope = leastSquare(tempPeaks)
            supInter, supSlope = leastSquare(tempTrough)
        except:
            continue

        inter, slope = leastSquare(prices)

        price_y = []
        #put prices in list for plotting
        for price in prices:
            price_y.append(price.price)

        res_y = genY(resInter, resSlope, maxResIndex, len(prices)-1)
        sup_y = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
        mean_y = genY(inter, slope, 0, len(prices))

        #check that there are at least 2 areas that have matches, and one is in the middle
        pos_matches = [False, False, False]
        neg_matches = [False, False, False]
        for i in range(0,3):
            for diff in bigPosDiff:
                if diff.index in range(maxResIndex + i*(len(prices)-maxResIndex)/3, maxResIndex + (i+1)*(len(prices)-maxResIndex)/3):
                    pos_matches[i] = True
            for diff in bigNegDiff:

                if diff.index in range(maxSupIndex + i*(len(prices)-maxSupIndex)/3, maxSupIndex + (i+1)*(len(prices)-maxSupIndex)/3):
                    neg_matches[i] = True

        #print pos_matches
        #print neg_matches

        buy_point, sell_point, pot_buy = trendType(resSlope, supSlope, resInter, supInter,
                                        len(prices), .1, prices[-1].price,
                                        len(prices)-1 - maxResIndex, len(prices)-1 - maxSupIndex )

        #only consider buying when suport matches in middle and at least one side
        pot_buy = pot_buy and (neg_matches[1] and (neg_matches[0] or neg_matches[2])) \
                 and (pos_matches[1] and (pos_matches[0] and pos_matches[2]))

        if sell_point > buy_point*(1.0 + minimumPercent/100) and pot_buy:
            if prices[-1].price <= buy_point and bought == False:
                bought = True
                boughtPrice = prices[-1].price
                sellCutoff = sell_point
                boughtIndex = j
                boughtTime = j
                print "Buy current price : " + str(prices[-1].price)
                print "Sell at price     : " + str(sell_point)
            elif prices[-1].price >= sell_point and bought == True:
                bought = False
                print "Sell current price: " + str(prices[-1].price)
                print "Buy at price      : " + str(buy_point)


        end_time = time.time()
        #print("total time taken this loop: ", end_time - start_time)

    if bought:
        sold_price = market_prices[-1]
        global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
        trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
        trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
        trades.write("(" + stock + ") current price: " + str(market_prices[-1]) + '\n')
        trades.write("(" + stock + ") perceant gain: " + str(float(market_prices[-1]-boughtPrice)/boughtPrice * 100) + '\n')
        trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
        investment *= (1+float(market_prices[-1]-boughtPrice)/boughtPrice)

    return investment

def analyzefortune500stocks():
    global total
    stocks = open('fortune500.txt', 'r')
    for line in stocks:
        line = line[:-1] if "\n" in line else line
        print line
        #i know this isnt how it would work since these would be going on in parrallel, but it
        #gives an idea

        investment = analyzeStock(stock=line, samplePeriod=samplePeriod, analysisRange=analysisRange,
                                  stepSize=stepSize, showChart=False, investment=initial_investment)
        if investment != initial_investment:
            #initial += initial_investment
            total += investment-initial_investment
            #global_stock_values.append(investment)
        trades = open('trades.txt', 'a')
        trades.write("Initial Investment: " + str(startingMoney) + '\n')
        trades.write("Total Value: " + str(total) + '\n')
        trades.write("Total Percent Gain: " + str((total-startingMoney)/startingMoney*100) + '\n')
        print "Initial Investment: " + str(startingMoney)
        print "Total Value: " + str(total)
        print "Total Percent Gain: " + str((total-startingMoney)/startingMoney*100)


def analyzebitstamp():
    global total
    investment = analyzefile(samplePeriod=samplePeriod, analysisRange=analysisRange,
                          stepSize=stepSize, showChart=False, investment=initial_investment)
    if investment != initial_investment:
        #initial += initial_investment
        total += investment-initial_investment
        #global_stock_values.append(investment)
    trades = open('trades.txt', 'a')
    trades.write("Initial Investment: " + str(startingMoney) + '\n')
    trades.write("Total Value: " + str(total) + '\n')
    trades.write("Total Percent Gain: " + str((total-startingMoney)/startingMoney*100) + '\n')
    print "Initial Investment: " + str(startingMoney)
    print "Total Value: " + str(total)
    print "Total Percent Gain: " + str((total-startingMoney)/startingMoney*100)



if __name__ == "__main__":
    #analyzefortune500stocks()
    analyzebitstamp()

#why false, true, true
#http://gyazo.com/4585b43a224831e154a90f1037117977
#There needs to be a check in place(if not already put?) that will make sure that the difference between the spread
#and the resistance is meaningful along with making sure the stock price is appropriate for our accoutn balance
# i.e. we dont want to trade soemthign with 5 cents between the support and resistance, espeically when its
#priced at 300$ per share which we could be something like 95% of our account balance
#then again you can make teh argument that with tight stop losses it might be worth putting 60%-90% of our free money in a single trade
#if the potential for profit is high
