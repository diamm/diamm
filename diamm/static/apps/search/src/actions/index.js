import {
    UPDATE_CURRENT_QUERY_TERM,
    RESET_COMPOSERS_FACET,
    RESET_CURRENT_QUERY,
    RESET_CURRENT_QUERY_TYPE,
    RESET_ARCHIVE_LOCATION_FACET,
    RESET_HAS_INVENTORY_FACET,
    RESET_SOURCE_TYPE_FACET,
    RESET_NOTATIONS_FACET,
    RESET_GENRES_FACET
} from "../constants";
import {
    performSearch
} from "./search_api";

export function updateCurrentQueryTerm (currentQuery)
{
    return {
        type: UPDATE_CURRENT_QUERY_TERM,
        currentQuery
    };
}

export function performQueryTermSearch (query)
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.set('q', query);
        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}


export function performInitialPageLoadSearch ()
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        let qstring = params.toString() || "";

        return dispatch(
            performSearch(qstring)
        );
    }
}

export function clearAll ()
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);

        for (let p of params)
        {
            params.delete(p[0]);
        }

        let qstring = params.toString();

        dispatch(
            performSearch(qstring)
        );

        dispatch({
            type: RESET_COMPOSERS_FACET
        });

        dispatch({
            type: RESET_CURRENT_QUERY
        });

        dispatch({
            type: RESET_CURRENT_QUERY_TYPE
        });

        dispatch({
            type: RESET_ARCHIVE_LOCATION_FACET
        });

        dispatch({
            type: RESET_SOURCE_TYPE_FACET
        });

        dispatch({
            type: RESET_NOTATIONS_FACET
        });

        dispatch({
            type: RESET_HAS_INVENTORY_FACET
        });

        dispatch({
            type: RESET_GENRES_FACET
        });
    }
}
