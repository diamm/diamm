port module Ports exposing (..)


port onUrlChange : (String -> msg) -> Sub msg


port pushUrl : String -> Cmd msg
