from django_jinja import library
import itertools


@library.global_function
def page_array(num_pages, current_page):
    """
    Construct a plausible sorted page array based on the number of pages
    and the current page.
    Ensures pages are >= 1
    :param args: c
    :return:
    """
    num_pages = max(num_pages, 1)
    current_page = min(max(current_page, 1), num_pages)

    r1 = list(range(1, 4))
    r2 = list(range(max(current_page - 2, 1), min(current_page + 2, num_pages)))
    r3 = list(range(num_pages - 2, num_pages + 1))

    all_numbers = r1 + r2 + r3
    unique_numbers = set(all_numbers)
    page_numbers = list(unique_numbers)
    page_numbers.sort()

    prev_page = 0
    out_arr = []
    for pnum in page_numbers:
        if pnum != prev_page + 1:
            out_arr.append(None)
        out_arr.append(pnum)
        prev_page = pnum

    return out_arr
