import {
    UPDATE_CORRECTION_REPORT_TEXT,
    CORRECTION_REPORT_SUBMITTED,
    CORRECTION_REPORT_SUBMITTING
} from "../constants"

const INITIAL_STATE = {
    noteContents: "",
    submitted: false,
    submitting: false
};

export default function correctionsReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CORRECTION_REPORT_TEXT):
            return { ...state, noteContents: action.note };
        case (CORRECTION_REPORT_SUBMITTING):
            return { ...state, submitting: true };
        case (CORRECTION_REPORT_SUBMITTED):
            return { noteContents: "", submitted: true, submitting: false };
        default:
            return state;
    }
}
