module Facets exposing (..)

import Element exposing (Element, column, fill, row, spacing, width)
import Facets.CheckboxFacet exposing (CheckBoxFacetModel, initialCheckboxModel, viewCheckboxFacet)
import Facets.SelectFacet exposing (SelectFacetModel, initialSelectModel, viewSelectFacet)
import Helpers exposing (viewMaybe)
import Msg exposing (Msg(..))
import RecordTypes exposing (CheckboxFacetTypes(..), FacetBlock, FacetItem, SearchBody, SelectFacetTypes(..))


type alias FacetModel =
    { city : Maybe Never
    , genres : Maybe CheckBoxFacetModel
    , notations : Maybe SelectFacetModel
    , composers : Maybe SelectFacetModel
    , sourceTypes : Maybe SelectFacetModel
    , hasInventory : Maybe Never
    , organizationType : Maybe Never
    , location : Maybe Never
    , archive : Maybe Never
    , anonymous : Maybe Never
    }


createFacetConfigurations : FacetBlock -> FacetModel
createFacetConfigurations facetBlock =
    let
        genreFacet =
            if not (List.isEmpty facetBlock.genres) then
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
    in
    { city = Nothing
    , genres = genreFacet
    , notations = notationsFacet
    , composers = composersFacet
    , sourceTypes = sourceTypesFacet
    , hasInventory = Nothing
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
