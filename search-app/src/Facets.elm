module Facets exposing (FacetModel, setAnonymous, setCities, setComposers, setCurrentState, setGenres, setHasInventory, setNotations, setOriginalFormat, setSourceComposers, setSourceTypes, updateFacetConfigurations, viewFacets)

import Element exposing (Element, column, fill, maximum, none, padding, paddingXY, row, spacing, text, width)
import Element.Border as Border
import Element.Font as Font
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, updateCheckboxModel, viewCheckboxFacet)
import Facets.OneChoiceFacet exposing (OneChoiceFacetModel, updateOneChoiceModel, viewOneChoiceFacet)
import Helpers exposing (viewMaybe)
import Maybe.Extra as ME
import Msg exposing (Msg(..))
import RecordTypes exposing (CheckboxFacetTypes(..), FacetBlock, OneChoiceFacetTypes(..))
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
    , organizationType : Maybe Never
    , location : Maybe Never
    , anonymous : Maybe OneChoiceFacetModel
    , originalFormat : Maybe OneChoiceFacetModel
    , currentState : Maybe OneChoiceFacetModel
    }


updateFacetConfigurations : FacetModel -> QueryArgs -> FacetBlock -> FacetModel
updateFacetConfigurations currentModel queryArgs facetBlock =
    let
        genreFacet =
            if not (List.isEmpty facetBlock.genres) then
                Just
                    (updateCheckboxModel
                        { identifier = "genres"
                        , available = facetBlock.genres
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.genres
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
    in
    { cities = citiesFacet
    , genres = genreFacet
    , notations = notationsFacet
    , composers = composersFacet
    , sourceComposers = sourceComposersFacet
    , sourceTypes = sourceTypesFacet
    , hasInventory = hasInventoryFacet
    , organizationType = Nothing
    , location = Nothing
    , anonymous = isAnonymous
    , originalFormat = originalFormatFacet
    , currentState = currentStateFacet
    }


viewFacets : FacetModel -> Element Msg
viewFacets facetModel =
    let
        genresFacet =
            viewMaybe (viewCheckboxFacet "Genres") facetModel.genres
                |> Element.map (UserInteractedWithCheckboxFacet Genres)

        composersFacet =
            viewMaybe (viewCheckboxFacet "Composers") facetModel.composers
                |> Element.map (UserInteractedWithCheckboxFacet Composers)

        sourceTypesFacet =
            viewMaybe
                (viewOneChoiceFacet
                    { title = "Source Types"
                    , optionTitleMap = []
                    }
                )
                facetModel.sourceTypes
                |> Element.map (UserInteractedWithOneChoiceFacet SourceTypes)

        notationsFacet =
            viewMaybe (viewCheckboxFacet "Notation") facetModel.notations
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
                facetModel.hasInventory
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
                facetModel.anonymous
                |> Element.map (UserInteractedWithOneChoiceFacet AnonymousComposer)

        citiesFacet =
            viewMaybe (viewOneChoiceFacet { title = "Archive Cities", optionTitleMap = [] }) facetModel.cities
                |> Element.map (UserInteractedWithOneChoiceFacet Cities)

        citiesHasValues =
            ME.isJust facetModel.cities

        sourceComposers =
            viewMaybe (viewCheckboxFacet "Source Composers") facetModel.sourceComposers
                |> Element.map (UserInteractedWithCheckboxFacet SourceComposers)

        originalFormatFacet =
            viewMaybe (viewOneChoiceFacet { title = "Original Format", optionTitleMap = [] }) facetModel.originalFormat
                |> Element.map (UserInteractedWithOneChoiceFacet OriginalFormat)

        currentStateFacet =
            viewMaybe (viewOneChoiceFacet { title = "Current state", optionTitleMap = [] }) facetModel.currentState
                |> Element.map (UserInteractedWithOneChoiceFacet CurrentState)

        sourceSectionIsVisible =
            List.map ME.isJust [ facetModel.sourceTypes, facetModel.hasInventory, facetModel.originalFormat, facetModel.currentState ]
                |> List.append (List.map ME.isJust [ facetModel.sourceComposers, facetModel.notations ])
                |> List.any identity
    in
    row
        [ width fill
        ]
        [ column
            [ width (fill |> maximum 400)
            , spacing 10
            ]
            [ row
                [ Font.semiBold
                , Font.size 18
                ]
                [ text "Result Filters" ]
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
                    ]
                }
            , viewFacetSection
                { isVisible = True
                , title = "Compositions"
                , facetBlocks =
                    [ genresFacet
                    , composersFacet
                    , anonymous
                    ]
                }
            , viewFacetSection
                { isVisible = citiesHasValues
                , title = "Archives"
                , facetBlocks =
                    [ citiesFacet ]
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


setSourceComposers : Maybe CheckBoxFacetModel -> { a | sourceComposers : Maybe CheckBoxFacetModel } -> { a | sourceComposers : Maybe CheckBoxFacetModel }
setSourceComposers newValue oldRecord =
    { oldRecord | sourceComposers = newValue }
