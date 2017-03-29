import {
    UPDATE_CONTRIBUTORS
} from "../constants"

// The response sent from the server will be a paginated response object, which
// we will use for the entire state object.
const INITIAL_STATE = null;

export default function contributorsReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CONTRIBUTORS):
            return action.payload;
        default:
            return state;
    }
}
