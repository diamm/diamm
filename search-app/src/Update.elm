module Update exposing (update)

import Cmd.Extra as CE
import Facets exposing (FacetModel, setAnonymous, setCities, setComposers, setCurrentState, setGenres, setHasInventory, setHostMainContents, setNotations, setOrganizationType, setOriginalFormat, setSourceComposers, setSourceTypes, updateFacetConfigurations)
import Facets.CheckboxFacet as CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg)
import Facets.OneChoiceFacet as OneChoice exposing (OneChoiceFacetModel, OneChoiceFacetMsg)
import Maybe.Extra as ME
import Model exposing (Model)
import Msg exposing (Msg(..))
import Ports exposing (pushUrl)
import RecordTypes exposing (CheckboxFacetTypes(..), FacetItem, OneChoiceFacetTypes(..), searchBodyDecoder)
import Request exposing (Response(..), createRequest, serverUrl)
import Route exposing (QueryArgs, Route(..), buildQueryParameters, defaultQueryArgs, setCurrentPage, setKeywordQuery, setQueryAnonymous, setQueryCities, setQueryComposers, setQueryCurrentState, setQueryGenres, setQueryHasInventory, setQueryHostMainContents, setQueryNotations, setQueryOrganizationType, setQueryOriginalFormat, setQuerySourceComposers, setQuerySourceTypes, setQueryType)


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
              }
            , Cmd.none
            )

        ServerRespondedWithSearchData (Err error) ->
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
            checkboxFacetHelper False model facet CheckboxFacet.OnToggleHide

        UserInteractedWithCheckboxFacet facet (CheckboxFacet.OnTextInput t) ->
            checkboxFacetHelper False model facet (CheckboxFacet.OnTextInput t)

        UserInteractedWithCheckboxFacet facet subMsg ->
            checkboxFacetHelper True model facet subMsg

        UserInteractedWithOneChoiceFacet facet OneChoice.OnToggleHide ->
            oneChoiceFacetHelper False model facet OneChoice.OnToggleHide

        UserInteractedWithOneChoiceFacet facet (OneChoice.OnTextInput t) ->
            oneChoiceFacetHelper False model facet (OneChoice.OnTextInput t)

        UserInteractedWithOneChoiceFacet facet subMsg ->
            oneChoiceFacetHelper True model facet subMsg

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
                ]
            )


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


checkboxFacetHelper : Bool -> Model -> CheckboxFacetTypes -> CheckBoxFacetMsg -> ( Model, Cmd Msg )
checkboxFacetHelper emitRequest model facet subMsg =
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
                    { facet = upd, queryArgs = queryPartialHelper fb setQueryGenres .genres }

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
            let
                cmds =
                    if emitRequest then
                        let
                            updatedUrl =
                                buildQueryParameters updatedFacetData.queryArgs
                                    |> serverUrl [ "search/" ]

                            updateResultsCmd =
                                createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                        in
                        Cmd.batch
                            [ updateResultsCmd
                            , Cmd.map (UserInteractedWithCheckboxFacet facet) newSubCmd
                            , pushUrl updatedUrl
                            ]

                    else
                        Cmd.map (UserInteractedWithCheckboxFacet facet) newSubCmd
            in
            ( { model
                | facets = newFacetBlock
              }
            , cmds
            )
        )
        updatedFacetData.facet
        |> Maybe.withDefault ( model, Cmd.none )


oneChoiceFacetHelper : Bool -> Model -> OneChoiceFacetTypes -> OneChoiceFacetMsg -> ( Model, Cmd Msg )
oneChoiceFacetHelper emitRequest model facet subMsg =
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
                    in
                    { facet = upd
                    , queryArgs = updateQueryHelper fb setQueryHasInventory .hasInventory
                    }

                AnonymousComposer ->
                    let
                        upd =
                            updatePartialHelper setAnonymous .anonymous

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd
                    , queryArgs = updateQueryHelper fb setQueryAnonymous .anonymous
                    }

                Cities ->
                    let
                        upd =
                            updatePartialHelper setCities .cities

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = updateQueryHelper fb setQueryCities .cities }

                SourceTypes ->
                    let
                        upd =
                            updatePartialHelper setSourceTypes .sourceTypes

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = updateQueryHelper fb setQuerySourceTypes .sourceTypes }

                OriginalFormat ->
                    let
                        upd =
                            updatePartialHelper setOriginalFormat .originalFormat

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = updateQueryHelper fb setQueryOriginalFormat .originalFormat }

                CurrentState ->
                    let
                        upd =
                            updatePartialHelper setCurrentState .currentState

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = updateQueryHelper fb setQueryCurrentState .currentState }

                HostMainContents ->
                    let
                        upd =
                            updatePartialHelper setHostMainContents .hostMainContents

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd, queryArgs = updateQueryHelper fb setQueryHostMainContents .hostMainContents }

                OrganizationType ->
                    let
                        upd =
                            updatePartialHelper setOrganizationType .organizationType

                        fb =
                            Maybe.map Tuple.first upd
                    in
                    { facet = upd
                    , queryArgs = updateQueryHelper fb setQueryOrganizationType .organizationType
                    }
    in
    Maybe.map
        (\( newFacetBlock, newSubCmd ) ->
            let
                cmds =
                    if emitRequest then
                        let
                            updatedUrl =
                                buildQueryParameters updatedFacetData.queryArgs
                                    |> serverUrl [ "search/" ]

                            updateResultsCmd =
                                createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                        in
                        Cmd.batch
                            [ updateResultsCmd
                            , Cmd.map (UserInteractedWithOneChoiceFacet facet) newSubCmd
                            , pushUrl updatedUrl
                            ]

                    else
                        Cmd.map (UserInteractedWithOneChoiceFacet facet) newSubCmd
            in
            ( { model
                | facets = newFacetBlock
              }
            , cmds
            )
        )
        updatedFacetData.facet
        |> Maybe.withDefault ( model, Cmd.none )
