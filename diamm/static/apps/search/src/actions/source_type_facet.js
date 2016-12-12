import {
    ADD_SOURCE_TYPE_TO_ACTIVE,
    REMOVE_SOURCE_TYPE_FROM_ACTIVE,
    CLEAR_ACTIVE_SOURCE_TYPES,
    UPDATE_CURRENT_SOURCE_TYPE_VALUE
} from "../constants";
import { performSearch } from "./search_api";


export function updateCurrentSourceTypeValue (value)
{
    return {
        type: UPDATE_CURRENT_SOURCE_TYPE_VALUE,
        value
    }
}

export function addSourceTypeToActive (value)
{
    return {
        type: ADD_SOURCE_TYPE_TO_ACTIVE,
        value
    }
}

export function removeSourceTypeFromActive (value)
{
    return {
        type: REMOVE_SOURCE_TYPE_FROM_ACTIVE,
        value
    }
}

export function clearActiveSourceTypes ()
{
    return {
        type: CLEAR_ACTIVE_SOURCE_TYPES
    }
}

export function performSourceTypeSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeSourceTypes = currentState.currentFacets.sourceTypes.active
        let params = new URLSearchParams(window.location.search);
        params.delete('sourcetype');
        activeSourceTypes.map( (p) => params.append('sourcetype', p));
        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}
