__author__ = 'Erics'

import google_intraday as gi
from function_script import matchIndexes, genY, leastSquare, findMatches, Price, Trade, generate_a_graph,background
import multiprocessing
import requests
from variables import analysisRange, stop_loss_perc, bufferPercent, minimumPercent, samplePeriod, stepSize, startingMoney, initial_investment, total
import time
from datetime import datetime, timedelta
import sqlite3
import threading

#import cProfile
#python -m cProfile -o profile.prof sideways.py
#snakeviz profile.prof
conn = sqlite3.connect('stocks.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS stocks (id INTEGER PRIMARY KEY, symbol TEXT, buy_date INTEGER, sell_date INTEGER, buy_price DOUBLE, sell_price DOUBLE);")
conn.commit()

database = False

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
    if -normCutoff < resNorm < normCutoff\
            and -normCutoff < supNorm < normCutoff:
        potBuy = True
        print "Sideways moving market."
    elif ((-normCutoff < resNorm < normCutoff)
            or (-normCutoff < supNorm < normCutoff)):
        if -normCutoff < resNorm < normCutoff and supNorm > 0:
            print "Triangle upward trend.  Predicted to break down."
        elif -normCutoff < supNorm < normCutoff and resNorm < 0:
            print "Triangle downward trend.  Predicted to break up."
    elif (resNorm > 0 and supNorm > 0) \
        and ((0.9*supNorm <= resNorm <= supNorm)
             or (0.9*resNorm <= supNorm <= resNorm)):
            potBuy = True
            print "Upward trending channel."
    elif (resNorm < 0 and supNorm < 0) \
            and ((resNorm <= supNorm and abs(0.9*resNorm) <= abs(supNorm))
                 or (supNorm <= resNorm and abs(0.9*supNorm) <= abs(resNorm))):
            potBuy = True
            print "Downward trending channel."
    elif (resNorm < 0 > supNorm) \
            or (resNorm < 0 and resNorm < supNorm)\
            or (supNorm > resNorm > 0):
        print "Wedge trend.  May break up or down."

    #print "buy point:  " + str((nextSup + diff*bsPoint))
    #print "sell point: " + str((nextRes - diff*bsPoint))
    return (nextSup + diff*bsPoint), (nextRes - diff*bsPoint), potBuy



def analyzeStock(stock, samplePeriod, analysisRange, stepSize, showChart, investment, read_csv, csvname=""):
    global global_percent_gain
    trades = open('trades.txt', 'a')

    data = None
    if read_csv:
        date = []
        open_ = []
        high = []
        low = []
        close = []
        with open(csvname, 'rb') as csvfile:
        #with open('data/cop10yeod.csv', 'rb') as csvfile:
            import csv
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i = 0
            for row in spamreader:
                if len(row) != 7:
                    continue
                if '.' not in str(row[4]) and len(str(row[4])) >=4:
                    continue
                if i % 5 == 0:
                    date.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                    open_.append(float(row[1]))
                    high.append(float(row[2]))
                    low.append(float(row[3]))
                    close.append(float(row[4]))
                i += 1
        data = gi.Quote()
        data.appendAll(date, open_, high, low, close)

    else:
        data = gi.GoogleIntradayQuote(stock, samplePeriod, 50)

    bought = False
    #sellCutoff = 0.0
    #sold_price = 0.0
    boughtPrice = 0.0
    buffer_zone = False
    #boughtIndex = 0
    boughtTime = ""
    bought_list = []
    start = 0
    for j in range(start, len(data.close) - analysisRange, stepSize):
        #start_time = time.time()
        #print j
        prices = []
        maxPrice = 0.0
        #print str(data.date[j]) + ' - ' + str(data.date[j+analysisRange])
        for i, item in enumerate(data.close[j:j+analysisRange]):
            maxPrice = item if item > maxPrice else maxPrice
            prices.append(Price(item, i))



        if bought:
            for trade in bought_list:
                if prices[-1].price >= trade.sell_cutoff:
                    sold_price = prices[-1].price
                    soldDate = data.date[j+analysisRange]
                    soldTime = data.time[j+analysisRange]
                    soldDateTime = datetime(soldDate.year, soldDate.month, soldDate.day,
                                            soldTime.hour, soldTime.minute, soldTime.second)
                    soldTimestamp = (soldDateTime - datetime(1970, 1, 1)).total_seconds()
                    global_percent_gain += float(sold_price-trade.buy_price)/trade.buy_price

                    #MAKE SURE the kwargs at the end have the correct values set then remove this comment, then implement it the second if statement below
                    res_y = genY(resInter, resSlope, j-boughtIndex-960, j-boughtIndex)
                    sup_y = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
                    mean_y = genY(inter, slope, 0, len(prices))
                    price_y = []
                    #put prices in list for plotting
                    for price in prices:
                        price_y.append(price.price)
                    generate_a_graph(prices,price_y,mean_y,maxResIndex,res_y,maxSupIndex,sup_y,str(j)+stock,"closed profitable trade",buy_price=trade.buy_price,buy_index=genY(resInter,resSlope,j-boughtIndex-960,j-boughtIndex),sold_price=sold_price,sold_index=prices[-1].index)
                    trades.write("(" + stock + ") bought time: " + str(trade.buy_time) + '\n')
                    trades.write("(" + stock + ") time to sell: " + str((soldTimestamp - trade.buy_time)/1000) + " seconds\n")
                    trades.write("(" + stock + ") bought at: " + str(trade.buy_price) + '\n')
                    trades.write("(" + stock + ") sold at  : " + str(sold_price) + '\n')
                    trades.write("(" + stock + ") percent gain: " + str(float(sold_price-trade.buy_price)/trade.buy_price * 100) + '\n')
                    trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                    trades.write("")
                    if database:
                        #print (stock, int(trade.buy_time), int(soldTimestamp), float(trade.buy_price), float(sold_price))
                        c.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?);", (None, stock, int(trade.buy_time), int(soldTimestamp), float(trade.buy_price), float(sold_price)))
                        conn.commit()
                    bought_list.remove(trade)
                    if len(bought_list) == 0:
                        bought = False
                    investment *= (1+float(sold_price-trade.buy_price)/trade.buy_price)
                    print "time to sell: " + str((soldTimestamp - trade.buy_time)/1000) + " seconds"
                    print "bought at: " + str(trade.buy_price)
                    print "sold at  : " + str(sold_price)
                elif prices[-1].price <= (trade.buy_price - trade.buy_price*stop_loss_perc/100):
                    sold_price = prices[-1].price
                    soldDate = data.date[j+analysisRange]
                    soldTime = data.time[j+analysisRange]
                    soldDateTime = datetime(soldDate.year, soldDate.month, soldDate.day,
                                            soldTime.hour, soldTime.minute, soldTime.second)
                    soldTimestamp = (soldDateTime - datetime(1970, 1, 1)).total_seconds()
                    global_percent_gain += float(sold_price-trade.buy_price)/trade.buy_price
                    trades.write("(" + stock + ") bought time: " + str(trade.buy_time) + '\n')
                    trades.write("(" + stock + ") Stop Loss time to sell: " + str((soldTimestamp - trade.buy_time)/1000) + " seconds\n")
                    trades.write("(" + stock + ") Stop Loss bought at: " + str(trade.buy_price) + '\n')
                    trades.write("(" + stock + ") Stop Loss sold at  : " + str(sold_price) + '\n')
                    trades.write("(" + stock + ") Stop Loss percent lost: " + str(float(sold_price-trade.buy_price)/trade.buy_price * 100) + '\n')
                    trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
                    trades.write("")
                    investment *= (1+float(sold_price-trade.buy_price)/trade.buy_price)
                    print "Stop Loss bought at: " + str(trade.buy_price)
                    print "Stop Loss sold at: " + str(sold_price)
                    if database:
                        c.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?);", (None, stock, int(trade.buy_time), int(soldTimestamp), float(trade.buy_price), float(sold_price)))
                        conn.commit()
                    bought_list.remove(trade)
                    if len(bought_list) == 0:
                        bought = False
                    continue
                else:
                    if not database:
                        continue
            if len(bought_list) == 1 and not database:
                continue

        #resDiff = []
        #supDiff = []
        #maxDiff = 0.0
        #maxNegDiff = 0.0

        #tempResPrice = []
        #tempSupPrice = []

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
            """A- This is potentially a very intensive loop.
            Function overhead in python is high. Maybe better to not turn it into a function?"""
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
        #print len(tempPeaks)
        try:
            resInter, resSlope = leastSquare(tempPeaks)
            supInter, supSlope = leastSquare(tempTrough)
        except:
            continue

        sup_val = supInter + supSlope*len(prices)
        res_val = resInter + resSlope*len(prices)

        max_buy_point = sup_val + (res_val-sup_val)*(0.2)
        min_buy_point = sup_val + (res_val-sup_val)*(0.1)

        if buffer_zone:

            inter, slope = leastSquare(prices)

            price_y = []
            #put prices in list for plotting
            for price in prices:
                price_y.append(price.price)

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

            #only consider buying when support matches in middle and at least one side
            pot_buy = pot_buy and (neg_matches[1] and (neg_matches[0] or neg_matches[2])) \
                and (pos_matches[1] and (pos_matches[0] and pos_matches[2]))

            # print "Sell Point: " + str(sell_point)
            # print "Buy Range:  " + str(min_buy_point) + ' - ' + str(max_buy_point)
            # print "Cur Price:  " + str(prices[-1].price)
            # print "buf Price:  " + str(sup_val + (res_val - sup_val)*(bufferPercent/100))

            if sell_point > prices[-1].price*(1.0 + minimumPercent/100) and pot_buy:
                if min_buy_point <= prices[-1].price <= max_buy_point and (database or (not database and bought == False)): #and bought == False:
                    if not database:
                        res_y = genY(resInter, resSlope, maxResIndex, len(prices)-1)
                        sup_y = genY(supInter, supSlope, maxSupIndex, len(prices)-1)
                        mean_y = genY(inter, slope, 0, len(prices))
                        generate_a_graph(prices,price_y,mean_y,maxResIndex,res_y,maxSupIndex,sup_y,str(j)+stock,"Generated buy order")
                    bought = True
                    buffer_zone = False
                    boughtPrice = prices[-1].price
                    sellCutoff = sell_point
                    boughtIndex = j
                    boughtTime = data.date[j+analysisRange]
                    boughtDate = data.date[j+analysisRange]
                    bought_time = data.time[j+analysisRange]
                    boughtDateTime = datetime(boughtDate.year, boughtDate.month, boughtDate.day,
                                                             bought_time.hour, bought_time.minute, bought_time.second)
                    boughtTimestamp = (boughtDateTime - datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
                    print "Buy current price : " + str(prices[-1].price)
                    print "Sell at price     : " + str(sell_point)
                    bought_list.append(Trade(boughtTimestamp, 0, sellCutoff, boughtPrice, 0.0))
                #elif prices[-1].price >= sell_point and bought == True:
                #    bought = False
                #    print "Sell current price: " + str(prices[-1].price)
                #    print "Buy at price      : " + str(buy_point)

        #check if within buffer zone
        if sup_val + (res_val-sup_val)*(bufferPercent/100) >= prices[-1].price:
            buffer_zone = True
        elif prices[-1].price < min_buy_point and buffer_zone:
            buffer_zone = True
        else:
            buffer_zone = False


        #end_time = time.time()
        #print("total time taken this loop: ", end_time - start_time)

    if bought:
        sold_price = data.close[-1]
        global_percent_gain += float(sold_price-boughtPrice)/boughtPrice
        trades.write("(" + stock + ") bought time: " + str(boughtTime) + '\n')
        trades.write("(" + stock + ") bought at: " + str(boughtPrice) + '\n')
        trades.write("(" + stock + ") current price: " + str(data.close[-1]) + '\n')
        trades.write("(" + stock + ") percent gain: " + str(float(data.close[-1]-boughtPrice)/boughtPrice * 100) + '\n')
        trades.write("Global percent gain: " + str(global_percent_gain*100) + '\n')
        investment *= (1+float(data.close[-1]-boughtPrice)/boughtPrice)

    return investment


def analyzefortune500stocks():
    global total
    stocks = open('fortune500.txt', 'r')
    for line in stocks:
        line = line[:-1] if "\n" in line else line
        print line
        #i know this isn't how it would work since these would be going on in parallel, but it
        #gives an idea

        investment = analyzeStock(stock=line, samplePeriod=samplePeriod, analysisRange=analysisRange,
                                  stepSize=stepSize, showChart=False, investment=initial_investment, read_csv=False)
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

    investment = analyzeStock(stock='CSC', samplePeriod=samplePeriod, analysisRange=analysisRange,
                              stepSize=stepSize, showChart=False, investment=initial_investment, read_csv=True, csvname='data/CSC.csv')

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
#and the resistance is meaningful along with making sure the stock price is appropriate for our account balance
# i.e. we don't want to trade something with 5 cents between the support and resistance, especially when its
#priced at 300$ per share which we could be something like 95% of our account balance
#then again you can make teh argument that with tight stop losses it might be worth
# putting 60%-90% of our free money in a single trade
#if the potential for profit is high