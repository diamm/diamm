def source_picker_label(source) -> str:
    date = source.date_statement or "undated"
    return f"{source.archive.siglum} {source.shelfmark} — {date}"
