module Update exposing (update)

import Cmd.Extra as CE
import Facets exposing (FacetModel, createFacetConfigurations, setComposers, setGenres, setHasInventory, setNotations, setSourceTypes)
import Facets.CheckboxFacet as CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg)
import Facets.OneChoiceFacet as OneChoice exposing (OneChoiceFacetModel, OneChoiceFacetMsg)
import Facets.SelectFacet as SelectFacet exposing (SelectFacetModel, SelectFacetMsg)
import Maybe.Extra as ME
import Model exposing (Model)
import Msg exposing (Msg(..))
import Ports exposing (pushUrl)
import RecordTypes exposing (CheckboxFacetTypes(..), FacetItem, OneChoiceFacetTypes(..), SelectFacetTypes(..), searchBodyDecoder)
import Request exposing (Response(..), createRequest, serverUrl)
import Route exposing (QueryArgs, Route(..), buildQueryParameters, defaultQueryArgs, setCurrentPage, setKeywordQuery, setQueryGenres, setQueryNotations, setQuerySourceTypes, setQueryType)


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
                        |> serverUrl [ "search" ]

                updateResultsCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( model
            , Cmd.batch
                [ updateResultsCmd
                , pushUrl newUrl
                ]
            )

        UserInteractedWithCheckboxFacet facet subMsg ->
            let
                updatedFacet =
                    Maybe.map
                        (\facetBlock ->
                            case facet of
                                Genres ->
                                    let
                                        helperPartial =
                                            checkboxFacetUpdateHelper subMsg facetBlock
                                    in
                                    helperPartial setGenres .genres
                        )
                        model.facets
                        |> ME.join

                updatedQueryArgs =
                    case facet of
                        Genres ->
                            let
                                queryArgs =
                                    model.currentQueryArgs

                                facetBlock =
                                    Maybe.map Tuple.first updatedFacet

                                partialHelper =
                                    queryArgsUpdateHelper queryArgs facetBlock
                            in
                            partialHelper setQueryGenres .genres
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    let
                        updatedUrl =
                            buildQueryParameters updatedQueryArgs
                                |> serverUrl [ "search" ]

                        updateResultsCmd =
                            createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                    in
                    ( { model
                        | facets = Just newFacetBlock
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

                updatedQueryArgs =
                    let
                        queryArgs =
                            model.currentQueryArgs

                        facetBlock =
                            Maybe.map Tuple.first updatedFacet

                        partialHelper =
                            queryArgsUpdateHelper queryArgs facetBlock
                    in
                    case facet of
                        Composers ->
                            partialHelper setQueryGenres .genres

                        SourceTypes ->
                            partialHelper setQuerySourceTypes .sourceTypes

                        Notations ->
                            partialHelper setQueryNotations .notations
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    let
                        updatedUrl =
                            buildQueryParameters updatedQueryArgs
                                |> serverUrl [ "search" ]

                        updateResultsCmd =
                            createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                    in
                    ( { model | facets = Just newFacetBlock }
                    , Cmd.batch
                        [ updateResultsCmd
                        , Cmd.map (UserInteractedWithSelectFacet facet) newSubCmd
                        , pushUrl updatedUrl
                        ]
                    )
                )
                updatedFacet
                |> Maybe.withDefault ( model, Cmd.none )

        UserInteractedWithOneChoiceFacet facet subMsg ->
            let
                updatedFacet =
                    Maybe.map
                        (\facetBlock ->
                            case facet of
                                HasInventory ->
                                    let
                                        helperPartial =
                                            oneChoiceFacetUpdateHelper subMsg facetBlock
                                    in
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
                newUrl =
                    buildQueryParameters model.currentQueryArgs
                        |> serverUrl [ "search" ]

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
                        let
                            _ =
                                Debug.log "no command" ( currentPage, parsedPageNumber )
                        in
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
                                    |> serverUrl [ "search" ]
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
                        |> serverUrl [ "search" ]
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
                        |> serverUrl [ "search" ]

                clearCmd =
                    createRequest ServerRespondedWithSearchData searchBodyDecoder newUrl
            in
            ( model
            , Cmd.batch
                [ clearCmd
                , pushUrl newUrl
                , clearAllCheckboxFacetsHelper
                , clearAllSelectFacetsHelper
                , clearAllOneChoiceFacetsHelper
                ]
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


clearAllCheckboxFacetsHelper : Cmd Msg
clearAllCheckboxFacetsHelper =
    List.map (\f -> CE.perform (UserInteractedWithCheckboxFacet f CheckboxFacet.OnClear)) [ Genres ]
        |> Cmd.batch


clearAllSelectFacetsHelper : Cmd Msg
clearAllSelectFacetsHelper =
    List.map (\f -> CE.perform (UserInteractedWithSelectFacet f SelectFacet.OnClear)) [ Composers, SourceTypes, Notations ]
        |> Cmd.batch


clearAllOneChoiceFacetsHelper : Cmd Msg
clearAllOneChoiceFacetsHelper =
    List.map (\f -> CE.perform (UserInteractedWithOneChoiceFacet f OneChoice.OnClear)) [ HasInventory ]
        |> Cmd.batch
