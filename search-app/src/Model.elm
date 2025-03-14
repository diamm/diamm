module Model exposing (..)

import Facets exposing (FacetModel)
import Request exposing (Response(..))


type alias Model =
    { response : Response
    , facets : Maybe FacetModel
    }


init : Model
init =
    { response = NoResponseToShow
    , facets = Nothing
    }
