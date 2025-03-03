module Msg exposing (..)

import Browser exposing (UrlRequest)
import Http
import Http.Detailed
import RecordTypes exposing (SearchBody)
import Url exposing (Url)


type Msg
    = NothingHappened
    | ServerRespondedWithSearchData (Result (Http.Detailed.Error String) ( Http.Metadata, SearchBody ))
