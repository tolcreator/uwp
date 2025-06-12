""" Script for describing traveller Spaces.

Spaces include simple spaces such as Subsectors and more complex
spaces such as Sectors and Domains which contain other spaces. """

import dice
import uwp
import system

density_dm = {
            "Rift": -2,
            "Sparse": -1,
            "Standard": 0,
            "Dense": +1
        }

class Space:
    """ A space is a 2D hexagonal grid that contains systems """

    def __init__(self, name, size = (8,10), density = "Standard", edition="MGT2e"):
        self.name = name
        self.size = size
        self.density = density
        self.edition = edition

    def generate(self):
        """ Generates a new space with new systems """
        self.systems = []
        systems = 0
        for row in range(1, self.size[0]+1):
            for column in range(1, self.size[1]+1):
                if dice.roll(1, 6) + density_dm[self.density] >= 4:
                    systems += 1
                    s = system.Factory(
                            name = f"system_{systems}",
                            coordinates = (row, column),
                            edition = self.edition)
                    s.generate()
                    self.systems.append(s)


    def __str__(self):
        """ Prints out a .sec file contents """
        ret = ""
        for system in self.systems:
            ret += system.__str__() + "\n"
        return ret


if __name__ == "__main__":
    s = Space("Test Subsec", size = (32, 20), density = "Standard")
    s.generate()
    print(s)







