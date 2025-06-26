""" Gets trade codes from a given UWP string """

import ehex

""" We're going to use these as indexes into the UWP string. """
STARPORT = 0
SIZE = 1
ATMO = 2
HYDRO = 3
POP = 4
GOV = 5
LAW = 6
TECH = 8

def _get_is_agricultural(uwp):
    if uwp[ATMO] in ['4', '5', '6', '7', '8', '9'] and \
            uwp[HYDRO] in ['4', '5', '6', '7', '8'] and \
            uwp[POP] in ['5', '6', '7']:
                return True
    return False

def _get_is_asteroid(uwp):
    if uwp[SIZE] == '0' and \
            uwp[ATMO] == '0' and \
            uwp[HYDRO] == '0':
                return True
    return False

def _get_is_barren(uwp):
    if uwp[POP] == '0' and \
            uwp[GOV] == '0' and \
            uwp[LAW] == '0':
                return True
    return False

def _get_is_desert(uwp):
    if uwp[ATMO] not in ['0', '1'] and \
            uwp[HYDRO] == '0':
                return True
    return False

def _get_is_fluid_oceans(uwp):
    if uwp[ATMO] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] and \
            uwp[HYDRO] != '0':
                return True
    return False

def _get_is_garden(uwp):
    if uwp[SIZE] in ['6', '7', '8'] and \
            uwp[ATMO] in ['5', '6', '8'] and \
            uwp[HYDRO] in ['5', '6', '7']:
                return True
    return False

def _get_is_high_population(uwp):
    if ehex.greater_than_or_equal_to(uwp[POP], '9'):
        return True
    return False

def _get_is_high_tech(uwp):
    if ehex.greater_than_or_equal_to(uwp[TECH], 'C'):
        return True
    return False

def _get_is_ice_capped(uwp):
    if uwp[ATMO] in ['0', '1'] and \
            uwp[HYDRO] != '0':
                return True
    return False

def _get_is_industrial(uwp):
    if _get_is_high_population(uwp) and \
            uwp[ATMO] in ['0', '1', '2', '4', '7', '9']:
                return True
    return False

def _get_is_low_population(uwp):
    if uwp[POP] in ['0', '1', '2', '3']:
        return True
    return False

def _get_is_low_tech(uwp):
    if uwp[TECH] in ['0', '1', '2', '3']:
        return True
    return False

def _get_is_non_agricultural(uwp):
    if uwp[ATMO] in ['0', '1', '2', '3'] and \
            uwp[HYDRO] in ['0', '1', '2', '3'] and \
            ehex.greater_than_or_equal_to(uwp[POP], '6'):
                return True
    return False

def _get_is_non_industrial(uwp):
    if uwp[POP] in ['0', '1', '2', '3', '4', '5', '6']:
        return True
    return False

def _get_is_poor(uwp):
    if uwp[ATMO] in ['2', '3', '4', '5'] and \
            uwp[HYDRO] in ['0', '1', '2', '3']:
                return True
    return False

def _get_is_rich(uwp):
    if uwp[ATMO] in ['6', '8'] and \
            uwp[POP] in ['6', '7', '8'] and \
            uwp[GOV] in ['4', '5', '6', '7', '8', '9']:
                return True
    return False

def _get_is_vacuum(uwp):
    if uwp[ATMO] == '0':
        return True
    return False

def _get_is_water_world(uwp):
    if uwp[HYDRO] == 'A':
        return True
    return False


trade_code_queries = [
    {"check": _get_is_agricultural,     "code": "Ag"},
    {"check": _get_is_asteroid,         "code": "As"},
    {"check": _get_is_barren,           "code": "Ba"},
    {"check": _get_is_desert,           "code": "De"},
    {"check": _get_is_fluid_oceans,     "code": "Fl"},
    {"check": _get_is_garden,           "code": "Ga"},
    {"check": _get_is_high_population,  "code": "Hi"},
    {"check": _get_is_high_tech,        "code": "Ht"},
    {"check": _get_is_ice_capped,       "code": "Ic"},
    {"check": _get_is_industrial,       "code": "In"},
    {"check": _get_is_low_population,   "code": "Lo"},
    {"check": _get_is_low_tech,         "code": "Lt"},
    {"check": _get_is_non_agricultural, "code": "Na"},
    {"check": _get_is_non_industrial,   "code": "Ni"},
    {"check": _get_is_poor,             "code": "Po"},
    {"check": _get_is_rich,             "code": "Ri"},
    {"check": _get_is_vacuum,           "code": "Va"},
    {"check": _get_is_water_world,      "code": "Wa"}
]


def get_trade_codes(uwp):
    trade_codes = []
    for query in trade_code_queries:
        if query["check"](uwp):
            trade_codes.append(query["code"])
    return trade_codes
















