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
        self.systems = []

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


class ContainerOfSpaces(Space):
    """ A Space that contains other Spaces """

    """ In the Real World this will be one of three things:
    1) A Quadrant that contains four Subsectors
    2) A Sector that contains sixteen Subsectors
    3) A Domain that contains four Sectors
    
    I can also see a space larger than domain that contains sixteen
    Sectors.

    I want to plan to have a ContainerOfSpaces able to contain other
    ContainerOfSpaces rather than just bottom level Spaces like Space
    or Subsector. 

    base: All ContainerOfSpaces will contain a Square number of spaces,
    i.e. 2x2, 4x4. base is the number to be squared, that is, a 
    ContainerOfSpaces contains base*base subspaces.

    Origin: The coordinate of the space within a larger space. This gives
    context to the coordinates within the Space, which can go from origin+1
    to size.

    Subspace Size is the size of subspaces this space contains. The overall
    size of this space is (subspace_size[0] * base, subspace_size[1] * base)

    density will be a list containing either one entry, in which case this
    will be the density for all subspaces, or a list containing base*base
    entries, giving the densities for every subspace. If we're clever, for
    domains these can themselves be lists.

    subspace_names will either be empty, which will prompt the container
    to create generic versions, or a list. This is somewhat complicated by
    notions like Domains, which contains further subspaces. These will have
    to be more complex data structures, and that subclass will have to 
    deal with them. """

    subspace_labels = [
            "A", "B", "C", "D",
            "E", "F", "G", "H",
            "I", "J", "K", "L",
            "M", "N", "O", "P"
            ]

    def __init__(self, name, base, origin = (0, 0), subspace_size = (8, 10),
                 density = "Standard", subspace_names = []):
        self.name = name
        self.base = base
        self.origin = origin
        self.n_subspaces = base ** 2
        self.subspace_size = subspace_size
        self.size = (subspace_size[0] * base, subspace_size[1] * base)

        self.setup_densities(density)
        self.setup_subspace_names(subspace_names)

        self.create_subspaces()

    def setup_densities(self, density):
        """ Two cases:
        A single string: All subspaces will have this density.
        A list: A density for each subspace. """
        self.density = []    

        if type(density) == list:
            if len(density) == self.n_subspaces:
                for entry in density:
                    self.density.append(entry)
            else:
                raise ValueError(
                        "Improper format in densities for ContainerOfSpaces")
        else:
            """ And we presume if else, it's a string """
            for i in range(self.n_subspaces):
                self.density.append(density)

    def setup_subspace_names(self, subspace_names):
        if subspace_names:
            if len(subspace_names) != self.n_subspaces:
                raise ValueError(f"Only {len(subspace_names)} subspace" \
                        f"names given of {self.n_subspaces} required")
            self.subspace_names = list(subspace_names)
        else:
            self.subspace_names = []
            for i in range(self.n_subspaces):
                ss_name = self.name + " " + ContainerOfSpaces.subspace_labels[i]
                self.subspace_names.append(ss_name)

    def create_subspaces(self):
        self.subspaces = []
        for row in range(self.base):
            for column in range(self.base):
                i = (row * self.base) + column
                # Work origin out beforehand
                origin = (self.origin[0] + (row * self.subspace_size[0]), 
                     self.origin[1] + (column * self.subspace_size[1]))
                subspace = self.create_subspace(
                        name = self.subspace_names[i],
                        size = self.subspace_size,
                        origin = origin,
                        density = self.density[i]
                        )
                self.subspaces.append(subspace)

    def create_subspace(self, name, size, origin, density):
        return Space(name, size, origin, density)

    def generate(self):
        """ Generates each subspace in turn """
        for subspace in self.subspaces:
            subspace.generate()

    def __str__(self):
        ret = ""
        for subspace in self.subspaces:
            ret += subspace.__str__()
        return ret


class ContainerOfSubsectors(ContainerOfSpaces):
    """ A Space that will contain Subsectors """

    def __init__(Self, name, base, origin = (0, 0),
                 density = "Standard", subspace_names = []):
        super().__init__(name, base, origin, (8, 10),
                         density, subspace_names)

    def create_subspace(self, name, size, origin, density):
        """ We ignore size, all subsectors are 8x10 """
        return Subsector(name, origin, density)


class Quadrant(ContainerOfSubsectors):
    """ A Quadrant is 2x2 Subsectors """
    def __init__(self, name, origin = (0, 0),
                 density = "Standard", subspace_names = []):
        super().__init__(name, 2, origin, density, subspace_names)

    def __str__(self):
        ret = f"# Quadrant '{self.name}'\n"
        ret += super().__str__()
        return ret


class Sector(ContainerOfSubsectors):
    """ A Sector is 4x4 Subsectors """
    def __init__(self, name, origin = (0, 0),
                 density = "Standard", subspace_names = []):
        super().__init__(name, 4, origin, density, subspace_names)

    def __str__(self):
        ret = f"# Sector '{self.name}'\n"
        ret += super().__str__()
        return ret


class ContainerOfSectors(ContainerOfSpaces):
    """ A Space that will contain Sectors """
    """ Right now that means, a Domain i.e. 2x2 Sectors
    But we might extend this with a 4x4 sector space."""

    def __init__(self, name, base, origin = (0, 0),
                 density = "Standard", subspace_names = []):
        super().__init__(name, base, origin, (32, 40),
                         density, subspace_names)
    
    def setup_densities(self, density):
        """ Case 1: 'Standard' Single density for whole domain """
        """ case 2: ['Standard', 'Standard'] density for each sector """
        """ Case 3: [['Standard', 'Standard'], ['Standard', 'Standard']] """
        """ Density for each subsector. """

        if type(density) == str:
            """ Case 1 """
            """ Turn it into Case 2 and let it fall through """
            sector_densities = []
            for i in range(self.n_subspaces):
                sector_densities.append(density)
            density = sector_densities

        if type(density) != list:
            raise ValueError(f"Got wrong density type:{type(density)} in"\
                    " ContainerOfSectors Case 1")
        elif len(density) != self.n_subspaces:
            raise ValueError(f"Got wrong sector density count: {len(density)}"\
                    "in ContainerOfSectors Case 2-3")

        for index, sector_density in enumerate(density):
            if type(sector_density) == str:
                """ Case 2 """
                """ Turn it into Case 3 and let it fall through """
                subsector_densities = []
                for subsector in range(16):
                    subsector_densities.append(sector_density)
                density[index] = subsector_densities
            elif type(sector_density) != list:
                raise ValueError(f"Got wrong density type:{type(sector_density)}"\
                        f" in ContainerOfSubsectors Case 2 element {index}")
            elif len(sector_density) != 16:
                raise ValueError("Got wrong subsector density count:"\
                        f"{len(sector_density)} in ContainerOfSubsectors"\
                        f"Case 2 element {index}")

        """ Everything should be clear now """
        self.density = list(density)

    def setup_subspace_names(self, subspace_names):
        """ Containers of Subsectors have to have names for the
        contained sectors, and names for the sectors they themselves
        contain. Therefore their subsector_names will be a list of
        elements, one per Sector.
        That list will contain the sector name and may contain a list
        of subsector names, or it may not. If not, these will have to be
        generated.

        To be clear there are THREE possible states:
        1) An empty list where we must generate all subspace names.
        2) A list of sector names, where we must generate subsector names
        3) A list containing lists, each sublist having a sector name and a list
        of subsector names.
        """
        self.subspace_names = []

        if not subspace_names:
            """ Case 1 """
            """ We're just going to do sector names here """
            """ At the end of this, this will look like case #2 """
            """ So rather than an else, we'll fall through """
            """ and let that handle the rest. """
            for i in range(self.n_subspaces):
                ss_name = self.name + " " + ContainerOfSpaces.subspace_labels[i]
                subspace_names.append([ss_name])

        for ss_names in subspace_names:
            if len(ss_names) == 1:
                """ Case 2 """
                subsector_names = []
                # A few times here we use 16 for the number of subsectors
                # in a sector. And that's true, but it seems a little like
                # cheating.
                for i in range(16):
                    ss_name = ss_names[0] + \
                            " " + ContainerOfSpaces.subspace_labels[i]
                    subsector_names.append(ss_name)
                ss_names.append(subsector_names)
                self.subspace_names.append(ss_names)
            elif len(ss_names[1]) == 16:
                """ Case 3 """
                self.subspace_names.append(list(ss_names))
            else:
                """ Panic? """
                raise ValueError("Incorrectly formatted subspace names"\
                        " for ContainerOfSectors")

    def create_subspaces(self):
        """ Almost identical to the super() version """
        """ But here create_subspace takes an extra parameter """
        """ i.e. subspace names """
        self.subspaces = []
        for row in range(self.base):
            for column in range(self.base):
                i = (row * self.base) + column
                # Work origin out beforehand
                origin = (self.origin[0] + (row * self.subspace_size[0]), 
                     self.origin[1] + (column * self.subspace_size[1]))
                subspace = self.create_subspace(
                        name = self.subspace_names[i][0],
                        size = self.subspace_size,
                        origin = origin,
                        density = self.density[i],
                        subspace_names = self.subspace_names[i][1]
                        )
                self.subspaces.append(subspace)

    def create_subspace(self, name, size, origin, density, subspace_names):
        return Sector(name, origin, density, subspace_names)


class Domain(ContainerOfSectors):
    """ A Domain is 2x2 Sectors """
    def __init__(self, name, origin = (0, 0),
                 density = "Standard", subspace_names = []):
        super().__init__(name, 2, origin, density, subspace_names)

    def __str__(self):
        ret = f"# Domain '{self.name}'\n"
        ret += super().__str__()
        return ret


if __name__ == "__main__":
    s = Domain("Test", density="Rift")
    s.generate()
    print(s)







