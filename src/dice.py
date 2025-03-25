""" Script for simulating dice

When used as a standalone script, it expects 0, 1, or 2 arguments.
0 arguments: roll 1d6
1 argument: roll one die of that size.
2 arguments: roll (1st argument) dice of size (2nd argument)
"""


import random
import sys

def roll(num_dice=1, sides=6):
    """ Simple function for rolling N dice of M sides """
    total = 0
    for die in range(num_dice):
        total += random.randint(1, sides)
    return total

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        result = roll(int(args[0]), int(args[1]))
    elif len(args) == 1:
        result = roll(sides = int(args[0]))
    else:
        result = roll()
    print(result)
