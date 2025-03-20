module Msg exposing (..)

import Facets.CheckboxFacet exposing (CheckBoxFacetMsg)
import Facets.OneChoiceFacet exposing (OneChoiceFacetMsg)
import Facets.SelectFacet exposing (SelectFacetMsg)
import Http
import Http.Detailed
import RecordTypes exposing (CheckboxFacetTypes, OneChoiceFacetTypes, RecordTypeFilters, SearchBody, SelectFacetTypes)
import Route exposing (Route)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
    | UrlChanged (Maybe Route)
    | UserInteractedWithSelectFacet SelectFacetTypes SelectFacetMsg
    | UserInteractedWithCheckboxFacet CheckboxFacetTypes CheckBoxFacetMsg
    | UserInteractedWithOneChoiceFacet OneChoiceFacetTypes OneChoiceFacetMsg
    | UserClickedRecordTypeFilter RecordTypeFilters
    | UserEnteredTextIntoQueryBox String
    | UserEnteredTextIntoPageGotoBox Int String
    | UserSubmittedPageGoto Int
    | UserPressedEnterOnQueryBox
