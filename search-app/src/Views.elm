module Views exposing (view)

import Element exposing (Element, alignLeft, alignRight, alignTop, centerX, column, el, fill, height, layout, maximum, none, padding, paddingXY, paragraph, pointer, px, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Events as Events exposing (onClick)
import Element.Font as Font
import Element.Input as Input exposing (placeholder)
import Facets exposing (viewFacets)
import Helpers exposing (onEnter, viewIf, viewMaybe)
import Html exposing (Html)
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (PaginationBlock, RecordTypeFilters(..), SearchBody, SearchTypesBlock, parseResultTypeToString)
import Request exposing (Response(..))
import Results exposing (resultView)
import Route exposing (extractPageNumberFromUrl)
import String.Extra as SE
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
                , paddingXY 20 0
                ]
                [ Input.text
                    [ width (px 1000)
                    , alignLeft
                    , Font.size 21
                    , Font.medium
                    , onEnter UserPressedEnterOnQueryBox
                    ]
                    { onChange = UserEnteredTextIntoQueryBox
                    , text = Maybe.withDefault "" (.keywordQuery model.currentQueryArgs)
                    , placeholder = Just (placeholder [] (text "Keyword search"))
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
                , paddingXY 20 0
                ]
                (mainFilterList (.resultType model.currentQueryArgs) body.types)
            , row
                [ width fill
                , height fill
                ]
                [ column
                    [ width (fill |> maximum 400)
                    , height fill
                    , Border.widthEach { top = 0, bottom = 0, left = 0, right = 2 }
                    , Border.color colourScheme.lightGrey
                    , spacing 10
                    , padding 20
                    , alignTop
                    ]
                    [ viewFacets model.facets
                    ]
                , column
                    [ width (fill |> maximum 900)
                    , height fill
                    , alignTop
                    , padding 20
                    , spacing 20
                    ]
                    [ row
                        [ width fill ]
                        [ column
                            [ width fill
                            , spacing 20
                            ]
                            (List.map resultView body.results)
                        ]
                    , viewPagination model.gotoPageValue body.pagination
                    ]
                , column
                    [ width (px 400)
                    , height fill
                    , alignTop
                    , padding 12
                    , spacing 20
                    , Border.widthEach { top = 0, bottom = 0, left = 2, right = 0 }
                    , Border.color colourScheme.lightGrey
                    ]
                    [ viewResultsControls body
                    , viewSelectedResults model
                    ]
                ]
            ]
        ]


mainFilterList : RecordTypeFilters -> SearchTypesBlock -> List (Element Msg)
mainFilterList currentSelection searchTypes =
    [ el
        [ alignLeft
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
        [ alignLeft
        , onClick (UserClickedRecordTypeFilter cfg.thisMenu)
        , pointer
        , Font.color colourScheme.red
        , selectedFont
        ]
        (text (cfg.label ++ countLabel))


viewResultsControls : SearchBody -> Element Msg
viewResultsControls body =
    row
        [ width fill
        , spacing 20
        ]
        [ column
            [ width fill ]
            [ el
                [ Font.medium
                , Font.size 24
                ]
                (text (String.fromInt body.count ++ " results found."))
            ]
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


viewSelectedResults : Model -> Element Msg
viewSelectedResults model =
    let
        cqa =
            model.currentQueryArgs

        selectedResultType =
            parseResultTypeToString cqa.resultType
                |> String.split "_"
                |> List.map SE.toTitleCase
                |> String.join " "

        resultType =
            row [ width fill ]
                [ paragraph
                    [ width fill ]
                    [ el [ Font.medium ] (text "Result type: "), text selectedResultType ]
                ]

        notations =
            selectedResultsTemplate "Notations" cqa.notations

        sourceTypes =
            selectedResultsTemplate "Source types" cqa.sourceTypes

        sourceComposers =
            selectedResultsTemplate "Source composers" cqa.sourceComposers

        hasInventory =
            selectedResultsTemplate "Has inventory" cqa.hasInventory

        originalFormat =
            selectedResultsTemplate "Original format" cqa.originalFormat

        currentState =
            selectedResultsTemplate "Current state" cqa.currentState

        compGenres =
            selectedResultsTemplate "Genres" cqa.genres

        compComposers =
            selectedResultsTemplate "Composition composers" cqa.composers

        compAnon =
            selectedResultsTemplate "Anonymous composer" cqa.anonymous

        archCity =
            selectedResultsTemplate "Archive city" cqa.cities
    in
    row
        [ width fill
        , height fill
        , alignTop
        ]
        [ column
            [ width fill
            , alignTop
            , spacing 10
            ]
            [ row
                [ width fill
                , paddingXY 0 10
                , Font.semiBold
                , Border.widthEach { top = 0, left = 0, bottom = 2, right = 0 }
                , Border.color colourScheme.lightGrey
                ]
                [ text "Options selected" ]
            , resultType
            , sourceTypes
            , sourceComposers
            , notations
            , hasInventory
            , originalFormat
            , currentState
            , compGenres
            , compComposers
            , compAnon
            , archCity
            ]
        ]


selectedResultsTemplate : String -> List String -> Element Msg
selectedResultsTemplate title options =
    if List.isEmpty options then
        none

    else
        row
            [ width fill ]
            [ column
                [ width fill
                , spacing 10
                ]
                [ row
                    [ Font.medium ]
                    [ text title ]
                , row
                    [ width fill ]
                    [ String.join ", " options
                        |> text
                        |> List.singleton
                        |> paragraph []
                    ]
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
