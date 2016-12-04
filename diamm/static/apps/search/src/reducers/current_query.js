import {
    UPDATE_CURRENT_QUERY_TERM,
    RESET_CURRENT_QUERY
} from "../constants";


const INITIAL_STATE = "";

export default function currentQuery (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CURRENT_QUERY_TERM):
            return action.currentQuery;
        case (RESET_CURRENT_QUERY):
            return INITIAL_STATE;
        default:
            return state;
    }
}
