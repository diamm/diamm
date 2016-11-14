import { SET_USER_INFO } from "../actions/index";

const INITIAL_STATE = null;

export default function (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case SET_USER_INFO:
            return action.payload;
        default:
            return state;
    }
}
