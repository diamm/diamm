module Results exposing (resultView)

import Element exposing (Element, alignLeft, alignRight, centerY, column, el, fill, height, image, link, maximum, minimum, moveUp, none, paddingXY, paragraph, px, row, spacing, text, width, wrappedRow)
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Helpers exposing (viewMaybe)
import Html
import Html.Attributes as HA
import RecordTypes exposing (ArchiveResultBody, CompositionResultBody, OrganizationResultBody, PersonResultBody, SearchResult(..), SetResultBody, SourceResultBody)
import String.Extra as SE
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


resultTemplate : { url : String, heading : String, resultType : String, publicImages : Bool, isVirtual : Bool, externalManifest : Bool } -> List (Element msg) -> Element msg
resultTemplate { url, heading, resultType, publicImages, isVirtual, externalManifest } body =
    row
        [ width fill ]
        [ column
            [ width (fill |> maximum 900)
            , spacing 8
            ]
            [ wrappedRow
                [ width fill
                , spacing 8
                , Font.size 21
                , width fill
                ]
                [ if publicImages then
                    publicImageIcon

                  else
                    none
                , if externalManifest then
                    externalManifestIcon

                  else
                    none
                , if isVirtual then
                    virtualSourceBadge

                  else
                    none
                , paragraph
                    [ alignLeft ]
                    [ link
                        [ Font.color colourScheme.lightBlue
                        , Font.medium
                        ]
                        { url = url
                        , label =
                            text (heading |> SE.ellipsis 140)
                        }
                    ]
                ]
            , row
                [ width fill, Font.size 18, Font.color colourScheme.midGrey ]
                [ text resultType ]
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


publicImageIcon : Element msg
publicImageIcon =
    statusIcon "fa fa-picture-o" "Public images available"


externalManifestIcon : Element msg
externalManifestIcon =
    image
        [ width (px 20)
        , height (px 20)
        , Element.htmlAttribute (HA.title "Linked IIIF manifest available")
        ]
        { src = "/static/images/iiif.png"
        , description = "Linked IIIF manifest available"
        }


virtualSourceBadge : Element msg
virtualSourceBadge =
    el
        [ Background.color colourScheme.lightBlue
        , Border.rounded 3
        , Font.color colourScheme.white
        , Font.medium
        , Font.size 12
        , paddingXY 6 2
        , alignLeft
        ]
        (text "Virtual")


statusIcon : String -> String -> Element msg
statusIcon iconClass label =
    el
        [ Font.color colourScheme.midGrey ]
        (Element.html
            (Html.i
                [ HA.class iconClass
                , HA.attribute "role" "img"
                , HA.attribute "aria-label" label
                , HA.title label
                ]
                []
            )
        )


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

        contentsStatement =
            viewMaybe (\t -> row [ width fill ] [ paragraph [] [ text t ] ]) source.contentsStatement
    in
    resultTemplate
        { url = source.url
        , heading = source.heading
        , resultType = "Source"
        , publicImages = source.publicImages
        , isVirtual = source.isVirtual
        , externalManifest = source.externalManifest
        }
        [ row
            [ width fill ]
            [ paragraph [] [ text (source.archiveCity ++ ", " ++ source.archiveName) ] ]
        , row
            [ width fill ]
            [ paragraph [] [ text (sourceType ++ sourceDate ++ sourceSurface) ]
            ]
        , contentsStatement
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
        , publicImages = False
        , isVirtual = False
        , externalManifest = False
        }
        [ row
            [ width fill ]
            [ paragraph [] [ text (archive.city ++ ", " ++ archive.country) ] ]
        ]


viewSetResult : SetResultBody -> Element msg
viewSetResult set =
    let
        sourceLabel =
            String.fromInt set.numSources
                ++ (if set.numSources == 1 then
                        " Source"

                    else
                        " Sources"
                   )
    in
    resultTemplate
        { url = set.url
        , heading = set.heading
        , resultType = "Set"
        , publicImages = False
        , isVirtual = False
        , externalManifest = False
        }
        [ row
            [ width fill ]
            [ text sourceLabel ]
        ]


viewPersonResult : PersonResultBody -> Element msg
viewPersonResult person =
    let
        variantNames =
            viewMaybe
                (\names ->
                    el
                        []
                        (text ("Variant names: " ++ String.join "; " names))
                )
                person.variantNames
    in
    resultTemplate
        { url = person.url
        , heading = person.heading
        , resultType = "Person"
        , publicImages = False
        , isVirtual = False
        , externalManifest = False
        }
        [ variantNames ]


viewCompositionResult : CompositionResultBody -> Element msg
viewCompositionResult composition =
    let
        composers =
            Maybe.map (\s -> el [] (text (String.join "; " s))) composition.composers
                |> Maybe.withDefault none
    in
    resultTemplate
        { url = composition.url
        , heading = composition.heading
        , resultType = "Composition"
        , publicImages = False
        , isVirtual = False
        , externalManifest = False
        }
        [ row
            [ width fill ]
            [ composers ]
        ]


viewOrganizationResult : OrganizationResultBody -> Element msg
viewOrganizationResult organization =
    resultTemplate
        { url = organization.url
        , heading = organization.heading
        , resultType = "Organization"
        , publicImages = False
        , isVirtual = False
        , externalManifest = False
        }
        [ row
            [ width fill ]
            [ viewMaybe text organization.location ]
        ]
