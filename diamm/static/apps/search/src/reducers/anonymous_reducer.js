import {
    CLEAR_ANONYMOUS_VALUE,
    UPDATE_ANONYMOUS_VALUE,
    RESET_ANONYMOUS_FACET
} from "../constants";

const INITIAL_STATE = {
    active: ""      // only one value can be active at a time.
};

export default function anonymous (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_ANONYMOUS_FACET):
            return INITIAL_STATE;
        case (UPDATE_ANONYMOUS_VALUE):
            return { ...state, active: action.value };
        case (CLEAR_ANONYMOUS_VALUE):
            return { ...state, active: "" };
        default:
            return state;
    }
}
