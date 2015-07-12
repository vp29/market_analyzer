__author__ = 'Erics'


class Indicators:

    @staticmethod
    def stochastic(data):
        #%K = 100[(C - L14)/(H14 - L14)]
        #%D is moving average of K
        low = data[0].low
        high = data[0].high
        for d in data:
            if d.low < low:
                low = d.low
        for d in data:
            if d.high > high:
                high = d.high

        K = 100*(data[-1].close-low)/(high-low)

        return K

    @staticmethod
    def average_true_range(data, prev_atr):

        tr = 0
        if prev_atr == None:
            for i, d in enumerate(data[1:]):
                low = d.low
                high = d.high
                prev_close = data[i-1].close
                tr += Indicators.true_range(high, low, prev_close)
        else:
            tr = prev_atr + (len(data)-1)*Indicators.true_range(data[-1].high, data[-1].low, data[-2].close)

        return tr/len(data)

    @staticmethod
    def candle_type(data):
        #assuming 2 most recent data points are passed in
        type = ""

        low = []
        bottom = []
        top = []
        high = []

        for d in data:
            low.append(d.low)
            bottom.append(d.close if d.close < d.open_ else d.open_)
            top.append(d.open_ if d.close < d.open_ else d.close)
            high.append(d.high)

        if(abs(bottom[-1] - top[-1])*2 < (bottom[-1]-low[-1]) and
           abs(bottom[-1]-top[-1])*.5 > (high[-1]-top[-1]) and
           abs(bottom[-1]-top[-1]) > .1*(high[-1]-low[-1]) and
           (data[-1].close > data[-1].open_)):
            type = "bullish hammer"
        elif(abs(bottom[-1] - top[-1])*2 < (high[-1] - top[-1]) and
           abs(bottom[-1]-top[-1])*.5 > (bottom[-1]-low[-1]) and
           abs(bottom[-1]-top[-1]) > .1*(high[-1]-low[-1]) and
           (data[-1].open_ > data[-1].close)):
            type = "bearish gravestone"
        elif((data[-2].close < data[-2].open_) and
            abs(bottom[-2]-top[-2]) > .75*(high[-2]-low[-2])):
            if(high[-1] <= low[-2] and
              abs(bottom[-1]-top[-1]) < .1*(high[-1]-low[-1]) and
              bottom[-1] > low[-1] + .5*(high[-1] - low[-1])):
                type = "bullish doji"
            elif((data[-1].close > data[-1].open_) and
              abs(bottom[-1]-top[-1]) > .75*(high[-1]-low[-1])):
                type = "bullish piercing"
        elif((data[-2].close > data[-2].open_) and
            abs(bottom[-2]-top[-2]) > .75*(high[-2]-low[-2])):
            if(high[-2] <= low[-1] and
              abs(bottom[-1]-top[-1]) < .1*(high[-1]-low[-1]) and
              bottom[-1] < low[-1] + .5*(high[-1] - low[-1])):
                type = "bearish doji"
            elif((data[-1].close < data[-1].open_) and
              abs(bottom[-1]-top[-1]) > .75*(high[-1]-low[-1])):
                type = "bearish piercing"

        return type

    @staticmethod
    def true_range(high, low, prev_close):
        val1 = high-low
        val2 = abs(high-prev_close)
        val3 = abs(low-prev_close)

        if val1 >= val2 and val1 >= val3:
            return val1
        elif val2 >= val1 and val2 >= val3:
            return val2
        elif val3 >= val1 and val3 >= val2:
            return val3

    @staticmethod
    def simple_moving_average(values):
        sum = 0

        for value in values:
            sum += value

        return sum / len(values)

