""" Script for dealing with UWPs """

import dice

# So called "hex" values can actually be larger than 'F'
hex_table = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
    ]

class Uwp:
    """ Base Class of UWP being that presented in Classic Traveller """

    def __init__(self, name = None, uwp_string = None):
        pass   

class WorldGenerator:
    """ A container for methods that generate UWP data

    Why a class and not a collection of functions? Because the intention
    is to present the rules from Classic Traveller here, and then create
    subclasses that can use the rules from other editions. """

    def __init__(self):
        pass
    
    def generate_starport(self):
        table = ['A', 'A', 'A', 'B', 'B', 'C', 'C', 'D', 'E', 'E', 'X']
        return table[dice.roll(2,6) - 1]

    def generate_size(self):
        """ Generates new world size """
        return dice.roll(2, 6) - 2

    def generate_atmosphere(self, size):
        """ Generates new world atmosphere given size """
        if size == 0:
            return 0
        atmo = dice.roll(2, 6) - 7 + size
        if atmo < 0:
            return 0
        return atmo

    def generate_hydrosphere(self, size, atmosphere):
        """ Generates new world hydrosphere given size and atmosphere

        A hydrosphere cannot be greater than 'A'."""
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

    def generate_population(self):
        """ Generates new world population """
        return dice.roll(2, 6) - 2

    def generate_government(self, population):
        """ Generates new world government given population """
        pop = dice.roll(2, 6) - 7 + population
        if pop < 0:
            return 0
        return pop

    def generate_law_level(self, government):
        """ Generates new world law level given government """
        law = dice.roll(2, 6) - 7 + government
        if law < 0:
            return 0
        return law

    def get_starport_tech_dm(self, starport):
        """ Gets the tech dice modifier for a given starport.

        Expects the starport to be a single character string. """
        
        dms = {'A': 6, 'B': 4, 'C': 2, 'X': -4}
        if starport in dms:
            return dms[starport]
        else:
            return 0

    def get_size_tech_dm(self, size):
        """ Gets the tech dice modifier for a given size.

        Expects the size to be an int. """
        if size <= 1:
            return 2
        elif size <= 4:
            return 1
        else:
            return 0

    def get_atmo_tech_dm(self, atmo):
        """ Gets the tech dice modifier for a given atmosphere.

        Expects the atmosphere to be an int. """
        if atmo <= 3:
            return 1
        elif atmo >= 0xA and atmo < 0xF:
            return 1
        return 0

    def get_hydro_tech_dm(self, hydro):
        """ Gets the tech dice modifier for a given hydrosphere.

        Expects the hydrosphere to be an int. """
        if hydro == 9:
            return 1
        elif hydro == 0xA:
            return 2
        return 0

    def get_pop_tech_dm(self, pop):
        """ Gets the tech dice modifier for a given population.

        Expects the population to be an int. """
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

    def get_gov_tech_dm(self, gov):
        """ Gets the tech dice modifier for a given government.

        Expects the government to be an int. """
        if gov == 0:
            return 1
        elif gov == 5:
            return 1
        elif gov == 0xD:
            return -2
        else:
            return 0

    def generate_tech_level(self, starport, size, atmosphere, \
                            hydrosphere, population, government):
        """ Calls all the tech_dm methods and generates a tech level """
        dm = self.get_starport_tech_dm(starport) + \
                self.get_size_tech_dm(size) + \
                self.get_atmo_tech_dm(atmosphere) + \
                self.get_hydro_tech_dm(hydrosphere) + \
                self.get_pop_tech_dm(population) + \
                self.get_gov_tech_dm(government)
        tech = dice.roll(1,6) + dm
        if tech < 0:
            tech = 0
        return tech

    def generate_world(self):
        """ Calls all the generate methods and generates a UWP """
        world = {}
        world["starport"] = self.generate_starport()
        world["size"] = self.generate_size()
        world["atmosphere"] = self.generate_atmosphere(world["size"])
        world["hydrosphere"] = self.generate_hydrosphere(world["size"],
                                                         world["atmosphere"])
        world["population"] = self.generate_population()
        world["government"] = self.generate_government(world["population"])
        world["law_level"] = self.generate_law_level(world["government"])
        world["tech_level"] = self.generate_tech_level(world["starport"],
                                                       world["size"],
                                                       world["atmosphere"],
                                                       world["hydrosphere"],
                                                       world["population"],
                                                       world["government"])
        return world

if __name__ == "__main__":
    wg = WorldGenerator()
    world = wg.generate_world()
    # This is a test. Eventually this will be the uwp class __str__ method
    for key, value in world.items():
        if key == "tech_level":
            print("-", end="")
        if key == "starport":
            print(value, end="")
        else:
            print(hex_table[value], end="")
                




    
        
        
    
        
