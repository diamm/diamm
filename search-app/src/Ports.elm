port module Ports exposing (onUrlChange, pushUrl)


port onUrlChange : (String -> msg) -> Sub msg


port pushUrl : String -> Cmd msg
