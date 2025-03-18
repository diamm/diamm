module Helpers exposing (..)

import Element exposing (Element, none)
import Html.Events
import Json.Decode as Decode
import Maybe.Extra as ME


choose : Bool -> (() -> a) -> (() -> a) -> a
choose predicate isTrue isFalse =
    if predicate then
        isTrue ()

    else
        isFalse ()


viewIf : Element msg -> Bool -> Element msg
viewIf viewFunc condition =
    choose condition (\() -> viewFunc) (\() -> none)


{-|

    A view helper that will either render the value of
    'body' with a given `viewFunc`, or return `Element.none`
    indicating nothing should be rendered.

    `viewFunc` can be partially applied with a `language` value
    allowing the body to be rendered in response to the user's
    selected language parameter.

-}
viewMaybe : (a -> Element msg) -> Maybe a -> Element msg
viewMaybe viewFunc maybeBody =
    ME.unpack (\() -> none) viewFunc maybeBody


onEnter : msg -> Element.Attribute msg
onEnter msg =
    Element.htmlAttribute
        (Html.Events.on "keyup"
            (Decode.field "key" Decode.string
                |> Decode.andThen
                    (\key ->
                        if key == "Enter" then
                            Decode.succeed msg

                        else
                            Decode.fail "Not the enter key"
                    )
            )
        )
