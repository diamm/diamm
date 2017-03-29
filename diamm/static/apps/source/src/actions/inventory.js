import {
    SHOW_INVENTORY_DETAILS_FOR_ITEM,
    SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM
} from "../constants";


export function showInventoryDetailsForItem (index)
{
    return {
        type: SHOW_INVENTORY_DETAILS_FOR_ITEM,
        index
    }
}

export function showAlphaInventoryDetailsForItem (index)
{
    return {
        type: SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM,
        index
    }
}
