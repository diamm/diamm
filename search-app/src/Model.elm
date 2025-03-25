module Model exposing (..)

import Facets exposing (FacetModel)
import RecordTypes exposing (RecordTypeFilters(..))
import Request exposing (Response(..))
import Route exposing (QueryArgs, Route)


type alias Model =
    { currentQueryArgs : QueryArgs
    , response : Response
    , facets : Maybe FacetModel
    , gotoPageValue : String
    }


init : QueryArgs -> Model
init initalQueryArgs =
    { currentQueryArgs = initalQueryArgs
    , response = NoResponseToShow
    , facets = Nothing
    , gotoPageValue = ""
    }


toNextQuery : Model -> QueryArgs
toNextQuery model =
    model.currentQueryArgs
