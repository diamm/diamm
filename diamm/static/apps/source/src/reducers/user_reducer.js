import { SET_USER_INFO } from "../constants";

const INITIAL_STATE = {
    username: null,
    isAuthenticated: false,
    isStaff: false,
    isSuperuser: false
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
