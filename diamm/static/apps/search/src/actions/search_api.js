import {
    SERVER_BASE_URL,
    UPDATE_SEARCH_RESULTS
} from "../constants";


export function performSearch (qstring)
{
    return (dispatch) =>
    {
        let querystring = qstring ? `?${qstring}` : "";

        return fetch(`${SERVER_BASE_URL}${querystring}`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then( (response) => {
                return response.json();
            })
            .then( (payload) => {
                window.history.replaceState("", "", `${SERVER_BASE_URL}${querystring}`);
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

export function fetchPage (url)
{
    /*
    * URLs for individual pages come back from the server as full ones, so we just have to tweak
    * the fetch API bit slightly.
    * */
    return (dispatch) =>
    {
        return fetch(url, {
            headers: {
                "Accept": "application/json"
            }
        }).then( (response) => {
            return response.json();
        }).then( (payload) => {
            window.history.replaceState("", "", url);
            return dispatch(updateSearchResults(payload))
        })
    }
}
