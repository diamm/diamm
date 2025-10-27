module Facets.Slider.RangeSlider exposing (CommonAttributes, ValueAttributes, defaultLabelFormatter, defaultStyles, defaultValueFormatter, onClick, sliderInputView, sliderTrackView, snapValue)

import Html exposing (Html, div)
import Html.Attributes
import Html.Events
import Json.Decode
import Round exposing (roundNum)


type alias ValueAttributes msg =
    { change : Float -> msg
    , value : Float
    , formatter : Float -> Float -> String
    }


type alias CommonAttributes =
    { max : Float
    , min : Float
    , step : Float
    , minFormatter : Float -> String
    , maxFormatter : Float -> String
    }


snapValue : Float -> Float -> Float
snapValue value step =
    let
        stepDecimals =
            step
                |> String.fromFloat
                |> String.split "."
                |> List.drop 1
                |> List.head

        precision =
            case stepDecimals of
                Just s ->
                    String.length s

                Nothing ->
                    0
    in
    (toFloat (round (value / step)) * step)
        |> roundNum precision


onChange : (Float -> msg) -> Json.Decode.Decoder Float -> Html.Attribute msg
onChange msg input =
    Html.Events.on "change" (Json.Decode.map msg input)


onInput : (Float -> msg) -> Json.Decode.Decoder Float -> Html.Attribute msg
onInput msg input =
    Html.Events.on "input" (Json.Decode.map msg input)


sliderInputView : CommonAttributes -> ValueAttributes msg -> Json.Decode.Decoder Float -> List String -> Html msg
sliderInputView commonAttributes valueAttributes input extraClasses =
    Html.input
        [ Html.Attributes.type_ "range"
        , Html.Attributes.min <| String.fromFloat commonAttributes.min
        , Html.Attributes.max <| String.fromFloat commonAttributes.max
        , Html.Attributes.step <| String.fromFloat commonAttributes.step
        , Html.Attributes.value <| String.fromFloat valueAttributes.value
        , Html.Attributes.class "input-range"
        , Html.Attributes.classList <| List.map (\c -> ( c, True )) extraClasses
        , onChange valueAttributes.change input

        --, onInput valueAttributes.change input
        ]
        []


sliderTrackView : Json.Decode.Decoder msg -> Html msg
sliderTrackView decoder =
    div [ Html.Attributes.class "input-range__track", onClick decoder ] []


onClick : Json.Decode.Decoder msg -> Html.Attribute msg
onClick decoder =
    Html.Events.on "click" decoder


defaultLabelFormatter : Float -> String
defaultLabelFormatter value =
    String.fromFloat value


defaultValueFormatter : Float -> Float -> String
defaultValueFormatter value max =
    if value == max then
        ""

    else
        String.fromFloat value


defaultStyles : String
defaultStyles =
    """
    input[type=range] {
      all: unset;
    }

    .input-range-parent-container {
        width: 100%;
    }

    .input-range-container {
      display: inline-flex;
      align-items: center;
      position: relative;
      height: 48px;
    }

    /* In the case of the double slider, each individual slider has it's width set to 100% of the parent element. Therefore, in order to set a fixed width, it is recommended to set it on the parent element and not override the width of the range slider. This is to ensure the flexibility of the component. */
    .input-range-container,
    input[type=range].input-range {
      width: 100%;
    }

    input[type=range].input-range,
    input[type=range].input-range:hover,
    input[type=range].input-range:focus {
      box-shadow: none;
    }

    input[type=range].input-range {
      -webkit-appearance: none;
      background-color: transparent;
      padding: 0;
      overflow: visible;
      pointer-events: none;
      height: 48px;
      border: 0;
    }

    input[type=range].input-range::-moz-focus-outer {
      border: 0;
    }

    input[type=range].input-range::-webkit-slider-thumb {
      -webkit-appearance: none;
      height: 20px;
      width: 20px;
      border: 1px solid rgba(33, 34, 36, 0.5);
      background-color: white;
      border-radius: 100%;
      box-shadow: 0 0 0 2px rgba(33, 34, 36, 0.07);
      cursor: pointer;
      pointer-events: all;
      z-index: 2;
      position: relative;
      opacity: 1;
    }

    input[type=range].input-range::-moz-range-track {
      background: transparent;
    }

    input[type=range].input-range::-moz-range-thumb {
      height: 32px;
      width: 32px;
      border: none;
      background-color: white;
      border-radius: 100%;
      box-shadow: 0 0 0 2px rgba(33, 34, 36, 0.07);
      cursor: pointer;
      pointer-events: all;
      z-index: 2;
      position: relative;
      transform: scale(1);
    }

    input[type=range].input-range::-ms-track {
      background-color: transparent;
      border-color: transparent;
      color: transparent;
    }

    input[type=range].input-range::-ms-fill-lower {
      background-color: transparent;
    }

    input[type=range].input-range::-ms-thumb {
      height: 32px;
      width: 32px;
      border: none;
      background-color: white;
      border-radius: 100%;
      box-shadow: 0 0 0 2px rgba(33, 34, 36, 0.07);
      cursor: pointer;
      pointer-events: all;
      z-index: 2;
      position: relative;
    }

    input[type=range].input-range:disabled, .input-range:disabled:hover {
      cursor: not-allowed;
      box-shadow: none;
      border: 0;
      background-color: transparent;
    }

    input[type=range].input-range:disabled::-webkit-slider-thumb, input[type=range].input-range:disabled:hover::-webkit-slider-thumb {
      cursor: not-allowed;
    }

    input[type=range].input-range:disabled::-moz-range-thumb, input[type=range].input-range:disabled:hover::-moz-range-thumb {
      cursor: not-allowed;
    }

    input[type=range].input-range:disabled::-ms-thumb, input[type=range].input-range:disabled:hover::-ms-thumb {
      cursor: not-allowed;
    }

    input[type=range].input-range:disabled ~ .input-range__track, input[type=range].input-range:disabled:hover ~ .input-range__track {
      cursor: not-allowed;
      background-color: #fafafa;
    }

    input[type=range].input-range:disabled ~ .input-range__progress, input[type=range].input-range:disabled:hover ~ .input-range__progress {
      cursor: not-allowed;
      background-color: #dcdee1;
    }

    .slider-thumb {
      height: 32px;
      width: 32px;
      border: none;
      background-color: white;
      border-radius: 100%;
      box-shadow: 0 0 0 2px rgba(33, 34, 36, 0.07);
      cursor: pointer;
      pointer-events: all;
      z-index: 2;
      position: relative;
    }

    .slider-thumb--first {
      margin-left: -16px;
    }

    .slider-thumb--second {
      margin-left: -16px;
    }

    input[type=range].input-range--first {
      position: absolute;
    }

    input[type=range].input-range--second {
      position: relative;
    }

    .input-range__track,
    .input-range__progress {
      border-radius: 8px;
      position: absolute;
      height: 8px;
      margin-top: -4px;
      top: 50%;
      z-index: 0;
    }

    .input-range__track:hover,
    .input-range__progress:hover {
      cursor: pointer;
    }

    .input-range__track {
      background-color: #dcdee1;
      left: 0;
      right: 0;
    }

    .input-range__track:hover {
      cursor: pointer;
    }

    .input-range__progress {
      background-color: #00a4ff;
    }

    .input-range-labels-container {
      display: flex;
      justify-content: space-between;
    }

    .input-range-label {
      font-weight: bold;
    }

    .input-range-label--current-value {
      color: #00a4ff;
      text-align: center;
      flex: 2;
    }

    .input-range-label:first-child {
      text-align: left;
    }

    .input-range-label:last-child {
      text-align: right;
    }
"""
