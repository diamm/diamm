module Error exposing (..)

import Http.Detailed


type ErrorResponse
    = BadUrlResponse { label : String }
    | BadBodyResponse { label : String, description : String }
    | BadBodyEncodedResponse { label : String }
    | NotFoundResponse { label : String }
    | BadRequestResponse { label : String, description : String }
    | GoneResponse { label : String }
    | NotImplementedResponse { label : String }
    | OtherBadStatusResponse { label : String, description : String, statusCode : Int }
    | NetworkErrorResponse { label : String }
    | TimeoutErrorResponse { label : String }


createErrorMessage : Http.Detailed.Error String -> ErrorResponse
createErrorMessage error =
    case error of
        Http.Detailed.BadUrl url ->
            BadUrlResponse { label = "A Bad URL was supplied: " ++ url }

        Http.Detailed.Timeout ->
            TimeoutErrorResponse
                { label = "A timeout error response was received." }

        Http.Detailed.NetworkError ->
            NetworkErrorResponse
                { label = "A problem with the network was detected."
                }

        Http.Detailed.BadStatus metadata message ->
            case metadata.statusCode of
                400 ->
                    BadRequestResponse
                        { label = "An improperly formatted request was received."
                        , description = message
                        }

                404 ->
                    NotFoundResponse
                        { label = "The page was not found"
                        }

                410 ->
                    GoneResponse
                        { label = "This record was deleted."
                        }

                501 ->
                    NotImplementedResponse
                        { label = "This route is known, but a handler for it has not been implemented."
                        }

                _ ->
                    OtherBadStatusResponse
                        { label = "Response status code: " ++ String.fromInt metadata.statusCode
                        , description = message
                        , statusCode = metadata.statusCode
                        }

        Http.Detailed.BadBody _ _ message ->
            BadBodyResponse
                { label = "Unexpected response"
                , description = message
                }


errorMessageString : ErrorResponse -> String
errorMessageString err =
    case err of
        BadUrlResponse { label } ->
            label

        BadBodyResponse { label } ->
            label

        BadBodyEncodedResponse { label } ->
            label

        NotFoundResponse { label } ->
            label

        BadRequestResponse { label } ->
            label

        GoneResponse { label } ->
            label

        NotImplementedResponse { label } ->
            label

        OtherBadStatusResponse { label } ->
            label

        NetworkErrorResponse { label } ->
            label

        TimeoutErrorResponse { label } ->
            label
