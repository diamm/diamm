module Facets exposing (FacetModel, createFacetConfigurations, setCities, setComposers, setGenres, setHasInventory, setNotations, setSourceTypes, viewFacets)

import Element exposing (Element, column, fill, maximum, row, spacing, width)
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, initialCheckboxModel, viewCheckboxFacet)
import Facets.OneChoiceFacet exposing (OneChoiceFacetModel, initialOneChoiceModel, viewOneChoiceFacet)
import Helpers exposing (viewMaybe)
import Maybe.Extra as ME
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
    , archive : Maybe Never
    , anonymous : Maybe Never
    }


createFacetConfigurations : Maybe FacetModel -> QueryArgs -> FacetBlock -> FacetModel
createFacetConfigurations currentModel queryArgs facetBlock =
    let
        genreFacet =
            if not (List.isEmpty facetBlock.genres) then
                Just
                    (initialCheckboxModel
                        { identifier = "genres"
                        , available = facetBlock.genres
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.genres
                        }
                    )

            else
                Nothing

        composersFacet =
            if not (List.isEmpty facetBlock.composers) then
                Just
                    (initialCheckboxModel
                        { identifier = "composers"
                        , available = facetBlock.composers
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.composers
                        }
                    )

            else
                Nothing

        notationsFacet =
            if not (List.isEmpty facetBlock.notations) then
                Just
                    (initialCheckboxModel
                        { identifier = "notations"
                        , available = facetBlock.notations
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.notations
                        }
                    )

            else
                Nothing

        sourceTypesFacet =
            if not (List.isEmpty facetBlock.sourceType) then
                Just
                    (initialCheckboxModel
                        { identifier = "sourceType"
                        , available = facetBlock.sourceType
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.sourceTypes
                        }
                    )

            else
                Nothing

        hasInventoryFacet =
            if not (List.isEmpty facetBlock.hasInventory) then
                Just
                    (initialOneChoiceModel
                        { identifier = "has-inventory"
                        , available = facetBlock.hasInventory
                        }
                    )

            else
                Nothing

        citiesFacet =
            if not (List.isEmpty facetBlock.cities) then
                Just
                    (initialCheckboxModel
                        { identifier = "cities"
                        , available = facetBlock.cities
                        , selected = List.map (\s -> { value = s, count = 0 }) queryArgs.cities
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
    , archive = Nothing
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
