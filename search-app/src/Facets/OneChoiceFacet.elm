module Facets.OneChoiceFacet exposing (OneChoiceFacetModel, OneChoiceFacetMsg(..), initialOneChoiceModel, update, viewOneChoiceFacet)

import Element exposing (Element, none)
import RecordTypes exposing (FacetItem)


type OneChoiceFacetMsg
    = NoOp
    | OnSelect FacetItem
    | OnRemoveItem FacetItem
    | OnClear


type alias OneChoiceFacetModel =
    { id : String
    , available : List FacetItem
    , selected : Maybe FacetItem
    }


initialOneChoiceModel : { identifier : String, available : List FacetItem } -> OneChoiceFacetModel
initialOneChoiceModel cfg =
    { id = cfg.identifier
    , available = cfg.available
    , selected = Nothing
    }


update : OneChoiceFacetMsg -> OneChoiceFacetModel -> ( OneChoiceFacetModel, Cmd OneChoiceFacetMsg )
update msg model =
    case msg of
        NoOp ->
            ( model, Cmd.none )

        OnSelect item ->
            ( model, Cmd.none )

        OnRemoveItem item ->
            ( model, Cmd.none )

        OnClear ->
            ( model, Cmd.none )


viewOneChoiceFacet : String -> OneChoiceFacetModel -> Element msg
viewOneChoiceFacet title facetModel =
    none
