class ExternalIdentifiers:
    RISM = 1
    VIAF = 2
    WIKIDATA = 3
    GND = 4
    MUSICBRAINZ = 5
    ORCID = 6
    BNF = 7
    LC = 8


IDENTIFIER_TYPES = (
    (ExternalIdentifiers.RISM, "RISM Online"),
    (ExternalIdentifiers.VIAF, "VIAF"),
    (ExternalIdentifiers.WIKIDATA, "Wikidata"),
    (ExternalIdentifiers.GND, "GND (Gemeinsame Normdatei)"),
    (ExternalIdentifiers.MUSICBRAINZ, "MusicBrainz Artist"),
    (ExternalIdentifiers.ORCID, "ORCID"),
    (ExternalIdentifiers.BNF, "Bibliothèque national de France"),
    (ExternalIdentifiers.LC, "Library of Congress"),
)

TYPE_PREFIX = {
    ExternalIdentifiers.RISM: ("rism", "https://rism.online/"),
    ExternalIdentifiers.VIAF: ("viaf", "https://viaf.org/viaf/"),
    ExternalIdentifiers.WIKIDATA: ("wkp", "https://www.wikidata.org/wiki/"),
    ExternalIdentifiers.GND: ("dnb", "https://d-nb.info/gnd/"),
    ExternalIdentifiers.MUSICBRAINZ: ("mbaid", "https://musicbrainz.org/artist/"),
    ExternalIdentifiers.ORCID: ("orcid", "https://orcid.org/"),
    ExternalIdentifiers.BNF: ("bnf", "https://catalogue.bnf.fr/ark:/12148/cb"),
    ExternalIdentifiers.LC: ("lc", "https://id.loc.gov/authorities/"),
}
