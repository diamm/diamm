module Model exposing (Model, init)

import Facets exposing (FacetModel)
import Request exposing (Response(..))
import Route exposing (QueryArgs)


type alias Model =
    { currentQueryArgs : QueryArgs
    , needsUpdating : Bool
    , response : Response
    , facets : FacetModel
    , gotoPageValue : String
    }


init : QueryArgs -> Model
init initalQueryArgs =
    { currentQueryArgs = initalQueryArgs
    , needsUpdating = False
    , response = Loading Nothing
    , facets =
        { cities = Nothing
        , genres = Nothing
        , notations = Nothing
        , composers = Nothing
        , sourceTypes = Nothing
        , hasInventory = Nothing
        , organizationType = Nothing
        , location = Nothing
        , anonymous = Nothing
        , sourceComposers = Nothing
        , originalFormat = Nothing
        , currentState = Nothing
        , hostMainContents = Nothing
        , dateRange = Nothing
        }
    , gotoPageValue = ""
    }
