module Route exposing (..)

import Url exposing (Url)
import Url.Parser as P
import Url.Parser.Query as Q


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


parseUrl : Url -> QueryArgs
parseUrl url =
    P.parse routeParser url
        |> Maybe.withDefault defaultQueryArgs


defaultQueryArgs : QueryArgs
defaultQueryArgs =
    { keywordQuery = Nothing
    , resultType = Nothing
    }


routeParser : P.Parser (QueryArgs -> a) a
routeParser =
    P.map QueryArgs
        (Q.map QueryArgs (Q.string "q")
            |> apply (Q.string "type")
        )
