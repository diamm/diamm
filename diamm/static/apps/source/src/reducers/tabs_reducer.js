import {
    SET_ACTIVE_TAB,
} from "../constants";

const INITIAL_STATE = {
    activeTab: null,
};

export default function (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case SET_ACTIVE_TAB:
            return { ...state, activeTab: action.tab };
        default:
            return state;
    }
}
