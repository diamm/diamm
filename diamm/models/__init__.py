from diamm.models.data.archive import Archive
from diamm.models.data.archive_identifier import ArchiveIdentifier
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
from diamm.models.data.bibliography_type import BibliographyType
from diamm.models.data.clef import Clef
from diamm.models.data.composition import Composition
from diamm.models.data.composition_bibliography import CompositionBibliography
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.composition_cycle import CompositionCycle
from diamm.models.data.composition_note import CompositionNote
from diamm.models.data.cycle import Cycle
from diamm.models.data.cycle_type import CycleType
from diamm.models.data.genre import Genre
from diamm.models.data.geographic_area import GeographicArea
# from diamm.models.data.page_condition import PageCondition
from diamm.models.data.image import Image
from diamm.models.data.image_note import ImageNote
from diamm.models.data.image_type import ImageType
from diamm.models.data.item import Item
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.models.data.item_composer import ItemComposer
from diamm.models.data.item_note import ItemNote
from diamm.models.data.language import Language
from diamm.models.data.legacy_id import LegacyId  # Yes, this belongs here. Used to track old PKs
from diamm.models.data.mensuration import Mensuration
from diamm.models.data.notation import Notation
from diamm.models.data.organization import Organization
from diamm.models.data.organization_identifier import OrganizationIdentifier
from diamm.models.data.organization_type import OrganizationType
from diamm.models.data.page import Page
from diamm.models.data.page_note import PageNote
from diamm.models.data.person import Person
from diamm.models.data.person_identifier import PersonIdentifier
from diamm.models.data.person_note import PersonNote
from diamm.models.data.person_role import PersonRole
from diamm.models.data.role import Role
from diamm.models.data.set import Set
from diamm.models.data.set_bibliography import SetBibliography
from diamm.models.data.source import Source
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source_catalogue_entry import SourceCatalogueEntry
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_authority import SourceAuthority
from diamm.models.data.source_manifest import SourceManifest
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_relationship_type import SourceRelationshipType
from diamm.models.data.source_url import SourceURL
from diamm.models.data.text import Text
from diamm.models.data.voice import Voice
from diamm.models.data.voice_type import VoiceType
from diamm.models.diamm_user import CustomUserModel
from diamm.models.site.commentary import Commentary
from diamm.models.site.content_page import ContentPage
from diamm.models.site.dissertation_page import DissertationPage
from diamm.models.site.home_page import HomePage
from diamm.models.site.news_index import NewsIndexPage
from diamm.models.site.news_page import NewsPage
from diamm.models.site.problem_report import ProblemReport
from diamm.models.site.publication_page import PublicationPage

# from diamm.models.migrate.legacy_source import LegacySource
# from diamm.models.migrate.legacy_archive import LegacyArchive
# from diamm.models.migrate.legacy_country import LegacyCountry
# from diamm.models.migrate.legacy_city import LegacyCity
# from diamm.models.migrate.legacy_composer import LegacyComposer
# from diamm.models.migrate.legacy_copyist import LegacyCopyist
# from diamm.models.migrate.legacy_language import LegacyLanguage
# from diamm.models.migrate.legacy_person import LegacyPerson
# from diamm.models.migrate.legacy_source_copyist import LegacySourceCopyist
# from diamm.models.migrate.legacy_bibliography import LegacyBibliography
# from diamm.models.migrate.legacy_author import LegacyAuthor
# from diamm.models.migrate.legacy_author_bibliography import LegacyAuthorBibliography
# from diamm.models.migrate.legacy_bibliography_source import LegacyBibliographySource
# from diamm.models.migrate.legacy_relationship_type import LegacyRelationshipType
# from diamm.models.migrate.legacy_source_person import LegacySourcePerson
# from diamm.models.migrate.legacy_source_notation import LegacySourceNotation
# from diamm.models.migrate.legacy_composition import LegacyComposition
# from diamm.models.migrate.legacy_composition_composer import LegacyCompositionComposer
# from diamm.models.migrate.legacy_item import LegacyItem
# from diamm.models.migrate.legacy_image import LegacyImage
# from diamm.models.migrate.legacy_secondary_image import LegacySecondaryImage
# from diamm.models.migrate.legacy_item_image import LegacyItemImage
# from diamm.models.migrate.legacy_provenance import LegacyProvenance
# from diamm.models.migrate.legacy_set import LegacySet
# from diamm.models.migrate.legacy_source_set import LegacySourceSet
# from diamm.models.migrate.legacy_clef import LegacyClef
# from diamm.models.migrate.legacy_text import LegacyText
# from diamm.models.migrate.legacy_text_language import LegacyTextLanguage
# from diamm.models.migrate.legacy_notation import LegacyNotation
# from diamm.models.migrate.legacy_bibliography_item import LegacyBibliographyItem
# from diamm.models.migrate.legacy_cycle_type import LegacyCycleType
# from diamm.models.migrate.legacy_composition_cycle import LegacyCompositionCycle
# from diamm.models.migrate.legacy_composition_cycle_composition import LegacyCompositionCycleComposition
# from diamm.models.migrate.legacy_note import LegacyNote
