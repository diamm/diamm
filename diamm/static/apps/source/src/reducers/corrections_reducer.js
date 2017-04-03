import {
    UPDATE_CORRECTION_REPORT_TEXT,
    CORRECTION_REPORT_SUBMITTED
} from "../constants"

const INITIAL_STATE = {
    noteContents: "",
    submitted: false
};

export default function correctionsReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CORRECTION_REPORT_TEXT):
            return { ...state, noteContents: action.note };
        case (CORRECTION_REPORT_SUBMITTED):
            return { noteContents: "", submitted: true };
        default:
            return state;
    }
}
