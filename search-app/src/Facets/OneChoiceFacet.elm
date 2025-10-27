module Facets.OneChoiceFacet exposing (OneChoiceFacetModel, OneChoiceFacetMsg(..), update, updateOneChoiceModel, viewOneChoiceFacet)

import Element exposing (Element, alignRight, clip, column, el, fill, height, maximum, none, padding, paddingXY, pointer, row, scrollbarX, scrollbarY, shrink, spacing, text, width)
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Element.Input as Input exposing (Option, labelHidden)
import List.Extra as LE
import Maybe.Extra as ME
import RecordTypes exposing (FacetItem)
import Style exposing (colourScheme)


type OneChoiceFacetMsg
    = NoOp
    | OnSelect FacetItem
    | OnRemoveItem FacetItem
    | OnTextInput String
    | OnToggleHide
    | OnClear


type alias OneChoiceFacetModel =
    { id : String
    , available : List FacetItem
    , allOptions : List FacetItem
    , selected : Maybe FacetItem
    , bodyHidden : Bool
    , filterText : Maybe String
    }


updateOneChoiceModel :
    { identifier : String
    , available : List FacetItem
    , selected : Maybe FacetItem
    , bodyHidden : Bool
    }
    -> OneChoiceFacetModel
updateOneChoiceModel cfg =
    let
        matchSelectedWithAvailable =
            Maybe.map
                (\s ->
                    List.filter (\v -> s.value == v.value) cfg.available
                        |> List.head
                )
                cfg.selected
                |> ME.join

        viewBody =
            cfg.bodyHidden && ME.isNothing cfg.selected
    in
    { id = cfg.identifier
    , available = cfg.available
    , allOptions = cfg.available
    , selected = matchSelectedWithAvailable
    , bodyHidden = viewBody
    , filterText = Nothing
    }


update : OneChoiceFacetMsg -> OneChoiceFacetModel -> ( OneChoiceFacetModel, Cmd OneChoiceFacetMsg )
update msg model =
    case msg of
        NoOp ->
            ( model, Cmd.none )

        OnSelect item ->
            ( { model
                | selected = Just item
              }
            , Cmd.none
            )

        OnRemoveItem _ ->
            ( model, Cmd.none )

        OnTextInput filterText ->
            let
                ( ft, av ) =
                    if String.isEmpty filterText then
                        ( Nothing, model.allOptions )

                    else
                        ( Just filterText, List.filter (\it -> String.contains (String.toLower filterText) (String.toLower it.value)) model.available )
            in
            ( { model | filterText = ft, available = av }, Cmd.none )

        OnToggleHide ->
            ( { model
                | bodyHidden = not model.bodyHidden
              }
            , Cmd.none
            )

        OnClear ->
            ( { model | selected = Nothing }, Cmd.none )


viewOneChoiceFacet :
    { title : String
    , optionTitleMap : List ( String, String )
    }
    -> OneChoiceFacetModel
    -> Element OneChoiceFacetMsg
viewOneChoiceFacet { title, optionTitleMap } facetModel =
    let
        showHideLabel =
            if facetModel.bodyHidden then
                "Show"

            else
                "Hide"

        facetBody =
            if facetModel.bodyHidden == False then
                let
                    filterControl =
                        if List.length facetModel.allOptions > 20 then
                            row
                                [ width fill
                                ]
                                [ Input.text
                                    []
                                    { label = labelHidden "filter"
                                    , onChange = OnTextInput
                                    , text = Maybe.withDefault "" facetModel.filterText
                                    , placeholder = Just (Input.placeholder [] (el [] (text "Filter options")))
                                    }
                                ]

                        else
                            none
                in
                [ filterControl
                , row
                    [ width fill
                    ]
                    [ column
                        [ width (fill |> maximum 340)
                        , clip
                        , scrollbarX
                        , scrollbarY
                        , height (shrink |> maximum 300)
                        , padding 10
                        , Border.innerShadow { offset = ( 1, 1 ), size = 0, blur = 6, color = colourScheme.lightGrey }
                        ]
                        [ Input.radio
                            [ spacing 10 ]
                            { onChange = OnSelect
                            , options = List.map (createOption optionTitleMap) facetModel.available
                            , selected = facetModel.selected
                            , label = Input.labelHidden "select"
                            }
                        ]
                    ]
                ]

            else
                [ none ]
    in
    row
        [ width fill
        ]
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


createOption : List ( String, String ) -> FacetItem -> Option FacetItem msg
createOption optionTitleMap inp =
    let
        label =
            LE.findMap
                (\( v, t ) ->
                    if v == inp.value then
                        Just t

                    else
                        Nothing
                )
                optionTitleMap
                |> Maybe.withDefault inp.value

        count =
            String.fromInt inp.count
    in
    Input.option inp (text (label ++ " (" ++ count ++ ")"))
