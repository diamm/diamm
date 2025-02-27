module Style exposing (..)

import Element


colourScheme :
    { black : Element.Color
    , red : Element.Color
    , grey : Element.Color
    , lightGrey : Element.Color
    , darkBlue : Element.Color
    , lightBlue : Element.Color
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
    }
