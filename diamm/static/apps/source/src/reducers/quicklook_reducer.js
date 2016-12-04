import {
    OPEN_QUICKLOOK_VIEW,
    CLOSE_QUICKLOOK_VIEW
} from "../constants";


const INITIAL_STATE = {};

export default function quickLookReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (OPEN_QUICKLOOK_VIEW):
            return action.payload;
        case (CLOSE_QUICKLOOK_VIEW):
            return INITIAL_STATE;
        default:
            return state;
    }
}

