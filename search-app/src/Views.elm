module Views exposing (view)

import Element exposing (Element, alignRight, centerX, column, el, fill, fillPortion, height, layout, maximum, none, padding, paddingXY, pointer, px, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Events as Events exposing (onClick)
import Element.Font as Font
import Element.Input as Input exposing (placeholder)
import Facets exposing (viewFacets)
import Helpers exposing (onEnter, viewMaybe)
import Html exposing (Html)
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (PaginationBlock, RecordTypeFilters(..), SearchBody, SearchTypesBlock)
import Request exposing (Response(..))
import Results exposing (resultView)
import Route exposing (extractPageNumberFromUrl)
import Style exposing (colourScheme)
import Url


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
                (mainFilterList (.resultType model.currentQueryArgs) body.types)
            , row
                [ width fill
                , height fill
                ]
                [ column
                    [ width (fill |> maximum 500)
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
                    [ width fill
                    , height fill
                    , padding 20
                    , spacing 20
                    ]
                    [ row
                        [ width fill ]
                        [ column
                            [ width fill
                            , spacing 16
                            ]
                            (List.map resultView body.results)
                        ]
                    , viewPagination model.gotoPageValue body.pagination
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


viewResultsControls : SearchBody -> Element Msg
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
                , onPress = Just UserClickedClearSearch
                }
            ]
        ]


viewPagination : String -> PaginationBlock -> Element Msg
viewPagination gotoPageValue pagination =
    let
        nextEl =
            case pagination.next of
                Just nextLink ->
                    let
                        pageNum =
                            Url.fromString nextLink
                                |> Maybe.andThen extractPageNumberFromUrl
                                |> Maybe.withDefault 1
                    in
                    el
                        [ Font.color colourScheme.lightBlue
                        , onClick (UserClickedPaginationLink pageNum)
                        , pointer
                        ]
                        (text "Next ›")

                Nothing ->
                    el [ Font.color colourScheme.midGrey ] (text "Next ›")

        previousEl =
            case pagination.previous of
                Just prevLink ->
                    let
                        pageNum =
                            Url.fromString prevLink
                                |> Maybe.andThen extractPageNumberFromUrl
                                |> Maybe.withDefault 1
                    in
                    el
                        [ Font.color colourScheme.lightBlue
                        , onClick (UserClickedPaginationLink pageNum)
                        , pointer
                        ]
                        (text "‹ Previous")

                Nothing ->
                    el [ Font.color colourScheme.midGrey ] (text "‹ Previous")

        lastPageNum =
            if pagination.numPages > 0 then
                pagination.numPages

            else
                1
    in
    row
        [ width fill
        , spacing 10
        , paddingXY 0 20
        , Font.size 18
        ]
        [ column
            []
            [ row
                [ spacing 18 ]
                [ el
                    []
                    (text ("Page " ++ String.fromInt pagination.currentPage ++ " of " ++ String.fromInt lastPageNum ++ " pages"))
                , text " | "
                , el
                    [ Font.color colourScheme.lightBlue
                    , onClick (UserClickedPaginationLink 1)
                    , pointer
                    ]
                    (text "« First")
                , previousEl
                , nextEl
                , el
                    [ Font.color colourScheme.lightBlue
                    , onClick (UserClickedPaginationLink lastPageNum)
                    , pointer
                    ]
                    (text "Last »")
                , text " | "
                ]
            ]
        , column
            []
            [ row
                [ width fill ]
                [ Input.text
                    [ Events.onLoseFocus (UserSubmittedPageGoto pagination.numPages)
                    , onEnter (UserSubmittedPageGoto pagination.numPages)
                    , spacing 10
                    , width (px 80)
                    ]
                    { label = Input.labelLeft [] (text "Go to page:")
                    , onChange = UserEnteredTextIntoPageGotoBox pagination.numPages
                    , placeholder = Nothing
                    , text = gotoPageValue
                    }
                ]
            ]
        ]
