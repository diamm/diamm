import {
    FETCH_SOURCE_INFO,
    RECEIVE_SOURCE_INFO
} from "../constants";

// set the initial state to null so that we can easily check
// to see if the source information has loaded. When loaded this will
// be a JavaScript object containing all the source information.
const INITIAL_STATE = null;

export default function (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case RECEIVE_SOURCE_INFO:
            return action.payload;
        default:
            return state;
    }
}
