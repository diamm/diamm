import {
    ADD_CITIES_TO_ACTIVE,
    REMOVE_CITIES_FROM_ACTIVE,
    UPDATE_CURRENT_CITIES_VALUE,
    CLEAR_ACTIVE_CITIES,
    RESET_CITIES_FACET
} from "../constants";

const INITIAL_STATE = {
    active: [],
    facetValue: ""
}

export default function cities (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_CITIES_FACET):
            return INITIAL_STATE;
        case (UPDATE_CURRENT_CITIES_VALUE):
            return { ...state, facetValue: action.value };
        case (ADD_CITIES_TO_ACTIVE):
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_CITIES):
            return { ...state, active: []};
        case (REMOVE_CITIES_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value)};
        default:
            return state;
    }
}