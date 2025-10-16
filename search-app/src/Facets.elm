module Facets exposing (FacetModel, setCities, setComposers, setGenres, setHasInventory, setNotations, setSourceTypes, updateFacetConfigurations, viewFacets)

import Element exposing (Element, column, fill, maximum, row, spacing, width)
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, updateCheckboxModel, viewCheckboxFacet)
import Facets.OneChoiceFacet exposing (OneChoiceFacetModel, updateOneChoiceModel, viewOneChoiceFacet)
import Helpers exposing (strToBool, viewMaybe)
import Msg exposing (Msg(..))
import RecordTypes exposing (CheckboxFacetTypes(..), FacetBlock, OneChoiceFacetTypes(..))
import Route exposing (QueryArgs)


type alias FacetModel =
    { cities : Maybe CheckBoxFacetModel
    , genres : Maybe CheckBoxFacetModel
    , notations : Maybe CheckBoxFacetModel
    , composers : Maybe CheckBoxFacetModel
    , sourceTypes : Maybe CheckBoxFacetModel
    , hasInventory : Maybe OneChoiceFacetModel
    , organizationType : Maybe Never
    , location : Maybe Never
    , anonymous : Maybe Never
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
                    (updateCheckboxModel
                        { identifier = "sourceType"
                        , available = facetBlock.sourceType
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.sourceTypes
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
                            List.map (\s -> { value = strToBool s, count = 0 }) queryArgs.hasInventory
                                |> List.head
                        , bodyHidden = Maybe.map .bodyHidden currentModel.hasInventory |> Maybe.withDefault True
                        }
                    )

            else
                Nothing

        citiesFacet =
            if not (List.isEmpty facetBlock.cities) then
                Just
                    (updateCheckboxModel
                        { identifier = "cities"
                        , available = facetBlock.cities
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.cities
                        , bodyHidden = Maybe.map .bodyHidden currentModel.cities |> Maybe.withDefault True
                        }
                    )

            else
                Nothing
    in
    { cities = citiesFacet
    , genres = genreFacet
    , notations = notationsFacet
    , composers = composersFacet
    , sourceTypes = sourceTypesFacet
    , hasInventory = hasInventoryFacet
    , organizationType = Nothing
    , location = Nothing
    , anonymous = Nothing
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
            viewMaybe (viewCheckboxFacet "Source Types") facetModel.sourceTypes
                |> Element.map (UserInteractedWithCheckboxFacet SourceTypes)

        notationsFacet =
            viewMaybe (viewCheckboxFacet "Notation") facetModel.notations
                |> Element.map (UserInteractedWithCheckboxFacet Notations)

        hasInventory =
            viewMaybe (viewOneChoiceFacet "Has Inventory") facetModel.hasInventory
                |> Element.map (UserInteractedWithOneChoiceFacet HasInventory)

        citiesFacet =
            viewMaybe (viewCheckboxFacet "Archive Cities") facetModel.cities
                |> Element.map (UserInteractedWithCheckboxFacet Cities)
    in
    row
        [ width fill
        ]
        [ column
            [ width (fill |> maximum 500)
            , spacing 10
            ]
            [ genresFacet
            , composersFacet
            , sourceTypesFacet
            , notationsFacet
            , hasInventory
            , citiesFacet
            ]
        ]


setSourceTypes : Maybe CheckBoxFacetModel -> { a | sourceTypes : Maybe CheckBoxFacetModel } -> { a | sourceTypes : Maybe CheckBoxFacetModel }
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


setCities : Maybe CheckBoxFacetModel -> { a | cities : Maybe CheckBoxFacetModel } -> { a | cities : Maybe CheckBoxFacetModel }
setCities newValue oldRecord =
    { oldRecord | cities = newValue }
