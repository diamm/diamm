import {
    ADD_CITIES_TO_ACTIVE,
    CLEAR_ACTIVE_CITIES,
    REMOVE_CITIES_FROM_ACTIVE,
    UPDATE_CURRENT_CITIES_VALUE
} from "../constants";
import { performSearch } from "./search_api";

export function updateCurrentCitiesValue (value)
{
    return {
        type: UPDATE_CURRENT_CITIES_VALUE,
        value
    }
}

export function addCitiesToActive (value)
{
    return {
        type: ADD_CITIES_TO_ACTIVE,
        value
    }
}

export function removeCitiesFromActive (value)
{
    return {
        type: REMOVE_CITIES_FROM_ACTIVE,
        value
    }
}

export function clearActiveCities ()
{
    return {
        type: CLEAR_ACTIVE_CITIES
    }
}

export function performCitiesSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeCities = currentState.currentFacets.cities.active;
        let params = new URLSearchParams(window.location.search);
        params.delete('cities');
        activeCities.map( (p) => params.append('cities', p));
        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        )
    }
}