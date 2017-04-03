import {
    ADD_ORGANIZATION_TYPE_TO_ACTIVE,
    RESET_ORGANIZATION_TYPE_FACET,
    CLEAR_ACTIVE_ORGANIZATION_TYPES,
    REMOVE_ORGANIZATION_TYPE_FROM_ACTIVE
} from "../constants";

const INITIAL_STATE = {
    showAll: false,
    active: [],
    facetValue: ""
};

export default function organizationTypes (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_ORGANIZATION_TYPE_FACET):
            return INITIAL_STATE;
        case (ADD_ORGANIZATION_TYPE_TO_ACTIVE):
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_ORGANIZATION_TYPES):
            return { ...state, active: [] };
        case (REMOVE_ORGANIZATION_TYPE_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value) };
        default:
            return state;
    }
}
