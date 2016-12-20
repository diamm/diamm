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
    # if it's null, just return null.
    if not value:
        return value
    return re.sub("\A0", "", value)
