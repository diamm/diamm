module Config exposing (defaultSearchUrl, serverUrl)

import Url exposing (Protocol(..), Url)


serverHost : String
serverHost =
    "dev.diamm.ac.uk"


serverUrl : String
serverUrl =
    "http://" ++ serverHost


defaultSearchUrl : Url
defaultSearchUrl =
    { protocol = Https
    , host = serverHost
    , port_ = Nothing
    , path = "search"
    , query = Nothing
    , fragment = Nothing
    }
