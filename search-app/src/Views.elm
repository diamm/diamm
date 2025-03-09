module Views exposing (..)

import Browser
import Element exposing (Element, alignBottom, alignRight, centerX, column, el, fill, fillPortion, height, htmlAttribute, layout, none, padding, px, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Element.Input as Input
import Helpers exposing (viewIf)
import Html exposing (Html)
import Html.Attributes as HA
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (FacetItem, SearchBody, SearchTypesBlock)
import Request exposing (Response(..))
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
            searchView searchBody

        _ ->
            none


searchView : SearchBody -> Element Msg
searchView body =
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
                    [ width (px 600)
                    , centerX
                    ]
                    { onChange = \_ -> NothingHappened
                    , text = ""
                    , placeholder = Nothing
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
                (mainFilterList body.types)
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
                    ]
                    [ viewResultsControls body
                    , row
                        [ width fill
                        , Border.widthEach { top = 0, bottom = 1, left = 0, right = 0 }
                        , Border.color colourScheme.lightGrey
                        ]
                        [ el
                            [ Font.bold ]
                            (text "Filter Results")
                        ]
                    , viewFacets body
                    ]
                , column
                    [ width (fillPortion 4)
                    , height fill
                    ]
                    [ el [ alignBottom ] (text "World") ]
                ]
            ]
        ]


mainFilterList : SearchTypesBlock -> List (Element Msg)
mainFilterList searchTypes =
    [ el
        [ centerX
        , Font.bold
        ]
        (text "Filter:")
    , el
        [ centerX
        , Font.bold
        ]
        (text "Show all")
    , el
        [ centerX ]
        (text ("Archive (" ++ String.fromInt searchTypes.archive ++ ")"))
    , el
        [ centerX ]
        (text ("Composition (" ++ String.fromInt searchTypes.composition ++ ")"))
    , el
        [ centerX ]
        (text ("Organization (" ++ String.fromInt searchTypes.organization ++ ")"))
    , el
        [ centerX ]
        (text ("Person (" ++ String.fromInt searchTypes.person ++ ")"))
    , el
        [ centerX ]
        (text ("Set (" ++ String.fromInt searchTypes.set ++ ")"))
    , el
        [ centerX ]
        (text ("Source (" ++ String.fromInt searchTypes.source ++ ")"))
    , el
        [ centerX ]
        (text ("Sources With Images (" ++ String.fromInt searchTypes.sourceWithImages ++ ")"))
    ]


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


viewFacets : SearchBody -> Element msg
viewFacets body =
    let
        facets =
            body.facets

        cityFacet =
            viewIf (viewCityFacet facets.city) (List.length facets.city > 0)

        anonymousFacet =
            viewIf (viewAnonymousFacet facets.anonymous) (List.length facets.anonymous > 0)

        genresFacet =
            viewIf (viewGenresFacet facets.genres) (List.length facets.genres > 0)
    in
    row
        []
        [ column
            []
            [ anonymousFacet
            , genresFacet
            , cityFacet
            ]
        ]


viewCityFacet : List FacetItem -> Element msg
viewCityFacet items =
    row
        [ width fill ]
        [ text "City facet" ]


viewAnonymousFacet : List FacetItem -> Element msg
viewAnonymousFacet items =
    row
        [ width fill ]
        [ text "Anonymous facet" ]


viewGenresFacet : List FacetItem -> Element msg
viewGenresFacet items =
    row
        [ width fill ]
        [ text "Genres facet" ]
