module RecordTypes exposing (FacetItem, SearchBody, SearchTypesBlock, searchBodyDecoder)

import Json.Decode as Decode exposing (Decoder, int, list, maybe, string)
import Json.Decode.Pipeline exposing (optional, required)


type alias PaginationBlock =
    { next : Maybe String
    , previous : Maybe String
    , currentPage : Int
    , numPages : Int
    }


type alias SearchTypesBlock =
    { archive : Int
    , composition : Int
    , organization : Int
    , person : Int
    , set : Int
    , source : Int
    , sourceWithImages : Int
    }


type alias SourceResultBody =
    { pk : String
    , url : String
    , heading : String
    }


type alias ArchiveResultBody =
    { pk : String
    , url : String
    , heading : String
    , siglum : String
    }


type alias CompositionResultBody =
    { pk : String
    , url : String
    , heading : String
    }


type alias OrganizationResultBody =
    { pk : String
    , url : String
    , heading : String
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


type alias FacetItem =
    { value : String, count : Int }


type alias FacetBlock =
    { city : List FacetItem
    , genres : List FacetItem
    , notations : List FacetItem
    , composers : List FacetItem
    , sourceType : List FacetItem
    , hasInventory : List FacetItem
    , organizationType : List FacetItem
    , location : List FacetItem
    , archive : List FacetItem
    , anonymous : List FacetItem

    --, archiveLocations : Maybe Never
    }


facetBlockDecoder : Decoder FacetBlock
facetBlockDecoder =
    Decode.succeed FacetBlock
        |> required "cities" (list facetItemDecoder)
        |> required "genres" (list facetItemDecoder)
        |> required "notations" (list facetItemDecoder)
        |> required "composers" (list facetItemDecoder)
        |> required "source_type" (list facetItemDecoder)
        |> required "has_inventory" (list facetItemDecoder)
        |> required "organization_type" (list facetItemDecoder)
        |> required "location" (list facetItemDecoder)
        |> required "archive" (list facetItemDecoder)
        |> required "anonymous" (list facetItemDecoder)


facetItemDecoder : Decoder FacetItem
facetItemDecoder =
    Decode.succeed FacetItem
        |> required "value" string
        |> required "count" int


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
        |> required "current_page" int
        |> required "num_pages" int


searchTypesBlockDecoder : Decoder SearchTypesBlock
searchTypesBlockDecoder =
    Decode.succeed SearchTypesBlock
        |> required "archive" int
        |> required "composition" int
        |> required "organization" int
        |> required "person" int
        |> required "set" int
        |> required "source" int
        |> required "sources_with_images" int


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


archiveResultBodyDecoder : Decoder ArchiveResultBody
archiveResultBodyDecoder =
    Decode.succeed ArchiveResultBody
        |> required "pk" string
        |> required "url" string
        |> required "heading" string
        |> required "siglum" string
