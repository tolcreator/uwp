""" Script for dealing with UWPs """

import dice
import ehex
import uwp_generator
import trade_codes

def check_is_uwp_string_valid(uwp_string):
    """ Checks if this is a well formed uwp_string with sane values

        A valid UWP is of the form S123456-7 where
        S indicates Starport and can be A,B,C,D,E or X
        1 through 7 are 'hex' values and must be on the hex table
        - separates tech level from the rest of the string and must
        be present. """

    if len(uwp_string) != 9:
        print(f"uwp_string '{uwp_string}' incorrect length:" \
                f"{len(uwp_string)}")
        return False

    if uwp_string[-2] != '-':
        print(f"uwp_string '{uwp_string}' second last character" \
                f"is not '-': '{uwp_string[-2]}'")
        return False

    if uwp_string[0] not in ['A', 'B', 'C', 'D', 'E', 'X']:
        print(f"uwp_string '{uwp_string}' invalid starport: {uwp_string[0]}")
        return False

    hexvalues = uwp_string[1:-2] + uwp_string[-1]

    for hexvalue in hexvalues:
        if not ehex.is_valid(hexvalue):
            print(f"In uwp_string '{uwp_string}' Found character that is" \
                    f" not a hex value: '{hexvalue}'")
            return False

    return True

class Uwp:

    def __init__(self, uwp_string = None):
        """ Creates the world from a given UWP, or generates a new one """
        if not uwp_string:
            uwp_string = uwp_generator.generate_uwp()

        if not check_is_uwp_string_valid(uwp_string):
            raise ValueError

        self.starport = uwp_string[0]
        self.size = ehex.hex_to_int(uwp_string[1])
        self.atmosphere = ehex.hex_to_int(uwp_string[2])
        self.hydrosphere = ehex.hex_to_int(uwp_string[3])
        self.population = ehex.hex_to_int(uwp_string[4])
        self.government = ehex.hex_to_int(uwp_string[5])
        self.law_level = ehex.hex_to_int(uwp_string[6])
        self.tech_level = ehex.hex_to_int(uwp_string[8])

        self.trade_codes = trade_codes.get_trade_codes(uwp_string)

    def __str__(self):
        return self.starport + \
                ehex.int_to_hex(self.size) + \
                ehex.int_to_hex(self.atmosphere) + \
                ehex.int_to_hex(self.hydrosphere) + \
                ehex.int_to_hex(self.population) + \
                ehex.int_to_hex(self.government) + \
                ehex.int_to_hex(self.law_level) + "-" +\
                ehex.int_to_hex(self.tech_level)

    def get_trade_codes(self):
        return self.trade_codes

if __name__ == "__main__":

    for i in range(80):
        w = Uwp()
        s = f"{w.__str__():<10}"
        for code in w.get_trade_codes():
            s += " " + code
        print(s)

