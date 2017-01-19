import {
    SHOW_INVENTORY_DETAILS_FOR_ITEM,
    SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM
} from "../constants";


// active items contain integers pointing to the array indexes in the source inventory.
const INITIAL_STATE = {
    activeSourceOrderItem: null,
    activeAlphaOrderItem: null
};


export default function inventoryReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (SHOW_INVENTORY_DETAILS_FOR_ITEM):
            return { ...state, activeSourceOrderItem: action.index };
        case (SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM):
            return { ...state, activeAlphaOrderItem: action.index };
        default:
            return state;
    }
}
