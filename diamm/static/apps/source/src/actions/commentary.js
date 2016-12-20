import _ from "lodash";

import {
    SERVER_BASE_URL,
    UPDATE_COMMENTARY,
    UPDATE_PRIVATE_COMMENT_TEXT,
    UPDATE_PUBLIC_COMMENT_TEXT,
    CLEAR_PRIVATE_COMMENT_TEXT,
    CLEAR_PUBLIC_COMMENT_TEXT
} from "../constants"
import Cookie from "js-cookie";

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
                public: groups[1] || [],
                private: groups[0] || []
            })
        });
    }
}

export function postComment (comment, privacy, objtype, objpk)
{
    return (dispatch) =>
    {
        let url = `${SERVER_BASE_URL}${COMMENTARY_ROUTE}/`;
        let csrftoken = Cookie.get('csrftoken');

        return fetch(url, {
            method: "POST",
            credentials: 'same-origin',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                comment: comment,
                comment_type: privacy === "public" ? 1 : 0,
                objtype: objtype,
                objpk: objpk
            })
        }).then( (response) => {
            switch(privacy)
            {
                case ("public"):
                    dispatch({
                        type: CLEAR_PUBLIC_COMMENT_TEXT
                    });
                case ("private"):
                    dispatch({
                        type: CLEAR_PRIVATE_COMMENT_TEXT
                    })
            }

            dispatch(
                fetchCommentary(objpk, objtype)
            );
        });
    }
}

export function updatePrivateCommentText (text)
{
    return {
        type: UPDATE_PRIVATE_COMMENT_TEXT,
        text
    }
}

export function updatePublicCommentText (text)
{
    return {
        type: UPDATE_PUBLIC_COMMENT_TEXT,
        text
    }
}
