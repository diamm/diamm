module Style exposing (animatedLoader, colourScheme, spinnerSvg)

import Color exposing (toCssString)
import Element exposing (Attribute, Element, html)
import Simple.Animation as Animation exposing (Animation)
import Simple.Animation.Animated as Animated
import Simple.Animation.Property as P
import Svg exposing (defs, svg)
import Svg.Attributes exposing (d, fill, viewBox)


colourScheme :
    { black : Element.Color
    , red : Element.Color
    , grey : Element.Color
    , midGrey : Element.Color
    , lightGrey : Element.Color
    , darkBlue : Element.Color
    , lightBlue : Element.Color
    , white : Element.Color
    }
colourScheme =
    { black =
        Element.fromRgb255
            { alpha = 1
            , blue = 27
            , green = 27
            , red = 27
            }
    , red =
        Element.fromRgb255
            { alpha = 1
            , red = 221
            , green = 28
            , blue = 26
            }
    , grey =
        Element.fromRgb255
            { alpha = 1
            , red = 42
            , green = 44
            , blue = 43
            }
    , midGrey =
        Element.fromRgb255
            { alpha = 1
            , red = 100
            , green = 120
            , blue = 120
            }
    , lightGrey =
        Element.fromRgb255
            { alpha = 1
            , red = 221
            , green = 222
            , blue = 221
            }
    , darkBlue =
        Element.fromRgb255
            { alpha = 1
            , red = 9
            , green = 113
            , blue = 178
            }
    , lightBlue =
        Element.fromRgb255
            { alpha = 1
            , red = 20
            , green = 133
            , blue = 204
            }
    , white =
        Element.fromRgb255
            { alpha = 1
            , red = 255
            , green = 255
            , blue = 255
            }
    }


spinnerSvg : Element.Color -> Element msg
spinnerSvg color =
    let
        htColor =
            Element.toRgb color
                |> Color.fromRgba
    in
    html
        (svg [ viewBox "0 0 512 512" ]
            [ defs []
                [ Svg.style []
                    [ Svg.text ".fa-secondary{opacity:.4}" ]
                ]
            , Svg.path
                [ d "M478.71 364.58zm-22 6.11l-27.83-15.9a15.92 15.92 0 0 1-6.94-19.2A184 184 0 1 1 256 72c5.89 0 11.71.29 17.46.83-.74-.07-1.48-.15-2.23-.21-8.49-.69-15.23-7.31-15.23-15.83v-32a16 16 0 0 1 15.34-16C266.24 8.46 261.18 8 256 8 119 8 8 119 8 256s111 248 248 248c98 0 182.42-56.95 222.71-139.42-4.13 7.86-14.23 10.55-22 6.11z"
                , Svg.Attributes.class "fa-secondary"
                , fill (toCssString htColor)
                ]
                []
            , Svg.path
                [ d "M271.23 72.62c-8.49-.69-15.23-7.31-15.23-15.83V24.73c0-9.11 7.67-16.78 16.77-16.17C401.92 17.18 504 124.67 504 256a246 246 0 0 1-25 108.24c-4 8.17-14.37 11-22.26 6.45l-27.84-15.9c-7.41-4.23-9.83-13.35-6.2-21.07A182.53 182.53 0 0 0 440 256c0-96.49-74.27-175.63-168.77-183.38z"
                , Svg.Attributes.class "fa-primary"
                , fill (toCssString htColor)
                ]
                []
            ]
        )


animatedUi : (List (Attribute msg) -> children -> Element msg) -> Animation -> List (Attribute msg) -> children -> Element msg
animatedUi =
    Animated.ui
        { behindContent = Element.behindContent
        , html = Element.html
        , htmlAttribute = Element.htmlAttribute
        }


animatedEl : Animation -> List (Attribute msg) -> Element msg -> Element msg
animatedEl =
    animatedUi Element.el


animatedLoader : List (Attribute msg) -> Element msg -> Element msg
animatedLoader attrs loaderImage =
    animatedEl
        (Animation.fromTo
            { duration = 500
            , options =
                [ Animation.loop ]
            }
            [ P.rotate -360 ]
            []
        )
        attrs
        loaderImage
