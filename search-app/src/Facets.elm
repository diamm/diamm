module Facets exposing (FacetModel, setAnonymous, setCities, setComposers, setCurrentState, setDateRange, setGenres, setHasInventory, setHostMainContents, setNotations, setOrganizationType, setOriginalFormat, setSourceComposers, setSourceTypes, updateFacetConfigurations, viewFacets)

import Element exposing (Element, alignLeft, alignRight, column, el, fill, htmlAttribute, maximum, none, padding, paddingXY, pointer, row, spacing, text, width)
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Element.Input as Input
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, updateCheckboxModel, viewCheckboxFacet)
import Facets.OneChoiceFacet exposing (OneChoiceFacetModel, updateOneChoiceModel, viewOneChoiceFacet)
import Facets.RangeFacet exposing (RangeFacetModel, initRangeModel, viewRangeFacet)
import Helpers exposing (viewMaybe)
import Html.Attributes as HA
import Maybe.Extra as ME
import Msg exposing (Msg(..))
import RecordTypes exposing (CheckboxFacetTypes(..), FacetBlock, OneChoiceFacetTypes(..), RangeFacetTypes(..))
import Route exposing (QueryArgs)
import Style exposing (colourScheme)


type alias FacetModel =
    { cities : Maybe OneChoiceFacetModel
    , genres : Maybe CheckBoxFacetModel
    , notations : Maybe CheckBoxFacetModel
    , composers : Maybe CheckBoxFacetModel
    , sourceComposers : Maybe CheckBoxFacetModel
    , sourceTypes : Maybe OneChoiceFacetModel
    , hasInventory : Maybe OneChoiceFacetModel
    , organizationType : Maybe OneChoiceFacetModel
    , location : Maybe Never
    , anonymous : Maybe OneChoiceFacetModel
    , originalFormat : Maybe OneChoiceFacetModel
    , currentState : Maybe OneChoiceFacetModel
    , hostMainContents : Maybe OneChoiceFacetModel
    , dateRange : Maybe RangeFacetModel
    }


updateFacetConfigurations : FacetModel -> QueryArgs -> FacetBlock -> FacetModel
updateFacetConfigurations currentModel queryArgs facetBlock =
    let
        genreFacet =
            if not (List.isEmpty facetBlock.genres) then
                let
                    incoming =
                        List.map (\s -> { value = s, count = 0 }) queryArgs.genres
                in
                Just
                    (updateCheckboxModel
                        { identifier = "genres"
                        , available = facetBlock.genres
                        , selected =
                            Maybe.map (\f -> f.selected) currentModel.genres
                                |> Maybe.withDefault incoming
                        , bodyHidden = Maybe.map .bodyHidden currentModel.genres |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        composersFacet =
            if not (List.isEmpty facetBlock.composers) then
                Just
                    (updateCheckboxModel
                        { identifier = "composers"
                        , available = facetBlock.composers
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.composers
                        , bodyHidden = Maybe.map .bodyHidden currentModel.composers |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        notationsFacet =
            if not (List.isEmpty facetBlock.notations) then
                Just
                    (updateCheckboxModel
                        { identifier = "notations"
                        , available = facetBlock.notations
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.notations
                        , bodyHidden = Maybe.map .bodyHidden currentModel.notations |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        sourceTypesFacet =
            if not (List.isEmpty facetBlock.sourceType) then
                Just
                    (updateOneChoiceModel
                        { identifier = "sourceType"
                        , available = facetBlock.sourceType
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.sourceTypes
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.sourceTypes |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        hasInventoryFacet =
            if not (List.isEmpty facetBlock.hasInventory) then
                Just
                    (updateOneChoiceModel
                        { identifier = "has-inventory"
                        , available = facetBlock.hasInventory
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.hasInventory
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.hasInventory |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        isAnonymous =
            if not (List.isEmpty facetBlock.anonymous) then
                Just
                    (updateOneChoiceModel
                        { identifier = "is-anonymous"
                        , available = facetBlock.anonymous
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.anonymous
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.anonymous |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        citiesFacet =
            if not (List.isEmpty facetBlock.cities) then
                Just
                    (updateOneChoiceModel
                        { identifier = "cities"
                        , available = facetBlock.cities
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.cities
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.cities |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        originalFormatFacet =
            if not (List.isEmpty facetBlock.originalFormat) then
                Just
                    (updateOneChoiceModel
                        { identifier = "original-format"
                        , available = facetBlock.originalFormat
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.originalFormat
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.originalFormat |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        currentStateFacet =
            if not (List.isEmpty facetBlock.currentState) then
                Just
                    (updateOneChoiceModel
                        { identifier = "current-state"
                        , available = facetBlock.currentState
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.currentState
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.currentState |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        sourceComposersFacet =
            if not (List.isEmpty facetBlock.sourceComposers) then
                Just
                    (updateCheckboxModel
                        { identifier = "source-composers"
                        , available = facetBlock.sourceComposers
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.sourceComposers
                        , bodyHidden = Maybe.map .bodyHidden currentModel.sourceComposers |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        hostMainContentsFacet =
            if not (List.isEmpty facetBlock.hostMainContents) then
                Just
                    (updateOneChoiceModel
                        { identifier = "host-contents"
                        , available = facetBlock.hostMainContents
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.hostMainContents
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.hostMainContents |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        organizationTypeFacet =
            if not (List.isEmpty facetBlock.organizationType) then
                Just
                    (updateOneChoiceModel
                        { identifier = "organization-type"
                        , available = facetBlock.organizationType
                        , selected =
                            List.map (\s -> { value = s, count = 0 }) queryArgs.organizationType
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.organizationType |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        dateRangeFacet =
            Maybe.map
                (\drFacet ->
                    initRangeModel
                        { identifier = "date-range"
                        , facetData = drFacet
                        , selected = Maybe.map .selected currentModel.dateRange |> ME.join
                        }
                )
                facetBlock.dateRange
    in
    { cities = citiesFacet
    , genres = genreFacet
    , notations = notationsFacet
    , composers = composersFacet
    , sourceComposers = sourceComposersFacet
    , sourceTypes = sourceTypesFacet
    , hasInventory = hasInventoryFacet
    , organizationType = organizationTypeFacet
    , location = Nothing
    , anonymous = isAnonymous
    , originalFormat = originalFormatFacet
    , currentState = currentStateFacet
    , hostMainContents = hostMainContentsFacet
    , dateRange = dateRangeFacet
    }


viewFacets : { a | needsUpdating : Bool, facets : FacetModel } -> Element Msg
viewFacets { needsUpdating, facets } =
    let
        genresFacet =
            viewMaybe (viewCheckboxFacet "Genres") facets.genres
                |> Element.map (UserInteractedWithCheckboxFacet Genres)

        composersFacet =
            viewMaybe (viewCheckboxFacet "Composers") facets.composers
                |> Element.map (UserInteractedWithCheckboxFacet Composers)

        sourceTypesFacet =
            viewMaybe
                (viewOneChoiceFacet
                    { title = "Source Types"
                    , optionTitleMap = []
                    }
                )
                facets.sourceTypes
                |> Element.map (UserInteractedWithOneChoiceFacet SourceTypes)

        notationsFacet =
            viewMaybe (viewCheckboxFacet "Notation") facets.notations
                |> Element.map (UserInteractedWithCheckboxFacet Notations)

        hasInventory =
            viewMaybe
                (viewOneChoiceFacet
                    { title = "Has Inventory"
                    , optionTitleMap =
                        [ ( "true", "Source has an inventory" )
                        , ( "false", "Source does not have an inventory" )
                        ]
                    }
                )
                facets.hasInventory
                |> Element.map (UserInteractedWithOneChoiceFacet HasInventory)

        anonymous =
            viewMaybe
                (viewOneChoiceFacet
                    { title = "Anonymous Composer"
                    , optionTitleMap =
                        [ ( "true", "Composer is anonymous" )
                        , ( "false", "Composer is not anonymous" )
                        ]
                    }
                )
                facets.anonymous
                |> Element.map (UserInteractedWithOneChoiceFacet AnonymousComposer)

        citiesFacet =
            viewMaybe (viewOneChoiceFacet { title = "Archive Cities", optionTitleMap = [] }) facets.cities
                |> Element.map (UserInteractedWithOneChoiceFacet Cities)

        sourceComposers =
            viewMaybe (viewCheckboxFacet "Source Composers") facets.sourceComposers
                |> Element.map (UserInteractedWithCheckboxFacet SourceComposers)

        originalFormatFacet =
            viewMaybe (viewOneChoiceFacet { title = "Original Format", optionTitleMap = [] }) facets.originalFormat
                |> Element.map (UserInteractedWithOneChoiceFacet OriginalFormat)

        currentStateFacet =
            viewMaybe (viewOneChoiceFacet { title = "Current state", optionTitleMap = [] }) facets.currentState
                |> Element.map (UserInteractedWithOneChoiceFacet CurrentState)

        hostMainContentsFacet =
            viewMaybe (viewOneChoiceFacet { title = "Host main contents", optionTitleMap = [] }) facets.hostMainContents
                |> Element.map (UserInteractedWithOneChoiceFacet HostMainContents)

        organizationTypeFacet =
            viewMaybe (viewOneChoiceFacet { title = "Organization type", optionTitleMap = [] }) facets.organizationType
                |> Element.map (UserInteractedWithOneChoiceFacet OrganizationType)

        sourceSectionIsVisible =
            List.map ME.isJust [ facets.sourceTypes, facets.hasInventory, facets.originalFormat, facets.currentState ]
                |> List.append (List.map ME.isJust [ facets.sourceComposers, facets.notations ])
                |> List.any identity

        compositionSectionIsVisible =
            List.map ME.isJust [ facets.genres, facets.composers ]
                |> List.append [ ME.isJust facets.anonymous ]
                |> List.any identity

        archivesSectionIsVisible =
            [ ME.isJust facets.cities ]
                |> List.any identity

        organizationsSectionIsVisible =
            [ ME.isJust facets.organizationType ]
                |> List.any identity

        dateRangeFacet =
            viewMaybe (viewRangeFacet { title = "Year range" }) facets.dateRange
                |> Element.map (UserInteractedWithRangeFacet DateRange)

        dateRangeIsVisible =
            ME.isJust facets.dateRange

        updateBtnCfg =
            if needsUpdating then
                { colour = colourScheme.red
                , submitMsg = Just UserClickedUpdateResults
                , pointer = pointer
                }

            else
                { colour = colourScheme.lightGrey
                , submitMsg = Nothing
                , pointer = htmlAttribute (HA.style "cursor" "not-allowed")
                }
    in
    row
        [ width fill
        ]
        [ column
            [ width (fill |> maximum 400)
            , spacing 10
            ]
            [ row
                [ width fill
                ]
                [ el
                    [ alignLeft
                    , Font.semiBold
                    , Font.size 18
                    ]
                    (text "Result Filters")
                , Input.button
                    [ Background.color updateBtnCfg.colour
                    , Font.color colourScheme.white
                    , Border.rounded 3
                    , padding 10
                    , alignRight
                    , updateBtnCfg.pointer
                    ]
                    { label = text "Update results"
                    , onPress = updateBtnCfg.submitMsg
                    }
                ]
            , viewFacetSection
                { isVisible = dateRangeIsVisible
                , title = "Date ranges"
                , facetBlocks =
                    [ dateRangeFacet ]
                }
            , viewFacetSection
                { isVisible = sourceSectionIsVisible
                , title = "Sources"
                , facetBlocks =
                    [ sourceTypesFacet
                    , sourceComposers
                    , notationsFacet
                    , hasInventory
                    , originalFormatFacet
                    , currentStateFacet
                    , hostMainContentsFacet
                    ]
                }
            , viewFacetSection
                { isVisible = compositionSectionIsVisible
                , title = "Compositions"
                , facetBlocks =
                    [ genresFacet
                    , composersFacet
                    , anonymous
                    ]
                }
            , viewFacetSection
                { isVisible = archivesSectionIsVisible
                , title = "Archives"
                , facetBlocks =
                    [ citiesFacet ]
                }
            , viewFacetSection
                { isVisible = organizationsSectionIsVisible
                , title = "Organizations"
                , facetBlocks = [ organizationTypeFacet ]
                }
            ]
        ]


viewFacetSection :
    { isVisible : Bool
    , title : String
    , facetBlocks : List (Element msg)
    }
    -> Element msg
viewFacetSection { isVisible, title, facetBlocks } =
    if isVisible then
        row
            [ width fill
            , Border.widthEach { top = 1, left = 0, right = 0, bottom = 0 }
            , Border.color colourScheme.lightGrey
            ]
            [ column
                [ width fill
                , spacing 10
                ]
                (row
                    [ Font.medium
                    , Font.size 20
                    , paddingXY 0 10
                    ]
                    [ text title ]
                    :: facetBlocks
                )
            ]

    else
        none


setSourceTypes : Maybe OneChoiceFacetModel -> { a | sourceTypes : Maybe OneChoiceFacetModel } -> { a | sourceTypes : Maybe OneChoiceFacetModel }
setSourceTypes newValue oldRecord =
    { oldRecord | sourceTypes = newValue }


setComposers : Maybe CheckBoxFacetModel -> { a | composers : Maybe CheckBoxFacetModel } -> { a | composers : Maybe CheckBoxFacetModel }
setComposers newValue oldRecord =
    { oldRecord | composers = newValue }


setNotations : Maybe CheckBoxFacetModel -> { a | notations : Maybe CheckBoxFacetModel } -> { a | notations : Maybe CheckBoxFacetModel }
setNotations newValue oldRecord =
    { oldRecord | notations = newValue }


setGenres : Maybe CheckBoxFacetModel -> { a | genres : Maybe CheckBoxFacetModel } -> { a | genres : Maybe CheckBoxFacetModel }
setGenres newValue oldRecord =
    { oldRecord | genres = newValue }


setHasInventory : Maybe OneChoiceFacetModel -> { a | hasInventory : Maybe OneChoiceFacetModel } -> { a | hasInventory : Maybe OneChoiceFacetModel }
setHasInventory newValue oldRecord =
    { oldRecord | hasInventory = newValue }


setAnonymous : Maybe OneChoiceFacetModel -> { a | anonymous : Maybe OneChoiceFacetModel } -> { a | anonymous : Maybe OneChoiceFacetModel }
setAnonymous newValue oldRecord =
    { oldRecord | anonymous = newValue }


setCities : Maybe OneChoiceFacetModel -> { a | cities : Maybe OneChoiceFacetModel } -> { a | cities : Maybe OneChoiceFacetModel }
setCities newValue oldRecord =
    { oldRecord | cities = newValue }


setOriginalFormat : Maybe OneChoiceFacetModel -> { a | originalFormat : Maybe OneChoiceFacetModel } -> { a | originalFormat : Maybe OneChoiceFacetModel }
setOriginalFormat newValue oldRecord =
    { oldRecord | originalFormat = newValue }


setCurrentState : Maybe OneChoiceFacetModel -> { a | currentState : Maybe OneChoiceFacetModel } -> { a | currentState : Maybe OneChoiceFacetModel }
setCurrentState newValue oldRecord =
    { oldRecord | currentState = newValue }


setHostMainContents : Maybe OneChoiceFacetModel -> { a | hostMainContents : Maybe OneChoiceFacetModel } -> { a | hostMainContents : Maybe OneChoiceFacetModel }
setHostMainContents newValue oldRecord =
    { oldRecord | hostMainContents = newValue }


setOrganizationType : Maybe OneChoiceFacetModel -> { a | organizationType : Maybe OneChoiceFacetModel } -> { a | organizationType : Maybe OneChoiceFacetModel }
setOrganizationType newValue oldRecord =
    { oldRecord | organizationType = newValue }


setSourceComposers : Maybe CheckBoxFacetModel -> { a | sourceComposers : Maybe CheckBoxFacetModel } -> { a | sourceComposers : Maybe CheckBoxFacetModel }
setSourceComposers newValue oldRecord =
    { oldRecord | sourceComposers = newValue }


setDateRange : Maybe RangeFacetModel -> { a | dateRange : Maybe RangeFacetModel } -> { a | dateRange : Maybe RangeFacetModel }
setDateRange newValue oldRecord =
    { oldRecord | dateRange = newValue }
