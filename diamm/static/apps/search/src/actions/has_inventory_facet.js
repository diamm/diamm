import {
    UPDATE_HAS_INVENTORY_VALUE,
    CLEAR_HAS_INVENTORY_VALUE
} from "../constants";
import { performSearch } from "./search_api";

export function updateHasInventoryValue (value)
{
    return {
        type: UPDATE_HAS_INVENTORY_VALUE,
        value
    }
}

export function clearHasInventoryValue ()
{
    return {
        type: CLEAR_HAS_INVENTORY_VALUE
    }
}

export function performHasInventorySearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeState = currentState.currentFacets.hasInventory.active;
        let params = new URLSearchParams(window.location.search);
        params.delete('has_inventory');

        // if the active value has been reset.
        if (activeState)
        {
            params.set('has_inventory', activeState);
        }

        let qstring = params.toString();

        return dispatch(
            performSearch(qstring)
        );
    }
}
