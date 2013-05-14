#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import argparse
import logging
from collections import namedtuple
from board import NonogramBoard


def parse_args():
    logging.basicConfig(format='[ %(levelname)8s ] %(message)s', level=logging.WARNING)
    parser = argparse.ArgumentParser(description=u'''This program can solve Nonogram puzzles (see http://en.wikipedia.org/wiki/Nonogram). For this board:
    |  2 1 1 1
    |3 1 1 2 1
----+----------
 2 1|
   3|
 1 1|
   3|
   2|

An example call would be: ./solve.py -x 3 -x 2 1 -x 1 1 -x 1 2 -x 1 1 -y 2 1 -y 3 -y 1 1 -y 3 -y 2 -s 5x5

After solving, the result is:

    |  2 1 1 1
    |3 1 1 2 1
----+----------
 2 1|█ █ ░ █ ░
   3|█ █ █ ░ ░
 1 1|█ ░ ░ ░ █
   3|░ █ █ █ ░
   2|░ ░ ░ █ █

where:
'░' = Empty
'█' = Filled
' ' = Unknown''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', '--y-rules', nargs='+', type=int, action='append', required=True, help='The rules for the vertical axis. A single rule is a number of space separated numbers. Add multiple arguments to add more rules. Example: -y 1 2 3 -y 4 5 6')
    parser.add_argument('-x', '--x-rules', nargs='+', type=int, action='append', required=True, help='The rules for the horizontal axis. A single rule is a number of space separated numbers. Add multiple arguments to add more rules. Example: -x 1 2 3 -x 4 5 6')
    parser.add_argument('-s', '--size', required=True, help='The size of the board, defined like 10x15, where 10 is the number of rows and 15 is the number of colums.')
    args = parser.parse_args()
    Size = namedtuple('Size', 'y x')
    args.size = Size(*map(int, args.size.split('x')))
    return args


def generate_permutations(rules, row):
    #rules = [2,1]
    #row = [None, None, None, None, None]
    #return [[True, True, None, True, None], [True, True, None, None, True], [None, True, True, None, True]]
    logging.debug('rules: ' + str(rules))
    logging.debug('row: ' + str(row))
    if not rules:
        return [None] * len(row)
    first = [True] * rules[0]
    if len(rules) == 1:
        if rules[0] > len(row):
            return [row]
        else:
            return embed(first, False, len(row))
    else:
        result = []
        len_rest = sum(rules[1:]) + len(rules[1:]) - 1
        # Try each starting index for the pattern that matches the first rule
        for i in xrange(len(row)):
            logging.debug('iter: ' + str(i))
            # Generate patterns that match the first rule
            starting_patterns = [x + [False] for x in embed(first, False, i + len(first), i)]
            # If the patterns for the rest of the rules don't fit, break
            if len(row) - len(starting_patterns[0]) < len_rest:
                logging.debug('break')
                break
            # For each pattern for the first rule, calculate all possible
            # patterns for the other rules
            for pattern in starting_patterns:
                logging.debug('start: ' + str(pattern))
                for rest in generate_permutations(rules[1:], row[len(pattern):]):
                    logging.debug('rest: ' + str(rest))
                    result.append(pattern + rest)
        return result


def overlay(permutations, row):
    result = copy.deepcopy(row)
    # Remove all permutations that have cells that do not agree with a True or
    # False in the row
    new_permutations = []
    for permutation in permutations:
        if all(r is None or r is p for r, p in zip(row, permutation)):
            new_permutations.append(permutation)
    permutations = new_permutations
    # If all permutations agree on a True or a False for a given spot, pick
    # that over the None in row, if present
    for i, permutation in enumerate(zip(*permutations)):
        # The row already contains a True or a False, permutations are
        # irrelevant
        if row[i] is not None:
            continue
        # all are equal
        if permutation and permutation.count(permutation[0]) == len(permutation):
            result[i] = permutation[0]
        # TODO: if row already contains True's or False's, take these into
        # account.
    return result


def embed(item, filler, length, start=0):
    # Fill a list with sublists, where each sublist contains the elements in
    # item (which is itself a list), filled left and right with the filler
    # element. Create every permutation, starting from the given start point.
    result = []
    for i in xrange(start, length - len(item) + 1):
        new = [filler] * i + item + [filler] * (length - i - len(item))
        result.append(new)
    return result


def solve_row(rules, row):
    permutations = generate_permutations(rules, row)
    return overlay(permutations, row)


def transpose(board):
    board.grid = zip(*board.grid)
    board.x_rules, board.y_rules = board.y_rules, board.x_rules
    #board.x_rules = [x[::-1] for x in board.x_rules]
    #board.y_rules = [x[::-1] for x in board.y_rules]


def main():
    args = parse_args()
    board = NonogramBoard(args.y_rules, args.x_rules, args.size)
    if not board.validate():
        logging.error('Board is not valid!')
    else:
        logging.info('Board is valid, solving:')
    changed = True
    while changed:
        board.print_board()
        changed = False
        # Try all rows
        for i, row in enumerate(board.grid):
            row = list(row)
            new_row = solve_row(board.y_rules[i], row)
            logging.debug('Comparing {} with {}!'.format(row, new_row))
            if new_row != row:
                logging.debug('Replacing {} with {}!'.format(row, new_row))
                changed = True
                board.grid[i] = new_row
        board.print_board()
        transpose(board)
        # Try all columns by transposing the new grid
        board.print_board()
        for i, column in enumerate(board.grid):
            column = list(column)
            new_column = solve_row(board.y_rules[i], column)
            logging.debug('Comparing {} with {}!'.format(column, new_column))
            if new_column != column:
                logging.debug('Replacing {} with {}!'.format(column, new_column))
                changed = True
                board.grid[i] = new_column
        transpose(board)
    board.print_board()


if __name__ == '__main__':
    main()
