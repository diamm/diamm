import {
    ADD_NOTATION_TO_ACTIVE,
    REMOVE_NOTATION_FROM_ACTIVE,
    CLEAR_ACTIVE_NOTATIONS,
    UPDATE_CURRENT_NOTATION_VALUE,
    RESET_NOTATIONS_FACET
} from "../constants";


const INITIAL_STATE = {
    active: [],
    facetValue: ""
};

export default function notations (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_NOTATIONS_FACET):
            return INITIAL_STATE;
        case (UPDATE_CURRENT_NOTATION_VALUE):
            return { ...state, facetValue: action.value };
        case (ADD_NOTATION_TO_ACTIVE):
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_NOTATIONS):
            return { ...state, active: []};
        case (REMOVE_NOTATION_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value)};
        default:
            return state;
    }
}
