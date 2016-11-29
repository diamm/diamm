import {
    UPDATE_CURRENT_QUERY_TERM
} from "../constants";


const INITIAL_STATE = "";

export default function currentQueryReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CURRENT_QUERY_TERM):
            return action.currentQuery;
        default:
            return state;
    }
}
