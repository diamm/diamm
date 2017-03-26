import re
from blessings import Terminal
import psycopg2 as psql
from django.conf import settings

term = Terminal()


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


def reset_table(sequence_id):
    print(term.yellow("\tUpdating the ID sequences for the Django tables, {0}".format(sequence_id)))
    db = settings.DATABASES['default']
    conn = psql.connect(database=db['NAME'],
                        user=db['USER'],
                        password=db['PASSWORD'],
                        host=db['HOST'],
                        port=db['PORT'],
                        cursor_factory=psql.extras.DictCursor)
    curs = conn.cursor()
    print(term.yellow("\t\tResetting table sequence"))
    sql_alt_bibl = "ALTER SEQUENCE %s RESTART WITH 1"
    curs.execute(sql_alt_bibl, (sequence_id,))

