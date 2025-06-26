""" Traveller 'ehex' values """

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

def greater_than(a, b):
    return hex_to_int(a) > hex_to_int(b)

def greater_than_or_equal_to(a, b):
    return hex_to_int(a) >= hex_to_int(b)

def less_than(a, b):
    return hex_to_int(a) < hex_to_int(b)

def less_than_or_equal_to(a, b):
    return hex_to_int(a) <= hex_to_int(b)

def is_valid(a):
    if a in hex_table:
        return True
    return False
