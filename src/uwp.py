""" Script for dealing with UWPs """

import dice

# So called "hex" values can actually be larger than 'F'
hex_table = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
    ]

def hex_to_int(hex_value):
    """ Converts a string 'hex' value into an int. """
    if hex_value in hex_table:
        return hex_table.index(hex_value)
    else:
        raise ValueError

def int_to_hex(value):
    """ Converts an int value into a string 'hex' value """
    if value < len(hex_table):
        return hex_table[value]
    else:
        raise ValueError

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
        if hexvalue not in hex_table:
            print(f"In uwp_string '{uwp_string}' Found character that is" \
                    f"not a hex value: '{hexvalue}'")
            return False

    return True

class World:
    """ Base Class of World being that presented in Classic Traveller """

    # All these private class _generate* methods are little helper functions
    # that implement the rules for world generation. They are here because
    # different rules sets (classic traveller, mongoose traveller, etc) use
    # slightly different rules for generating worlds, and so these are intended
    # to be overriden when necessary by child classes
    # Why class methods?
    # 1) They may be overriden by child classes
    # 2) Some of them may need to call other _generate* methods or other
    #    similar helpers like the _get_*_tech_dm methods
    @classmethod
    def _generate_starport(cls):
        table = ['A', 'A', 'A', 'B', 'B', 'C', 'C', 'D', 'E', 'E', 'X']
        return table[dice.roll(2,6) - 2]

    @classmethod
    def _generate_size(cls):
        return dice.roll(2, 6) - 2

    @classmethod
    def _generate_atmosphere(cls, size):
        if size == 0:
            return 0
        atmo = dice.roll(2, 6) - 7 + size
        if atmo < 0:
            return 0
        return atmo

    @classmethod
    def _generate_hydrosphere(cls, size, atmosphere):
        dm = 0
        if size == 0:
            return 0
        if atmosphere <= 1 or atmosphere >= 10:
            dm = -4
        hydro = dice.roll(2, 6) - 7 + size + dm
        if hydro < 0:
            return 0
        if hydro > 0xA:
            return 0xA
        return hydro

    @classmethod 
    def _generate_population(cls):
        return dice.roll(2, 6) - 2

    @classmethod
    def _generate_government(cls, population):
        pop = dice.roll(2, 6) - 7 + population
        if pop < 0:
            return 0
        return pop

    @classmethod
    def _generate_law_level(cls, government):
        law = dice.roll(2, 6) - 7 + government
        if law < 0:
            return 0
        return law

    # All these private class _get_*_tech_dm methods are used to help the
    # _generate_tech_level method. Again some may be overriden by
    # child classes as different editions may have slightly different
    # rules for the tech dms.

    @classmethod
    def _get_starport_tech_dm(cls, starport):
        """ Expects the starport to be a single character string. """
        dms = {'A': 6, 'B': 4, 'C': 2, 'X': -4}
        if starport in dms:
            return dms[starport]
        else:
            return 0

    @classmethod
    def _get_size_tech_dm(cls, size):
        if size <= 1:
            return 2
        elif size <= 4:
            return 1
        else:
            return 0

    @classmethod
    def _get_atmo_tech_dm(cls, atmo):
        if atmo <= 3:
            return 1
        elif atmo >= 0xA and atmo < 0xF:
            return 1
        return 0

    @classmethod
    def _get_hydro_tech_dm(cls, hydro):
        if hydro == 9:
            return 1
        elif hydro == 0xA:
            return 2
        return 0

    @classmethod
    def _get_pop_tech_dm(cls, pop):
        if pop == 0:
            return 0
        elif pop <= 5:
            return 1
        elif pop == 9:
            return 2
        elif pop == 0xA:
            return 4
        else:
            return 0

    @classmethod
    def _get_gov_tech_dm(cls, gov):
        if gov == 0:
            return 1
        elif gov == 5:
            return 1
        elif gov == 0xD:
            return -2
        else:
            return 0

    @classmethod
    def _generate_tech_level(cls, starport, size, atmosphere, \
                              hydrosphere, population, government):
        """ Calls all the tech_dm methods and generates a tech level """
        dm = cls._get_starport_tech_dm(starport) + \
             cls._get_size_tech_dm(size) + \
             cls._get_atmo_tech_dm(atmosphere) + \
             cls._get_hydro_tech_dm(hydrosphere) + \
             cls._get_pop_tech_dm(population) + \
             cls._get_gov_tech_dm(government)
        tech = dice.roll(1,6) + dm
        if tech < 0:
            tech = 0
        return tech

    def create_from_new_generation(self):
        """ Generates a new world using the various _generate methods """
        self.starport = self._generate_starport()
        self.size = self._generate_size()
        self.atmosphere = self._generate_atmosphere(self.size)
        self.hydrosphere = self._generate_hydrosphere(self.size, self.atmosphere)
        self.population = self._generate_population()
        self.government = self._generate_government(self.population)
        self.law_level = self._generate_law_level(self.government)
        self.tech_level = self._generate_tech_level(
                self.starport, self.size, self.atmosphere,
                self.hydrosphere, self.population, self.government)

    def create_from_uwp_string(self, uwp_string):
        """ Checks UWP validity and creates the world from these values """
        if not check_is_uwp_string_valid(uwp_string):
            raise ValueError

        self.starport = uwp_string[0]
        self.size = hex_to_int(uwp_string[1])
        self.atmosphere = hex_to_int(uwp_string[2])
        self.hydrosphere = hex_to_int(uwp_string[3])
        self.population = hex_to_int(uwp_string[4])
        self.government = hex_to_int(uwp_string[5])
        self.law_level = hex_to_int(uwp_string[6])
        self.tech_level = hex_to_int(uwp_string[8])

    def __init__(self, uwp_string = None):
        """ Creates the world from a given UWP, or generates a new one """
        if uwp_string:
            self.create_from_uwp_string(uwp_string)
        else:
            self.create_from_new_generation()

    def __str__(self):
        return self.starport + \
                int_to_hex(self.size) + \
                int_to_hex(self.atmosphere) + \
                int_to_hex(self.hydrosphere) + \
                int_to_hex(self.population) + \
                int_to_hex(self.government) + \
                int_to_hex(self.law_level) + "-" +\
                int_to_hex(self.tech_level)

    # All of these methods check for various trade codes
    def get_is_trade_agricultural(self):
        if self.atmosphere in [4, 5, 6, 7, 8, 9] and \
                self.hydrosphere in [4, 5, 6, 7, 8] and \
                self.population in [5, 6, 7]:
                    return True
        return False

    def get_is_trade_non_agricultural(self):
        if self.atmosphere <= 3 and \
                self.hydrosphere <= 3 and \
                self.population >= 6:
                    return True
        return False

    def get_is_trade_industrial(self):
        if self.atmosphere in [0, 1, 2, 4, 7, 9] and \
                self.population >= 9:
                    return True
        return False

    def get_is_trade_non_industrial(self):
        if self.population <= 6:
            return True
        return False

    def get_is_trade_rich(self):
        if self.atmosphere in [6, 8] and \
                self.population in [6, 7, 8] and \
                self.government in [4, 5, 6, 7, 8, 9]:
                    return True
        return False

    def get_is_trade_poor(self):
        if self.atmosphere in [2, 3, 4, 5] and \
                self.hydrosphere <= 3:
                    return True
        return False

    def get_is_trade_water(self):
        if self.hydrosphere == 0xA:
            return True
        return False

    def get_is_trade_desert(self):
        if self.hydrosphere == 0:
            return True
        return False

    def get_is_trade_vacuum(self):
        if self.atmosphere == 0:
            return True
        return False

    def get_is_trade_asteroid(self):
        if self.size == 0:
            return True
        return False

    def get_is_trade_ice_capped(self):
        if self.atmosphere in [0, 1] and \
                self.hydrosphere != 0:
                    return True
        return False

    def get_trade_codes(self):
        """ These checks presented in the same order as in CT """

        """ We calculate these every time rather than storing them
        because this is information *about* uwp, not something uwp
        should know itself. We return a list rather than a string because
        it is not uwp's job to print this, and we may need the list
        for other purposes.
        I can see a case to be made for pre calculating after generation
        or initialisation with a given UWP. """

        trade_codes = []
        if self.get_is_trade_agricultural():
            trade_codes.append("Ag")
        if self.get_is_trade_non_agricultural():
            trade_codes.append("Na")
        if self.get_is_trade_industrial():
            trade_codes.append("In")
        if self.get_is_trade_non_industrial():
            trade_codes.append("Ni")
        if self.get_is_trade_rich():
            trade_codes.append("Ri")
        if self.get_is_trade_poor():
            trade_codes.append("Po")
        if self.get_is_trade_water():
            trade_codes.append("Wa")
        if self.get_is_trade_desert():
            trade_codes.append("De")
        if self.get_is_trade_vacuum():
            trade_codes.append("Va")
        if self.get_is_trade_asteroid():
            trade_codes.append("As")
        if self.get_is_trade_ice_capped():
            trade_codes.append("Ic")
        
        return trade_codes

class MGT2eWorld(World):
    """ World Generation rules from Mongoose Traveller 2nd Edition """

    # We need to override the various helper functions for _generate_world
    # in the cases where the MT2e rules differ from Classic Traveller
    @classmethod
    def _generate_atmosphere(cls, size):
        atmo = dice.roll(2, 6) - 7 + size
        if atmo < 0:
            return 0
        return atmo

    @classmethod
    def _generate_hydrosphere(cls, size, atmosphere):
        """ I'm going to ignore the DMs for 'Temperature' as temperature
        is not part of the UWP and so there is no way to record it."""

        dm = 0
        if size == 0 or size == 1:
            return 0
        if atmosphere in [0, 1, 0xA, 0xB, 0xC]:
            dm = -4
        hydro = dice.roll(2, 6) - 7 + size + dm
        if hydro < 0:
            return 0
        if hydro > 0xA:
            return 0xA
        return hydro

    @classmethod
    def _generate_starport(cls, population):
        """ MT2e has DMs for starports based on population.

            Unlike the base class method, this one takes a parameter
            (i.e. population). This means we'll also have to override the
            create_from_new_generation method. """

        if population >= 8:
            dm = 1
        elif population >= 0xA:
            dm = 2
        elif population <= 4:
            dm = -1
        elif population <= 2:
            dm = -2
        else:
            dm = 0
        port_roll = dice.roll(2, 6) + dm
        if port_roll <= 2:
            return 'X'
        if port_roll <= 4:
            return 'E'
        if port_roll <= 6:
            return 'D'
        if port_roll <= 8:
            return 'C'
        if port_roll <= 10:
            return 'B'
        return 'A'

    @classmethod
    def _get_hydro_tech_dm(cls, hydro):
        if hydro == 0 or hydro == 9:
            return 1
        elif hydro == 0xA:
            return 2
        return 0


    @classmethod
    def _get_gov_tech_dm(cls, gov):
        if gov in [0, 5]:
            return 1
        elif gov == 7:
            return 2
        elif gov in [0xD, 0xE]:
            return -2
        else:
            return 0

    @classmethod
    def generate_world(cls):
        uwp = {}
        uwp["size"] = cls._generate_size()
        uwp["atmosphere"] = cls._generate_atmosphere(uwp["size"])
        uwp["hydrosphere"] = cls._generate_hydrosphere(
                uwp["size"], uwp["atmosphere"])
        uwp["population"] = cls._generate_population()
        uwp["starport"] = cls._generate_starport(uwp["population"])
        uwp["government"] = cls._generate_government(uwp["population"])
        uwp["law_level"] = cls._generate_law_level(uwp["government"])
        uwp["tech_level"] = cls._generate_tech_level(
                uwp["starport"], uwp["size"], uwp["atmosphere"],
                uwp["hydrosphere"], uwp["population"], uwp["government"])
        return uwp

    def create_from_new_generation(self):
        """ MT2e requires population for starport """
        self.size = self._generate_size()
        self.atmosphere = self._generate_atmosphere(self.size)
        self.hydrosphere = self._generate_hydrosphere(self.size, self.atmosphere)
        self.population = self._generate_population()
        self.starport = self._generate_starport(self.population)
        self.government = self._generate_government(self.population)
        self.law_level = self._generate_law_level(self.government)
        self.tech_level = self._generate_tech_level(
                self.starport, self.size, self.atmosphere,
                self.hydrosphere, self.population, self.government)

    # Updates to Trade Classifications
    def get_is_trade_asteroid(self):
        if self.size == 0 and \
                self.atmosphere == 0 and \
                self.hydrosphere == 0:
                    return True
        return False

    def get_is_trade_barren(self):
        if self.population == 0 and \
                self.government == 0 and \
                self.law_level == 0:
                    return True
        return False

    def get_is_trade_fluid_oceans(self):
        if self.atmosphere >= 10 and \
                self.hydrosphere >= 1:
                    return True
        return False

    def get_is_trade_garden(self):
        if self.size in [6, 7, 8] and \
                self.atmosphere in [5, 6, 8] and \
                self.hydrosphere in [5, 6, 7]:
                    return True
        return False

    def get_is_trade_high_population(self):
        if self.population >= 9:
            return True
        return False

    def get_is_trade_high_tech(self):
        if self.tech_level >= 0xC:
            return True
        return False

    def get_is_trade_low_population(self):
        if self.population <= 3:
            return True
        return False

    def get_is_trade_low_tech(self):
        if self.tech_level <= 5:
            return True
        return False

    def get_trade_codes(self):
        """ Checks presented in same order as in MGT2e """
        trade_codes = []
        if self.get_is_trade_agricultural():
            trade_codes.append("Ag")
        if self.get_is_trade_asteroid():
            trade_codes.append("As")
        if self.get_is_trade_barren():
            trade_codes.append("Ba")
        if self.get_is_trade_desert():
            trade_codes.append("De")
        if self.get_is_trade_fluid_oceans():
            trade_codes.append("Fl")
        if self.get_is_trade_garden():
            trade_codes.append("Ga")
        if self.get_is_trade_high_population():
            trade_codes.append("Hi")
        if self.get_is_trade_high_tech():
            trade_codes.append("Ht")
        if self.get_is_trade_ice_capped():
            trade_codes.append("Ic")
        if self.get_is_trade_industrial():
            trade_codes.append("In")
        if self.get_is_trade_low_population():
            trade_codes.append("Lo")
        if self.get_is_trade_low_tech():
            trade_codes.append("Lt")
        if self.get_is_trade_non_agricultural():
            trade_codes.append("Na")
        if self.get_is_trade_non_industrial():
            trade_codes.append("Ni")
        if self.get_is_trade_poor():
            trade_codes.append("Po")
        if self.get_is_trade_rich():
            trade_codes.append("Ri")
        if self.get_is_trade_vacuum():
            trade_codes.append("Va")
        if self.get_is_trade_water():
            trade_codes.append("Wa")

        return trade_codes


def Factory(uwp_string = None, edition = "MGT2e"):
    """ Gives appropriate version per the edition """
    uwp_per_edition = {
        "CT": World,
        "MGT2e": MGT2eWorld
    }
    return uwp_per_edition[edition](uwp_string)


if __name__ == "__main__":
    world = MGT2eWorld()

    print(world)
    print(world.get_trade_codes())

    world = MGT2eWorld(uwp_string = "A867977-8")

    print(world)
    print(world.get_trade_codes())


