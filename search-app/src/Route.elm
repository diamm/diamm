module Route exposing (..)

import Url exposing (Url)
import Url.Parser as P exposing ((<?>), s)
import Url.Parser.Query as Q


type Route
    = SearchPageRoute QueryArgs
    | UnknownRoute


type alias QueryArgs =
    { keywordQuery : Maybe String
    , resultType : Maybe String
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


routeParser : P.Parser (Route -> a) a
routeParser =
    P.map SearchPageRoute (s "search" <?> queryParamsParser)


queryParamsParser : Q.Parser QueryArgs
queryParamsParser =
    Q.map QueryArgs (Q.string "q")
        |> apply (Q.string "type")


defaultQueryArgs : QueryArgs
defaultQueryArgs =
    { keywordQuery = Nothing
    , resultType = Nothing
    }


locationHrefToRoute : String -> Maybe Route
locationHrefToRoute locationHref =
    case Url.fromString locationHref of
        Nothing ->
            Nothing

        Just url ->
            parseUrl url
