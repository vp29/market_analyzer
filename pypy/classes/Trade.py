__author__ = 'Erics'

class Trade:
    buy_time = 0
    sell_time = 0
    exit_cutoff = 0.0 #can be for short or long
    buy_price = 0.0
    sell_price = 0.0
    investment = 0.0
    symbol = ""
    actual_type = ""
    long_short = ""
    res_line = None
    sup_line = None
    mean_line = None
    enter_url = ""
    exit_url = ""
    id = ""
    enter_time = 0

    def __init__(self, buy_time, sell_time, exit_cutoff, buy_price, sell_price, long_short, investment=0.0, symbol="",actual_type="", id=0):
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.exit_cutoff = exit_cutoff
        self.sell_price = sell_price
        self.buy_price = buy_price
        self.long_short = long_short
        self.investment = investment
        self.symbol = symbol
        self.actual_type = actual_type
        self.id = id

    def __repr__(self):
        return "Symbol:     " + self.symbol + "\n" + \
                "Sale Type:  " + self.long_short + "\n" +\
                "Bought at:  " + str(self.buy_price) + "\n" + \
                "Sell at:    " + str(self.sell_price) + "\n" + \
                "Trend:      " + self.actual_type + "\n" + \
                "Trade time: " + str(abs(self.buy_time - self.sell_time)) + "\n"