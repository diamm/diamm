import {
    UPDATE_CURRENT_QUERY_TYPE,
    RESET_CURRENT_QUERY_TYPE
} from "../constants";


const INITIAL_STATE = "all";

export default function currentQueryType (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CURRENT_QUERY_TYPE):
            return action.facettype;
        case (RESET_CURRENT_QUERY_TYPE):
            return INITIAL_STATE;
        default:
            return state;
    }
}
