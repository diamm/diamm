module Main exposing (main)

import Browser
import Browser.Navigation as Nav
import Config as C
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (searchBodyDecoder)
import Request exposing (createRequest, serverUrl)
import Update
import Url exposing (Url)
import Views


type alias Flags =
    {}


main : Program Flags Model Msg
main =
    Browser.element
        { init = init

        --, onUrlChange = Msg.ClientChangedUrl
        --, onUrlRequest = Msg.UserRequestedUrlChange
        , subscriptions = \_ -> Sub.none
        , update = Update.update
        , view = Views.view
        }


init : Flags -> ( Model, Cmd Msg )
init flags =
    let
        model =
            Model.init

        initialRequest =
            serverUrl [ "search" ] []
                |> createRequest ServerRespondedWithSearchData searchBodyDecoder
    in
    ( model, initialRequest )
