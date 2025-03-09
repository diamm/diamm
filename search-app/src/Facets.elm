module Facets exposing (..)

import Msg exposing (Msg(..))
import RecordTypes exposing (FacetItem)
import Select
import Simple.Fuzzy


type alias SelectFacetModel =
    { id : String
    , available : List FacetItem
    , itemToLabel : FacetItem -> String
    , selected : List FacetItem
    , selectState : Select.State
    , selectConfig : Select.Config Msg FacetItem
    }


type alias FacetModel =
    { city : Maybe Never
    , genres : SelectFacetModel
    , notations : Maybe Never
    , composers : SelectFacetModel
    , sourceType : Maybe Never
    , hasInventory : Maybe Never
    , organizationType : Maybe Never
    , location : Maybe Never
    , archive : Maybe Never
    , anonymous : Maybe Never
    }


initialSelectModel :
    { identifier : String
    , available : List FacetItem
    }
    -> SelectFacetModel
initialSelectModel cfg =
    { id = cfg.identifier
    , available = cfg.available
    , itemToLabel = .value
    , selected = []
    , selectState = Select.init cfg.identifier
    , selectConfig = selectConfig
    }


selectConfig : Select.Config Msg FacetItem
selectConfig =
    Select.newConfig
        { onSelect = \_ -> NothingHappened
        , toLabel = .value
        , filter = filter 2 .value
        , toMsg = \_ -> NothingHappened
        }


filter : Int -> (FacetItem -> String) -> String -> List FacetItem -> Maybe (List FacetItem)
filter minChars toLabel query items =
    if String.length query < minChars then
        Nothing

    else
        items
            |> Simple.Fuzzy.filter toLabel query
            |> Just
