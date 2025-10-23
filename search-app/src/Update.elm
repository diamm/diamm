module Update exposing (update)

import Cmd.Extra as CE
import Facets exposing (FacetModel, setAnonymous, setCities, setComposers, setCurrentState, setDateRange, setGenres, setHasInventory, setHostMainContents, setNotations, setOrganizationType, setOriginalFormat, setSourceComposers, setSourceTypes, updateFacetConfigurations)
import Facets.CheckboxFacet as CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg)
import Facets.OneChoiceFacet as OneChoice exposing (OneChoiceFacetModel, OneChoiceFacetMsg)
import Facets.RangeFacet as RangeFacet exposing (RangeFacetModel, RangeFacetMsg)
import Helpers exposing (resetViewportOf)
import Maybe.Extra as ME
import Model exposing (Model)
import Msg exposing (Msg(..))
import Ports exposing (pushUrl)
import RecordTypes exposing (CheckboxFacetTypes(..), FacetItem, OneChoiceFacetTypes(..), RangeFacetTypes(..), searchBodyDecoder)
import Request exposing (Response(..), createRequest, serverUrl)
import Route exposing (QueryArgs, Route(..), buildQueryParameters, defaultQueryArgs, setCurrentPage, setKeywordQuery, setQueryAnonymous, setQueryCities, setQueryComposers, setQueryCurrentState, setQueryDateRange, setQueryGenres, setQueryHasInventory, setQueryHostMainContents, setQueryNotations, setQueryOrganizationType, setQueryOriginalFormat, setQuerySourceComposers, setQuerySourceTypes, setQueryType)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ServerRespondedWithSearchData (Ok ( _, response )) ->
            let
                facets =
                    updateFacetConfigurations model.facets model.currentQueryArgs response.facets
            in
            ( { model
                | response = Response response
                , facets = facets
                , gotoPageValue = ""
                , needsUpdating = False
              }
            , Cmd.none
            )

        ServerRespondedWithSearchData (Err _) ->
            ( model, Cmd.none )

        NothingHappened ->
            ( model, Cmd.none )

        ClientChangedUrl route ->
            let
                newModel =
                    Maybe.map
                        (\r ->
                            case r of
                                SearchPageRoute newQargs ->
                                    { model | currentQueryArgs = newQargs }

                                UnknownRoute ->
                                    model
                        )
                        route
                        |> Maybe.withDefault model
            in
            ( newModel, Cmd.none )

        ClientCompletedViewportReset ->
            ( model, Cmd.none )

        UserClickedRecordTypeFilter typeFilter ->
            let
                newQueryArgs =
                    model.currentQueryArgs
                        |> setQueryType typeFilter
                        |> setCurrentPage 1

                newUrl =
                    buildQueryParameters newQueryArgs
                        |> serverUrl [ "search/" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( model
            , Cmd.batch
                [ updateResultsCmd
                , pushUrl newUrl
                ]
            )

        -- interrupt the hiding since we don't need to update the query args for this action
        UserInteractedWithCheckboxFacet facet CheckboxFacet.OnToggleHide ->
            checkboxFacetHelper model facet CheckboxFacet.OnToggleHide

        UserInteractedWithCheckboxFacet facet (CheckboxFacet.OnTextInput t) ->
            checkboxFacetHelper model facet (CheckboxFacet.OnTextInput t)

        UserInteractedWithCheckboxFacet facet subMsg ->
            checkboxFacetHelper model facet subMsg

        UserInteractedWithOneChoiceFacet facet OneChoice.OnToggleHide ->
            oneChoiceFacetHelper model facet OneChoice.OnToggleHide

        UserInteractedWithOneChoiceFacet facet (OneChoice.OnTextInput t) ->
            oneChoiceFacetHelper model facet (OneChoice.OnTextInput t)

        UserInteractedWithOneChoiceFacet facet subMsg ->
            oneChoiceFacetHelper model facet subMsg

        UserInteractedWithRangeFacet facet subMsg ->
            rangeFacetHelper model facet subMsg

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
                newUrl =
                    buildQueryParameters model.currentQueryArgs
                        |> serverUrl [ "search/" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( model
            , Cmd.batch [ updateResultsCmd, pushUrl newUrl ]
            )

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
            ( { model
                | gotoPageValue = guardedPageNumber
              }
            , Cmd.none
            )

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

                            newUrl =
                                buildQueryParameters newQueryArgs
                                    |> serverUrl [ "search/" ]
                        in
                        Cmd.batch
                            [ createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
                            , pushUrl newUrl
                            ]
            in
            ( model, newCmd )

        UserClickedPaginationLink pageNumber ->
            let
                newQueryArgs =
                    model.currentQueryArgs
                        |> setCurrentPage pageNumber

                newUrl =
                    buildQueryParameters newQueryArgs
                        |> serverUrl [ "search/" ]
            in
            ( model
            , Cmd.batch
                [ createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
                , pushUrl newUrl
                , resetViewportOf ClientCompletedViewportReset "search-results-list"
                ]
            )

        UserClickedClearSearch ->
            let
                newUrl =
                    buildQueryParameters defaultQueryArgs
                        |> serverUrl [ "search/" ]

                clearCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( { model | currentQueryArgs = defaultQueryArgs }
            , Cmd.batch
                [ clearCmd
                , pushUrl newUrl
                , clearAllCheckboxFacetsHelper
                , clearAllOneChoiceFacetsHelper
                , clearAllRangeFacetsHelper
                ]
            )

        UserClickedUpdateResults ->
            let
                updatedUrl =
                    buildQueryParameters model.currentQueryArgs
                        |> serverUrl [ "search/" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl

                cmds =
                    Cmd.batch
                        [ updateResultsCmd
                        , pushUrl updatedUrl
                        ]
            in
            ( model, cmds )


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


rangeFacetUpdateHelper :
    RangeFacetMsg
    -> FacetModel
    -> (Maybe RangeFacetModel -> FacetModel -> FacetModel)
    -> (FacetModel -> Maybe RangeFacetModel)
    -> Maybe ( FacetModel, Cmd RangeFacetMsg )
rangeFacetUpdateHelper subMsg model facetModelUpdateFn selector =
    facetUpdateHelper subMsg RangeFacet.update model facetModelUpdateFn selector


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


queryArgsUpdateHelper :
    QueryArgs
    -> Maybe FacetModel
    -> (List String -> QueryArgs -> QueryArgs)
    -> (FacetModel -> Maybe { a | selected : List FacetItem })
    -> QueryArgs
queryArgsUpdateHelper queryArgs facetBlock queryArgsUpdateFn selector =
    Maybe.map
        (\fm ->
            let
                fvalues =
                    Maybe.map (\g -> List.map .value g.selected) (selector fm)
                        |> Maybe.withDefault []
            in
            queryArgsUpdateFn fvalues queryArgs
        )
        facetBlock
        |> Maybe.withDefault queryArgs


oneChoiceQueryArgsUpdateHelper :
    QueryArgs
    -> Maybe FacetModel
    -> (List String -> QueryArgs -> QueryArgs)
    -> (FacetModel -> Maybe { a | selected : Maybe FacetItem })
    -> QueryArgs
oneChoiceQueryArgsUpdateHelper queryArgs facetBlock queryArgsUpdateFn selector =
    Maybe.map
        (\fm ->
            let
                fvalues =
                    Maybe.map
                        (\f ->
                            Maybe.map (\g -> g.value |> List.singleton) f.selected
                        )
                        (selector fm)
                        |> ME.join
                        |> Maybe.withDefault []
            in
            queryArgsUpdateFn fvalues queryArgs
        )
        facetBlock
        |> Maybe.withDefault queryArgs


rangeFacetQueryArgsUpdateHelper :
    QueryArgs
    -> Maybe FacetModel
    -> (Maybe ( String, String ) -> QueryArgs -> QueryArgs)
    -> (FacetModel -> Maybe { a | selected : Maybe ( Float, Float ) })
    -> QueryArgs
rangeFacetQueryArgsUpdateHelper queryArgs facetBlock queryArgsUpdateFn selector =
    let
        valueConverter num =
            if num == -1 then
                "*"

            else
                String.fromFloat num
    in
    Maybe.map
        (\fm ->
            let
                fvalues =
                    Maybe.map
                        (\f ->
                            Maybe.map (\( l, h ) -> ( valueConverter l, valueConverter h )) f.selected
                        )
                        (selector fm)
                        |> ME.join
            in
            queryArgsUpdateFn fvalues queryArgs
        )
        facetBlock
        |> Maybe.withDefault queryArgs


clearAllCheckboxFacetsHelper : Cmd Msg
clearAllCheckboxFacetsHelper =
    List.map
        (\f ->
            CE.perform (UserInteractedWithCheckboxFacet f CheckboxFacet.OnClear)
        )
        [ Genres, Composers, Notations, SourceComposers ]
        |> Cmd.batch


clearAllOneChoiceFacetsHelper : Cmd Msg
clearAllOneChoiceFacetsHelper =
    List.map
        (\f ->
            CE.perform (UserInteractedWithOneChoiceFacet f OneChoice.OnClear)
        )
        [ HasInventory
        , AnonymousComposer
        , Cities
        , SourceTypes
        , OriginalFormat
        , CurrentState
        , HostMainContents
        , OrganizationType
        ]
        |> Cmd.batch


clearAllRangeFacetsHelper : Cmd Msg
clearAllRangeFacetsHelper =
    CE.perform (UserInteractedWithRangeFacet DateRange RangeFacet.OnClear)


checkboxFacetHelper : Model -> CheckboxFacetTypes -> CheckBoxFacetMsg -> ( Model, Cmd Msg )
checkboxFacetHelper model facet subMsg =
    let
        updatedFacetData =
            let
                updatePartialHelper =
                    checkboxFacetUpdateHelper subMsg model.facets

                queryArgs =
                    model.currentQueryArgs

                queryPartialHelper =
                    queryArgsUpdateHelper queryArgs
            in
            case facet of
                Genres ->
                    let
                        upd =
                            updatePartialHelper setGenres .genres

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd
                    , queryArgs = queryPartialHelper fb setQueryGenres .genres
                    }

                Composers ->
                    let
                        upd =
                            updatePartialHelper setComposers .composers

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = queryPartialHelper fb setQueryComposers .composers }

                Notations ->
                    let
                        upd =
                            updatePartialHelper setNotations .notations

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = queryPartialHelper fb setQueryNotations .notations }

                SourceComposers ->
                    let
                        upd =
                            updatePartialHelper setSourceComposers .sourceComposers

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd
                    , queryArgs = queryPartialHelper fb setQuerySourceComposers .sourceComposers
                    }
    in
    Maybe.map
        (\( newFacetBlock, newSubCmd ) ->
            ( { model
                | facets = newFacetBlock
                , currentQueryArgs = updatedFacetData.queryArgs
                , needsUpdating = updatedFacetData.queryArgs /= model.currentQueryArgs
              }
            , Cmd.map (UserInteractedWithCheckboxFacet facet) newSubCmd
            )
        )
        updatedFacetData.facet
        |> Maybe.withDefault ( model, Cmd.none )


oneChoiceFacetHelper : Model -> OneChoiceFacetTypes -> OneChoiceFacetMsg -> ( Model, Cmd Msg )
oneChoiceFacetHelper model facet subMsg =
    let
        updatedFacetData =
            let
                updatePartialHelper =
                    oneChoiceFacetUpdateHelper subMsg model.facets

                queryArgs =
                    model.currentQueryArgs

                updateQueryHelper =
                    oneChoiceQueryArgsUpdateHelper queryArgs
            in
            case facet of
                HasInventory ->
                    let
                        upd =
                            updatePartialHelper setHasInventory .hasInventory

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryHasInventory .hasInventory
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                AnonymousComposer ->
                    let
                        upd =
                            updatePartialHelper setAnonymous .anonymous

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryAnonymous .anonymous
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                Cities ->
                    let
                        upd =
                            updatePartialHelper setCities .cities

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryCities .cities
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                SourceTypes ->
                    let
                        upd =
                            updatePartialHelper setSourceTypes .sourceTypes

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQuerySourceTypes .sourceTypes
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                OriginalFormat ->
                    let
                        upd =
                            updatePartialHelper setOriginalFormat .originalFormat

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryOriginalFormat .originalFormat
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                CurrentState ->
                    let
                        upd =
                            updatePartialHelper setCurrentState .currentState

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryCurrentState .currentState
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                HostMainContents ->
                    let
                        upd =
                            updatePartialHelper setHostMainContents .hostMainContents

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryHostMainContents .hostMainContents
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }

                OrganizationType ->
                    let
                        upd =
                            updatePartialHelper setOrganizationType .organizationType

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryOrganizationType .organizationType
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }
    in
    Maybe.map
        (\( newFacetBlock, newSubCmd ) ->
            ( { model
                | facets = newFacetBlock
                , currentQueryArgs = updatedFacetData.queryArgs
                , needsUpdating = updatedFacetData.queryArgs /= model.currentQueryArgs
              }
            , Cmd.map (UserInteractedWithOneChoiceFacet facet) newSubCmd
            )
        )
        updatedFacetData.facet
        |> Maybe.withDefault ( model, Cmd.none )


rangeFacetHelper : Model -> RangeFacetTypes -> RangeFacetMsg -> ( Model, Cmd Msg )
rangeFacetHelper model facet subMsg =
    let
        updatedFacetData =
            case facet of
                DateRange ->
                    let
                        updatePartialHelper =
                            rangeFacetUpdateHelper subMsg model.facets

                        queryArgs =
                            model.currentQueryArgs

                        updateQueryHelper =
                            rangeFacetQueryArgsUpdateHelper queryArgs

                        upd =
                            updatePartialHelper setDateRange .dateRange

                        fb =
                            Maybe.map Tuple.first upd

                        qargs =
                            updateQueryHelper fb setQueryDateRange .dateRange
                    in
                    { facet = upd
                    , queryArgs = qargs
                    }
    in
    Maybe.map
        (\( newFacetBlock, newSubCmd ) ->
            ( { model
                | facets = newFacetBlock
                , currentQueryArgs = updatedFacetData.queryArgs
                , needsUpdating = updatedFacetData.queryArgs /= model.currentQueryArgs
              }
            , Cmd.map (UserInteractedWithRangeFacet facet) newSubCmd
            )
        )
        updatedFacetData.facet
        |> Maybe.withDefault ( model, Cmd.none )
