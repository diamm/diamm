import {
    UPDATE_SEARCH_RESULTS
} from "../constants";

const INITIAL_STATE = {};

export default function resultsReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_SEARCH_RESULTS):
            return action.results;
        default:
            return state;
    }
}
