import {
    CLEAR_HAS_INVENTORY_VALUE,
    UPDATE_HAS_INVENTORY_VALUE,
    RESET_HAS_INVENTORY_FACET
} from "../constants";

const INITIAL_STATE = {
    active: ""      // only one value can be active at a time.
};

export default function hasInventory (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_HAS_INVENTORY_FACET):
            return INITIAL_STATE;
        case (UPDATE_HAS_INVENTORY_VALUE):
            return { ...state, active: action.value };
        case (CLEAR_HAS_INVENTORY_VALUE):
            return { ...state, active: "" };
        default:
            return state;
    }
}
