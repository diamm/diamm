module Facets.CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg(..), update, updateCheckboxModel, viewCheckboxFacet)

import Element exposing (Element, alignRight, clip, column, el, fill, height, maximum, none, padding, paddingXY, pointer, px, row, scrollbarX, scrollbarY, spacing, text, width)
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Element.Input as Input exposing (labelHidden)
import RecordTypes exposing (FacetItem)
import Set exposing (Set)
import Style exposing (colourScheme)


type CheckBoxFacetMsg
    = NoOp
    | OnSelect FacetItem
    | OnRemoveItem FacetItem
    | OnTextInput String
    | OnToggleHide
    | OnClear


type alias CheckBoxFacetModel =
    { id : String
    , available : List FacetItem
    , allOptions : List FacetItem
    , selected : List FacetItem
    , filterText : Maybe String
    , bodyHidden : Bool
    }


updateCheckboxModel :
    { identifier : String
    , available : List FacetItem
    , selected : List FacetItem
    , bodyHidden : Bool
    }
    -> CheckBoxFacetModel
updateCheckboxModel cfg =
    let
        viewBody =
            cfg.bodyHidden && List.isEmpty cfg.selected
    in
    { id = cfg.identifier
    , available = cfg.available
    , allOptions = cfg.available -- holds a list of all the options so that we can reset the available ones from the whole list.
    , selected = cfg.selected
    , filterText = Nothing
    , bodyHidden = viewBody
    }


update : CheckBoxFacetMsg -> CheckBoxFacetModel -> ( CheckBoxFacetModel, Cmd CheckBoxFacetMsg )
update msg model =
    case msg of
        OnSelect value ->
            ( { model | selected = value :: model.selected }, Cmd.none )

        OnRemoveItem checkedItem ->
            let
                newSelected =
                    List.filter (\it -> it.value /= checkedItem.value) model.selected
            in
            ( { model | selected = newSelected }, Cmd.none )

        OnTextInput filterText ->
            let
                ( ft, av ) =
                    if String.isEmpty filterText then
                        ( Nothing, model.allOptions )

                    else
                        ( Just filterText, List.filter (\it -> String.contains (String.toLower filterText) (String.toLower it.value)) model.available )
            in
            ( { model | filterText = ft, available = av }, Cmd.none )

        OnClear ->
            ( { model
                | selected = []
                , filterText = Nothing
                , available = model.allOptions
              }
            , Cmd.none
            )

        OnToggleHide ->
            ( { model | bodyHidden = not model.bodyHidden }, Cmd.none )

        NoOp ->
            ( model, Cmd.none )


viewCheckboxFacet : String -> CheckBoxFacetModel -> Element CheckBoxFacetMsg
viewCheckboxFacet title facetModel =
    let
        showHideLabel =
            if facetModel.bodyHidden then
                "Show"

            else
                "Hide"

        facetBody =
            if facetModel.bodyHidden == False then
                let
                    selectedValues =
                        List.map .value facetModel.selected
                            |> Set.fromList

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
                        , height (px 300)
                        , Border.innerShadow { offset = ( 1, 1 ), size = 0, blur = 6, color = colourScheme.lightGrey }
                        , spacing 10
                        , padding 10
                        ]
                        (List.map (viewFacetItemCheckbox selectedValues) facetModel.available)
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


viewFacetItemCheckbox : Set String -> FacetItem -> Element CheckBoxFacetMsg
viewFacetItemCheckbox selected facetItem =
    let
        isChecked =
            Set.member facetItem.value selected

        checkedMsg item checkState =
            if checkState then
                OnSelect item

            else
                OnRemoveItem item
    in
    row
        [ width fill ]
        [ Input.checkbox
            [ spacing 12 ]
            { onChange = checkedMsg facetItem
            , icon = Input.defaultCheckbox
            , checked = isChecked
            , label =
                Input.labelRight
                    []
                    (text (facetItem.value ++ " (" ++ String.fromInt facetItem.count ++ ")"))
            }
        ]
