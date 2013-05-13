# -*- coding: utf-8 -*-


class NonogramBoard(object):
    """A board used in the Nonogram game"""

    def __init__(self, y_rules, x_rules, size):
        self.y_rules = y_rules
        self.x_rules = x_rules
        self.size = size
        self.grid = []
        for _ in xrange(self.size.y):
            row = [None] * self.size.x
            self.grid.append(row)

    def validate(self):
        # Validate size
        for rule in self.y_rules:
            if sum(rule) + len(rule) - 1 > self.size.y:
                return False
        for rule in self.x_rules:
            if sum(rule) + len(rule) - 1 > self.size.x:
                return False

        # Validate rules
        return True

    def print_board(self):
        result = u''
        # The rules on top
        max_y = max(map(len, self.y_rules))
        max_x = max(map(len, self.x_rules))
        padded_x_rules = [[' '] * (max_x - len(x)) + x for x in self.x_rules]
        padded_y_rules = [[' '] * (max_y - len(y)) + y for y in self.y_rules]
        for row in list(zip(*padded_x_rules)):
            result += u'  ' * max_y
            result += u'|'
            result += u' '.join(str(x) for x in row)
            result += u'\n'
        result += u'--' * max_x
        result += u'+'
        result += u'--' * len(padded_x_rules)
        result += u'\n'

        for i, row in enumerate(self.grid):
            try:
                rule = padded_y_rules[i]
            except IndexError:
                rule = []
            result += u' ' + u' '.join(str(x) for x in rule)
            result += u'|'
            for cell in row:
                if cell is True:
                    result += u'█ '
                elif cell is False:
                    result += u'░ '
                elif cell is None:
                    result += u'  '
            result += u'\n'
        print result
