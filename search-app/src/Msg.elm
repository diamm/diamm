module Msg exposing (Msg(..))

import Facets.CheckboxFacet exposing (CheckBoxFacetMsg)
import Facets.OneChoiceFacet exposing (OneChoiceFacetMsg)
import Http
import Http.Detailed
import RecordTypes exposing (CheckboxFacetTypes, OneChoiceFacetTypes, RecordTypeFilters, SearchBody)
import Route exposing (Route)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
    | ClientChangedUrl (Maybe Route)
    | UserInteractedWithCheckboxFacet CheckboxFacetTypes CheckBoxFacetMsg
    | UserInteractedWithOneChoiceFacet OneChoiceFacetTypes OneChoiceFacetMsg
    | UserClickedRecordTypeFilter RecordTypeFilters
    | UserEnteredTextIntoQueryBox String
    | UserEnteredTextIntoPageGotoBox Int String
    | UserSubmittedPageGoto Int
    | UserClickedPaginationLink Int
    | UserPressedEnterOnQueryBox
    | UserClickedClearSearch
