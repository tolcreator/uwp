""" Script for describing traveller Spaces.

Spaces include simple spaces such as Subsectors and more complex
spaces such as Sectors and Domains which contain other spaces. """

import dice
import json
import sys
import system
import uwp

density_dm = {
            "Rift": -2,
            "Sparse": -1,
            "Standard": 0,
            "Dense": +1
        }

class Space:
    """ A space is a 2D hexagonal grid that contains systems """

    def __init__(self, name, size = (8,10), origin = (0,0), density = "Standard",
                 maturity = "Standard", tech_cap = None):
        self.name = name
        self.size = size
        self.origin = origin
        self.density = density
        self.maturity = maturity
        self.tech_cap = tech_cap
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
                    s.generate(self.maturity, self.tech_cap)
                    self.systems.append(s)


    def __str__(self):
        """ Prints out a .sec file contents """
        ret = ""
        for system in self.systems:
            ret += system.__str__() + "\n"
        return ret


class Subsector(Space):
    """ A Subsector is 8x10 hexes """

    def __init__(self, name, origin = (0, 0), density = "Standard",
                 maturity = "Standard", tech_cap = None):
        super().__init__(name, (8, 10), origin, density, maturity, tech_cap)

    def __str__(self):
        ret = f"# Subsector '{self.name}' at '{self.origin[0]},{self.origin[1]}'\n"
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

    density is either a string containing the density for the whole space,
    or a list of densities for each subspace. These can themselves be lists
    if these subspaces themselves contain subspaces.

    maturity is like density, but for maturity

    tech_cap is like density, but with an Integer or None instead of a string

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
                 density = "Standard", maturity = "Standard", tech_cap = None,
                 subspace_names = []):
        self.name = name
        self.base = base
        self.origin = origin
        self.n_subspaces = base ** 2
        self.subspace_size = subspace_size
        self.size = (subspace_size[0] * base, subspace_size[1] * base)

        self.density = self.setup_subspace_fields(density)
        self.maturity = self.setup_subspace_fields(maturity)
        self.tech_cap = self.setup_subspace_fields(tech_cap)

        self.setup_subspace_names(subspace_names)

        self.create_subspaces()

    def setup_subspace_fields(self, field):
        """ Two cases:
        A single value: All subspaces will have this value
        A list: A value for each subspace. """
        fields = []

        if type(field) == list:
            if len(field) == self.n_subspaces:
                for entry in field:
                    fields.append(entry)
            else:
                raise ValueError(
                        "Improper format for subspace field for ContainerOfSpaces")
        else:
            """ And we presume if else, it's a single value """
            for i in range(self.n_subspaces):
                fields.append(field)
        return fields

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
                        density = self.density[i],
                        maturity = self.maturity[i],
                        tech_cap = self.tech_cap[i]
                        )
                self.subspaces.append(subspace)

    def create_subspace(self, name, size, origin, density, maturity, tech_cap):
        return Space(name, size, origin, density, maturity, tech_cap)

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

    def __init__(Self, name, base, origin = (0, 0), density = "Standard", 
                 maturity = "Standard", tech_cap = None, subspace_names = []):
        super().__init__(name, base, origin, (8, 10),
                         density, maturity, tech_cap, subspace_names)

    def create_subspace(self, name, size, origin, density, maturity, tech_cap):
        """ We ignore size, all subsectors are 8x10 """
        return Subsector(name, origin, density, maturity, tech_cap)


class Quadrant(ContainerOfSubsectors):
    """ A Quadrant is 2x2 Subsectors """
    def __init__(self, name, origin = (0, 0), density = "Standard", 
                 maturity = "Standard", tech_cap = None, subspace_names = []):
        super().__init__(name, 2, origin, density, 
                         maturity, tech_cap, subspace_names)

    def __str__(self):
        ret = f"# Quadrant '{self.name}' at '{self.origin[0]},{self.origin[1]}'\n"
        ret += super().__str__()
        return ret


class Sector(ContainerOfSubsectors):
    """ A Sector is 4x4 Subsectors """
    def __init__(self, name, origin = (0, 0), density = "Standard",
                 maturity = "Standard", tech_cap = None, subspace_names = []):

        print("Sector Density:\n", density)
        print("\nSector Subspace Names:\n", subspace_names)


        super().__init__(name, 4, origin, density, 
                         maturity, tech_cap, subspace_names)

    def __str__(self):
        ret = f"# Sector '{self.name}'\n"
        ret = f"# Sector '{self.name}' at '{self.origin[0]},{self.origin[1]}'\n"
        ret += super().__str__()
        return ret


class ContainerOfSectors(ContainerOfSpaces):
    """ A Space that will contain Sectors """
    """ Right now that means, a Domain i.e. 2x2 Sectors
    But we might extend this with a 4x4 sector space."""

    def __init__(self, name, base, origin = (0, 0), density = "Standard", 
                 maturity = "Standard", tech_cap = None, subspace_names = []):
        super().__init__(name, base, origin, (32, 40),
                         density, maturity, tech_cap, subspace_names)
    
    def setup_subspace_fields(self, field):
        """ Case 1: 'Standard' Single field for whole domain """
        """ case 2: ['Standard', 'Standard'] field for each sector """
        """ Case 3: [['Standard', 'Standard'], ['Standard', 'Standard']] """
        """ field for each subsector. """

        if type(field) != list:
            """ Case 1 """
            """ Turn it into Case 2 and let it fall through """
            sector_fields = []
            for i in range(self.n_subspaces):
                sector_fields.append(field)
            field = sector_fields


        if len(field) != self.n_subspaces:
            raise ValueError(f"Got wrong sector field count: {len(field)}"\
                    "in ContainerOfSectors Case 2-3")

        for index, sector_field in enumerate(field):
            if type(sector_field) != list:
                """ Case 2 """
                """ Turn it into Case 3 and let it fall through """
                subsector_fields = []
                for subsector in range(16):
                    subsector_fields.append(sector_field)
                sector_field = subsector_fields
                field[index] = sector_field

            if len(sector_field) != 16:
                raise ValueError("Got wrong subsector field count:"\
                        f" {len(sector_field)} in ContainerOfSubsectors"\
                        f" Case 2 element {index}")

        """ Everything should be clear now """
        return list(field)

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

        if not subspace_names:
            """ Case 1 """
            """ We're just going to do sector names here """
            """ At the end of this, this will look like case #2 """
            """ So rather than an else, we'll fall through """
            """ and let that handle the rest. """
            for i in range(self.n_subspaces):
                ss_name = self.name + " " + ContainerOfSpaces.subspace_labels[i]
                subspace_names.append(ss_name)

        for index, ss_names in enumerate(subspace_names):
            if type(ss_names) == str:
                """ Case 2. Turn this into case 3 and let it fall through """
                sector_names = []
                sector_names.append(ss_names)
                subsector_names = []
                for i in range(16):
                    subsector_name = ss_names + " " + \
                            ContainerOfSpaces.subspace_labels[i]
                    subsector_names.append(subsector_name)
                sector_names.append(subsector_names)
                subspace_names[index] = sector_names
            elif type(ss_names) == list:
                """ Case 3. But lets check it. """
                if len(ss_names) != 2:
                    raise ValueError("Improper format for sector names in"\
                            f"ContainerOfSectors: Got len {len(ss_names)}")
                if type(ss_names[1]) != list:
                    raise ValueError("Improper format for subsector names in"\
                            f"ContainerOfSectors: got type {type(ss_names[1])}")
                if len(ss_names[1]) != 16:
                    raise ValueError("Improper format for subsector names in"\
                            f"ContainerOfSectors: got len {len(ss_names[1])}")
            else:
                """ Panic? """
                raise ValueError("Improper format for sector names in"\
                        f"ContainerOfSectors: type {type(ss_names)}")

        """ Everything should now be as case 3 """
        self.subspace_names = list(subspace_names)

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
                        maturity = self.maturity[i],
                        tech_cap = self.tech_cap[i],
                        subspace_names = self.subspace_names[i][1]
                        )
                self.subspaces.append(subspace)

    def create_subspace(self, name, size, origin, 
                        density, maturity, tech_cap, subspace_names):
        return Sector(name, origin,
                      density, maturity, tech_cap, subspace_names)


class Domain(ContainerOfSectors):
    """ A Domain is 2x2 Sectors """
    def __init__(self, name, origin = (0, 0), density = "Standard", 
                 maturity = "Standard", tech_cap = None, subspace_names = []):

        print("Domain Density:\n", density)
        print("\nDomain Subspace Names:\n", subspace_names)
    

        super().__init__(name, 2, origin, density,
                         maturity, tech_cap, subspace_names)

    def __str__(self):
        ret = f"# Domain '{self.name}' at '{self.origin[0]},{self.origin[1]}'\n"
        ret += super().__str__()
        return ret


def create_subsector_from_dict(descriptor):
    print(descriptor)
    return None

def create_quadrant_from_dict(descriptor):
    print(descriptor)
    return None

def create_sector_from_dict(descriptor):
    print(descriptor)
    return None

def create_domain_from_dict(descriptor):
    print(descriptor)

    domain = Domain(
            name = descriptor["Name"],
            origin = tuple(descriptor["Origin"]),
            density = descriptor["Density"],
            maturity = descriptor["Maturity"],
            tech_cap = descriptor["Tech cap"],
            subspace_names = descriptor["Subspace names"]
            )
    return domain


def create_space_from_json(jdescriptor):
    descriptor = json.loads(jdescriptor)
    size = descriptor["Size"]
    space_creators = {
            "Subsector": create_subsector_from_dict,
            "Quadrant": create_quadrant_from_dict,
            "Sector": create_sector_from_dict,
            "Domain": create_domain_from_dict
            }
    if size in space_creators:
        return space_creators[size](descriptor)
    else:
        print(f"Don't know what to do with a space of size '{size}'")
        return None

if __name__ == "__main__":
    sample_domain = {
        "Size": "Domain",
        "Name": "Radio Club",
        "Origin": (0, 0),
        "Density": [    "Rift",
                        "Sparse",
                        "Standard",
                        [   "Rift", "Rift", "Sparse", "Sparse",
                            "Rift", "Sparse", "Standard", "Standard",
                            "Sparse", "Standard", "Standard", "Standard",
                            "Sparse", "Standard", "Standard", "Dense"
                        ]
                    ],
        "Maturity": [   "Backwater",
                        "Backwater",
                        "Standard",
                        [   "Backwater", "Backwater", "Backwater", "Backwater",
                            "Backwater", "Backwater", "Backwater", "Backwater",
                            "Backwater", "Standard", "Standard", "Standard",
                            "Cluster", "Standard", "Backwater", "Mature"
                        ]
                    ],
        "Tech cap": [   0xC,
                        0xD,
                        0xE,
                        [   0xA, 0xA, 0xA, 0xA,
                            0xA, 0xC, 0xC, 0xC,
                            0xC, 0xC, 0xC, 0xC,
                            0xF, 0xD, 0xD, 0xE
                         ]
                    ],
        "Subspace names": [ "Spring",
                            "Summer",
                            "Autumn",
                            [    "Winter", 
                                [   "Alpha", "Beta", "Gamma", "Delta",
                                    "Epsilon", "Zeta", "Eta", "Theta",
                                    "Iota", "Kappa", "Lambda", "Mu",
                                    "Nu", "Xi", "Omicron", "Pi"
                                ]
                            ]
                          ]
    }
    s = create_space_from_json(json.dumps(sample_domain))
    s.generate()
    print(s)
    
    
