module Msg exposing (..)

import Browser exposing (UrlRequest)
import Url exposing (Url)


type Msg
    = ClientChangedUrl Url
    | UserRequestedUrlChange UrlRequest
    | NothingHappened
