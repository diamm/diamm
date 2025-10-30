def format_person_name(name_blk: dict) -> str:
    last_name: str | None = name_blk.get("last_name")
    first_name: str | None = name_blk.get("first_name")
    floruit: str | None = name_blk.get("floruit", "")
    # NB: uncertain is only present when the name is given relative to something, e.g., a composition.
    uncertain: bool = name_blk.get("uncertain", False)
    latest_year: int | None = name_blk.get("latest_year")
    earliest_year: int | None = name_blk.get("earliest_year")
    latest_year_approximate: bool = name_blk.get("latest_year_approximate", False)
    earliest_year_approximate: bool = name_blk.get("earliest_year_approximate", False)

    year_str = []
    if floruit:
        year_str.append(f"{floruit}")
    else:
        if earliest_year:
            year_str.append(
                f"{'ca. ' if earliest_year_approximate else ''}{earliest_year}"
            )
        if latest_year:
            year_str.append(
                f"-{'ca. ' if latest_year_approximate else ''}{latest_year}"
            )

    year_stmt: str | None = f"({''.join(year_str)})" if year_str else None

    name_str = []
    if last_name:
        name_str.append(f"{last_name}")
    if first_name:
        name_str.append(f"{', ' if last_name else ''}{first_name}")
    if year_stmt:
        name_str.append(f" {year_stmt}")
    if uncertain:
        name_str.append(" (?)")

    return "".join(name_str)


def contents_statement(doc: dict) -> str | None:
    num_anon: int = doc.get("number_of_anonymous_compositions_i", 0)
    num_attrib: int = doc.get("number_of_attributed_compositions_i", 0)
    num_comptn: int = doc.get("number_of_compositions_i", 0)
    num_comprs: int = doc.get("number_of_composers_i", 0)
    num_uninv_cmp: int = doc.get("number_of_uninventoried_composers_i", 0)

    out_stmt: list = []
    if num_comptn > 0:
        out_stmt.append(f"Contains {num_comptn} composition{'s'[: num_comptn ^ 1]}")
    if num_comprs > 0:
        if num_attrib != num_comptn:
            out_stmt.append(f", {num_attrib} ")
        out_stmt.append(f" from {num_comprs} composer{'s'[: num_comprs ^ 1]}")

    if num_anon > 0:
        out_stmt.append(f", {num_anon} {'is' if num_anon == 1 else 'are'} anonymous")

    if len(out_stmt) > 0:
        out_stmt.append(".")

    if num_uninv_cmp > 0:
        out_stmt.append(
            f" Contains uninventoried compositions from {num_uninv_cmp} composer{'s'[: num_uninv_cmp ^ 1]}."
        )

    return "".join(out_stmt) or None
