import {
    CLOSE_PROBLEM_REPORT_VIEW,
    OPEN_PROBLEM_REPORT_VIEW,
    UPDATE_PROBLEM_REPORT_TEXT
} from "../constants";
import { post } from "./api";


export function openProblemReport ()
{
    return {
        type: OPEN_PROBLEM_REPORT_VIEW
    }
}

export function closeProblemReport ()
{
    return {
        type: CLOSE_PROBLEM_REPORT_VIEW
    }
}

export function updateProblemReportText (note)
{
    return {
        type: UPDATE_PROBLEM_REPORT_TEXT,
        note
    }
}

export function submitProblemReport (text)
{
    return (dispatch) =>
    {
        return post("")
    }
}
