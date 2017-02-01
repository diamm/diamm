import {
    CORRECTION_REPORT_SUBMITTED,
    UPDATE_CORRECTION_REPORT_TEXT,
    SERVER_BASE_URL,
} from "../constants";
import Cookie from "js-cookie";
import {
    CORRECTIONS_ROUTE
} from "../routes";


export function updateCorrectionReportText (note)
{
    return {
        type: UPDATE_CORRECTION_REPORT_TEXT,
        note
    }
}

export function submitCorrectionReport (text, sourceId)
{
    return (dispatch) =>
    {
        let url = `${SERVER_BASE_URL}${CORRECTIONS_ROUTE}/`;
        let csrftoken = Cookie.get('csrftoken');
        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                objtype: "source",
                objpk: sourceId,
                note: text
            })
        })
        .then( (response) =>
        {
            return response.json();
        })
        .then( (payload) =>
        {
            dispatch({
                type: CORRECTION_REPORT_SUBMITTED
            })
        });
    }
}
