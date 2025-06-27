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

    def __init__(self, name, size = (8,10), origin = (0,0), density = "Standard"):
        self.name = name
        self.size = size
        self.origin = origin
        self.density = density

    def generate(self):
        """ Generates a new space with new systems """
        self.systems = []
        systems = 0
        for row in range(1, self.size[0]+1):
            for column in range(1, self.size[1]+1):
                if dice.roll(1, 6) + density_dm[self.density] >= 4:
                    systems += 1
                    s = system.System(
                            name = f"{self.name} {systems}",
                            coordinates = (row + self.origin[0], 
                                           column + self.origin[1]))
                    s.generate()
                    self.systems.append(s)


    def __str__(self):
        """ Prints out a .sec file contents """
        ret = ""
        for system in self.systems:
            ret += system.__str__() + "\n"
        return ret

class Subsector(Space):
    """ A Subsector is 8x10 hexes """

    def __init__(self, name, origin = (0, 0), density = "Standard"):
        super().__init__(name, (8, 10), origin, density)

    def __str__(self):
        ret = f"# Subsector '{self.name}'\n"
        ret += super().__str__()
        return ret

class ContainerOfSubsectors(Space):
    """ A Space that contains Subsectors """

    """ Subsectors will always be laid out in a square grid
    i.e. 2x2, 4x4, never e.g. 2x4
    therefore "base" indicates the size of the space, and it will contain
    base rows and base columns of subsectors, or base*base subsectors.

    Density is a list. If this contains a single element, this will be the
    density for the whole of the space. If it contains <base^2> elements,
    then each element gives the density for that subsector. Any other number
    of elements is an error.

    Subsector names is a list. It can be empty, in which case generic names
    based on the overall space name will be generated. If it contains
    <base^2> elements, then each one is the name of a subsector. Any other
    number of elements is an error."""
    
    def __init__(self, name, base, origin = (0, 0), 
                 density = ["Standard"], subsector_names = []):
        self.name = name
        self.origin = origin
        self.n_subsectors = base ** 2
        self.size = (8 * base, 10 * base)
        
        # Densities
        self.density = []    
        if len(density) != 1 and len(density) != self.n_subsectors:
            raise ValueError(f"Got {len(density)} densities," \
                    f"expected 1 or {self.n_subsectors}")
        for i in range(self.n_subsectors):
            if(len(density)) == 1:
                self.density.append(density[0])
            else:
                self.density.append(density[i])        

        # Subsector names
        # In the real world there will only be quadrants (base 2)
        # and sectors (base 4)
        subsector_identifiers = [
                "A", "B", "C", "D",
                "E", "F", "G", "H",
                "I", "J", "K", "L",
                "M", "N", "O", "P"
                ]
        if subsector_names:
            if len(subsector_names != self.n_subsectors):
                raise ValueError(f"Only {len(subsector_names)} subsector" \
                        "names given of {self.n_subsectors} required")
            self.subsector_names = list(subsector_names)
        else:
            self.subsector_names = []
            for i in range(self.n_subsectors):
                ss_name = name + " " + subsector_identifiers[i]
                self.subsector_names.append(ss_name)

        self.subsectors = []
        for row in range(base):
            for column in range(base):
                i = (row*base) + column
                # Work origin out beforehand
                o = (self.origin[0] + (row*8), self.origin[1] + (column*10))
                subsector = Subsector(
                        self.subsector_names[i],
                        origin = o,
                        density = self.density[i])
                self.subsectors.append(subsector)

    def generate(self):
        """ Generates each subsector in turn """
        for subsector in self.subsectors:
            subsector.generate()

    def __str__(self):
        ret = ""
        for subsector in self.subsectors:
            ret += subsector.__str__()
        return ret

class Quadrant(ContainerOfSubsectors):
    """ A Quadrant is 2x2 Subsectors """
    def __init__(self, name, origin = (0, 0),
                 density = ["Standard"], subsector_names = []):
        super().__init__(name, 2, origin, density, subsector_names)

    def __str__(self):
        ret = f"# Quadrant '{self.name}'\n"
        ret += super().__str__()
        return ret

class Sector(ContainerOfSubsectors):
    """ A Sector is 4x4 Subsectors """
    def __init__(self, name, origin = (0, 0),
                 density = ["Standard"], subsector_names = []):
        super().__init__(name, 4, origin, density, subsector_names)

    def __str__(self):
        ret = f"# Sector '{self.name}'\n"
        ret += super().__str__()
        return ret


if __name__ == "__main__":
    s = Sector("Test")
    s.generate()
    print(s)







