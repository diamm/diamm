module Facets.SelectFacet exposing (..)

import Element exposing (Element, alignRight, column, el, fill, html, padding, pointer, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Html.Attributes as HA
import RecordTypes exposing (FacetItem, facetItemToLabel)
import Select
import Simple.Fuzzy
import Style exposing (colourScheme)


type SelectFacetMsg
    = NoOp
    | OnSelect (Maybe FacetItem)
    | OnRemoveItem FacetItem
    | SelectMsg (Select.Msg FacetItem)
    | OnFocus
    | OnBlur
    | OnEsc
    | OnClear


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
        |> Select.withEmptySearch True
        |> Select.withNotFound "No matches"
        |> Select.withInputWrapperAttrs [ HA.class "control" ]
        |> Select.withInputAttrs [ HA.class "input" ]
        |> Select.withClear False
        |> Select.withMenuAttrs [ HA.style "border" "1px solid #000", HA.style "box-shadow" "5px 6px 8px -2px #E0E0E0" ]


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

        OnClear ->
            ( { model | selected = [] }, Cmd.none )


viewSelectFacet : String -> SelectFacetModel -> Element SelectFacetMsg
viewSelectFacet title facetModel =
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
                |> List.map
                    (\t ->
                        el
                            [ Background.color colourScheme.red
                            , padding 8
                            , Font.color colourScheme.white
                            , Border.rounded 4
                            , Font.size 12
                            ]
                            (text t)
                    )
    in
    row
        [ width fill
        , Border.widthEach { top = 1, left = 0, right = 0, bottom = 0 }
        , Border.color colourScheme.lightGrey
        ]
        [ column
            [ width fill
            , spacing 10
            , padding 10
            ]
            [ row
                [ width fill ]
                [ el [ Font.semiBold ] (text title)
                , el
                    [ alignRight
                    , Events.onClick OnClear
                    , Font.color colourScheme.red
                    , pointer
                    ]
                    (text "Clear all")
                ]
            , row
                [ width fill ]
                [ facetView ]
            , row
                [ width fill
                , spacing 6
                ]
                [ column
                    [ width fill
                    , spacing 6
                    ]
                    selected
                ]
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
