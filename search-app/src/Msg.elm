module Msg exposing (..)

import Facets.CheckboxFacet exposing (CheckBoxFacetMsg)
import Facets.SelectFacet exposing (SelectFacetMsg)
import Http
import Http.Detailed
import RecordTypes exposing (CheckboxFacetTypes, RecordTypeFilters, SearchBody, SelectFacetTypes)
import Route exposing (Route)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
    | UrlChanged (Maybe Route)
    | UserInteractedWithSelectFacet SelectFacetTypes SelectFacetMsg
    | UserInteractedWithCheckboxFacet CheckboxFacetTypes CheckBoxFacetMsg
    | UserClickedRecordTypeFilter RecordTypeFilters
    | UserEnteredTextIntoQueryBox String
    | UserPressedEnterOnQueryBox
