module Request exposing (..)

import Config as C
import Http exposing (Expect)
import Http.Detailed
import Json.Decode exposing (Decoder)
import RecordTypes exposing (SearchBody)
import Url.Builder exposing (QueryParameter)


type Response
    = Loading (Maybe SearchBody)
    | Response SearchBody
    | Error (Http.Detailed.Error String)
    | NoResponseToShow


createRequest :
    (Result (Http.Detailed.Error String) ( Http.Metadata, a ) -> msg)
    -> Decoder a
    -> String
    -> Cmd msg
createRequest responseMsg responseDecoder url =
    createRequestWithAcceptAndExpect "application/json" (Http.Detailed.expectJson responseMsg responseDecoder) url


createRequestWithAcceptAndExpect : String -> Expect msg -> String -> Cmd msg
createRequestWithAcceptAndExpect accept expect url =
    Http.request
        { method = "GET"
        , headers =
            [ Http.header "Accept" accept
            ]
        , url = url
        , body = Http.emptyBody
        , expect = expect
        , timeout = Nothing
        , tracker = Nothing
        }


serverUrl : List String -> List QueryParameter -> String
serverUrl pathSegments queryParameters =
    let
        cleanedSegments =
            List.map
                (\segment ->
                    if String.startsWith "/" segment then
                        String.dropLeft 1 segment

                    else
                        segment
                )
                pathSegments
    in
    Url.Builder.crossOrigin C.serverUrl cleanedSegments queryParameters
