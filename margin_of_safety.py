#!/usr/bin/env python3

import math
import sys

import yaml

import tty

class Test():
    THRESHOLDS = {
            'public-utility': 1.75,
            'railroad': 2,
            'industrial': 3
            }

    def __init__(self, business_type='industrial', highlight=False):
        self.value = 0
        self.error = 0
        self.delta = 0
        self.delta_error = 0

        if not business_type:
            business_type = 'industrial'
        elif business_type not in self.THRESHOLDS:
            raise RuntimeError("Unsupported Enterprise type")

        self.business_type = business_type
        self.highlight = highlight

    def run(self, x, y):
        ''' 
                x err: sqrt(x)
                y err: sqrt(y)
              xy corr: 0
                value: x / (x - y)
                  err: sqrt(xy * (x + y) / (x - y)^4)
        '''

        try:
            self.value = x / (x - y)
            self.error = (math.sqrt(x * y * (x + y) / ((x - y) ** 4))
                          if x > 0 and y > 0 else 0)

            threshold = self.THRESHOLDS[self.business_type]
            self.delta = self.value - threshold
            self.delta_error = 100 * math.fabs(self.delta) / threshold

        except ZeroDivisionError:
            self.value = 0
            self.error = 0
            self.delta = 0
            self.delta_error = 0

    def __str__(self):
        format_string = ''
        color = None
        if self.highlight:
            format_string += '> '
            if self.delta < 0:
                color = tty.boldred
            else:
                color = tty.boldgreen
        else:
            if self.value < 0 or self.delta > 0:
                color = tty.green
            else:
                color = tty.red

        format_string += (color + '{0:.2f}' + tty.reset +
                         ' +/- {1:.2f} (delta: {2:.2f} | {3:.1f}%)')

        return format_string.format(self.value, self.error,
                                    self.delta, self.delta_error)

class FixedChargesTest(Test):
    def __init__(self, gross_income, net_income,
                 business_type=None, highlight=False):
        Test.__init__(self, business_type, highlight)

        self.gross_income = gross_income
        self.net_income = net_income

    def run(self):
        Test.run(self, self.gross_income, self.net_income)

    def __str__(self):
        return 'Fixed Charges earned: ' + Test.__str__(self)

class NetDeductionsTest(Test):
    def __init__(self, operating_income, net_income,
                 business_type=None, highlight=False):
        Test.__init__(self, business_type, highlight)

        self.operating_income = operating_income
        self.net_income = net_income

    def run(self):
        Test.run(self, self.operating_income, self.net_income)

    def __str__(self):
        return 'Net Deductions earned: ' + Test.__str__(self)

class InterestCoverateTest():
    def __init__(self, business_type, income):
        ''' The income should be a dictionary with keys:

            operating       operating income
            gross           gross income
            net             net income
        '''

        highlight_net_deductions = income['operating'] > income['gross']
        self.net_deductions_test = NetDeductionsTest(
                income['operating'], income['net'], business_type,
                highlight=highlight_net_deductions)

        self.fixed_charges_test = FixedChargesTest(
                income['gross'], income['net'], business_type,
                highlight=not highlight_net_deductions)

        self.value = 0
        self.error = 0

    def run(self):
        self.net_deductions_test.run()
        self.fixed_charges_test.run()

    def __str__(self):
        return str(self.net_deductions_test) + '\n' + str(self.fixed_charges_test)

def ioget(input_type):
    value = None
    if 'type' == input_type:
        BUSINESS_TYPES = list(Test.THRESHOLDS.keys())
        while True:
            try:
                print('select business type:')
                print(*['{0}: {1}'.format(k,v)
                        for k, v in enumerate(BUSINESS_TYPES)],
                      sep='\n')
                value = BUSINESS_TYPES[int(input('> '))]
                break
            except ValueError:
                print('please, enter an',
                      tty.makebold('integer'), 'value',
                      len(BUSINESS_TYPES), file=sys.stderr)
            except IndexError:
                print('please, enter an integer value up to',
                      tty.makebold(str(len(BUSINESS_TYPES))),
                      file=sys.stderr)

    elif 'name' == input_type:
        value = input('business name: ')

    elif input_type in ['operating', 'gross', 'net']:
        prompt = 'input {0} income: '.format(input_type.capitalize())
        while True:
            try:
                value = int(input(prompt))
                break
            except ValueError:
                print('please, enter interger value', file=sys.stderr)
    else:
        raise RuntimeError("unsupported input type")

    return value

def print_business_info(business):
    print('business:', tty.makebold(business['name']),
          'category:', tty.makebold(business['type']),
          'with income')

    income = business['income']
    income_names = ['operating', 'gross', 'net']
    align = 2 + max(len(name) for name in income_names)
    for name in ['operating', 'gross', 'net']:
        print("{name:>{align}}:".format(name=name, align=align),
              income[name])

class InputData():
    ''' Each business is categorized by:

        category
        name
        income:
            - operating
            - gross
            - net

    '''

    def __init__(self):
        self.data = []

    def __iter__(self):
        return iter(self.data)

    def load(self, filenames):
        for filename in filenames:
            with open(filename, 'r') as input_:
                data = yaml.load(input_)
                if 'thresholds' in data:
                    Test.THRESHOLDS = {
                            k: float(v)
                            for k, v in data['thresholds'].items()
                            }

                if 'businesses' in data:
                    data = data['businesses']

                for business in data:
                    self.data.append(business)

        if not self.data:
            self.data.append({'income':{}})

        self._validate()

    def _validate(self):
        for business in self.data:
            print('validating', business)
            for key in ['name', 'type']:
                if key not in business:
                    business[key] = ioget(key)

            income = business['income']
            for key in ['operating', 'gross', 'net']:
                if key not in income:
                    income[key] = ioget(key)

        print('-' * 15)

    def __str__(self):
        return str(self.data)

if "__main__" == __name__:
    data = InputData()
    data.load(sys.argv[1:])

    print('Business types and thresholds')
    max_align = 2 + max(len(name) for name in Test.THRESHOLDS.keys())
    for business_type, threshold in sorted(Test.THRESHOLDS.items(),
                                           key=lambda x: x[1]):
        print('{0:>{align}}:'.format(business_type, align=max_align),
              threshold)

    print('-' * 15)


    for business in data:
        print_business_info(business)

        interest_coverage_test = InterestCoverateTest(business['type'],
                                                      business['income'])
        interest_coverage_test.run()
        print(interest_coverage_test)
        print('-' * 15)
