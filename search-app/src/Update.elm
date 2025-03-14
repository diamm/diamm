module Update exposing (..)

import Facets exposing (createFacetConfigurations)
import Facets.SelectFacet as SelectFacet
import Maybe.Extra as ME
import Model exposing (Model)
import Msg exposing (Msg(..))
import RecordTypes exposing (FacetTypes(..))
import Request exposing (Response(..))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ServerRespondedWithSearchData (Ok ( _, response )) ->
            let
                facets =
                    Just (createFacetConfigurations response.facets)
            in
            ( { model
                | response = Response response
                , facets = facets
              }
            , Cmd.none
            )

        ServerRespondedWithSearchData (Err error) ->
            ( model, Cmd.none )

        NothingHappened ->
            ( model, Cmd.none )

        UrlChanged route ->
            ( model, Cmd.none )

        UserInteractedWithSelectFacet facet subMsg ->
            let
                ( newModel, newCmd ) =
                    Maybe.map
                        (\facetBlock ->
                            case facet of
                                Genres ->
                                    Maybe.map
                                        (\genreFacet ->
                                            let
                                                ( subModel, subCmd ) =
                                                    SelectFacet.update subMsg genreFacet

                                                newFacetBlock =
                                                    { facetBlock | genres = Just subModel }

                                                updatedModel =
                                                    { model | facets = Just newFacetBlock }
                                            in
                                            ( updatedModel, Cmd.map (UserInteractedWithSelectFacet facet) subCmd )
                                        )
                                        facetBlock.genres
                        )
                        model.facets
                        |> ME.join
                        |> Maybe.withDefault ( model, Cmd.none )
            in
            ( newModel, newCmd )
