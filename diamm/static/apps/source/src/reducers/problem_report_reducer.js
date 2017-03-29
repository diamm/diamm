import {
    OPEN_PROBLEM_REPORT_VIEW,
    CLOSE_PROBLEM_REPORT_VIEW,
    UPDATE_PROBLEM_REPORT_TEXT
} from "../constants";

const INITIAL_STATE = {
    visible: false,
    noteContents: ""
};

export default function problemReportReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (OPEN_PROBLEM_REPORT_VIEW):
            return { ...state, visible: true };
        case (CLOSE_PROBLEM_REPORT_VIEW):
            return { ...state, visible: false };
        case (UPDATE_PROBLEM_REPORT_TEXT):
            return { ...state, noteContents: action.note };
        default:
            return state;
    }
}
