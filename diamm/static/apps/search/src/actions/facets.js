import {
    performSearch
} from "./search_api";

import {
    UPDATE_CURRENT_QUERY_TYPE,
    UPDATE_ARCHIVE_LOCATION_FACET,
    RESET_ARCHIVE_LOCATION_FACET,
    UPDATE_CURRENT_COMPOSER_VALUE
} from "../constants";


export function updateCurrentComposerValue (value)
{
    return {
        type: UPDATE_CURRENT_COMPOSER_VALUE,
        value
    }
}

export function performComposerSearch (value)
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.set('composers_ss', value);
        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}

/*
*
* Accepts a value and an action type and just forwards both to the reducer.
*
* */
export function toggleFacetShowAll (toggle, type)
{
    return { type, toggle }
}


export function performTypeFacetQuery (type)
{
    return (dispatch) => {
        let params = new URLSearchParams(window.location.search);

        params.set('type', type);

        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}

export function setActiveTypeFacet (facettype)
{
    return {
        type: UPDATE_CURRENT_QUERY_TYPE,
        facettype
    }
}


export function setArchiveLocationFacet (activeType, activeSelect)
{
    return {
        type: UPDATE_ARCHIVE_LOCATION_FACET,
        activeType,
        activeSelect
    }
}

export function performArchiveLocationQuery (activeType, activeSelect)
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.delete('country_s');
        params.delete('city_s');

        params.set(activeType, activeSelect);
        let qstring = params.toString();

        dispatch(
            performSearch(qstring)
        );

    };
}

export function resetArchiveLocationFacet ()
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.delete('country_s');
        params.delete('city_s');

        let qstring = params.toString();

        dispatch(
            performSearch(qstring)
        );

        dispatch({
            type: RESET_ARCHIVE_LOCATION_FACET
        })
    };
}
