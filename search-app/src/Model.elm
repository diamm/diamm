module Model exposing (..)

import Request exposing (Response(..))


type alias Model =
    { response : Response }


init : Model
init =
    { response = NoResponseToShow }
