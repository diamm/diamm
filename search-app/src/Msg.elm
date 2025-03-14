module Msg exposing (..)

import Facets.SelectFacet exposing (SelectFacetMsg)
import Http
import Http.Detailed
import RecordTypes exposing (FacetTypes, SearchBody)
import Route exposing (Route)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
    | UrlChanged (Maybe Route)
    | UserInteractedWithSelectFacet FacetTypes SelectFacetMsg
