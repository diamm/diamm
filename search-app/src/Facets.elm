module Facets exposing (..)

import Element exposing (Element, column, fill, row, spacing, width)
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, initialCheckboxModel, viewCheckboxFacet)
import Facets.OneChoiceFacet exposing (OneChoiceFacetModel, initialOneChoiceModel, viewOneChoiceFacet)
import Facets.SelectFacet exposing (SelectFacetModel, initialSelectModel, viewSelectFacet)
import Helpers exposing (viewMaybe)
import Maybe.Extra as ME
import Msg exposing (Msg(..))
import RecordTypes exposing (CheckboxFacetTypes(..), FacetBlock, FacetItem, OneChoiceFacetTypes(..), SearchBody, SelectFacetTypes(..))


type alias FacetModel =
    { city : Maybe Never
    , genres : Maybe CheckBoxFacetModel
    , notations : Maybe SelectFacetModel
    , composers : Maybe SelectFacetModel
    , sourceTypes : Maybe SelectFacetModel
    , hasInventory : Maybe OneChoiceFacetModel
    , organizationType : Maybe Never
    , location : Maybe Never
    , archive : Maybe Never
    , anonymous : Maybe Never
    }


createFacetConfigurations : Maybe FacetModel -> FacetBlock -> FacetModel
createFacetConfigurations currentModel facetBlock =
    let
        genreFacet =
            if ME.isJust currentModel then
                Maybe.map .genres currentModel
                    |> ME.join

            else if not (List.isEmpty facetBlock.genres) then
                Just
                    (initialCheckboxModel
                        { identifier = "genres"
                        , available = facetBlock.genres
                        }
                    )

            else
                Nothing

        composersFacet =
            if not (List.isEmpty facetBlock.composers) then
                Just
                    (initialSelectModel
                        { identifier = "composers"
                        , available = facetBlock.composers
                        }
                    )

            else
                Nothing

        notationsFacet =
            if not (List.isEmpty facetBlock.notations) then
                Just
                    (initialSelectModel
                        { identifier = "notations"
                        , available = facetBlock.notations
                        }
                    )

            else
                Nothing

        sourceTypesFacet =
            if not (List.isEmpty facetBlock.sourceType) then
                Just
                    (initialSelectModel
                        { identifier = "sourceType"
                        , available = facetBlock.sourceType
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
    in
    { city = Nothing
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
            viewMaybe (viewSelectFacet "Composers") facetModel.composers
                |> Element.map (UserInteractedWithSelectFacet Composers)

        sourceTypesFacet =
            viewMaybe (viewSelectFacet "Source Types") facetModel.sourceTypes
                |> Element.map (UserInteractedWithSelectFacet SourceTypes)

        notationsFacet =
            viewMaybe (viewSelectFacet "Notation") facetModel.notations
                |> Element.map (UserInteractedWithSelectFacet Notations)

        hasInventory =
            viewMaybe (viewOneChoiceFacet "Has Inventory") facetModel.hasInventory
                |> Element.map (UserInteractedWithOneChoiceFacet HasInventory)
    in
    row
        [ width fill
        ]
        [ column
            [ width fill
            , spacing 10
            ]
            [ genresFacet
            , composersFacet
            , sourceTypesFacet
            , notationsFacet
            , hasInventory
            ]
        ]


setSourceTypes : Maybe SelectFacetModel -> { a | sourceTypes : Maybe SelectFacetModel } -> { a | sourceTypes : Maybe SelectFacetModel }
setSourceTypes newValue oldRecord =
    { oldRecord | sourceTypes = newValue }


setComposers : Maybe SelectFacetModel -> { a | composers : Maybe SelectFacetModel } -> { a | composers : Maybe SelectFacetModel }
setComposers newValue oldRecord =
    { oldRecord | composers = newValue }


setNotations : Maybe SelectFacetModel -> { a | notations : Maybe SelectFacetModel } -> { a | notations : Maybe SelectFacetModel }
setNotations newValue oldRecord =
    { oldRecord | notations = newValue }


setGenres : Maybe CheckBoxFacetModel -> { a | genres : Maybe CheckBoxFacetModel } -> { a | genres : Maybe CheckBoxFacetModel }
setGenres newValue oldRecord =
    { oldRecord | genres = newValue }


setHasInventory : Maybe OneChoiceFacetModel -> { a | hasInventory : Maybe OneChoiceFacetModel } -> { a | hasInventory : Maybe OneChoiceFacetModel }
setHasInventory newValue oldRecord =
    { oldRecord | hasInventory = newValue }
