module Update exposing (..)

import Model exposing (Model)
import Msg exposing (Msg(..))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ServerRespondedWithSearchData (Ok ( _, response )) ->
            let
                _ =
                    Debug.log "response" response
            in
            ( model, Cmd.none )

        ServerRespondedWithSearchData (Err error) ->
            ( model, Cmd.none )

        NothingHappened ->
            ( model, Cmd.none )
