import {
    SERVER_BASE_URL,
    UPDATE_CONTRIBUTORS
} from "../constants";
import {
    CONTRIBUTORS_ROUTE
} from "../routes";

export function fetchContributors (pk, objtype)
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.set('pk', pk);
        params.set('type', objtype);
        let qstring = params.toString();

        let url  = `${SERVER_BASE_URL}${CONTRIBUTORS_ROUTE}?${qstring}`;

        return fetch(url, {
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        }).then( (response) =>
        {
            return response.json();
        }).then( (payload) =>
        {
            dispatch({
                type: UPDATE_CONTRIBUTORS,
                payload
            })
        })
    }
}
