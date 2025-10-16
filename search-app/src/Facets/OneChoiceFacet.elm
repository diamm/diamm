module Facets.OneChoiceFacet exposing (OneChoiceFacetModel, OneChoiceFacetMsg(..), update, updateOneChoiceModel, viewOneChoiceFacet)

import Element exposing (Element, alignRight, clip, column, el, fill, height, maximum, none, padding, paddingXY, pointer, px, row, spacing, text, width)
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Element.Input as Input exposing (Option)
import RecordTypes exposing (BooleanFacetItem)
import Style exposing (colourScheme)


type OneChoiceFacetMsg
    = NoOp
    | OnSelect BooleanFacetItem
    | OnRemoveItem BooleanFacetItem
    | OnToggleHide
    | OnClear


type alias OneChoiceFacetModel =
    { id : String
    , available : List BooleanFacetItem
    , selected : Maybe BooleanFacetItem
    , bodyHidden : Bool
    }


updateOneChoiceModel : { identifier : String, available : List BooleanFacetItem, selected : Maybe BooleanFacetItem, bodyHidden : Bool } -> OneChoiceFacetModel
updateOneChoiceModel cfg =
    { id = cfg.identifier
    , available = cfg.available
    , selected = cfg.selected
    , bodyHidden = cfg.bodyHidden
    }


update : OneChoiceFacetMsg -> OneChoiceFacetModel -> ( OneChoiceFacetModel, Cmd OneChoiceFacetMsg )
update msg model =
    case msg of
        NoOp ->
            ( model, Cmd.none )

        OnSelect item ->
            ( { model | selected = Just item }, Cmd.none )

        OnRemoveItem item ->
            ( model, Cmd.none )

        OnToggleHide ->
            ( { model | bodyHidden = not model.bodyHidden }, Cmd.none )

        OnClear ->
            ( { model | selected = Nothing }, Cmd.none )


viewOneChoiceFacet : String -> OneChoiceFacetModel -> Element OneChoiceFacetMsg
viewOneChoiceFacet title facetModel =
    let
        showHideLabel =
            if facetModel.bodyHidden then
                "Show"

            else
                "Hide"

        facetBody =
            if facetModel.bodyHidden == False then
                [ row
                    [ width fill
                    , padding 10
                    ]
                    [ column
                        [ width (fill |> maximum 440)
                        , clip
                        , height (px 100)
                        , Border.innerShadow { offset = ( 1, 1 ), size = 0, blur = 6, color = colourScheme.lightGrey }
                        , spacing 10
                        , padding 10
                        ]
                        [ Input.radio
                            []
                            { onChange = OnSelect
                            , options = List.map createOption facetModel.available
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
        , Border.widthEach { top = 1, left = 0, right = 0, bottom = 0 }
        , Border.color colourScheme.lightGrey
        ]
        [ column
            [ width fill
            , spacing 10
            , padding 10
            ]
            (row
                [ width fill
                , paddingXY 0 5
                , spacing 5
                ]
                [ el [ Font.semiBold ] (text title)
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
                    (text "Clear all")
                ]
                :: facetBody
            )
        ]


createOption : BooleanFacetItem -> Option BooleanFacetItem msg
createOption inp =
    let
        label =
            if inp.value then
                "True"

            else
                "False"

        count =
            String.fromInt inp.count
    in
    Input.option inp (text (label ++ " (" ++ count ++ ")"))
