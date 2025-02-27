module Main exposing (main)

import Browser
import Browser.Navigation as Nav
import Model exposing (Model)
import Msg exposing (Msg)
import Update
import Url exposing (Url)
import Views


type alias Flags =
    {}


main : Program Flags Model Msg
main =
    Browser.application
        { init = init
        , onUrlChange = Msg.ClientChangedUrl
        , onUrlRequest = Msg.UserRequestedUrlChange
        , subscriptions = \_ -> Sub.none
        , update = Update.update
        , view = Views.view
        }


init : Flags -> Url -> Nav.Key -> ( Model, Cmd Msg )
init flags initialUrl key =
    let
        model =
            Model.init
    in
    ( model, Cmd.none )
