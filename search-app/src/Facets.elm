module Facets exposing (..)

import Element exposing (Element, column, fill, row, text, width)
import Facets.SelectFacet exposing (SelectFacetModel, initialSelectModel, viewSelectFacet)
import Helpers exposing (viewMaybe)
import Msg exposing (Msg(..))
import RecordTypes exposing (FacetBlock, FacetItem, FacetTypes(..), SearchBody)


type alias FacetModel =
    { city : Maybe Never
    , genres : Maybe SelectFacetModel
    , notations : Maybe Never
    , composers : Maybe SelectFacetModel
    , sourceType : Maybe Never
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
                    (initialSelectModel
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
    in
    { city = Nothing
    , genres = genreFacet
    , notations = Nothing
    , composers = composersFacet
    , sourceType = Nothing
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
            viewMaybe viewSelectFacet facetModel.genres
                |> Element.map (UserInteractedWithSelectFacet Genres)
    in
    row
        [ width fill ]
        [ column
            [ width fill ]
            [ genresFacet
            ]
        ]


viewCityFacet : List FacetItem -> Element msg
viewCityFacet items =
    row
        [ width fill ]
        [ text "City facet" ]


viewAnonymousFacet : List FacetItem -> Element msg
viewAnonymousFacet items =
    row
        [ width fill ]
        [ text "Anonymous facet" ]
