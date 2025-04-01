module Style exposing (colourScheme)

import Element


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
            , red = 169
            , green = 172
            , blue = 171
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
