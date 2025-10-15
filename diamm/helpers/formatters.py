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
