module Config exposing (serverHost, serverUrl)


serverHost : String
serverHost =
    "dev.diamm.ac.uk"


serverUrl : String
serverUrl =
    "https://" ++ serverHost
