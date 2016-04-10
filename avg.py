#!/usr/bin/env python3

import math
import sys

if "__main__" == __name__:
    values = list(float(x) for x in sys.argv[1:])
    if not values:
        print("usage:", sys.argv[0], "value [values]")
    else:
        length = len(values)
        average = sum(values) / length

        sigma = math.sqrt(sum((x - average) ** 2 for x in values) / length)

        print("{:.2f} +- {:.2f} ({:.0%})".format(average, sigma, sigma / average))
