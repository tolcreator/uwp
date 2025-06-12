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
        """ Using CT rules for UWP because we are a CT system """
        self.uwp = uwp.Factory(uwp_string = None, edition = "CT")

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
        """ Note that CT only has rules for gas giant presence

        P = Population Multiplier
        B = Belts (i.e. Planetoid Belts)
        G = Gas Giants """

        if dice.roll(2, 6) <= 9:
            self.gas_giants = 1
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


class MGT2eSystem(System):
    """ MGT2e lacks rules for things like PBG

    This subclass substitutes in the rules from Megatraveller for these """

    def generate_uwp(self):
        self.uwp = uwp.Factory(uwp_string = None, edition = "MGT2e")

    def generate_pbg(self):
        """ Uses MT rules for generating PBG """

        # Population Multiplier
        # By RAW MT uses d6s to emulate 1d10
        # We'll just use 1d10
        self.population_multiplier = dice.roll(1, 10) - 1
        # Another departure from RAW, we're going to sanitise
        # the population multiplier to ignore 0s unless the populaiton
        # itself is 0.
        if self.population_multiplier == 0 and self.uwp.population != 0:
            self.population_multiplier = 1

        # Planetoid Belts
        if dice.roll(2, 6) >= 8:
            # MT has '13' be 3 belts: But gives no DMs, so how do we get 13?
            belt_quantity_table = [
                    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3
                    ]
            self.belts = belt_quantity_table[dice.roll(2, 6)]
        else:
            self.belts = 0

        # Gas Giants
        if dice.roll(2, 6) >= 5:
            gas_giant_quantity_table = [
                    0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5, 5
                    ]
            self.gas_giants = gas_giant_quantity_table[dice.roll(2, 6)]
        else:
            self.gas_giants = 0



def Factory(name, coordinates, edition = "MGT2e"):
    """ Gives appropriate version per the edition """
    system_per_edition = {
        "CT": System,
        "MGT2e": MGT2eSystem
    }
    return system_per_edition[edition](name, coordinates)


if __name__ == "__main__":
    earth = uwp.Factory(uwp_string = "A867977-8")
    solar_system = System(name = "Earth", coordinates = (0,0), uwp = earth)
    print(solar_system)

    rando_system = System(name = "Rando", 
                          coordinates = (dice.roll(1,10), dice.roll(1,8)))
    rando_system.generate()
    print(rando_system)
