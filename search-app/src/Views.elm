module Views exposing (..)

import Element exposing (Element, alignBottom, alignRight, centerX, column, el, fill, fillPortion, height, layout, none, padding, pointer, px, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Events exposing (onClick)
import Element.Font as Font
import Element.Input as Input exposing (placeholder)
import Facets exposing (FacetModel, viewFacets)
import Helpers exposing (onEnter, viewIf, viewMaybe)
import Html exposing (Html)
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (FacetBlock, FacetItem, RecordTypeFilters(..), SearchBody, SearchTypesBlock)
import Request exposing (Response(..))
import Results exposing (resultView)
import Style exposing (colourScheme)


view : Model -> Html Msg
view model =
    layout
        [ Font.family
            [ Font.typeface "Rubik"
            ]
        , Font.size 16
        , width fill
        , height fill
        ]
        (responseRouter model)


responseRouter : Model -> Element Msg
responseRouter model =
    case model.response of
        Response searchBody ->
            searchView model searchBody

        _ ->
            none


searchView : Model -> SearchBody -> Element Msg
searchView model body =
    row
        [ width fill
        , height fill
        ]
        [ column
            [ width fill
            , height fill
            ]
            [ row
                [ width fill
                , height (px 82)
                , Background.color colourScheme.lightGrey
                ]
                [ Input.text
                    [ width (px 800)
                    , centerX
                    , Font.size 21
                    , Font.medium
                    , onEnter UserPressedEnterOnQueryBox
                    ]
                    { onChange = UserEnteredTextIntoQueryBox
                    , text = Maybe.withDefault "" (.keywordQuery model.currentQueryArgs)
                    , placeholder = Just (placeholder [] (text "Search"))
                    , label = Input.labelHidden "Search input"
                    }
                ]
            , row
                [ width fill
                , height (px 45)
                , Border.widthEach { top = 0, bottom = 2, left = 0, right = 0 }
                , Border.color colourScheme.lightGrey
                , Font.size 16
                , spacing 15
                ]
                (mainFilterList model.activeRecordType body.types)
            , row
                [ width fill
                , height fill
                ]
                [ column
                    [ width (fillPortion 1)
                    , height fill
                    , Border.widthEach { top = 0, bottom = 0, left = 0, right = 2 }
                    , Border.color colourScheme.lightGrey
                    , padding 12
                    , spacing 10
                    ]
                    [ viewResultsControls body
                    , viewMaybe viewFacets model.facets
                    ]
                , column
                    [ width (fillPortion 3)
                    , height fill
                    , padding 20
                    ]
                    [ row
                        [ width fill ]
                        [ column
                            [ width fill
                            , spacing 16
                            ]
                            (List.map resultView body.results)
                        ]
                    , row
                        []
                        []
                    ]
                ]
            ]
        ]


mainFilterList : RecordTypeFilters -> SearchTypesBlock -> List (Element Msg)
mainFilterList currentSelection searchTypes =
    [ el
        [ centerX
        , Font.bold
        ]
        (text "Filter:")
    , viewFilter { currentSelection = currentSelection, thisMenu = ShowAllRecords, count = 0, label = "Show All" }
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = ArchiveRecords, count = f, label = "Archive" }) searchTypes.archive
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = CompositionRecords, count = f, label = "Composition" }) searchTypes.composition
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = OrganizationRecords, count = f, label = "Organization" }) searchTypes.organization
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = PersonRecords, count = f, label = "Person" }) searchTypes.person
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = SetRecords, count = f, label = "Set" }) searchTypes.set
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = SourceRecords, count = f, label = "Source" }) searchTypes.source
    , viewMaybe (\f -> viewFilter { currentSelection = currentSelection, thisMenu = SourcesWithImagesRecords, count = f, label = "Sources With Images" }) searchTypes.sourceWithImages
    ]


viewFilter :
    { currentSelection : RecordTypeFilters
    , thisMenu : RecordTypeFilters
    , label : String
    , count : Int
    }
    -> Element Msg
viewFilter cfg =
    let
        countLabel =
            if cfg.count > 0 then
                " (" ++ String.fromInt cfg.count ++ ")"

            else
                ""

        selectedFont =
            if cfg.currentSelection == cfg.thisMenu then
                Font.semiBold

            else
                Font.regular
    in
    el
        [ centerX
        , onClick (UserClickedRecordTypeFilter cfg.thisMenu)
        , pointer
        , Font.color colourScheme.red
        , selectedFont
        ]
        (text (cfg.label ++ countLabel))


viewResultsControls : SearchBody -> Element msg
viewResultsControls body =
    row
        [ width fill ]
        [ column
            [ width fill ]
            [ el [ Font.bold ] (text (String.fromInt body.count ++ " results found.")) ]
        , column
            [ width fill ]
            [ Input.button
                [ Background.color colourScheme.red
                , Font.color colourScheme.white
                , Border.rounded 3
                , padding 10
                , alignRight
                ]
                { label = text "Clear Search"
                , onPress = Nothing
                }
            ]
        ]
