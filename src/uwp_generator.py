""" Group functions for generating UWPs """

""" We are using Mongoose Traveller 2e rules with a few additions
1) We are using 'space opera' and 'hard science' flags from 1e
2) We may use custom rules for more or less developed regions like
   those in Traveller: The New Era. """

import dice
import ehex

def _generate_size():
    return dice.roll(2, 6) - 2

def _generate_atmosphere(size, space_opera):
    atmo = dice.roll(2, 6) + size - 7
    if atmo < 0:
        return 0

    if space_opera:
        if size <= 2:
            return 0
        if size in [3, 4]:
            if atmo <= 2:
                return 0
            elif atmo <= 5:
                return 1
            else:
                return 0xA            
    return atmo

def _generate_temperature(atmosphere):
    """ temperature is not part of the UWP but used as a modifier """
    if atmosphere in [2, 3]:
        dm = -2
    elif atmosphere in [4, 5, 0xE]:
        dm = -1
    elif atmosphere in [8, 9]:
        dm = 1
    elif atmosphere in [0xA, 0xD, 0xF]:
        dm = 2
    elif atmosphere in [0xB, 0xC]:
        dm = 6
    else:
        dm = 0

    temp_roll = dice.roll(2, 6) + dm
    if temp_roll <= 2:
        return "Frozen"
    if temp_roll <= 4:
        return "Cold"
    if temp_roll <= 9:
        return "Temperate"
    if temp_roll <= 11:
        return "Hot"
    return "Boiling"

def _generate_hydrosphere(size, atmosphere, temperature, space_opera):
    dm = 0

    if size == 0 or size == 1:
        return 0

    if atmosphere in [0, 1, 0xA, 0xB, 0xC]:
        dm += -4

    if atmosphere not in [0xD, 0xF]:
        if temperature == "Hot":
            dm += -2
        if temperature == "Boiling":
            dm += -6

    if space_opera:
        if size in [3,4] and atmosphere == 0xA:
            dm -= 6
        if atmosphere in [0, 1]:
            dm -= 6
        if atmosphere in [2, 3, 0xB, 0xC]:
            dm -= 4

    hydro = dice.roll(2, 6) - 7 + size + dm

    if hydro < 0:
        return 0
    if hydro > 0xA:
        return 0xA
    return hydro

def _generate_population(size, atmosphere, hard_science):
    dm = 0
    if hard_science:
        if size <= 2 or size >= 0xA:
            dm -= 1
        if atmosphere in [5, 6, 8]:
            dm += 1
        else:
            dm -= 1
    pop = dice.roll(2, 6) + dm
    if pop < 0:
        return 0
    if pop > 0xA:
        return 0xA
    return pop

def _generate_government(population):
    if population == 0:
        return 0

    gov = dice.roll(2, 6) - 7 + population
    if gov < 0:
        return 0
    return gov


def _generate_law_level(population, government):
    if population == 0:
        return 0

    law = dice.roll(2, 6) - 7 + government
    if law < 0:
        return 0
    return law

def _generate_starport(population, hard_science):

    # MGT2e already has modifiers for starport based on population,
    # if much more subtle than pop-7. This result ends up in huge
    # tech levels, as high pop and starport both contribute hugely
    # to tech. Just leaving it to MGT2e gives more regular results.
    hard_science = False

    if population == 0:
        return 'X'

    starport_table = [
        'X', 'X', 'X', 'E', 'E', 'D', 'D', 'C', 'C', 'B', 'B', 'A'
            ]
    dm = 0
    if hard_science:
        dm = population - 7
    else:
        if population <= 2:
            dm = -2
        elif population <= 4:
            dm = -1
        elif population >= 0xA:
            dm = 2
        elif population >= 8:
            dm = 1

    port_lookup = dice.roll(2, 6) + dm
    if port_lookup >= len(starport_table):
        return 'A'
    if port_lookup < 0:
        port_lookup = 0
    return starport_table[port_lookup]

def _get_starport_tech_dm(starport):
    if starport == 'X':
        return -4
    if starport == 'C':
        return 2
    if starport == 'B':
        return 4
    if starport == 'A':
        return 6
    return 0

def _get_size_tech_dm(size):
    if size <= 1:
        return 2
    if size <= 4:
        return 1
    return 0

def _get_atmosphere_tech_dm(atmosphere):
    if atmosphere <= 3 or atmosphere >= 0xA:
        return 1
    return 0

def _get_hydrosphere_tech_dm(hydrosphere):
    if hydrosphere in [0, 9]:
        return 1
    if hydrosphere == 0xA:
        return 2
    return 0

def _get_population_tech_dm(population):
    if population in [1, 2, 3, 4, 5, 8]:
        return 1
    if population == 9:
        return 2
    if population == 0xA:
        return 4
    return 0

def _get_government_tech_dm(government):
    if government in [0, 5]:
        return 1
    if government == 7:
        return 2
    if government in [0xD, 0xE]:
        return -2
    return 0

def _generate_tech_level(
        starport, size, atmosphere, 
        hydrosphere, population, government):

    if population == 0:
        return 0

    dm = 0
    dm += _get_starport_tech_dm(starport)
    dm += _get_size_tech_dm(size)
    dm += _get_atmosphere_tech_dm(atmosphere)
    dm += _get_hydrosphere_tech_dm(hydrosphere)
    dm += _get_population_tech_dm(population)
    dm += _get_government_tech_dm(government)

    tech = dice.roll(1, 6) + dm
    if tech < 0:
        return 0
    return tech

def generate_uwp(space_opera = True, hard_science = True):
    size = _generate_size()
    atmosphere = _generate_atmosphere(size, space_opera)
    temperature = _generate_temperature(atmosphere)
    hydrosphere = _generate_hydrosphere(size, atmosphere,
                                        temperature, space_opera)
    population = _generate_population(size, atmosphere, hard_science)
    government = _generate_government(population)
    law_level = _generate_law_level(population, government)
    starport = _generate_starport(population, hard_science)
    tech_level = _generate_tech_level(
            starport, size, atmosphere,
            hydrosphere, population, government)

    uwp = f"{starport}" \
          f"{ehex.int_to_hex(size)}" \
          f"{ehex.int_to_hex(atmosphere)}" \
          f"{ehex.int_to_hex(hydrosphere)}" \
          f"{ehex.int_to_hex(population)}" \
          f"{ehex.int_to_hex(government)}" \
          f"{ehex.int_to_hex(law_level)}-" \
          f"{ehex.int_to_hex(tech_level)}"

    return uwp


if __name__ == "__main__":
    for i in range(80):
        uwp = generate_uwp()
        print(uwp)













