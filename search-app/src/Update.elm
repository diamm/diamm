module Update exposing (..)

import Facets exposing (FacetModel, createFacetConfigurations, setComposers, setGenres, setHasInventory, setNotations, setSourceTypes)
import Facets.CheckboxFacet as CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg)
import Facets.OneChoiceFacet as OneChoice exposing (OneChoiceFacetModel, OneChoiceFacetMsg)
import Facets.SelectFacet as SelectFacet exposing (SelectFacetModel, SelectFacetMsg)
import Maybe.Extra as ME
import Model exposing (Model, toNextQuery)
import Msg exposing (Msg(..))
import Ports exposing (pushUrl)
import RecordTypes exposing (CheckboxFacetTypes(..), OneChoiceFacetTypes(..), SelectFacetTypes(..), searchBodyDecoder)
import Request exposing (Response(..), createRequest, serverUrl)
import Route exposing (buildQueryParameters, defaultQueryArgs, removeGenreValue, setCurrentPage, setKeywordQuery, setType, updateGenreValues)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ServerRespondedWithSearchData (Ok ( _, response )) ->
            let
                facets =
                    Just (createFacetConfigurations model.facets response.facets)
            in
            ( { model
                | response = Response response
                , facets = facets
                , gotoPageValue = ""
              }
            , Cmd.none
            )

        ServerRespondedWithSearchData (Err error) ->
            ( model, Cmd.none )

        NothingHappened ->
            ( model, Cmd.none )

        ClientChangedUrl route ->
            ( model, Cmd.none )

        UserClickedRecordTypeFilter typeFilter ->
            let
                newQueryArgs =
                    model.currentQueryArgs
                        |> setType typeFilter
                        |> setCurrentPage 1

                newUrl =
                    buildQueryParameters newQueryArgs
                        |> serverUrl [ "search" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( { model
                | currentQueryArgs = newQueryArgs
              }
            , Cmd.batch [ updateResultsCmd, pushUrl newUrl ]
            )

        UserInteractedWithCheckboxFacet facet subMsg ->
            let
                updatedFacet =
                    Maybe.map
                        (\facetBlock ->
                            let
                                helperPartial =
                                    checkboxFacetUpdateHelper subMsg facetBlock
                            in
                            case facet of
                                Genres ->
                                    helperPartial setGenres .genres
                        )
                        model.facets
                        |> ME.join

                updatedQueryArgs =
                    let
                        queryArgs =
                            model.currentQueryArgs

                        facetBlock : Maybe FacetModel
                        facetBlock =
                            Maybe.map Tuple.first updatedFacet
                    in
                    case facet of
                        Genres ->
                            Maybe.map
                                (\fm ->
                                    let
                                        fvalues =
                                            Maybe.map (\g -> List.map .value g.selected) fm.genres
                                                |> Maybe.withDefault []
                                    in
                                    { queryArgs | genres = fvalues }
                                )
                                facetBlock
                                |> Maybe.withDefault queryArgs

                updatedUrl =
                    buildQueryParameters updatedQueryArgs
                        |> serverUrl [ "search" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    ( { model
                        | facets = Just newFacetBlock
                        , currentQueryArgs = updatedQueryArgs
                      }
                    , Cmd.batch
                        [ updateResultsCmd
                        , Cmd.map (UserInteractedWithCheckboxFacet facet) newSubCmd
                        , pushUrl updatedUrl
                        ]
                    )
                )
                updatedFacet
                |> Maybe.withDefault ( model, Cmd.none )

        UserInteractedWithSelectFacet facet subMsg ->
            let
                updatedFacet =
                    Maybe.map
                        (\facetBlock ->
                            let
                                -- partially apply the update helper with the common
                                -- parameters then call it with the actual field selectors.
                                helperPartial =
                                    selectFacetUpdateHelper subMsg facetBlock
                            in
                            case facet of
                                Composers ->
                                    helperPartial setComposers .composers

                                SourceTypes ->
                                    helperPartial setSourceTypes .sourceTypes

                                Notations ->
                                    helperPartial setNotations .notations
                        )
                        model.facets
                        |> ME.join
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    ( { model | facets = Just newFacetBlock }
                    , Cmd.map (UserInteractedWithSelectFacet facet) newSubCmd
                    )
                )
                updatedFacet
                |> Maybe.withDefault ( model, Cmd.none )

        UserInteractedWithOneChoiceFacet facet subMsg ->
            let
                updatedFacet =
                    Maybe.map
                        (\facetBlock ->
                            let
                                -- partially apply the update helper with the common
                                -- parameters then call it with the actual field selectors.
                                helperPartial =
                                    oneChoiceFacetUpdateHelper subMsg facetBlock
                            in
                            case facet of
                                HasInventory ->
                                    helperPartial setHasInventory .hasInventory
                        )
                        model.facets
                        |> ME.join
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    ( { model
                        | facets = Just newFacetBlock
                      }
                    , Cmd.map (UserInteractedWithOneChoiceFacet facet) newSubCmd
                    )
                )
                updatedFacet
                |> Maybe.withDefault ( model, Cmd.none )

        UserEnteredTextIntoQueryBox queryText ->
            let
                newText =
                    if String.isEmpty queryText then
                        Nothing

                    else
                        Just queryText

                newQueryArgs =
                    setKeywordQuery newText model.currentQueryArgs
            in
            ( { model
                | currentQueryArgs = newQueryArgs
              }
            , Cmd.none
            )

        UserPressedEnterOnQueryBox ->
            let
                updateResultsCmd =
                    buildQueryParameters model.currentQueryArgs
                        |> serverUrl [ "search" ]
                        |> createRequest ServerRespondedWithSearchData searchBodyDecoder
            in
            ( model, updateResultsCmd )

        UserEnteredTextIntoPageGotoBox totalPages pageNumber ->
            let
                parsedPageNumber =
                    String.toInt pageNumber
                        |> Maybe.withDefault 1

                guardedPageNumber =
                    if parsedPageNumber > totalPages then
                        String.fromInt totalPages

                    else if parsedPageNumber < 1 then
                        "1"

                    else
                        pageNumber
            in
            ( { model | gotoPageValue = guardedPageNumber }, Cmd.none )

        UserSubmittedPageGoto totalPages ->
            let
                parsedPageNumber =
                    String.toInt model.gotoPageValue
                        |> Maybe.withDefault 1

                currentPage =
                    .currentPage model.currentQueryArgs

                newCmd =
                    if currentPage == parsedPageNumber then
                        Cmd.none

                    else
                        let
                            guardedPageNumber =
                                if parsedPageNumber > totalPages then
                                    totalPages

                                else if parsedPageNumber < 1 then
                                    1

                                else
                                    parsedPageNumber

                            -- we don't update the model with this new value since it will be updated
                            -- when the response comes in.
                            newQueryArgs =
                                model.currentQueryArgs
                                    |> setCurrentPage guardedPageNumber
                        in
                        buildQueryParameters newQueryArgs
                            |> serverUrl [ "search" ]
                            |> createRequest ServerRespondedWithSearchData searchBodyDecoder
            in
            ( model, newCmd )

        UserClickedPaginationLink pageNumber ->
            let
                newQueryArgs =
                    model.currentQueryArgs
                        |> setCurrentPage pageNumber

                newUrl =
                    buildQueryParameters newQueryArgs
                        |> serverUrl [ "search" ]
            in
            ( { model | currentQueryArgs = newQueryArgs }
            , Cmd.batch
                [ createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
                , pushUrl newUrl
                ]
            )

        UserClickedClearSearch ->
            let
                newUrl =
                    buildQueryParameters defaultQueryArgs
                        |> serverUrl [ "search" ]

                clearCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( { model | currentQueryArgs = defaultQueryArgs }
            , Cmd.batch [ clearCmd, pushUrl newUrl ]
            )


selectFacetUpdateHelper :
    SelectFacetMsg
    -> FacetModel
    -> (Maybe SelectFacetModel -> FacetModel -> FacetModel)
    -> (FacetModel -> Maybe SelectFacetModel)
    -> Maybe ( FacetModel, Cmd SelectFacetMsg )
selectFacetUpdateHelper subMsg model facetModelUpdateFn selector =
    facetUpdateHelper subMsg SelectFacet.update model facetModelUpdateFn selector


checkboxFacetUpdateHelper :
    CheckBoxFacetMsg
    -> FacetModel
    -> (Maybe CheckBoxFacetModel -> FacetModel -> FacetModel)
    -> (FacetModel -> Maybe CheckBoxFacetModel)
    -> Maybe ( FacetModel, Cmd CheckBoxFacetMsg )
checkboxFacetUpdateHelper subMsg model facetModelUpdateFn selector =
    facetUpdateHelper subMsg CheckboxFacet.update model facetModelUpdateFn selector


oneChoiceFacetUpdateHelper :
    OneChoiceFacetMsg
    -> FacetModel
    -> (Maybe OneChoiceFacetModel -> FacetModel -> FacetModel)
    -> (FacetModel -> Maybe OneChoiceFacetModel)
    -> Maybe ( FacetModel, Cmd OneChoiceFacetMsg )
oneChoiceFacetUpdateHelper subMsg model facetModelUpdateFn selector =
    facetUpdateHelper subMsg OneChoice.update model facetModelUpdateFn selector


facetUpdateHelper :
    msg
    -> (msg -> a -> ( a, Cmd msg ))
    -> FacetModel
    -> (Maybe a -> FacetModel -> FacetModel)
    -> (FacetModel -> Maybe a)
    -> Maybe ( FacetModel, Cmd msg )
facetUpdateHelper subMsg updateFn model facetModelUpdateFn selector =
    selector model
        |> Maybe.map
            (\facet ->
                let
                    ( subModel, subCmd ) =
                        updateFn subMsg facet

                    newFacetBlock =
                        facetModelUpdateFn (Just subModel) model
                in
                ( newFacetBlock, subCmd )
            )
