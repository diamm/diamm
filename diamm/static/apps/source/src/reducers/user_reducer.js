import { SET_USER_INFO } from "../constants";

const INITIAL_STATE = {
    username: null,
    isAuthenticated: null,
    isStaff: null,
    isSuperuser: null
};

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
