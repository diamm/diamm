module Views exposing (..)

import Browser
import Element exposing (Element, alignBottom, centerX, column, el, fill, fillPortion, height, htmlAttribute, layout, none, px, row, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Element.Input as Input
import Html exposing (Html)
import Html.Attributes as HA
import Model exposing (Model)
import Msg exposing (Msg(..))
import Style exposing (colourScheme)


view : Model -> Html Msg
view model =
    layout
        [ Font.family
            [ Font.typeface "Rubik" ]
        , width fill
        , height fill
        ]
        (searchView model)


searchView : Model -> Element Msg
searchView model =
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
                ]
                [ el
                    [ centerX
                    , Font.size 16
                    , Font.bold
                    ]
                    (text "Filters")
                , el
                    []
                    (text "Show all")
                ]
            , row
                [ width fill
                , height fill
                ]
                [ column
                    [ width (fillPortion 1)
                    , height fill
                    , Border.widthEach { top = 0, bottom = 0, left = 0, right = 2 }
                    , Border.color colourScheme.lightGrey
                    ]
                    [ text "hello" ]
                , column
                    [ width (fillPortion 4)
                    , height fill
                    ]
                    [ el [ alignBottom ] (text "World") ]
                ]
            ]
        ]
