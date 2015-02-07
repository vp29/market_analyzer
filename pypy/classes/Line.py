__author__ = 'Erics'

class Line:
    intercept = 0.0
    slope = 0.0
    start = 0
    end = 0

    def __init__(self, intercept, slope, start, end):
        self.intercept = intercept
        self.slope = slope
        self.start = start
        self.end = end

    def get_values(self):
        y_values = []
        for i in range(self.start, self.end):
            y_values.append(self.intercept + self.slope*i)

        return y_values