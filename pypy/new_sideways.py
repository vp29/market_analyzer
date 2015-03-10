from __future__ import division
from classes.Helper import Helper
from classes.Data import Data
from classes.Database import Database
from classes.Trade import Trade
from classes.Data import Data
from classes.Line import Line
from classes.Diff import Diff
from variables import *
import sqlite3
import pymysql
import time

table_name = str(time.time()//1)
table_name = table_name[:-2]
print table_name

#table_name = '1424992244'

DATABASE = True
GRAPHING = True

if DATABASE:
    db = Database(table_name)

def analyze_stock(symbol, filename):
    print symbol
    data = Helper.read_csv(filename)

    trades = []
    start = 0
    short_buffer_zone = False
    long_buffer_zone = False
    long_term_range = 3*analysisRange
    for i in range(start+(long_term_range//3)*2, len(data) - analysisRange, stepSize):
        #start_time = time.time()
        prices = data[i: i+analysisRange]
        long_prices = data[i-2*analysisRange//3: i+analysisRange]
        for j in range(0, len(prices)):
            prices[j].index = j
        close = prices[-1].close

        for trade in trades:
            trade.prices.append(prices[-1])
            if trade.long_short == "long":
                if close >= trade.exit_cutoff:
                    trade.sell_price = close
                    trade.sell_time = prices[-1].timestamp
                    if GRAPHING:
                        trade.res_line.end = len(trade.prices)-1
                        trade.sup_line.end = len(trade.prices)-1
                        trade.mean_line.end = len(trade.prices)-1
                        url = Helper.generate_a_graph(trade.res_line, trade.sup_line, trade.mean_line, trade.prices, symbol + " long gain " + str(i), "testing" + str(i), trade.exit_cutoff, buy_price=trade.buy_price, buy_index=analysisRange, sold_price=trade.sell_price, sold_index=len(trade.prices)-1)
                        trade.exit_url = url
                    if DATABASE:
                        db.insert_trade(trade)
                    trades.remove(trade)
                    print trade
                #stop loss exit
                elif close <= trade.stop_loss_val:
                    trade.sell_price = close
                    trade.sell_time = prices[-1].timestamp
                    if GRAPHING:
                        trade.res_line.end = len(trade.prices)-1
                        trade.sup_line.end = len(trade.prices)-1
                        trade.mean_line.end = len(trade.prices)-1
                        url = Helper.generate_a_graph(trade.res_line, trade.sup_line, trade.mean_line, trade.prices, symbol + " long stop loss " + str(i), "testing" + str(i), trade.exit_cutoff, buy_price=trade.buy_price, buy_index=analysisRange, sold_price=trade.sell_price, sold_index=len(trade.prices)-1)
                        trade.exit_url = url
                    if DATABASE:
                        db.insert_trade(trade)
                    trades.remove(trade)
                    print trade
                #if we go past mean, set stop loss at close - 25% of difference
                elif close > trade.buy_price + (trade.exit_cutoff-trade.buy_price)/2:
                    trades.remove(trade)
                    if trade.stop_loss_val < close - (trade.exit_cutoff-trade.buy_price)/4:
                        trade.stop_loss_val = close - (trade.exit_cutoff-trade.buy_price)/4
                    trades.append(trade)
                #if we go over even_stop_loss_perc, set stop loss as buy_price
                #elif close >= (trade.buy_price + (trade.exit_cutoff - trade.buy_price)*even_stop_loss_perc/100):
                #    trades.remove(trade)
                #    trade.stop_loss_val = trade.stop_loss_val if trade.stop_loss_val > trade.buy_price else trade.buy_price
                #    trades.append(trade)
                else:
                    continue
            elif trade.long_short == "short":
                if close <= trade.exit_cutoff:
                    trade.buy_price = close
                    trade.buy_time = prices[-1].timestamp
                    if GRAPHING:
                        trade.res_line.end = len(trade.prices)-1
                        trade.sup_line.end = len(trade.prices)-1
                        trade.mean_line.end = len(trade.prices)-1
                        url = Helper.generate_a_graph(trade.res_line, trade.sup_line, trade.mean_line, trade.prices, symbol + " short gain " + str(i), "testing" + str(i), trade.exit_cutoff, buy_price=trade.buy_price, buy_index=len(trade.prices)-1, sold_price=trade.sell_price, sold_index=analysisRange)
                        trade.exit_url = url
                    if DATABASE:
                        db.insert_trade(trade)
                    trades.remove(trade)
                    print trade
                elif close >= trade.stop_loss_val:
                    trade.buy_price = close
                    trade.buy_time = prices[-1].timestamp
                    if GRAPHING:
                        trade.res_line.end = len(trade.prices)-1
                        trade.sup_line.end = len(trade.prices)-1
                        trade.mean_line.end = len(trade.prices)-1
                        url = Helper.generate_a_graph(trade.res_line, trade.sup_line, trade.mean_line, trade.prices, symbol + " short stop loss " + str(i), "testing" + str(i), trade.exit_cutoff, buy_price=trade.buy_price, buy_index=len(trade.prices)-1, sold_price=trade.sell_price, sold_index=analysisRange)
                        trade.exit_url = url
                    if DATABASE:
                        db.insert_trade(trade)
                    trades.remove(trade)
                    print trade
                #if we go past mean, set stop loss at 25% of difference
                elif close < trade.sell_price - (trade.sell_price-trade.exit_cutoff)/2:
                    trades.remove(trade)
                    if trade.stop_loss_val > close + (trade.sell_price-trade.exit_cutoff)/4:
                        trade.stop_loss_val = close + (trade.sell_price-trade.exit_cutoff)/4
                    trades.append(trade)
                #if we go over even_stop_loss_perc, set stop loss as buy_price
                #elif close <= (trade.sell_price - (trade.sell_price-trade.exit_cutoff)*even_stop_loss_perc/100):
                #    trades.remove(trade)
                #    trade.stop_loss_val = trade.stop_loss_val if trade.stop_loss_val < trade.sell_price else trade.sell_price
                #    trades.append(trade)
                else:
                    continue

        res_diff = []
        sup_diff = []
        max_num_res_index = 0
        max_num_sup_index = 0
        max_res_index = 0
        max_sup_index = 0

        #try:
        for j in range(0,1):#range(0, analysisRange-1):
            temp_prices = prices[j:]
            inter, slope = Helper.least_square(temp_prices)
            #print inter
            #print slope
            y_vals = Line(inter, slope, j, analysisRange).get_values()
            diff_vals = []
            for z in range(0, len(temp_prices)):
                diff_vals.append(temp_prices[z].close - y_vals[z]) #[x - y for x, y in zip(temp_prices, y_vals)]

            try:
                res_diff, max_num_res_index, max_res_index = Helper.find_matches(diff_vals, max_num_res_index,
                                                                             max_res_index, 1, resCutoff, j)
            except:
                None

            try:
                sup_diff, max_num_sup_index, max_sup_index = Helper.find_matches(diff_vals, max_num_sup_index,
                                                                             max_sup_index, -1, supCutoff, j)
            except:
                None
        #except:
        #    None

        #print len(sup_diff)
        #print len(res_diff)

        temp_peaks = Helper.match_indexes(res_diff, prices)
        temp_troughs = Helper.match_indexes(sup_diff, prices)

        try:
            res_inter, res_slope = Helper.least_square(temp_peaks)
            sup_inter, sup_slope = Helper.least_square(temp_troughs)
        except:
            #print "error"
            continue

        res_val = res_inter + res_slope*analysisRange
        sup_val = sup_inter + sup_slope*analysisRange

        max_long_buy_point = sup_val + (res_val-sup_val)*resMaxBuyPer/100
        min_long_buy_point = sup_val + (res_val-sup_val)*resMinBuyPer/100

        max_short_sell_point = res_val - (res_val-sup_val)*supMinBuyPer/100
        min_short_sell_point = res_val - (res_val-sup_val)*supMaxBuyPer/100

        if long_buffer_zone or short_buffer_zone:

            inter, slope = Helper.least_square(prices)
            #long_inter, long_slope = Helper.least_square(long_prices)
            resLine = Line(res_inter, res_slope, max_res_index, analysisRange)
            supLine = Line(sup_inter, sup_slope, max_sup_index, analysisRange)
            meanLine = Line(inter, slope, 0, analysisRange)

            #check that there are at least 2 areas that have matches, and one is in the middle
            pos_matches = [False, False, False]
            neg_matches = [False, False, False]
            for k in range(0,3):
                for diff in res_diff:
                    if diff.index in range(max_res_index + k*(len(prices)-max_res_index)//3, max_res_index + (k+1)*(len(prices)-max_res_index)//3):
                        pos_matches[k] = True
                for diff in sup_diff:
                    if diff.index in range(max_sup_index + k*(len(prices)-max_sup_index)//3, max_sup_index + (k+1)*(len(prices)-max_sup_index)//3):
                        neg_matches[k] = True

            buy_point, sell_point, pot_buy, actual_type = Helper.trendType(res_slope, sup_slope, res_inter, sup_inter,
                                                              analysisRange, supMinBuyPer/100, resMinBuyPer/100, close,
                                                              analysisRange-1 - max_res_index,
                                                              analysisRange-1 - max_sup_index)

            #only consider buying when support matches in middle and at least one side
            long_pot_buy = pot_buy and (neg_matches[1] and (neg_matches[0] or neg_matches[2])) \
                and (pos_matches[1] and (pos_matches[0] and pos_matches[2]))
            short_pot_buy = long_pot_buy# and (neg_matches[1] and (neg_matches[0] and neg_matches[2])) \
                #and (pos_matches[1] and (pos_matches[0] or pos_matches[2]))

            #print "Sell Point: " + str(sell_point)
            #print "Buy Range:  " + str(min_long_buy_point) + ' - ' + str(max_long_buy_point)
            #print "Cur Price:  " + str(close)
            #print "buf Price:  " + str(sup_val + (res_val - sup_val)*(bufferPercent/100))

            if longStocks and long_buffer_zone and sell_point > close*(1.0 + minimumPercent/100) and long_pot_buy:
                if min_long_buy_point <= close <= max_long_buy_point: #and bought == False:

                    #print Helper.calculate_rsi(prices)
                    long_buffer_zone = False
                    #url = Helper.generate_a_graph(resLine, supLine, meanLine, prices, symbol + " long " + str(i), "testing" + str(i))

                    t = Trade(prices[-1].timestamp, 0.0, sell_point, close, 0.0, "long", 0.0, symbol, actual_type)
                    t.stop_loss_val = close - close*stop_loss_perc/100
                    t.prices = prices
                    #t.enter_url = url
                    t.res_line = resLine
                    t.sup_line = supLine
                    t.mean_line = meanLine
                    trades.append(t)
            elif shortStocks and short_buffer_zone and buy_point < close/(1.0 + minimumPercent/100) and short_pot_buy:
                if min_short_sell_point <= close <= max_short_sell_point: #and bought == False:

                    #print Helper.calculate_rsi(prices)
                    short_buffer_zone = False
                    #url = Helper.generate_a_graph(resLine, supLine, meanLine, prices, symbol + " long " + str(i), "testing" + str(i))

                    t = Trade(0, prices[-1].timestamp, buy_point, 0.0, close, "short", 0.0, symbol, actual_type)
                    t.stop_loss_val = close + close*stop_loss_perc/100
                    t.prices = prices
                    #t.enter_url = url
                    t.res_line = resLine
                    t.sup_line = supLine
                    t.mean_line = meanLine
                    trades.append(t)

        #check if within buffer zone
        if sup_val + (res_val-sup_val)*(bufferPercent/100) >= close:
            long_buffer_zone = True
        elif close < min_long_buy_point and long_buffer_zone:
            long_buffer_zone = True
        else:
            long_buffer_zone = False

        if res_val - (res_val-sup_val)*(bufferPercent/100) <= close:
            short_buffer_zone = True
        elif close > max_short_sell_point and short_buffer_zone:
            short_buffer_zone = True
        else:
            short_buffer_zone = False

        #print ("loop time: ", time.time() - start_time)

def analyze_sandp():
    stocks = open("sandp500stocklist.txt", "r")

    for stock in stocks:
        stock = stock[:-1]
        analyze_stock(stock, "data/sandp/" + stock + "-20050101 075000-60sec.csv")


if __name__ == "__main__":
    analyze_sandp()
    #analyze_stock("CSC", "data/CSC.csv")
    #Helper.analyze_db(db, 15000)
    #Helper.analyze_db_more_indepth(db, 15000, 0.5)
    #trades = db.read_trades_symbol('WMT')
    #for trade in trades:
    #    print trade.id
    #    print trade
    #db.remove_item(5109)