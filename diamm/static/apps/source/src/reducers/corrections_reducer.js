import {
    UPDATE_CORRECTION_REPORT_TEXT
} from "../constants"

const INITIAL_STATE = {
    noteContents: ""
};

export default function correctionsReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CORRECTION_REPORT_TEXT):
            return { ...state, noteContents: action.note };
        default:
            return state;
    }
}
