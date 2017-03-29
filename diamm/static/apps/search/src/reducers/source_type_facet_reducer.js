import {
    ADD_SOURCE_TYPE_TO_ACTIVE,
    CLEAR_ACTIVE_SOURCE_TYPES,
    REMOVE_SOURCE_TYPE_FROM_ACTIVE,
    UPDATE_CURRENT_SOURCE_TYPE_VALUE,
    RESET_SOURCE_TYPE_FACET
} from "../constants";

const INITIAL_STATE = {
    active: [],
    facetValue: ""
};

export default function sourceTypes (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_SOURCE_TYPE_FACET):
            return INITIAL_STATE;
        case (ADD_SOURCE_TYPE_TO_ACTIVE):
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_SOURCE_TYPES):
            return { ...state, active: [] };
        case (REMOVE_SOURCE_TYPE_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value)};
        case (UPDATE_CURRENT_SOURCE_TYPE_VALUE):
            return { ...state, facetValue: action.value };
        default:
            return state;
    }
}
