module Facets.RangeFacet exposing (RangeFacetModel, RangeFacetMsg(..), initRangeModel, update, viewRangeFacet)

import Element exposing (Element, alignRight, column, el, fill, html, none, paddingXY, pointer, row, spacing, text, width)
import Element.Events as Events
import Element.Font as Font
import Facets.Slider.DoubleSlider as DoubleSlider
import RecordTypes exposing (RangeFacetItem)
import Style exposing (colourScheme)


type RangeFacetMsg
    = NoOp
    | OnLowSliderChange Float
    | OnHighSliderChange Float
    | OnToggleHide
    | OnClear


type alias RangeFacetModel =
    { id : String
    , doubleSlider : DoubleSlider.DoubleSlider RangeFacetMsg
    , maxValue : Float
    , minValue : Float
    , bodyHidden : Bool
    , selected : Maybe ( Float, Float )
    }


initRangeModel :
    { identifier : String
    , facetData : RangeFacetItem
    , selected : Maybe ( Float, Float )
    }
    -> RangeFacetModel
initRangeModel { identifier, facetData, selected } =
    let
        defaultLow =
            List.filterMap (\{ value } -> String.toFloat value) facetData.buckets
                |> List.minimum
                |> Maybe.withDefault (toFloat facetData.min)

        facetLow =
            case selected of
                Nothing ->
                    defaultLow

                Just ( l, _ ) ->
                    if l == -1 then
                        defaultLow

                    else
                        l

        defaultHigh =
            List.filterMap (\{ value } -> String.toFloat value) facetData.buckets
                |> List.maximum
                |> Maybe.withDefault (toFloat facetData.max)

        facetHigh =
            case selected of
                Nothing ->
                    defaultHigh

                Just ( _, h ) ->
                    if h == -1 then
                        defaultHigh

                    else
                        h

        stepWidth =
            20

        quantizedMax =
            (toFloat facetData.max / toFloat stepWidth)
                |> round
                |> (*) stepWidth
                |> toFloat
    in
    { id = identifier
    , maxValue = quantizedMax
    , minValue = toFloat facetData.min
    , doubleSlider =
        DoubleSlider.init
            { min = toFloat facetData.min
            , max = quantizedMax
            , lowValue = facetLow
            , highValue = facetHigh
            , step = 20
            , onHighChange = OnHighSliderChange
            , onLowChange = OnLowSliderChange
            }
    , bodyHidden = False
    , selected = selected
    }


update : RangeFacetMsg -> RangeFacetModel -> ( RangeFacetModel, Cmd RangeFacetMsg )
update msg model =
    case msg of
        NoOp ->
            ( model, Cmd.none )

        OnLowSliderChange num ->
            let
                newSlider =
                    DoubleSlider.updateLowValue num model.doubleSlider

                lowerNumber =
                    if num <= model.minValue then
                        -1

                    else if num > model.maxValue then
                        model.maxValue

                    else
                        num

                selectedTuple =
                    case model.selected of
                        Nothing ->
                            Just ( lowerNumber, -1 )

                        Just ( _, h ) ->
                            Just ( lowerNumber, h )
            in
            ( { model
                | doubleSlider = newSlider
                , selected = selectedTuple
              }
            , Cmd.none
            )

        OnHighSliderChange num ->
            let
                newSlider =
                    DoubleSlider.updateHighValue num model.doubleSlider

                upperNumber =
                    if num >= model.maxValue then
                        -1

                    else if num <= model.minValue then
                        model.minValue

                    else
                        num

                selectedTuple =
                    case model.selected of
                        Nothing ->
                            Just ( -1, upperNumber )

                        Just ( l, _ ) ->
                            Just ( l, upperNumber )
            in
            ( { model
                | doubleSlider = newSlider
                , selected = selectedTuple
              }
            , Cmd.none
            )

        OnToggleHide ->
            ( { model
                | bodyHidden = not model.bodyHidden
              }
            , Cmd.none
            )

        OnClear ->
            let
                resetSlider =
                    DoubleSlider.updateHighValue model.maxValue model.doubleSlider
                        |> DoubleSlider.updateLowValue model.minValue
            in
            ( { model
                | selected = Nothing
                , doubleSlider = resetSlider
              }
            , Cmd.none
            )


viewRangeFacet : { title : String } -> RangeFacetModel -> Element RangeFacetMsg
viewRangeFacet { title } model =
    let
        showHideLabel =
            if model.bodyHidden then
                "Show"

            else
                "Hide"

        facetBody =
            if model.bodyHidden then
                [ none ]

            else
                [ row
                    [ width fill ]
                    [ column
                        [ width fill ]
                        [ DoubleSlider.view model.doubleSlider
                            |> html
                        ]
                    ]
                ]
    in
    row
        [ width fill ]
        [ column
            [ width fill
            , spacing 10
            ]
            (row
                [ width fill
                , paddingXY 0 5
                , spacing 5
                ]
                [ el [ Font.medium ] (text title)
                , el
                    [ Events.onClick OnToggleHide
                    , Font.color colourScheme.red
                    , pointer
                    ]
                    (text showHideLabel)
                , el
                    [ alignRight
                    , Events.onClick OnClear
                    , Font.color colourScheme.red
                    , pointer
                    ]
                    (text "Clear selection")
                ]
                :: facetBody
            )
        ]
