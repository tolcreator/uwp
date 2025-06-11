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
        self.gas_giant = gas

    def generate(self):
        """ Generates all system details"""

        self.uwp = uwp.Factory(uwp_string = None, edition = "CT")

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

        if dice.roll(2, 6) <= 9:
            self.gas_giant = True
        else:
            self.gas_giant = False

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
        """ Best approximation using CT rules """
        if self.gas_giant:
            return "100"
        else:
            return "101"

    def __str__(self):
        """ Should return a valid line for a .sec file """
        """ We're leaving travel zone and allegiance blank
        and skipping stellar data entirely. """
        return  f"{self.name:<20}" \
                f"{self.coordinates[0]:02d}{self.coordinates[1]:02d} " \
                f"{self.uwp}  " \
                f"{self.get_base_code()} " \
                f"{self.get_trade_codes_str():<15}" \
                "    " \
                f"{self.get_pbg_str()}" \
                "    "


class MGT2eSystem(System):
    pass


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
