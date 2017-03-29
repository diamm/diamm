import {
    UPDATE_CURRENT_COMPOSER_VALUE,
    ADD_COMPOSER_TO_ACTIVE,
    CLEAR_ACTIVE_COMPOSERS,
    RESET_COMPOSERS_FACET,
    REMOVE_COMPOSER_FROM_ACTIVE
} from "../constants";


const INITIAL_STATE = {
    active: [],
    facetValue: ""
};

export default function composers (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CURRENT_COMPOSER_VALUE):
            return { ...state, facetValue: action.value };
        case (ADD_COMPOSER_TO_ACTIVE):
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_COMPOSERS):
            return { ...state, active: []};
        case (REMOVE_COMPOSER_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value)};
        case (RESET_COMPOSERS_FACET):
            return INITIAL_STATE;
        default:
            return state;
    }
}
