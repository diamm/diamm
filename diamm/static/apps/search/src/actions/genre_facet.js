import {
    ADD_GENRE_TO_ACTIVE,
    REMOVE_GENRE_FROM_ACTIVE,
    CLEAR_ACTIVE_GENRES
} from "../constants";
import {
    performSearch
} from "./search_api";


export function addGenreToActive (value)
{
    return {
        type: ADD_GENRE_TO_ACTIVE,
        value
    }
}

export function removeGenreFromActive (value)
{
    return {
        type: REMOVE_GENRE_FROM_ACTIVE,
        value
    }
}

export function clearActiveGenres ()
{
    return {
        type: CLEAR_ACTIVE_GENRES
    }
}

export function performGenreSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeGenres = currentState.currentFacets.genres.active;

        let params = new URLSearchParams(window.location.search);
        params.delete('genre');
        activeGenres.map( (p) => params.append('genre', p));
        let qstring = params.toString();

        dispatch(
            performSearch(qstring)
        )
    }
}
