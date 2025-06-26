""" Script for handling traveller Systems. 

That is: System coordinates, system name, and various extended features
such as bases, gas giants, planetoid belts. """

import dice
import uwp

class System:
    """ Base Class of System being that presented in Classic Traveller """

    def __init__(self, name, coordinates, uwp = None,
                 naval = False, scout = False, gas = False):
        self.name = name
        self.coordinates = coordinates
        self.uwp = uwp
        self.naval_base = naval
        self.scout_base = scout
        # CT only notes gas giant presence, not number
        if gas:
            self.gas_giants = 1
        else:
            self.gas_giants = 0
        # CT doesn't have notions of population multiplier
        # or planetoid belts. But we'll set them here anyway
        self.belts = 0
        self.population_multiplier = 1

    def generate_uwp(self):
        self.uwp = uwp.Uwp(uwp_string = None)

    def generate_bases(self):
        """ Note that this requires the system to have a valid UWP """
        if self.uwp.starport in ['A', 'B'] and dice.roll(2, 6) >= 8:
            self.naval_base = True
        else:
            self.naval_base = False

        scout_dm = 0
        if self.uwp.starport == 'C':
            scout_dm = -1
        elif self.uwp.starport == 'B':
            scout_dm = -2
        elif self.uwp.starport == 'A':
            scout_dm = -3

        if self.uwp.starport in ['A', 'B', 'C', 'D'] and \
            (dice.roll(2, 6) + scout_dm) >= 7:
            self.scout_base = True
        else:
            self.scout_base = False

    def generate_pbg(self):
        """ P = Population Multiplier
            B = Belts (i.e. Planetoid Belts)
            G = Gas Giants """

        # Population multiplier
        self.population_multiplier = dice.roll(1, 9)

        # Planetoid belts. Using MegaTraveller rules.
        if dice.roll(2, 6) >= 8:
            # MT has '13' be 3 belts, but gives no DMs. How do we get to 13?
            belt_quantity_table = [
                #   0  1  2  3  4  5  6  7  8  9  10 11 12 13
                    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3
                    ]
            self.belts = belt_quantity_table[dice.roll(2, 6)]
        else:
            self.belts = 0

        # Gas Giants. Again using MegaTraveller rules.
        if dice.roll(2, 6) >= 5:
            gas_giant_quantity_table = [
                #   0  1  2  3  4  5  6  7  8  9  10 11 12
                    0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5, 5
                    ]
            self.gas_giants = gas_giant_quantity_table[dice.roll(2, 6)]
        else:
            self.gas_giants = 0

    def generate(self):
        """ Generates all system details"""
        self.generate_uwp()
        self.generate_bases()
        self.generate_pbg()

    def get_base_code(self):
        if self.naval_base and self.scout_base:
            return 'B'
        if self.naval_base:
            return 'N'
        if self.scout_base:
            return 'S'
        return ' '

    def get_trade_codes_str(self):
        trade_codes = sorted(self.uwp.get_trade_codes())
        return " ".join(trade_codes)

    def get_pbg_str(self):
        """ Future proofed against subclasses that have these features """
        return "{}{}{}".format(
                self.population_multiplier,
                self.belts,
                self.gas_giants)

    def __str__(self):
        """ Should return a valid line for a .sec file """
        """ We're leaving travel zone and allegiance blank
        and skipping stellar data entirely. """
        return  f"{self.name:<20}" \
                f"{self.coordinates[0]:02d}{self.coordinates[1]:02d} " \
                f"{self.uwp}  " \
                f"{self.get_base_code()} " \
                f"{self.get_trade_codes_str():<20}" \
                "    " \
                f"{self.get_pbg_str()}" \
                "    "

if __name__ == "__main__":
    count = 0
    for x in range(1, 9):
        for y in range(1, 11):
            if dice.roll(1, 6) >= 4:
                count += 1
                s = System(name = f"{count}", coordinates = (x, y))
                s.generate()
                print(s)
