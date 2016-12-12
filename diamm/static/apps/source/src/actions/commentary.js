import _ from "lodash";

import {
    SERVER_BASE_URL,
    UPDATE_COMMENTARY
} from "../constants"

import {
    COMMENTARY_ROUTE
} from "../routes"


export function fetchCommentary (pk, objtype)
{
    return (dispatch) =>
    {
        let params = new URLSearchParams(window.location.search);
        params.set('pk', pk);
        params.set('type', objtype);
        let qstring = params.toString();
        let url = `${SERVER_BASE_URL}${COMMENTARY_ROUTE}?${qstring}`;

        console.log(url);

        return fetch(url, {
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        })
        .then( (response) =>
        {
            return response.json()
        })
        .then( (payload) =>
        {
            let groups = _.chain(payload.results).groupBy('comment_type').value();
            dispatch({
                type: UPDATE_COMMENTARY,
                public: groups[1],
                private: groups[0]
            })
        });
    }
}
