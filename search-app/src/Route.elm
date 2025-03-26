module Route exposing (..)

import Dict
import Helpers exposing (prepareQuery)
import Maybe.Extra as ME
import RecordTypes exposing (RecordTypeFilters(..), resultTypeOptions)
import Url exposing (Url)
import Url.Builder exposing (QueryParameter)
import Url.Parser as P exposing ((<?>), s)
import Url.Parser.Query as Q


type Route
    = SearchPageRoute QueryArgs
    | UnknownRoute


type alias QueryArgs =
    { keywordQuery : Maybe String
    , resultType : RecordTypeFilters
    , composers : List String
    , notations : List String
    , genres : List String
    , sourceTypes : List String
    , currentPage : Int
    }


{-|

    Creates a pipeline-like Query parser.

-}
apply : Q.Parser a -> Q.Parser (a -> b) -> Q.Parser b
apply argParser funcParser =
    Q.map2 (<|) funcParser argParser


parseUrl : Url -> Maybe Route
parseUrl url =
    P.parse routeParser url


extractPageNumberFromUrl : Url -> Maybe Int
extractPageNumberFromUrl url =
    prepareQuery url.query
        |> Dict.get "page"
        |> Maybe.andThen (\ll -> List.head ll)
        |> Maybe.andThen String.toInt


routeParser : P.Parser (Route -> a) a
routeParser =
    P.map SearchPageRoute (s "search" <?> queryParamsParser)


queryParamsParser : Q.Parser QueryArgs
queryParamsParser =
    Q.map QueryArgs (Q.string "q")
        |> apply resultTypeParamParser
        |> apply composerParamParser
        |> apply notationParamParser
        |> apply genreParamParser
        |> apply pageParamParser


resultTypeParamParser : Q.Parser RecordTypeFilters
resultTypeParamParser =
    Q.custom "type" typeQueryStringToResultType


composerParamParser : Q.Parser (List String)
composerParamParser =
    Q.custom "composer" identity


notationParamParser : Q.Parser (List String)
notationParamParser =
    Q.custom "notation" identity


pageParamParser : Q.Parser Int
pageParamParser =
    Q.map (Maybe.withDefault 1) (Q.int "page")


genreParamParser : Q.Parser (List String)
genreParamParser =
    Q.custom "genre" identity


typeQueryStringToResultType : List String -> RecordTypeFilters
typeQueryStringToResultType typeList =
    List.map parseStringToResultMode typeList
        |> List.head
        |> Maybe.withDefault ShowAllRecords


parseStringToResultMode : String -> RecordTypeFilters
parseStringToResultMode string =
    Dict.fromList resultTypeOptions
        |> Dict.get string
        |> Maybe.withDefault ShowAllRecords


defaultQueryArgs : QueryArgs
defaultQueryArgs =
    { keywordQuery = Nothing
    , resultType = ShowAllRecords
    , composers = []
    , notations = []
    , genres = []
    , sourceTypes = []
    , currentPage = 1
    }


locationHrefToRoute : String -> Maybe Route
locationHrefToRoute locationHref =
    case Url.fromString locationHref of
        Nothing ->
            Nothing

        Just url ->
            parseUrl url


buildQueryParameters : QueryArgs -> List QueryParameter
buildQueryParameters queryArgs =
    let
        typeParam =
            [ Url.Builder.string "type" (parseResultTypeToString queryArgs.resultType) ]

        qParam =
            queryArgs.keywordQuery
                |> ME.unwrap [] (\q -> [ Url.Builder.string "q" q ])

        composerParam =
            List.map (Url.Builder.string "composer") queryArgs.composers

        pageParam =
            [ String.fromInt queryArgs.currentPage
                |> Url.Builder.string "page"
            ]

        genresParam =
            List.map (Url.Builder.string "genre") queryArgs.genres
    in
    List.concat [ qParam, typeParam, composerParam, genresParam, pageParam ]


parseResultTypeToString : RecordTypeFilters -> String
parseResultTypeToString typeFilter =
    List.filter (\( _, m ) -> m == typeFilter) resultTypeOptions
        |> List.head
        |> Maybe.withDefault ( "all", ShowAllRecords )
        |> Tuple.first


setQueryType : RecordTypeFilters -> { a | resultType : RecordTypeFilters } -> { a | resultType : RecordTypeFilters }
setQueryType newType oldRecord =
    { oldRecord | resultType = newType }


setKeywordQuery : Maybe String -> { a | keywordQuery : Maybe String } -> { a | keywordQuery : Maybe String }
setKeywordQuery newQuery oldRecord =
    { oldRecord | keywordQuery = newQuery }


setCurrentPage : Int -> { a | currentPage : Int } -> { a | currentPage : Int }
setCurrentPage newPage oldRecord =
    { oldRecord | currentPage = newPage }



--updateGenreValues : String -> { a | genres : List String } -> { a | genres : List String }
--updateGenreValues addValue qargs =
--    { qargs | genres = addValue :: qargs.genres }


setQueryGenres : List String -> { a | genres : List String } -> { a | genres : List String }
setQueryGenres newValues oldRecord =
    { oldRecord | genres = newValues }


setQueryNotations : List String -> { a | notations : List String } -> { a | notations : List String }
setQueryNotations newValues oldRecord =
    { oldRecord | notations = newValues }


setQuerySourceTypes : List String -> { a | sourceTypes : List String } -> { a | sourceTypes : List String }
setQuerySourceTypes newValues oldRecord =
    { oldRecord | sourceTypes = newValues }



--removeGenreValue : String -> { a | genres : List String } -> { a | genres : List String }
--removeGenreValue remValue qargs =
--    { qargs | genres = List.filter ((/=) remValue) qargs.genres }
