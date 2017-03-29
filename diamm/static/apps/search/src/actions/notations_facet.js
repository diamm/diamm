import {
    ADD_NOTATION_TO_ACTIVE,
    REMOVE_NOTATION_FROM_ACTIVE,
    CLEAR_ACTIVE_NOTATIONS,
    UPDATE_CURRENT_NOTATION_VALUE
} from "../constants";
import { performSearch } from "./search_api";

export function updateCurrentNotationValue (value)
{
    return {
        type: UPDATE_CURRENT_NOTATION_VALUE,
        value
    }
}

export function addNotationToActive (value)
{
    return {
        type: ADD_NOTATION_TO_ACTIVE,
        value
    }
}

export function removeNotationFromActive (value)
{
    return {
        type: REMOVE_NOTATION_FROM_ACTIVE,
        value
    }
}

export function clearActiveNotations ()
{
    return {
        type: CLEAR_ACTIVE_NOTATIONS
    }
}

export function performNotationSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeNotations = currentState.currentFacets.notations.active;
        let params = new URLSearchParams(window.location.search);
        params.delete('notation');
        activeNotations.map( (p) => params.append('notation', p));
        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}
