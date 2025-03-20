module Results exposing (..)

import Element exposing (Element, column, el, fill, link, none, row, spacing, text, width)
import Element.Font as Font
import Helpers exposing (viewMaybe)
import RecordTypes exposing (ArchiveResultBody, CompositionResultBody, OrganizationResultBody, PersonResultBody, SearchResult(..), SetResultBody, SourceResultBody)
import Style exposing (colourScheme)


resultView : SearchResult -> Element msg
resultView result =
    case result of
        SourceResult sourceBody ->
            viewSourceResult sourceBody

        CompositionResult compositionBody ->
            viewCompositionResult compositionBody

        ArchiveResult archiveBody ->
            viewArchiveResult archiveBody

        OrganizationResult organizationBody ->
            viewOrganizationResult organizationBody

        PersonResult personBody ->
            viewPersonResult personBody

        SetResult setBody ->
            viewSetResult setBody


resultTemplate : { url : String, heading : String, resultType : String } -> List (Element msg) -> Element msg
resultTemplate { url, heading, resultType } body =
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
                            [ Font.size 21, Font.medium ]
                            (text heading)
                    }
                , el
                    [ Font.size 21
                    , Font.color colourScheme.midGrey
                    ]
                    (text resultType)
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
    let
        sourceType =
            Maybe.map (\s -> s ++ ", ") source.sourceType
                |> Maybe.withDefault ""

        sourceDate =
            Maybe.map (\s -> s ++ ", ") source.dateStatement
                |> Maybe.withDefault ""

        sourceSurface =
            Maybe.withDefault "" source.surface
    in
    resultTemplate
        { url = source.url
        , heading = source.heading
        , resultType = "Source"
        }
        [ row
            [ width fill ]
            [ text (source.archiveCity ++ ", " ++ source.archiveName) ]
        , row
            [ width fill ]
            [ text (sourceType ++ sourceDate ++ sourceSurface) ]
        ]


viewArchiveResult : ArchiveResultBody -> Element msg
viewArchiveResult archive =
    let
        archiveHeading =
            archive.heading ++ " (" ++ archive.siglum ++ ")"
    in
    resultTemplate
        { url = archive.url
        , heading = archiveHeading
        , resultType = "Archive"
        }
        [ row
            [ width fill ]
            [ text (archive.city ++ ", " ++ archive.country) ]
        ]


viewSetResult : SetResultBody -> Element msg
viewSetResult set =
    resultTemplate
        { url = set.url
        , heading = set.heading
        , resultType = "Set"
        }
        []


viewPersonResult : PersonResultBody -> Element msg
viewPersonResult person =
    resultTemplate
        { url = person.url
        , heading = person.heading
        , resultType = "Person"
        }
        []


viewCompositionResult : CompositionResultBody -> Element msg
viewCompositionResult composition =
    resultTemplate
        { url = composition.url
        , heading = composition.heading
        , resultType = "Composition"
        }
        []


viewOrganizationResult : OrganizationResultBody -> Element msg
viewOrganizationResult organization =
    resultTemplate
        { url = organization.url
        , heading = organization.heading
        , resultType = "Organization"
        }
        [ row
            [ width fill ]
            [ viewMaybe text organization.location ]
        ]
