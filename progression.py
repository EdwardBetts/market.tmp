#!/usr/bin/env python3

import sys

POINTS_IN_AVERAGE = 5

def values(number_of_points):
    values = [1] * POINTS_IN_AVERAGE
    point = 0
    while number_of_points:
        if point < len(values):
            yield values[point], 0
        else:
            average = sum(values) / len(values)
            value = 2 * average
            values.append(value)
            values.pop(0)

            yield value, average

        number_of_points -= 1
        point += 1

if "__main__" == __name__:
    points = int(sys.argv[1]) if 1 < len(sys.argv) else 10
    for x, (y, average) in enumerate(values(points)):
        print("{0:>2d}".format(x),
              "{0:4.1f}".format(y),
              "avg: {0:4.1f}".format(average))
