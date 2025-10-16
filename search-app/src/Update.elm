module Update exposing (update)

import Cmd.Extra as CE
import Facets exposing (FacetModel, setCities, setComposers, setGenres, setHasInventory, setNotations, setSourceTypes, updateFacetConfigurations)
import Facets.CheckboxFacet as CheckboxFacet exposing (CheckBoxFacetModel, CheckBoxFacetMsg)
import Facets.OneChoiceFacet as OneChoice exposing (OneChoiceFacetModel, OneChoiceFacetMsg)
import Helpers exposing (boolToStr)
import Maybe.Extra as ME
import Model exposing (Model)
import Msg exposing (Msg(..))
import Ports exposing (pushUrl)
import RecordTypes exposing (BooleanFacetItem, CheckboxFacetTypes(..), FacetItem, OneChoiceFacetTypes(..), searchBodyDecoder)
import Request exposing (Response(..), createRequest, serverUrl)
import Route exposing (QueryArgs, Route(..), buildQueryParameters, defaultQueryArgs, setCurrentPage, setKeywordQuery, setQueryCities, setQueryComposers, setQueryGenres, setQueryHasInventory, setQueryNotations, setQuerySourceTypes, setQueryType)


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
            facetUpdateHelperNoQuery model facet CheckboxFacet.OnToggleHide

        UserInteractedWithCheckboxFacet facet (CheckboxFacet.OnTextInput t) ->
            facetUpdateHelperNoQuery model facet (CheckboxFacet.OnTextInput t)

        UserInteractedWithCheckboxFacet facet subMsg ->
            let
                updatedFacet =
                    let
                        helperPartial =
                            checkboxFacetUpdateHelper subMsg model.facets
                    in
                    case facet of
                        Genres ->
                            helperPartial setGenres .genres

                        Composers ->
                            helperPartial setComposers .composers

                        SourceTypes ->
                            helperPartial setSourceTypes .sourceTypes

                        Notations ->
                            helperPartial setNotations .notations

                        Cities ->
                            helperPartial setCities .cities

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
                        Genres ->
                            partialHelper setQueryGenres .genres

                        Composers ->
                            partialHelper setQueryComposers .composers

                        SourceTypes ->
                            partialHelper setQuerySourceTypes .sourceTypes

                        Notations ->
                            partialHelper setQueryNotations .notations

                        Cities ->
                            partialHelper setQueryCities .cities
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    let
                        updatedUrl =
                            buildQueryParameters updatedQueryArgs
                                |> serverUrl [ "search/" ]

                        updateResultsCmd =
                            createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                    in
                    ( { model
                        | facets = newFacetBlock
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

        UserInteractedWithOneChoiceFacet facet OneChoice.OnToggleHide ->
            oneChoiceFacetHelperNoQuery model facet OneChoice.OnToggleHide

        UserInteractedWithOneChoiceFacet facet subMsg ->
            let
                updatedFacet =
                    let
                        helperPartial =
                            oneChoiceFacetUpdateHelper subMsg model.facets
                    in
                    case facet of
                        HasInventory ->
                            helperPartial setHasInventory .hasInventory

                updatedQueryArgs =
                    let
                        queryArgs =
                            model.currentQueryArgs

                        facetBlock =
                            Maybe.map Tuple.first updatedFacet

                        partialHelper =
                            oneChoiceQueryArgsUpdateHelper queryArgs facetBlock
                    in
                    case facet of
                        HasInventory ->
                            partialHelper setQueryHasInventory .hasInventory
            in
            Maybe.map
                (\( newFacetBlock, newSubCmd ) ->
                    let
                        updatedUrl =
                            buildQueryParameters updatedQueryArgs
                                |> serverUrl [ "search/" ]

                        updateResultsCmd =
                            createRequest ServerRespondedWithSearchData searchBodyDecoder updatedUrl
                    in
                    ( { model
                        | facets = newFacetBlock
                      }
                    , Cmd.batch
                        [ Cmd.map (UserInteractedWithOneChoiceFacet facet) newSubCmd
                        , pushUrl updatedUrl
                        , updateResultsCmd
                        ]
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
    -> (FacetModel -> Maybe { a | selected : Maybe BooleanFacetItem })
    -> QueryArgs
oneChoiceQueryArgsUpdateHelper queryArgs facetBlock queryArgsUpdateFn selector =
    Maybe.map
        (\fm ->
            let
                fvalues =
                    Maybe.map
                        (\f ->
                            Maybe.map (\g -> g.value |> boolToStr |> List.singleton) f.selected
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
    List.map (\f -> CE.perform (UserInteractedWithCheckboxFacet f CheckboxFacet.OnClear)) [ Genres, Composers, SourceTypes, Notations, Cities ]
        |> Cmd.batch


clearAllOneChoiceFacetsHelper : Cmd Msg
clearAllOneChoiceFacetsHelper =
    (\f -> CE.perform (UserInteractedWithOneChoiceFacet f OneChoice.OnClear)) HasInventory


facetUpdateHelperNoQuery : Model -> CheckboxFacetTypes -> CheckBoxFacetMsg -> ( Model, Cmd Msg )
facetUpdateHelperNoQuery model facet subMsg =
    let
        helperPartial =
            checkboxFacetUpdateHelper subMsg model.facets

        updatedFacets =
            case facet of
                Genres ->
                    helperPartial setGenres .genres

                Composers ->
                    helperPartial setComposers .composers

                SourceTypes ->
                    helperPartial setSourceTypes .sourceTypes

                Notations ->
                    helperPartial setNotations .notations

                Cities ->
                    helperPartial setCities .cities
    in
    Maybe.map
        (\( newFacetModel, newFacetCmd ) ->
            ( { model
                | facets = newFacetModel
              }
            , Cmd.map (UserInteractedWithCheckboxFacet facet) newFacetCmd
            )
        )
        updatedFacets
        |> Maybe.withDefault ( model, Cmd.none )


oneChoiceFacetHelperNoQuery : Model -> OneChoiceFacetTypes -> OneChoiceFacetMsg -> ( Model, Cmd Msg )
oneChoiceFacetHelperNoQuery model facet subMsg =
    let
        helperPartial =
            oneChoiceFacetUpdateHelper subMsg model.facets

        updatedFacets =
            case facet of
                HasInventory ->
                    helperPartial setHasInventory .hasInventory
    in
    Maybe.map
        (\( newFacetModel, newFacetCmd ) ->
            ( { model | facets = newFacetModel }
            , Cmd.map (UserInteractedWithOneChoiceFacet facet) newFacetCmd
            )
        )
        updatedFacets
        |> Maybe.withDefault ( model, Cmd.none )
