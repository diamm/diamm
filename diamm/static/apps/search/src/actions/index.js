import {
    SERVER_BASE_URL,
    UPDATE_CURRENT_QUERY_TERM,
    UPDATE_SEARCH_RESULTS
} from "../constants";
import "whatwg-fetch";


export function updateCurrentQueryTerm (currentQuery)
{
    return {
        type: UPDATE_CURRENT_QUERY_TERM,
        currentQuery
    };
}

export function performSearch (queryValue)
{
    console.log('Perform search ' + queryValue);
    let params = { q: queryValue };
    let qstring = Object.keys(params).map(k => encodeURIComponent(k) + "=" + encodeURIComponent(params[k])).join("&");
    qstring = "?" + qstring;

    return (dispatch) =>
    {
        console.log("fetching");

        return fetch(`${SERVER_BASE_URL}${qstring}`, {
                headers: {
                    "Accept": "application/json"
                }
            })
            .then( (response) => {
                return response.json();
            })
            .then( (payload) => {
                window.history.replaceState("", "", `${SERVER_BASE_URL}${qstring}`);
                return dispatch(updateSearchResults(payload))
            });
    };
}

export function updateSearchResults (results)
{
    return {
        type: UPDATE_SEARCH_RESULTS,
        results
    };
}
