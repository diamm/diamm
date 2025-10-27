module Msg exposing (Msg(..))

import Facets.CheckboxFacet exposing (CheckBoxFacetMsg)
import Facets.OneChoiceFacet exposing (OneChoiceFacetMsg)
import Facets.RangeFacet exposing (RangeFacetMsg)
import Http
import Http.Detailed
import RecordTypes exposing (CheckboxFacetTypes, OneChoiceFacetTypes, RangeFacetTypes, RecordTypeFilters, SearchBody)
import Route exposing (Route)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
    | ClientChangedUrl (Maybe Route)
    | ClientCompletedViewportReset
    | UserInteractedWithCheckboxFacet CheckboxFacetTypes CheckBoxFacetMsg
    | UserInteractedWithOneChoiceFacet OneChoiceFacetTypes OneChoiceFacetMsg
    | UserInteractedWithRangeFacet RangeFacetTypes RangeFacetMsg
    | UserClickedRecordTypeFilter RecordTypeFilters
    | UserEnteredTextIntoQueryBox String
    | UserEnteredTextIntoPageGotoBox Int String
    | UserSubmittedPageGoto Int
    | UserClickedPaginationLink Int
    | UserPressedEnterOnQueryBox
    | UserClickedUpdateResults
    | UserClickedClearSearch
