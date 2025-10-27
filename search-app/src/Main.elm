module Main exposing (Flags, main)

import Browser
import Model exposing (Model)
import Msg exposing (Msg(..))
import Ports exposing (onUrlChange)
import RecordTypes exposing (searchBodyDecoder)
import Request exposing (createRequest, serverUrl)
import Route exposing (Route(..), buildQueryParameters, defaultQueryArgs, defaultSearchUrl, locationHrefToRoute, parseUrl)
import Update
import Url
import Views


type alias Flags =
    { initialUrl : String }


main : Program Flags Model Msg
main =
    Browser.element
        { init = init
        , subscriptions = subscriptions
        , update = Update.update
        , view = Views.view
        }


init : Flags -> ( Model, Cmd Msg )
init flags =
    let
        initialRoute =
            Url.fromString flags.initialUrl
                |> Maybe.withDefault defaultSearchUrl
                |> parseUrl
                |> Maybe.withDefault UnknownRoute

        initialQueryParams =
            case initialRoute of
                SearchPageRoute queryArgs ->
                    queryArgs

                _ ->
                    defaultQueryArgs

        model =
            Model.init initialQueryParams

        apiRequestQueryParameters =
            buildQueryParameters initialQueryParams

        initialRequest =
            serverUrl [ "search" ] apiRequestQueryParameters
                |> createRequest ServerRespondedWithSearchData searchBodyDecoder
    in
    ( model, initialRequest )


subscriptions : Model -> Sub Msg
subscriptions model =
    onUrlChange (locationHrefToRoute >> ClientChangedUrl)
