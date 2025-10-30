module RecordTypes exposing (ArchiveResultBody, CheckboxFacetTypes(..), CompositionResultBody, FacetBlock, FacetItem, OneChoiceFacetTypes(..), OrganizationResultBody, PaginationBlock, PersonResultBody, RangeFacetItem, RangeFacetTypes(..), RecordTypeFilters(..), SearchBody, SearchResult(..), SearchTypesBlock, SetResultBody, SourceResultBody, parseResultTypeToString, resultTypeOptions, searchBodyDecoder)

import Json.Decode as Decode exposing (Decoder, bool, int, list, maybe, string)
import Json.Decode.Pipeline exposing (optional, required)


type CheckboxFacetTypes
    = Genres
    | Composers
    | Notations
    | SourceComposers


type OneChoiceFacetTypes
    = HasInventory
    | AnonymousComposer
    | Cities
    | SourceTypes
    | OriginalFormat
    | CurrentState
    | HostMainContents
    | OrganizationType


type RangeFacetTypes
    = DateRange


type alias PaginationBlock =
    { next : Maybe String
    , previous : Maybe String
    , first : String
    , last : String
    , currentPage : Int
    , numPages : Int
    }


type alias SearchTypesBlock =
    { archive : Maybe Int
    , composition : Maybe Int
    , organization : Maybe Int
    , person : Maybe Int
    , set : Maybe Int
    , source : Maybe Int
    , sourceWithImages : Maybe Int
    }


type alias SourceResultBody =
    { pk : String
    , url : String
    , heading : String
    , archiveName : String
    , archiveCity : String
    , sourceType : Maybe String
    , dateStatement : Maybe String
    , surface : Maybe String
    , measurements : Maybe String
    , numberOfCompositions : Maybe Int
    , publicImages : Bool
    , contentsStatement : Maybe String
    }


type alias ArchiveResultBody =
    { pk : String
    , url : String
    , heading : String
    , siglum : String
    , city : String
    , country : String
    }


type alias CompositionResultBody =
    { pk : String
    , url : String
    , heading : String
    , composers : Maybe (List String)
    , numSources : Maybe Int
    }


type alias OrganizationResultBody =
    { pk : String
    , url : String
    , heading : String
    , location : Maybe String
    }


type alias PersonResultBody =
    { pk : String
    , url : String
    , heading : String
    }


type alias SetResultBody =
    { pk : String
    , url : String
    , heading : String
    }


type SearchResult
    = SourceResult SourceResultBody
    | ArchiveResult ArchiveResultBody
    | CompositionResult CompositionResultBody
    | OrganizationResult OrganizationResultBody
    | PersonResult PersonResultBody
    | SetResult SetResultBody


type RecordTypeFilters
    = SourceRecords
    | ArchiveRecords
    | CompositionRecords
    | OrganizationRecords
    | PersonRecords
    | SetRecords
    | SourcesWithImagesRecords
    | ShowAllRecords


resultTypeOptions : List ( String, RecordTypeFilters )
resultTypeOptions =
    [ ( "all", ShowAllRecords )
    , ( "source", SourceRecords )
    , ( "archive", ArchiveRecords )
    , ( "organization", OrganizationRecords )
    , ( "composition", CompositionRecords )
    , ( "person", PersonRecords )
    , ( "sources_with_images", SourcesWithImagesRecords )
    , ( "set", SetRecords )
    ]


parseResultTypeToString : RecordTypeFilters -> String
parseResultTypeToString typeFilter =
    List.filter (\( _, m ) -> m == typeFilter) resultTypeOptions
        |> List.head
        |> Maybe.withDefault ( "all", ShowAllRecords )
        |> Tuple.first


type alias FacetItem =
    { value : String, count : Int }


type alias RangeFacetItem =
    { min : Int
    , max : Int
    , buckets : List FacetItem
    }


type alias FacetBlock =
    { cities : List FacetItem
    , genres : List FacetItem
    , notations : List FacetItem
    , composers : List FacetItem
    , sourceType : List FacetItem
    , hasInventory : List FacetItem
    , organizationType : List FacetItem
    , location : List FacetItem
    , anonymous : List FacetItem
    , sourceComposers : List FacetItem
    , originalFormat : List FacetItem
    , currentState : List FacetItem
    , hostMainContents : List FacetItem
    , dateRange : Maybe RangeFacetItem

    --, archiveLocations : Maybe Never
    }


facetBlockDecoder : Decoder FacetBlock
facetBlockDecoder =
    Decode.succeed FacetBlock
        |> optional "cities" (list facetItemDecoder) []
        |> optional "genres" (list facetItemDecoder) []
        |> optional "notations" (list facetItemDecoder) []
        |> optional "composers" (list facetItemDecoder) []
        |> optional "source_type" (list facetItemDecoder) []
        |> optional "has_inventory" (list facetItemDecoder) []
        |> optional "organization_type" (list facetItemDecoder) []
        |> optional "location" (list facetItemDecoder) []
        |> optional "anonymous" (list facetItemDecoder) []
        |> optional "source_composers" (list facetItemDecoder) []
        |> optional "original_format" (list facetItemDecoder) []
        |> optional "current_state" (list facetItemDecoder) []
        |> optional "host_main_contents" (list facetItemDecoder) []
        |> optional "date_range" (maybe rangeFacetItemDecoder) Nothing


facetItemDecoder : Decoder FacetItem
facetItemDecoder =
    Decode.succeed FacetItem
        |> required "value" string
        |> required "count" int


rangeFacetItemDecoder : Decoder RangeFacetItem
rangeFacetItemDecoder =
    Decode.succeed RangeFacetItem
        |> required "min" int
        |> required "max" int
        |> required "buckets" (list facetItemDecoder)


type alias SearchBody =
    { count : Int
    , pagination : PaginationBlock
    , query : String
    , types : SearchTypesBlock
    , results : List SearchResult
    , facets : FacetBlock
    }


searchBodyDecoder : Decoder SearchBody
searchBodyDecoder =
    Decode.succeed SearchBody
        |> required "count" int
        |> required "pagination" paginationBlockDecoder
        |> required "query" string
        |> required "types" searchTypesBlockDecoder
        |> required "results" (list searchResultDecoder)
        |> required "facets" facetBlockDecoder


paginationBlockDecoder : Decoder PaginationBlock
paginationBlockDecoder =
    Decode.succeed PaginationBlock
        |> optional "next" (maybe string) Nothing
        |> optional "previous" (maybe string) Nothing
        |> required "first" string
        |> required "last" string
        |> required "current_page" int
        |> required "num_pages" int


searchTypesBlockDecoder : Decoder SearchTypesBlock
searchTypesBlockDecoder =
    Decode.succeed SearchTypesBlock
        |> optional "archive" (maybe int) Nothing
        |> optional "composition" (maybe int) Nothing
        |> optional "organization" (maybe int) Nothing
        |> optional "person" (maybe int) Nothing
        |> optional "set" (maybe int) Nothing
        |> optional "source" (maybe int) Nothing
        |> optional "sources_with_images" (maybe int) Nothing


searchResultDecoder : Decoder SearchResult
searchResultDecoder =
    Decode.field "type" string
        |> Decode.andThen individualResultDecoder


individualResultDecoder : String -> Decoder SearchResult
individualResultDecoder typeValue =
    case typeValue of
        "source" ->
            Decode.map SourceResult sourceResultBodyDecoder

        "person" ->
            Decode.map PersonResult personResultBodyDecoder

        "organization" ->
            Decode.map OrganizationResult organizationResultBodyDecoder

        "archive" ->
            Decode.map ArchiveResult archiveResultBodyDecoder

        "set" ->
            Decode.map SetResult setResultBodyDecoder

        "composition" ->
            Decode.map CompositionResult compositionResultBodyDecoder

        _ ->
            Decode.fail ("Unknown value " ++ typeValue ++ " for result type.")


sourceResultBodyDecoder : Decoder SourceResultBody
sourceResultBodyDecoder =
    Decode.succeed SourceResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string
        |> required "archive_name" string
        |> required "source_archive_city" string
        |> optional "source_type" (maybe string) Nothing
        |> optional "date_statement" (maybe string) Nothing
        |> optional "surface" (maybe string) Nothing
        |> optional "measurements" (maybe string) Nothing
        |> optional "number_of_compositions" (maybe int) Nothing
        |> required "public_images" bool
        |> optional "contents_statement" (maybe string) Nothing


personResultBodyDecoder : Decoder PersonResultBody
personResultBodyDecoder =
    Decode.succeed PersonResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string


organizationResultBodyDecoder : Decoder OrganizationResultBody
organizationResultBodyDecoder =
    Decode.succeed OrganizationResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string
        |> optional "location" (maybe string) Nothing


setResultBodyDecoder : Decoder SetResultBody
setResultBodyDecoder =
    Decode.succeed SetResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string


compositionResultBodyDecoder : Decoder CompositionResultBody
compositionResultBodyDecoder =
    Decode.succeed CompositionResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string
        |> optional "composers" (maybe (list string)) Nothing
        |> optional "sources" (maybe int) Nothing


archiveResultBodyDecoder : Decoder ArchiveResultBody
archiveResultBodyDecoder =
    Decode.succeed ArchiveResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string
        |> required "siglum" string
        |> required "city" string
        |> required "country" string
