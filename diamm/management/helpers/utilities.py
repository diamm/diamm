import re


def convert_yn_to_boolean(value):
    if value == "Y":
        return True
    elif value == "N":
        return False
    else:
        return False


# Removes zeros from the beginning of a string.
def remove_leading_zeroes(value):
    return re.sub("\A0", "", value)
