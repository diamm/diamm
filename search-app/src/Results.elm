module Results exposing (..)

import Element exposing (Element, column, el, fill, link, none, row, spacing, text, width)
import Element.Font as Font
import RecordTypes exposing (SearchResult(..), SourceResultBody)
import Style exposing (colourScheme)


resultView : SearchResult -> Element msg
resultView result =
    case result of
        SourceResult sourceBody ->
            viewSourceResult sourceBody

        CompositionResult compositionBody ->
            none

        ArchiveResult archiveBody ->
            none

        OrganizationResult organizationBody ->
            none

        PersonResult personBody ->
            none

        SetResult setBody ->
            none


resultTemplate : String -> String -> List (Element msg) -> Element msg
resultTemplate url heading body =
    row
        [ width fill ]
        [ column
            [ width fill
            , spacing 8
            ]
            [ row
                [ width fill
                , spacing 10
                ]
                [ link
                    [ Font.color colourScheme.lightBlue ]
                    { url = url
                    , label =
                        el
                            [ Font.size 24 ]
                            (text heading)
                    }
                , el
                    [ Font.size 24, Font.color colourScheme.midGrey ]
                    (text "Source")
                ]
            , row
                [ width fill ]
                [ column
                    [ width fill
                    , spacing 8
                    ]
                    body
                ]
            ]
        ]


viewSourceResult : SourceResultBody -> Element msg
viewSourceResult source =
    resultTemplate
        source.url
        source.heading
        [ row
            [ width fill ]
            [ text (source.archiveCity ++ ", " ++ source.archiveName) ]
        , row
            [ width fill ]
            [ text (source.sourceType ++ ", " ++ source.dateStatement ++ ", " ++ source.surface) ]
        ]
