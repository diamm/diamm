import {
    UPDATE_ANONYMOUS_VALUE,
    CLEAR_ANONYMOUS_VALUE
} from "../constants";
import { performSearch } from "./search_api";

export function updateAnonymousValue (value)
{
    return {
        type: UPDATE_ANONYMOUS_VALUE,
        value
    }
}

export function clearAnonymousValue ()
{
    return {
        type: CLEAR_ANONYMOUS_VALUE
    }
}

export function performAnonymousSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeState = currentState.currentFacets.anonymous.active;
        let params = new URLSearchParams(window.location.search);
        params.delete('anonymous');

        // if the active value has been reset.
        if (activeState)
        {
            params.set('anonymous', activeState);
        }

        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        );
    }
}
