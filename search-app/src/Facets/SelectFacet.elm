module Facets.SelectFacet exposing (..)

import Element exposing (Element, column, fill, html, row, text, width)
import RecordTypes exposing (FacetItem, facetItemToLabel)
import Select
import Simple.Fuzzy


type SelectFacetMsg
    = NoOp
    | OnSelect (Maybe FacetItem)
    | OnRemoveItem FacetItem
    | SelectMsg (Select.Msg FacetItem)
    | OnFocus
    | OnBlur
    | OnEsc


type alias SelectFacetModel =
    { id : String
    , available : List FacetItem
    , itemToLabel : FacetItem -> String
    , selected : List FacetItem
    , selectState : Select.State
    , selectConfig : Select.Config SelectFacetMsg FacetItem
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


selectConfig : Select.Config SelectFacetMsg FacetItem
selectConfig =
    Select.newConfig
        { onSelect = OnSelect
        , toLabel = .value
        , filter = filter 2 .value
        , toMsg = SelectMsg
        }


update : SelectFacetMsg -> SelectFacetModel -> ( SelectFacetModel, Cmd SelectFacetMsg )
update msg model =
    case msg of
        NoOp ->
            ( model, Cmd.none )

        OnSelect facetItem ->
            let
                selected =
                    Maybe.map (List.singleton >> List.append model.selected) facetItem
                        |> Maybe.withDefault []
            in
            ( { model | selected = selected }, Cmd.none )

        OnRemoveItem facetItem ->
            let
                selected =
                    List.filter (\curItem -> curItem /= facetItem)
                        model.selected
            in
            ( { model | selected = selected }, Cmd.none )

        SelectMsg subMsg ->
            let
                ( updated, cmd ) =
                    Select.update
                        model.selectConfig
                        subMsg
                        model.selectState
            in
            ( { model
                | selectState = updated
              }
            , cmd
            )

        OnFocus ->
            ( model, Cmd.none )

        OnBlur ->
            ( model, Cmd.none )

        OnEsc ->
            ( model, Cmd.none )


viewSelectFacet : SelectFacetModel -> Element SelectFacetMsg
viewSelectFacet facetModel =
    let
        facetView =
            Select.view
                facetModel.selectConfig
                facetModel.selectState
                facetModel.available
                facetModel.selected
                |> html

        selected =
            List.map facetItemToLabel facetModel.selected
                |> List.map text
    in
    row
        [ width fill ]
        [ column
            [ width fill ]
            [ row
                [ width fill ]
                [ facetView ]
            , row
                [ width fill ]
                selected
            ]
        ]


filter : Int -> (FacetItem -> String) -> String -> List FacetItem -> Maybe (List FacetItem)
filter minChars toLabel query items =
    if String.length query < minChars then
        Nothing

    else
        items
            |> Simple.Fuzzy.filter toLabel query
            |> Just
