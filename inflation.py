#!/usr/bin/env python3

import sys

if "__main__" == __name__:
    # http://www.usinflationcalculator.com/inflation/current-inflation-rates/
    values = list(float(x) for x in sys.argv[1:]) if 1 < len(sys.argv) else [1.9, 3.3, 3.4, 2.5, 4.1, 0.1, 2.7, 1.5, 3.0, 1.7, 1.5]

    inflation = 1
    for x in values:
        inflation *= 1 + x / 100

    inflation -= 1
    inflation *= 100

    print("inflation calculated for", len(values), "years is",
          "{0:.1f} %".format(inflation))
    print("sum", "{0:.1f} %".format(sum(values)))
