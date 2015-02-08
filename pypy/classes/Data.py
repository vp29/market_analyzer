__author__ = 'Erics'

class Data:
    open_ = 0.0
    high = 0.0
    low = 0.0
    close = 0.0
    volume = 0.0
    timestamp = 0

    index = 0

    def __init__(self, open_, high, low, close, volume, timestamp, index=0):
        self.open_ = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.timestamp = timestamp
        self.index = index