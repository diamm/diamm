module Facets.CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg(..), initialCheckboxModel, update, viewCheckboxFacet)

import Element exposing (Element, alignRight, clipY, column, el, fill, height, padding, pointer, px, row, scrollbarY, spacing, text, width)
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Element.Input as Input
import RecordTypes exposing (FacetItem)
import Set exposing (Set)
import Style exposing (colourScheme)


type CheckBoxFacetMsg
    = NoOp
    | OnSelect FacetItem
    | OnRemoveItem FacetItem
    | OnClear


type alias CheckBoxFacetModel =
    { id : String
    , available : List FacetItem
    , selected : List FacetItem
    }


initialCheckboxModel : { identifier : String, available : List FacetItem } -> CheckBoxFacetModel
initialCheckboxModel cfg =
    { id = cfg.identifier
    , available = cfg.available
    , selected = []
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

        OnClear ->
            ( { model | selected = [] }, Cmd.none )

        NoOp ->
            ( model, Cmd.none )


viewCheckboxFacet : String -> CheckBoxFacetModel -> Element CheckBoxFacetMsg
viewCheckboxFacet title facetModel =
    let
        selectedValues =
            List.map .value facetModel.selected
                |> Set.fromList
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
                [ width fill
                , padding 10
                ]
                [ column
                    [ width fill
                    , clipY
                    , scrollbarY
                    , height (px 300)
                    , Border.innerShadow { offset = ( 1, 1 ), size = 0, blur = 6, color = colourScheme.lightGrey }
                    , spacing 10
                    , padding 10
                    ]
                    (List.map (viewFacetItemCheckbox selectedValues) facetModel.available)
                ]
            ]
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
        []
        [ Input.checkbox
            [ spacing 12 ]
            { onChange = checkedMsg facetItem
            , icon = Input.defaultCheckbox
            , checked = isChecked
            , label =
                Input.labelRight
                    []
                    (text facetItem.value)
            }
        ]
